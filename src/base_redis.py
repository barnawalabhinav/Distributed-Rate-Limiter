from __future__ import annotations

import time

from redis.client import Redis
from constants import REQ_EXPIRY_TIME, LOAD, WRK_GRP, CLI_REQ


# This is the redis client providing interface to interact with common redis database
class BaseRedis:
    def __init__(self, port):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()

    def create_group(self):
        self.rds.xgroup_create(LOAD, WRK_GRP, id="0", mkstream=True)

    def add_request(self, cli_req: str):
        self.rds.xadd(LOAD, {CLI_REQ: cli_req})

    def fetch_request(self, worker_name, cnt):
        fileName = self.rds.xreadgroup(WRK_GRP, worker_name, {LOAD: ">"}, count=cnt, noack=True)
        if fileName:
            return fileName[0][1]
        return None

    def set(self, key, arg):
        self.rds.set(key, arg)

    def get(self, key):
        return self.rds.get(key)

    def get_req_count(self, cli_id: str) -> int:
        return len(self.rds.keys(f'{cli_id}:Processed:*'))

    def add_req(self, cli_id: str, req_time: int, req_id: str) -> None:
        time_to_expiry = REQ_EXPIRY_TIME*1000 - int(time.time()*1000) + req_time
        if time_to_expiry > 0:
            self.rds.set(f'{cli_id}:Processed:{req_time}:{req_id}', 1)
            self.rds.pexpire(f'{cli_id}:Processed:{req_time}:{req_id}', time_to_expiry)
