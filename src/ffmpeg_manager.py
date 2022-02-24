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
ffmpeg_video_stream = subprocess.Popen(
    [
        "/usr/bin/ffmpeg",  # ffmpeg binary location
        "-y",  # overwrite output files without asking
        "-f",  # force input file format
        "image2pipe",  # allows to pipe images to ffmpeg
        "-vcodec",  # set the video codec
        "png",  # input images are PNGs
        "-r",  # set input frame rate
        f"{EMULATOR_FPS}",
        "-s",  # set input frame size
        f"{EMULATOR_WIDTH}x{EMULATOR_HEIGHT}",
        "-i",  # input file url
        "pipe:0",  # use stdin (pipe n°0) for input
        "-f",  # force input or output file format
        "flv",  # output an flv video
        "-s",  # set output frame size
        f"{FFMPEG_WIDTH}x{FFMPEG_HEIGHT}",
        "-r",  # set output frame rate
        f"{FFMPEG_FPS}",
        "-b:v",  # set video output bitrate
        FFMPEG_BITRATE,
        "-fflags",  # set format flags
        "nobuffer",  # reduce the latency introduced by buffering during initial input streams analysis
        "-flags",  # set generic flags
        "low_delay",  # force low delay
        "-strict",  # specify how strictly to follow the standards
        "experimental",  # allow non standardized experimental encoders...
        RTMP_STREAM_URI,  # where to output the video
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT,
)

ffmpeg_audio_stream = subprocess.Popen(
    # [
    #     "/usr/bin/ffmpeg",  # FFMPEG_BIN
    #     "-i",
    #     "-",
    #     "-f",
    #     "s24le",
    #     "-acodec",
    #     "pcm_s24le",
    #     "-ar",
    #     "44100",  # ouput will have 44100 Hz
    #     "-ac",
    #     "2",  # stereo (set to '1' for mono)
    #     RTMP_STREAM_URI,
    # ],
    # [
    #     "/usr/bin/ffmpeg",  # FFMPEG_BIN
    #     "-f",  # audio format
    #     "s24le",
    #     "-acodec",  # audio codec
    #     "pcm_s24le",
    #     "-ar",  # audio sampling rate
    #     "44100",
    #     "-ac",  # number of audio canals
    #     "2",  # stereo (set to '1' for mono)
    #     "-i",
    #     "pipe:",
    #     "-y",
    #     "-f",
    #     "flv",
    #     # "-tune",
    #     # "zerolatency",
    #     "-fflags",  # set format flags
    #     "nobuffer",  # reduce the latency introduced by buffering during initial input streams analysis
    #     "-flags",  # set generic flags
    #     "low_delay",  # force low delay
    #     "-strict",  # specify how strictly to follow the standards
    #     "experimental",  # allow non standardized experimental things
    #     RTMP_STREAM_URI,
    # ],
    [
        "/usr/bin/ffmpeg",  # FFMPEG_BIN
        "-f",
        "-y",
        "s24le",
        "-acodec",
        "pcm_s24le",
        "-ar",
        "44100",  # ouput will have 44100 Hz
        "-ac",
        "2",  # stereo (set to '1' for mono)
        "-i",
        "-",
        "-f",
        "bonjour",
    ],
    stdin=subprocess.PIPE,
    # stdout=subprocess.STDOUT,
    # stderr=subprocess.STDOUT,
)

# https://stackoverflow.com/questions/67388548/multiple-named-pipes-in-ffmpeg
