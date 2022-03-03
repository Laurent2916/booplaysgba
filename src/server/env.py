from os import getenv

WEBSOCKET_HOST: str = getenv("WEBSOCKET_HOST", "localhost")
WEBSOCKET_PORT: int = int(getenv("WEBSOCKET_PORT", 6789))
WEBSOCKET_URI: str = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/"
WEBSOCKET_SERVE: str = getenv("WEBSOCKET_SERVE", "localhost")

REDIS_HOST: str = getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(getenv("REDIS_PORT", 6379))

USER_TIMEOUT: float = float(getenv("USER_TIMEOUT", 0.5))

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
