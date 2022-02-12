import asyncio
import logging
import threading
import time

import mgba.core
import redis
from mgba._pylib import ffi


async def save(core: mgba.core.Core) -> None:
    state = core.save_raw_state()
    current_time = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(f"states/{current_time}.state", "wb") as state_file:
        for byte in state:
            state_file.write(byte.to_bytes(4, byteorder="big", signed=False))
    logging.debug(f"state saved : {current_time}.state")


async def load(core: mgba.core.Core, filename: str) -> None:
    state = ffi.new("unsigned char[397312]")  # pulled 397312 straight from my ass, TODO: check mGBA sources ?
    with open(f"states/{filename}.state", "rb") as state_file:
        for i in range(len(state)):
            state[i] = int.from_bytes(state_file.read(4), byteorder="big", signed=False)
    core.load_raw_state(state)
    logging.debug(f"state loaded : {filename}")


class RedisManager(threading.Thread):
    def __init__(self, redis: redis.Redis, loop: asyncio.AbstractEventLoop, core: mgba.core.Core) -> None:
        super().__init__()

        self.loop = loop
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe("admin")
        self.core = core

    def parse_message(self, message: dict[str, str]) -> None:
        if message["type"] == "message":
            match message["data"].decode("utf-8").split(":", 1):
                case ["save"]:
                    asyncio.ensure_future(save(self.core), loop=self.loop)
                case ["load", filename]:
                    asyncio.ensure_future(load(self.core, filename), loop=self.loop)
                case _:
                    logging.debug(f"Command not understood: {message}")

    def run(self) -> None:
        while True:
            for message in self.pubsub.listen():
                self.parse_message(message)