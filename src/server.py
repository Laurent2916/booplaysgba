import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import websockets


class User:
    """Store infos related to a connected user."""

    websocket: Any
    last_message: float
    has_voted: bool

    def __init__(self, websocket: Any) -> None:
        """Construct a User object.

        Args:
            websocket (Any): the websocket used by the user.
        """
        self.websocket = websocket
        self.last_message = time.time()
        self.has_voted = False

    async def send(self, data: str):
        """Send data through the user's websocket.

        Args:
            data (str): message to send.
        """
        await self.websocket.send(data)

    def __str__(self) -> str:
        """Convert user to string.

        Returns:
            str: string representing the user.
        """
        return f"{self.websocket.remote_address} ({self.websocket.id})"


@dataclass
class Users(set):
    """Store `User`s connected to the server."""

    emulator: Optional[User] = None
    admin: Optional[User] = None

    def register(self, user: User):
        """Register a user in the set.

        Args:
            user (User): the user to register.
        """
        self.add(user)
        logging.debug(f"user registered: {user}")

    def unregister(self, user: User):
        """Unregister a user in the set.

        Args:
            user (User): the user to unregister.
        """
        self.remove(user)
        logging.debug(f"user unregistered: {self}")

    def clear(self) -> None:
        """Clear the `has_voted` of each user in the set."""
        for user in self:
            user.has_voted = False


@dataclass
class Votes(dict):
    """Store the votes sent by users."""

    def __init__(self) -> None:
        """Construct a `Votes` object."""
        super(Votes, self)
        self["a"] = 0
        self["b"] = 0
        self["select"] = 0
        self["start"] = 0
        self["right"] = 0
        self["left"] = 0
        self["up"] = 0
        self["down"] = 0
        self["r"] = 0
        self["l"] = 0

    def clear(self) -> None:
        """Clear the `VOTES` dict."""
        for key in self.keys():
            self[key] = 0

    def next_vote(self):
        """Return the most voted action in the last frame.

        Returns:
            str: the most voted action.
        """
        if any(self.values()):
            return max(self, key=self.get)
        else:
            return "null"


logging.basicConfig(level=logging.DEBUG)

PASSWORD_ADMIN: str = "password"
PASSWORD_EMU: str = "password"
VOTES: Votes = Votes()
USERS: Users = Users()


async def parse_message(user: User, msg: dict[str, str]):
    """Parse the `user`'s `msg`.

    Args:
        user (User): the sender of the message.
        msg (dict[str, str]): the data received (through the websocket).
    """
    if "auth" in msg:
        data = msg["auth"]
        if USERS.emulator is not None and data == PASSWORD_EMU:
            USERS.emulator = user
            logging.debug(f"emulator authenticated: {user}")
        elif USERS.admin is not None and data == PASSWORD_ADMIN:
            USERS.admin = user
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
        if USERS.emulator is not None and user == USERS.admin:
            if data == "save":
                await USERS.emulator.send('{"admin":"save"}')
            elif data == "load":
                await USERS.emulator.send('{"admin":"load"}')
            else:
                logging.error(f"unsupported admin action: {data}")
        else:
            logging.error(f"user is not admin: {user}")

    if "emu" in msg:
        data = msg["emu"]
        if user == USERS.emulator:
            if data == "get":
                await USERS.emulator.send(f'{{"action":"{VOTES.next_vote()}"}}')
                VOTES.clear()
                USERS.clear()
            else:
                logging.error(f"unsupported emulator action: {data}")
        else:
            logging.error(f"user is not emulator: {user}")


async def handler(websocket: Any, path: str):
    """Handle the messages sent by a user.

    Args:
        websocket (Any): the websocket used by the user.
        path (str): the path used by the websocket. (?)
    """
    try:
        # Register user
        user = User(websocket)
        USERS.register(user)
        # Manage received messages
        async for json_message in websocket:
            message: dict[str, str] = json.loads(json_message)
            await parse_message(user, message)
    finally:
        # Unregister user
        USERS.unregister(user)


async def main():
    """Start the websocket server."""
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
