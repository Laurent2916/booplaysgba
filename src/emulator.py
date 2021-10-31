import asyncio
import logging

import mgba.core
import mgba.image
import mgba.log
import numpy as np
import pyvirtualcam
import websockets

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
            test = core.save_raw_state()

            while True:

                if core.frame_counter % 30 == 0:
                    await websocket.send('{"action":"get"}')
                    response = await websocket.recv()
                    if response in KEYMAP:
                        key = KEYMAP[response]
                        core.set_keys(key)
                        logging.debug(f"pressing: {key}")

                        # with open("pokemon.state", "w") as f:
                        #     f.write(test)
                        core.load_raw_state(test)
                        print(str(test))

                core.run_frame()
                core.clear_keys(*KEYMAP.values())

                frame = np.array(screen.to_pil().convert("RGB"), np.uint8)
                cam.send(frame)
                cam.sleep_until_next_frame()


asyncio.run(main())
