from __future__ import annotations

import time

from redis.client import Redis
from constants import REQ_EXPIRY_TIME


# This is the redis client providing interface to interact with common redis database
class BaseRedis:
    def __init__(self, port):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()

    # TODO: Implement read and write operations and other functionalities, need to make it fault tolerant

    def set(self, key, arg):
        self.rds.set(key, arg)

    def get(self, key):
        return self.rds.get(key)

    def get_req_count(self, cli_id: str) -> int:
        return len(self.rds.keys(f'{cli_id}:Processed:*'))

    def add_req(self, cli_id: str, req_time: int, req_id: str) -> None:
        time_to_expiry = REQ_EXPIRY_TIME - int(time.time() + 0.5) + req_time
        if time_to_expiry > 0:
            self.rds.set(f'{cli_id}:Processed:{req_time}:{req_id}', 1)
            self.rds.expire(f'{cli_id}:Processed:{req_time}:{req_id}', time_to_expiry)