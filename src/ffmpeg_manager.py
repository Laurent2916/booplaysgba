import subprocess

from settings import (
    EMULATOR_FPS,
    EMULATOR_HEIGHT,
    EMULATOR_WIDTH,
    FFMPEG_BITRATE,
    FFMPEG_FPS,
    FFMPEG_HEIGHT,
    FFMPEG_WIDTH,
    RTMP_STREAM_URI,
)

# launch ffmpeg process
ffmpeg_stream = subprocess.Popen(
    [
        "/usr/bin/ffmpeg",
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        f"{EMULATOR_FPS}",
        "-s",
        f"{EMULATOR_WIDTH}x{EMULATOR_HEIGHT}",
        "-i",
        "-",
        "-f",
        "flv",
        "-s",
        f"{FFMPEG_WIDTH}x{FFMPEG_HEIGHT}",
        "-r",
        f"{FFMPEG_FPS}",
        "-b:v",
        FFMPEG_BITRATE,
        "-fflags",
        "nobuffer",
        "-flags",
        "low_delay",
        "-strict",
        "experimental",
        RTMP_STREAM_URI,
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
