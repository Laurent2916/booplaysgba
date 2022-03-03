"""Websocket server, responsible for proxying user inputs."""

import asyncio
import logging
import time

import redis
import websockets
import websockets.exceptions
import websockets.server
import websockets.typing
from utils import User, Users

from env import (
    KEYS_ID,
    KEYS_RESET,
    REDIS_HOST,
    REDIS_PORT,
    USER_TIMEOUT,
    WEBSOCKET_PORT,
    WEBSOCKET_SERVE,
)


async def parse_message(user: User, message: websockets.typing.Data) -> None:
    """Parse the user's message.

    Args:
        user (User): the sender of the message.
        message (str): the key received (through the websocket).
    """
    msg = KEYS_ID[int(message)]
    if user.last_message + USER_TIMEOUT > time.time():
        logging.debug(f"dropping action: {msg} from {user}")
    elif msg in KEYS_ID:
        r.incr(msg)
        user.last_message = time.time()
        logging.debug(f"received action: {msg} from {user}")
    else:
        logging.error(f"unsupported action: {msg} from {user}")


async def handler(
    websocket: websockets.server.WebSocketServerProtocol, path: str
) -> None:
    """Handle the messages sent by a user.

    Args:
        websocket: the websocket used by the user.
        path (str): the path used by the websocket.
    """
    # register user
    user = User(websocket)
    USERS.register(user)

    try:  # manage received messages
        async for message in user.websocket:
            await parse_message(user, message)
    except websockets.exceptions.ConnectionClosed:
        logging.error(f"connection with user {user} is already closed")
    except RuntimeError:
        logging.error(f"two coroutines called recv() concurrently, user={user}")
    finally:
        USERS.unregister(user)  # unregister user


async def main() -> None:
    """Start the websocket server."""
    logging.debug("Server started !")
    async with websockets.server.serve(handler, WEBSOCKET_SERVE, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":

    # setup logging format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)-8s  %(message)s",
        datefmt="(%F %T)",
    )

    # change log levels for some libs
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("asyncio.coroutines").setLevel(logging.ERROR)
    logging.getLogger("websockets.server").setLevel(logging.ERROR)
    logging.getLogger("websockets.protocol").setLevel(logging.ERROR)

    # connect to redis database
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r.mset(KEYS_RESET)  # type: ignore

    # create a User set
    USERS: Users = Users()

    # start the websocket server
    asyncio.run(main())
