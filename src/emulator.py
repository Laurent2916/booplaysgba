import logging
from subprocess import PIPE, Popen

import mgba.core
import mgba.image
import mgba.log
import numpy as np
import pyvirtualcam
import redis

from settings import FPS, HEIGHT, KEYS, MGBA_KEYS, POLLING_RATE, REDIS_INIT, WIDTH

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
    votes = list(map(int, r.mget(KEYS)))
    if any(votes):
        r.mset(REDIS_INIT)
        return votes.index(max(votes))
    else:
        return -1


stream = Popen(
    [
        "/usr/bin/ffmpeg",
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        f"{FPS}",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-i",
        "-",
        "-f",
        "flv",
        "-b:v",
        "2M",
        "rtmp://localhost:1935/live/test",
    ],
    stdin=PIPE,
)

with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
    logging.debug(f"Using virtual camera: {cam.device}")

    while True:
        if not (core.frame_counter % POLLING_RATE):
            core.clear_keys(*MGBA_KEYS)
            next_key = next_action()
            if next_key != -1:
                core.set_keys(next_key)

        core.run_frame()

        image = screen.to_pil().convert("RGB")
        image.save(stream.stdin, "PNG")

        cam.send(np.array(image, np.uint8))
        cam.sleep_until_next_frame()
