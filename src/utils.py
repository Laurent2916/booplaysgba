import logging
import time
from dataclasses import dataclass

import websockets.server
import websockets.typing


class User:
    """Store infos related to a connected user."""

    websocket: websockets.server.WebSocketServerProtocol
    last_message: float

    def __init__(self, websocket: websockets.server.WebSocketServerProtocol) -> None:
        """Construct a User object.

        Args:
            websocket (WebSocketServerProtocol): the websocket used by the user.
        """
        self.websocket = websocket
        self.last_message = time.time()

    async def send(self, data: str) -> None:
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

    def register(self, user: User) -> None:
        """Register a user in the set.

        Args:
            user (User): the user to register.
        """
        self.add(user)
        logging.debug(f"user registered: {user}")

    def unregister(self, user: User) -> None:
        """Unregister a user in the set.

        Args:
            user (User): the user to unregister.
        """
        self.remove(user)
        logging.debug(f"user unregistered: {user}")
