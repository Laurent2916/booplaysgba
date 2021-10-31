import asyncio
import json
import logging

import mgba.core
import mgba.image
import mgba.log
import numpy as np
import pyvirtualcam
import websockets
from mgba._pylib import ffi

WIDTH = 240
HEIGHT = 160
URI: str = "ws://127.0.0.1:6789/"
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
screen = mgba.image.Image(WIDTH, HEIGHT)
core.set_video_buffer(screen)
core.reset()
mgba.log.silence()

logging.basicConfig(level=logging.DEBUG)


async def main():
    with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=60) as cam:
        logging.debug(f"Using virtual camera: {cam.device}")
        async with websockets.connect(URI) as websocket:
            await websocket.send('{"auth":"password"}')
            logging.debug(f"connected to: {websocket}")

            while True:

                if core.frame_counter % 30 == 0:  # 2Hz
                    await websocket.send('{"emu":"get"}')
                    message = await websocket.recv()
                    data = json.loads(message)

                    if "action" in data:
                        action = data["action"]
                        if action in KEYMAP:
                            key = KEYMAP[action]
                            core.set_keys(key)
                            logging.debug(f"pressing: {key}")
                        else:
                            logging.error(f"unsupported action: {data}")

                    if "admin" in data:
                        admin = data["admin"]
                        if admin == "save":
                            state = core.save_raw_state()
                            with open("states/test.state", "wb") as state_file:
                                for byte in state:
                                    state_file.write(byte.to_bytes(4, byteorder="big", signed=False))
                        elif admin == "load":
                            state = ffi.new("unsigned char[397312]")
                            with open("states/test.state", "rb") as state_file:
                                for i in range(len(state)):
                                    ptdr = state_file.read(4)
                                    state[i] = int.from_bytes(ptdr, byteorder="big", signed=False)
                            core.load_raw_state(state)

                        else:
                            logging.error(f"unsupported admin: {data}")

                core.run_frame()
                core.clear_keys(*KEYMAP.values())

                frame = np.array(screen.to_pil().convert("RGB"), np.uint8)
                cam.send(frame)
                cam.sleep_until_next_frame()


asyncio.run(main())
