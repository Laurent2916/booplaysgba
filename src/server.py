import asyncio
import json
import logging
import time
from typing import Union

import redis
import websockets

from settings import (
    KEYS_ID,
    KEYS_RESET,
    PASSWORD_ADMIN,
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

            response: dict[str, Union[str, list[str]]] = dict()
            response["auth"] = "success"
            states = r.smembers("states")
            stringlist = [x.decode("utf-8") for x in states]
            response["states"] = sorted(stringlist)
            await user.send(json.dumps(response))

    if "admin" in message:
        if user == USERS.admin:
            data = message["admin"]
            if data == "save":
                r.publish("admin", "save")
            elif data.startswith("load:"):
                r.publish("admin", data)
            else:
                logging.error(f"unsupported admin action: {data}")
        else:
            logging.error(f"user is not admin: {user}")

    if "action" in message:
        data = message["action"]

        if user.last_message + USER_TIMEOUT > time.time():
            logging.debug(f"dropping action: {data}")
            return None
        elif data in KEYS_ID:
            r.incr(data)
            user.last_message = time.time()
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
        if user == USERS.admin:
            USERS.admin = None
        USERS.unregister(user)


async def main():
    """Start the websocket server."""
    async with websockets.serve(handler, WEBSOCKET_SERVE, WEBSOCKET_PORT):  # nosec
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
