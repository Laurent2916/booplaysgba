import asyncio
import logging
import time
from subprocess import PIPE, Popen  # nosec

import mgba.core
import mgba.image
import mgba.log
import redis

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

core = mgba.core.load_path(EMULATOR_ROM_PATH)
screen = mgba.image.Image(EMULATOR_WIDTH, EMULATOR_HEIGHT)
core.set_video_buffer(screen)
core.reset()

logging.basicConfig(level=logging.DEBUG)
mgba.log.silence()
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def next_action():
    """Select the next key from the redis database.

    Returns:
        int: key used by mgba
    """
    votes: list[int] = list(map(int, r.mget(KEYS_ID)))
    if any(votes):
        r.mset(KEYS_RESET)
        return votes.index(max(votes))
    else:
        return -1


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


async def state_manager():
    ps = r.pubsub()
    ps.subscribe("admin")
    while True:
        message = ps.get_message(ignore_subscribe_messages=True)
        if message is not None:
            logging.debug(message)
        await asyncio.sleep(5.0)


async def emulator():
    while True:
        last_frame_t = time.time()

        if not (core.frame_counter % EMULATOR_POLLING_RATE):
            core.clear_keys(*KEYS_MGBA)
            next_key = next_action()
            if next_key != -1:
                core.set_keys(next_key)

        core.run_frame()

        image = screen.to_pil().convert("RGB")
        image.save(stream.stdin, "PNG")

        sleep_t = last_frame_t - time.time() + EMULATOR_SPF
        if sleep_t > 0:
            # time.sleep(sleep_t)
            await asyncio.sleep(sleep_t)


async def main():
    task_emulator = asyncio.create_task(emulator())
    task_state_manager = asyncio.create_task(state_manager())
    await task_emulator
    await task_state_manager


if __name__ == "__main__":
    asyncio.run(main())
