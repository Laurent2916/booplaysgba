import logging
import time
from dataclasses import dataclass
from typing import Any

import websockets.server
import websockets.typing
from mgba._pylib import ffi


class User:
    """Store infos related to a connected user."""

    websocket: websockets.server.WebSocketServerProtocol
    last_message: float

    def __init__(self, websocket: Any) -> None:
        """Construct a User object.

        Args:
            websocket (Any): the websocket used by the user.
        """
        self.websocket = websocket
        self.last_message = time.time()

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
        logging.debug(f"user unregistered: {user}")


async def save(core):
    state = core.save_raw_state()
    current_time = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(f"states/{current_time}.state", "wb") as state_file:
        for byte in state:
            state_file.write(byte.to_bytes(4, byteorder="big", signed=False))
    logging.debug(f"state saved : {current_time}.state")


async def load(core, filename):
    state = ffi.new("unsigned char[397312]")  # pulled 397312 straight from my ass
    # TODO: checker les sources mgba pour savoir d'où sort 397312
    with open(f"states/{filename}.state", "rb") as state_file:
        for i in range(len(state)):
            state[i] = int.from_bytes(state_file.read(4), byteorder="big", signed=False)
    core.load_raw_state(state)
    logging.debug(f"state loaded : {filename}")
