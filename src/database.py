from __future__ import annotations
import json
import time
import os
from typing import Final
from redis.client import Redis
from constants import START_PORT, CLI_REQ

IDLE_TIME: Final[int] = 1000


# This is the redis client providing interface to interact with common redis database
class DataBase:
    def __init__(self):
        self.rds = Redis(host='localhost', port=START_PORT -
                         2, db=0, decode_responses=False)
        self.rds.flushall()

    # TODO: Implement read and write operations and other functionalities, need to make it fault tolerant
