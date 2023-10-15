from __future__ import annotations

import os
import json
import time
from typing import Any
from redis.client import Redis

from apiServer import ApiServer
from constants import START_PORT, CLI_REQ, LOAD, SER_GRP, IDLE_TIME


# This is the redis client providing interface to interact with the load balancer
class LoadBal:
    def __init__(self, port: int):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()
        # self.rds.xgroup_create(LOAD, SER_GRP, id="0", mkstream=True)

    # TODO: Implement read and write operations and other functionalities, decide if it has to be fault tolerant

    def add_request(self, cli_req: str):
        self.rds.lpush(LOAD, cli_req)

    def dist_request(self, server: ApiServer, cnt: int):
        req = self.rds.lpop(LOAD, cnt)
        if not req:
            return
        server.add_request(req)
