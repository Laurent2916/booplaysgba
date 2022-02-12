"""Emulator server, responsible for handling user inputs and outputting video & sound."""

import asyncio
import logging
import random
import time

import mgba.core
import mgba.image
import mgba.log
import redis

from ffmpeg_manager import ffmpeg_stream
from redis_manager import RedisManager
from settings import (
    EMULATOR_HEIGHT,
    EMULATOR_POLLING_RATE,
    EMULATOR_RAND_RATE,
    EMULATOR_ROM_PATH,
    EMULATOR_SPF,
    EMULATOR_WIDTH,
    KEYS_ID,
    KEYS_MGBA,
    KEYS_RESET,
    REDIS_HOST,
    REDIS_PORT,
)
from state_manager import StateManager


def next_action(core: mgba.core.Core) -> None:
    """Select the next key from the redis database.

    Returns:
        int: key used by mgba.
    """
    votes: list[int] = list(map(int, r.mget(KEYS_ID)))
    if any(votes):
        r.mset(KEYS_RESET)
        core.set_keys(votes.index(max(votes)))
    elif EMULATOR_RAND_RATE != 0.0 and random.random() < EMULATOR_RAND_RATE:
        core.set_keys(random.choice(KEYS_MGBA))
    else:
        core.clear_keys(*KEYS_MGBA)


async def emulator() -> None:
    """Start the main loop responsible for handling inputs and sending images to ffmpeg."""
    while True:
        last_frame_t = time.time()

        # poll redis for keys
        if not (core.frame_counter % EMULATOR_POLLING_RATE):
            next_action(core)

        # mGBA run next frame
        core.run_frame()

        # save frame to PNG image
        image = screen.to_pil().convert("RGB")
        image.save(ffmpeg_stream.stdin, "PNG")

        # TODO: get audio

        # sleep until next frame, if necessary
        sleep_t = last_frame_t - time.time() + EMULATOR_SPF
        if sleep_t > 0:
            await asyncio.sleep(sleep_t)


async def main() -> None:
    """Start the emulator."""
    logging.debug("Emulator started !")
    loop = asyncio.get_event_loop()

    # launch the thread to manage state files
    state_manager = StateManager(r)
    state_manager.start()

    # launch the thread to manage incoming messages from redis
    redis_manager = RedisManager(r, loop, core)
    redis_manager.start()

    # launch the event loop, which the emulator relies on
    task_emulator = loop.create_task(emulator())
    await task_emulator


if __name__ == "__main__":
    # setup mGBA emulator
    core: mgba.core.Core = mgba.core.load_path(EMULATOR_ROM_PATH)
    screen: mgba.image.Image = mgba.image.Image(EMULATOR_WIDTH, EMULATOR_HEIGHT)
    core.set_video_buffer(screen)
    core.reset()

    # setup logging format
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)-8s  %(message)s", datefmt="(%F %T)"
    )

    # change log levels for some libs
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("asyncio.coroutines").setLevel(logging.ERROR)
    logging.getLogger("watchdog.observers").setLevel(logging.ERROR)
    mgba.log.silence()

    # connect to redis database
    r: redis.Redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    # TODO: handle signals (SIGINT, ...)

    # start the emulator
    asyncio.run(main())
