import logging
import time
from dataclasses import dataclass
from typing import Any, Optional


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
