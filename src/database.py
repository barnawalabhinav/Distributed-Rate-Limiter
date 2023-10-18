from __future__ import annotations

from redis.client import Redis


# This is the redis client providing interface to interact with common redis database
class DataBase:
    def __init__(self, port):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()

    # TODO: Implement read and write operations and other functionalities, need to make it fault tolerant

    def set(self, key, arg):
        self.rds.set(key, arg)

    def get(self, key):
        return self.rds.get(key)
