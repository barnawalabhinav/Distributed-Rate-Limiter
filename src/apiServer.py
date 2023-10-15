from __future__ import annotations

import os
import json
import time
from typing import Final
from redis.client import Redis

from constants import CLI_REQ, LOAD, WRK_GRP, IDLE_TIME


# This is the redis client providing interface to interact with main rate limiters on api servers
class ApiServer:
    def __init__(self, port):
        self.rds = Redis(host='localhost', port=port, password='pass', db=0, decode_responses=False)
        self.rds.flushall()
        self.rds.xgroup_create(LOAD, WRK_GRP, id="0", mkstream=True)

    # TODO: Implement read and write operations and other functionalities, need to make it fault tolerant

    def add_request(self, cli_req: str):
        self.rds.xadd(LOAD, {CLI_REQ: cli_req})

    def fetch_request(self, ser_name, cnt):
        fileName = self.rds.xreadgroup(WRK_GRP, ser_name, {LOAD: ">"}, count=cnt)
        if fileName:
            return fileName[0][1]
        pending_msgs = self.rds.xpending(LOAD, WRK_GRP)
        if (pending_msgs['pending'] == 0):
            return None
        fileName = self.rds.xautoclaim(LOAD, WRK_GRP, ser_name, IDLE_TIME, 0, count=cnt)
        if (len(fileName[1]) > 0):
            return fileName[1]
        return None
