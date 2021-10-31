import asyncio
import json
import logging
import time
from typing import Any

import websockets

logging.basicConfig(level=logging.DEBUG)


class User:
    websocket: Any = None
    last_message: float = time.time()
    has_voted: bool = False

    def register(self, websocket: Any):
        self.websocket = websocket
        USERS.add(self)
        logging.debug(
            f"user registered: {self}",
        )

    def unregister(self):
        # self.websocket.close()
        USERS.remove(self)
        logging.debug(
            f"user unregistered: {self}",
        )

    def __str__(self) -> str:
        return f"{self.websocket.remote_address} ({self.websocket.id})"


USERS: set[User] = set()
EMULATOR: Any = None
PASSWORD: str = "password"

VOTES: dict[str, int] = {
    "a": 0,
    "b": 0,
    "select": 0,
    "start": 0,
    "right": 0,
    "left": 0,
    "up": 0,
    "down": 0,
    "r": 0,
    "l": 0,
}


def clear_votes():
    for key in VOTES.keys():
        VOTES[key] = 0
    for user in USERS:
        user.has_voted = False
    logging.info(f"votes cleared: {VOTES}")


def next_move():
    if any(VOTES.values()):
        return max(VOTES, key=VOTES.get)
    else:
        return "null"


async def handler(websocket, path):
    try:
        global EMULATOR

        # Register user
        user = User()
        user.register(websocket)

        # Manage received messages
        async for message in websocket:
            data = json.loads(message)

            if "auth" in data:
                auth: str = data["auth"]
                logging.debug(f"auth received: {auth}")
                if not EMULATOR and auth == PASSWORD:
                    EMULATOR = websocket
                    user.unregister()
                    logging.debug(f"emulator authenticated: {EMULATOR}")

            if "action" in data:
                action: str = data["action"]

                if action in VOTES:
                    VOTES[action] += 1
                    user.last_message = time.time()
                    user.has_voted = True
                    logging.debug(f"key received: {action} ({VOTES[action]}), from {user}")
                else:
                    logging.error(f"unsupported action: {data}")

            if "admin" in data:
                admin = data["admin"]

                print(admin)

                if admin == "save":
                    await EMULATOR.send('{"admin":"save"}')
                elif admin == "load":
                    await EMULATOR.send('{"admin":"load"}')
                else:
                    logging.error(f"unsupported admin: {admin}")

            if "emu" in data:
                emu: str = data["emu"]

                if emu == "get":
                    if EMULATOR and websocket == EMULATOR:
                        move = next_move()
                        await EMULATOR.send(f'{{"action":"{move}"}}')
                        logging.info(f"vote sent: {move}")
                        clear_votes()
                    else:
                        logging.error(f"user is not EMULATOR: {user}")
                else:
                    logging.error(f"unsupported emu: {data}")

    finally:
        # Unregister user
        user.unregister()


async def main():
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
