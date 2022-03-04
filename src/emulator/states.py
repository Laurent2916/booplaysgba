import logging
import os

import watchdog.observers
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileSystemEventHandler

import redis
from env import EMULATOR_STATES_PATH


class StateHandler(FileSystemEventHandler):
    def __init__(self, redis: redis.Redis) -> None:
        super().__init__()
        self.redis = redis

    def on_created(self, event: FileCreatedEvent) -> None:
        """Called when a file or directory is created.

        Args
            event (FileCreatedEvent): Event representing file/directory creation.
        """
        filename = event.src_path.split("/")[-1]
        filename = filename.removesuffix(".state")
        self.redis.sadd("states", filename)
        logging.debug(f"new statefile: {filename}")

    def on_deleted(self, event: FileDeletedEvent) -> None:
        """Called when a file or directory is deleted.

        Args
            event (FileDeletedEvent): Event representing file/directory deletion.
        """
        filename = event.src_path.split("/")[-1]
        filename = filename.removesuffix(".state")
        self.redis.srem("state", filename)
        logging.debug(f"deleted statefile: {filename}")


class StateManager(watchdog.observers.Observer):
    def __init__(self, redis: redis.Redis):
        super().__init__()

        # setup states in redis
        files = os.listdir(EMULATOR_STATES_PATH)
        statefiles = list(filter(lambda x: x.endswith(".state"), files))
        states = list(map(lambda x: x.removesuffix(".state"), statefiles))
        redis.sadd("states", *states)
        logging.debug("redis server populated with states")

        state_handler = StateHandler(redis)
        self.schedule(state_handler, EMULATOR_STATES_PATH, recursive=False)
