from os import getenv

RTMP_HOST: str = getenv("RTMP_HOST", "localhost")
RTMP_PORT: int = int(getenv("RTMP_PORT", 1935))
RTMP_URI: str = f"rtmp://{RTMP_HOST}:{RTMP_PORT}/"
RTMP_STREAM_PATH: str = getenv("RTMP_STREAM_PATH", "live")
RTMP_STREAM_KEY: str = getenv("RTMP_STREAM_KEY", "test")
RTMP_STREAM_URI: str = RTMP_URI + f"{RTMP_STREAM_PATH}/{RTMP_STREAM_KEY}"

REDIS_HOST: str = getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(getenv("REDIS_PORT", 6379))

EMULATOR_WIDTH: int = int(getenv("EMULATOR_WIDTH", 240))
EMULATOR_HEIGHT: int = int(getenv("EMULATOR_HEIGHT", 160))
EMULATOR_FPS: int = int(getenv("EMULATOR_FPS", 60))
EMULATOR_SPF: float = 1.0 / EMULATOR_FPS
EMULATOR_INPUT_HZ: int = int(getenv("EMULATOR_INPUT_HZ", 10))
EMULATOR_POLLING_RATE: int = EMULATOR_FPS // EMULATOR_INPUT_HZ
EMULATOR_ROM_PATH: str = getenv("EMULATOR_ROM_PATH", "../../roms/pokemon.gba")
EMULATOR_STATES_PATH: str = getenv("EMULATOR_STATES_PATH", "../../states/")
EMULATOR_RAND_RATE: float = float(getenv("EMULATOR_RAND_RATE", 0.0))

FFMPEG_WIDTH: int = int(getenv("FFMPEG_WIDTH", EMULATOR_WIDTH))
FFMPEG_HEIGHT: int = int(getenv("FFMPEG_HEIGHT", EMULATOR_HEIGHT))
FFMPEG_FPS: int = int(getenv("FFMPEG_FPS", 30))
FFMPEG_BITRATE: str = getenv("FFMPEG_BIRATE", "2M")

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
KEYS_ID: tuple[str, ...] = tuple(KEYMAP.keys())
KEYS_MGBA: tuple[int, ...] = tuple(KEYMAP.values())
KEYS_RESET: dict[str, int] = {x: 0 for x in KEYS_ID}
