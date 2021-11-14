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


# class States(set):
#     def save(self, core):
#         state = core.save_raw_state()
#         with open(f"states/{time.strftime('%Y-%m-%dT%H:%M:%S')}.state", "wb") as state_file:
#             for byte in state:
#                 state_file.write(byte.to_bytes(4, byteorder="big", signed=False))

#     def load(self, core, state):
#         state = ffi.new("unsigned char[397312]")
#         with open("states/test.state", "rb") as state_file:
#             for i in range(len(state)):
#                 state[i] = int.from_bytes(state_file.read(4), byteorder="big", signed=False)
#         core.load_raw_state(state)
