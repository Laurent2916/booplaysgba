"""Emulator server, responsible for handling user inputs and outputting video & sound."""

import asyncio
import logging
import os
import threading
import time
from subprocess import PIPE, Popen  # nosec

import mgba.core
import mgba.image
import mgba.log
import redis

import utils
from settings import (
    EMULATOR_FPS,
    EMULATOR_HEIGHT,
    EMULATOR_POLLING_RATE,
    EMULATOR_ROM_PATH,
    EMULATOR_SPF,
    EMULATOR_WIDTH,
    FFMPEG_BITRATE,
    FFMPEG_FPS,
    FFMPEG_HEIGHT,
    FFMPEG_WIDTH,
    KEYS_ID,
    KEYS_MGBA,
    KEYS_RESET,
    REDIS_HOST,
    REDIS_PORT,
    RTMP_STREAM_URI,
)

core: mgba.core.Core = mgba.core.load_path(EMULATOR_ROM_PATH)
screen: mgba.image.Image = mgba.image.Image(EMULATOR_WIDTH, EMULATOR_HEIGHT)
core.set_video_buffer(screen)
core.reset()

logging.basicConfig(level=logging.DEBUG)
mgba.log.silence()

r: redis.Redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


# Launch ffmpeg process
stream = Popen(
    [
        "/usr/bin/ffmpeg",
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        f"{EMULATOR_FPS}",
        "-s",
        f"{EMULATOR_WIDTH}x{EMULATOR_HEIGHT}",
        "-i",
        "-",
        "-f",
        "flv",
        "-s",
        f"{FFMPEG_WIDTH}x{FFMPEG_HEIGHT}",
        "-r",
        f"{FFMPEG_FPS}",
        "-b:v",
        FFMPEG_BITRATE,
        "-fflags",
        "nobuffer",
        "-flags",
        "low_delay",
        "-strict",
        "experimental",
        # "-loglevel",
        # "quiet",
        RTMP_STREAM_URI,
    ],
    stdin=PIPE,
)


def next_action():
    """Select the next key from the redis database.

    Returns:
        int: key used by mgba.
    """
    votes: list[int] = list(map(int, r.mget(KEYS_ID)))
    if any(votes):
        r.mset(KEYS_RESET)
        return votes.index(max(votes))
    else:
        return -1


def state_manager(loop: asyncio.AbstractEventLoop):
    """Subscribe and respond to messages received from redis.

    Args:
        loop (asyncio.AbstractEventLoop): the asyncio event loop.
    """
    ps = r.pubsub()
    ps.subscribe("admin")

    while True:
        for message in ps.listen():
            if message["type"] == "message":
                match message["data"].decode("utf-8").split(":"):
                    case ["save"]:
                        asyncio.ensure_future(utils.save(core), loop=loop)
                    case ["load", filename]:
                        asyncio.ensure_future(utils.load(core, filename), loop=loop)
                    case _:
                        print(f"Command not understood: {message}")


async def emulator():
    """Start the main loop responsible for handling inputs and sending images to ffmpeg."""
    while True:
        last_frame_t = time.time()

        # poll redis for keys
        if not (core.frame_counter % EMULATOR_POLLING_RATE):
            core.clear_keys(*KEYS_MGBA)
            next_key = next_action()
            if next_key != -1:
                core.set_keys(next_key)

        # mGBA run next frame
        core.run_frame()

        # save frame to PNG image
        image = screen.to_pil().convert("RGB")
        image.save(stream.stdin, "PNG")

        # sleep until next frame, if necessary
        sleep_t = last_frame_t - time.time() + EMULATOR_SPF
        if sleep_t > 0:
            await asyncio.sleep(sleep_t)


async def main():
    """Start the emulator."""
    loop = asyncio.get_event_loop()

    # setup states in redis
    files = os.listdir("states")
    states = list(filter(lambda x: x.endswith(".state"), files))
    for state in states:
        r.sadd("states", state.removesuffix(".state"))  # voir si oneline possible

    # launch the thread to save/load states/games
    thread = threading.Thread(target=state_manager, args=(loop,))
    thread.start()

    # launch the event loop, which the emulator relies on
    task_emulator = loop.create_task(emulator())
    await task_emulator


if __name__ == "__main__":
    asyncio.run(main())

    # TODO: write code when ctrl+C -> save redis database ?
