"""Websocket server, responsible for proxying user inputs."""

import asyncio
import logging
import time

import redis
import websockets
import websockets.exceptions
import websockets.server
import websockets.typing

from settings import (
    KEYS_ID,
    KEYS_RESET,
    REDIS_HOST,
    REDIS_PORT,
    USER_TIMEOUT,
    WEBSOCKET_PORT,
    WEBSOCKET_SERVE,
)
from utils import User, Users

logging.basicConfig(level=logging.DEBUG)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
r.mset(KEYS_RESET)

USERS: Users = Users()


async def parse_message(user: User, message: websockets.typing.Data) -> None:
    """Parse the user's message.

    Args:
        user (User): the sender of the message.
        message (str): the key received (through the websocket).
    """
    if user.last_message + USER_TIMEOUT > time.time():
        logging.debug(f"dropping action: {message!r} from {user}")
        return None
    elif message in KEYS_ID:
        r.incr(message)
        user.last_message = time.time()
        logging.debug(f"received action: {message!r} from {user}")
    else:
        logging.error(f"unsupported action: {message!r} from {user}")


async def handler(websocket: websockets.server.WebSocketServerProtocol, path: str):
    """Handle the messages sent by a user.

    Args:
        websocket: the websocket used by the user.
        path (str): the path used by the websocket.
    """
    # Register user
    user = User(websocket)
    USERS.register(user)
    logging.debug(f"registered user {user}")

    try:  # Manage received messages
        async for message in user.websocket:
            await parse_message(user, message)
    except websockets.exceptions.ConnectionClosed:
        logging.error(f"connection with user {user} is already closed")
    except RuntimeError:
        logging.error(f"two coroutines called recv() concurrently, user={user}")
    finally:
        USERS.unregister(user)
        logging.debug(f"unregistered user {user}")


async def main():
    """Start the websocket server."""
    async with websockets.serve(handler, WEBSOCKET_SERVE, WEBSOCKET_PORT):  # nosec
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
