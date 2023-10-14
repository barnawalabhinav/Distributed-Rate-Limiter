from __future__ import annotations
import json
import time
import os
from typing import Final
from redis.client import Redis
from constants import START_PORT, CLI_REQ

IDLE_TIME: Final[int] = 1000


# This is the redis client providing interface to interact with the load balancer
class LoadBal:
    def __init__(self):
        self.rds = Redis(host='localhost', port=START_PORT-1, db=0, decode_responses=False)
        self.rds.flushall()
        # self.rds.xgroup_create(CLI_REQ, Worker.GROUP, id="0", mkstream=True)

    # TODO: Implement read and write operations and other functionalities, decide if it has to be fault tolerant