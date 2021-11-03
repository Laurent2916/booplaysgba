import asyncio
import json
import logging
import time

import mgba.core
import mgba.image
import mgba.log
import numpy as np
import pyvirtualcam
import websockets
from mgba._pylib import ffi

WIDTH: int = 240
HEIGHT: int = 160
URI: str = "ws://127.0.0.1:6789/"
FPS: int = 60
HZ: int = 10
POLLING_RATE: int = FPS // HZ
KEYMAP: dict[str, int] = {
    "a": 0,
    "b": 1,
    "select": 2,
    "start": 3,
    "right": 4,
    "left": 5,
    "up": 6,
    "down": 7,
    "r": 8,
    "l": 9,
}

core = mgba.core.load_path("roms/pokemon.gba")
# core = mgba.core.load_path("roms/BtnTest.gba")
screen = mgba.image.Image(WIDTH, HEIGHT)
core.set_video_buffer(screen)
core.reset()
mgba.log.silence()

# logging.basicConfig(level=logging.DEBUG)


def parse_message(message: dict[str, str]):
    """Parse the server's reponse.

    Args:
        message (dict[str, str]): the data received (through the websocket).
    """
    if "action" in message:
        data = message["action"]
        if data in KEYMAP:
            key = KEYMAP[data]
            core.set_keys(key)
            logging.debug(f"pressing: {key}")
        elif data == "null":
            pass
        else:
            logging.error(f"unsupported action: {data}")

    if "admin" in message:
        data = message["admin"]
        if data == "save":  # voodoo magic incomming
            state = core.save_raw_state()
            with open(f"states/{time.strftime('%Y-%m-%dT%H:%M:%S')}.state", "wb") as state_file:
                for byte in state:
                    state_file.write(byte.to_bytes(4, byteorder="big", signed=False))
        elif data == "load":  # black magic incomming
            state = ffi.new("unsigned char[397312]")
            with open("states/test.state", "rb") as state_file:
                for i in range(len(state)):
                    state[i] = int.from_bytes(state_file.read(4), byteorder="big", signed=False)
            core.load_raw_state(state)
        else:
            logging.error(f"unsupported admin: {data}")


async def main():
    """Start the emulator."""
    with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
        logging.debug(f"Using virtual camera: {cam.device}")
        async with websockets.connect(URI) as websocket:
            await websocket.send('{"auth":"emulator_password"}')
            logging.debug(f"connected to: {websocket}")

            while True:
                if not (core.frame_counter % POLLING_RATE):
                    core.clear_keys(*KEYMAP.values())
                    await websocket.send('{"emu":"get"}')
                    json_message = await websocket.recv()
                    message = json.loads(json_message)
                    parse_message(message)

                core.run_frame()

                frame = np.array(screen.to_pil().convert("RGB"), np.uint8)
                cam.send(frame)
                cam.sleep_until_next_frame()


asyncio.run(main())
