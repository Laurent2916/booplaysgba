import asyncio
import json
import logging
import time
from typing import Any

import websockets

logging.basicConfig(level=logging.DEBUG)


class User:
    """Store infos related to a connected user."""

    websocket: Any = None
    last_message: float = time.time()
    has_voted: bool = False

    def register(self, websocket: Any):
        """Register a user in the `USERS` set.

        Args:
            websocket (Any): the websocket used by the user.
        """
        self.websocket = websocket
        USERS.add(self)
        logging.debug(
            f"user registered: {self}",
        )

    def unregister(self):
        """Unregister a user from the `USERS` set."""
        # self.websocket.close()
        USERS.remove(self)
        logging.debug(
            f"user unregistered: {self}",
        )

    async def send(self, data: str):
        """Send data through the user's websocket.

        Args:
            data (str): message to send.
        """
        self.websocket.send(data)

    def __str__(self) -> str:
        """Convert user to string.

        Returns:
            str: string representing the user.
        """
        return f"{self.websocket.remote_address} ({self.websocket.id})"


USERS: set[User] = set()
EMULATOR: User
ADMIN: User
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
    """Clear the `VOTES` dict."""
    for key in VOTES.keys():
        VOTES[key] = 0
    for user in USERS:
        user.has_voted = False


def next_move():
    """Return the most voted action in the last frame.

    Returns:
        str: the most voted action.
    """
    if any(VOTES.values()):
        return max(VOTES, key=VOTES.get)
    else:
        return "null"


async def parse_message(user: User, msg: dict[str, str]):
    """Parse the `user`'s `msg`.

    Args:
        user (User): the sender of the message.
        msg (dict[str, str]): the message received through websocket.
    """
    # Special users
    global EMULATOR
    global ADMIN

    if "auth" in msg:
        data = msg["auth"]
        if not EMULATOR and data == PASSWORD:
            EMULATOR = user
            logging.debug(f"emulator authenticated: {user}")
        elif not ADMIN and data == PASSWORD:
            ADMIN = user
            logging.debug(f"admin authenticated: {user}")

    if "action" in msg:
        data = msg["action"]
        if data in VOTES:
            VOTES[data] += 1
            user.last_message = time.time()
            user.has_voted = True
        else:
            logging.error(f"unsupported action: {data}")

    if "admin" in msg:
        data = msg["admin"]
        if user == ADMIN:
            if data == "save":
                await EMULATOR.send('{"admin":"save"}')
            elif data == "load":
                await EMULATOR.send('{"admin":"load"}')
            else:
                logging.error(f"unsupported admin action: {data}")
        else:
            logging.error(f"user is not ADMIN: {user}")

    if "emu" in msg:
        data = msg["emu"]
        if user == EMULATOR:
            if data == "get":
                move = next_move()
                await EMULATOR.send(f'{{"action":"{move}"}}')
                clear_votes()
            else:
                logging.error(f"unsupported emulator action: {data}")
        else:
            logging.error(f"user is not EMULATOR: {user}")


async def handler(websocket: Any, path: str):
    """Handle the messages sent by a user.

    Args:
        websocket (Any): the websocket used by the user
        path (str): the path used by the websocket ?
    """
    try:
        # Register user
        user = User()
        user.register(websocket)
        # Manage received messages
        async for json_message in websocket:
            message: dict[str, str] = json.loads(json_message)
            await parse_message(user, message)
    finally:
        # Unregister user
        user.unregister()


async def main():
    """Start the websocket server."""
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
