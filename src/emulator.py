import logging

import mgba.core
import mgba.image
import mgba.log
import numpy as np
import pyvirtualcam
import redis

WIDTH: int = 240
HEIGHT: int = 160
URI: str = "ws://127.0.0.1:6789/"
FPS: int = 60
HZ: int = 10
POLLING_RATE: int = FPS // HZ
VOTES: dict[str, int] = {
    "a": 0,
    "b": 0,
    "select": 0,
    "start": 0,
    "right": 0,
    "left": 0,
    "up": 0,
    "down": 0,
    "r": 0,
    "l": 0,
}
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

logging.basicConfig(level=logging.DEBUG)
mgba.log.silence()
r = redis.Redis(host="localhost", port=6379, db=0)


def next_action():
    """Select the next key from the redis database.

    Returns:
        int: key used by mgba
    """
    for key in VOTES.keys():
        VOTES[key] = int(r.get(key))
        r.set(key, 0)

    if any(VOTES.values()):
        return KEYMAP[max(VOTES, key=VOTES.get)]
    else:
        return -1


with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
    logging.debug(f"Using virtual camera: {cam.device}")

    while True:
        if not (core.frame_counter % POLLING_RATE):
            core.clear_keys(*KEYMAP.values())
            next_key = next_action()
            if next_key != -1:
                core.set_keys(next_key)

        core.run_frame()

        frame = np.array(screen.to_pil().convert("RGB"), np.uint8)
        cam.send(frame)
        cam.sleep_until_next_frame()
