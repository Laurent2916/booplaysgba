import asyncio
import json
import logging
import os
import time
from typing import Any

import websockets

from utils import User, Users, Votes

# logging.basicConfig(level=logging.DEBUG)

PASSWORD_ADMIN: str = "admin_password"
PASSWORD_EMU: str = "emulator_password"
VOTES: Votes = Votes()
USERS: Users = Users()


async def send_states(user: User) -> None:
    files = os.listdir("states")
    states = list(filter(lambda x: x.endswith(".state"), files))
    message = json.dumps({"state": states})
    await user.send(message)


async def parse_message(user: User, message: dict[str, str]) -> None:
    """Parse the user's message.

    Args:
        user (User): the sender of the message.
        message (dict[str, str]): the data received (through the websocket).
    """
    if "auth" in message:
        data = message["auth"]
        if USERS.emulator is None and data == PASSWORD_EMU and user != USERS.admin:
            USERS.emulator = user
            logging.debug(f"emulator authenticated: {user}")
            await user.send('{"auth":"success"}')
        elif USERS.admin is None and data == PASSWORD_ADMIN and user != USERS.emulator:
            USERS.admin = user
            logging.debug(f"admin authenticated: {user}")
            await user.send('{"auth":"success"}')

    if "action" in message:
        data = message["action"]
        if data in VOTES:
            VOTES[data] += 1
            user.last_message = time.time()
            user.has_voted = True
        else:
            logging.error(f"unsupported action: {data}")

    if "admin" in message:
        data = message["admin"]
        if USERS.emulator is not None and user == USERS.admin:
            if data == "save":
                await USERS.emulator.send('{"admin":"save"}')
            elif data == "load":
                await USERS.emulator.send('{"admin":"load"}')
            else:
                logging.error(f"unsupported admin action: {data}")
        else:
            logging.error(f"user is not admin: {user}")

    if "emu" in message:
        data = message["emu"]
        if user == USERS.emulator:
            if data == "get":
                await USERS.emulator.send(f'{{"action":"{VOTES.next_vote()}"}}')
                VOTES.clear()
                USERS.clear()
            else:
                logging.error(f"unsupported emulator action: {data}")
        else:
            logging.error(f"user is not emulator: {user}")

    if "state" in message:
        data = message["state"]
        if user == USERS.admin:
            if data == "get":
                await send_states(user)
            else:
                logging.error(f"unsupported state action: {data}")
        else:
            logging.error(f"user is not admin: {user}")


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
        if user == USERS.admin:
            USERS.admin = None
            logging.debug(f"admin disconnected: {user}")
        elif user == USERS.emulator:
            logging.debug(f"emulator disconnected: {user}")
            USERS.emulator = None


async def main():
    """Start the websocket server."""
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
