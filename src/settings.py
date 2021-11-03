WIDTH: int = 240
HEIGHT: int = 160

URI: str = "ws://127.0.0.1:6789/"
PASSWORD_ADMIN: str = "password_admin"

FPS: int = 60
HZ: int = 10
POLLING_RATE: int = FPS // HZ
USER_TIMEOUT: float = 0.5

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
KEYS: tuple = tuple(KEYMAP.keys())
MGBA_KEYS: tuple = tuple(KEYMAP.values())
REDIS_INIT: dict = dict([(x, 0) for x in KEYS])
