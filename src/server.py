import asyncio
import json
import logging
import time

import redis
import websockets

from settings import KEYS, PASSWORD_ADMIN, REDIS_INIT, USER_TIMEOUT
from utils import User, Users

logging.basicConfig(level=logging.DEBUG)

r = redis.Redis(host="localhost", port=6379, db=0)
r.mset(REDIS_INIT)

USERS: Users = Users()


async def parse_message(user: User, message: dict[str, str]) -> None:
    """Parse the user's message.

    Args:
        user (User): the sender of the message.
        message (dict[str, str]): the data received (through the websocket).
    """
    if "auth" in message:
        data = message["auth"]
        if USERS.admin is None and data == PASSWORD_ADMIN:
            USERS.admin = user
            logging.debug(f"admin authenticated: {user}")
            await user.send('{"auth":"success"}')

    if "action" in message:
        data = message["action"]

        if user.last_message + USER_TIMEOUT > time.time():
            logging.debug(f"dropping action: {data}")
            return None
        elif data in KEYS:
            r.incr(data)
            user.last_message = time.time()
            user.has_voted = True
        else:
            logging.error(f"unsupported action: {data}")


async def handler(websocket, path: str):
    """Handle the messages sent by a user.

    Args:
        websocket: the websocket used by the user.
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
