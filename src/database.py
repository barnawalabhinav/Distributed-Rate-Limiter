from __future__ import annotations

import time
import numpy as np

from redis.client import Redis
from base_redis import BaseRedis
from constants import RAFT_PORTS

# This is the redis client providing interface to interact with common redis database
class DataBase(BaseRedis):
    def __init__(self, port):
        super(DataBase, self).__init__(port)
        self.comm_lat = [5, 10] # Time taken to communicate in milliseconds

    def set(self, key, arg):
        time.sleep(np.random.default_rng().uniform(self.comm_lat[0], self.comm_lat[1])/1000)
        super(DataBase, self).set(key, arg)
        # while True:
        #     try:
        #         super(DataBase, self).set(key, arg)
        #         break
        #     except:
        #         for port in RAFT_PORTS:
        #             try:
        #                 client = Redis(host='localhost', port=port, db=0, decode_responses=False)
        #                 info = client.execute_command('INFO raft').decode().split('\n')
        #                 if (info[8].strip().split(':')[1] == 'leader'):
        #                     super(DataBase, self).rds = client
        #             except:
        #                 None

    def get(self, key):
        time.sleep(np.random.default_rng().uniform(self.comm_lat[0], self.comm_lat[1])/1000)
        return super(DataBase, self).get(key)
        # while True:
        #     try:
        #         return super(DataBase, self).get(key)
        #     except:
        #         for port in RAFT_PORTS:
        #             try:
        #                 client = Redis(host='localhost', port=port, db=0, decode_responses=False)
        #                 info = client.execute_command('INFO raft').decode().split('\n')
        #                 if (info[8].strip().split(':')[1] == 'leader'):
        #                     super(DataBase, self).rds = client
        #             except:
        #                 None

    def get_req_count(self, cli_id: str) -> int:
        time.sleep(np.random.default_rng().uniform(self.comm_lat[0], self.comm_lat[1])/1000)
        return super(DataBase, self).get_req_count(cli_id)
        # while True:
        #     try:
        #         return super(DataBase, self).get_req_count(cli_id)
        #     except:
        #         for port in RAFT_PORTS:
        #             try:
        #                 client = Redis(host='localhost', port=port, db=0, decode_responses=False)
        #                 info = client.execute_command('INFO raft').decode().split('\n')
        #                 if (info[8].strip().split(':')[1] == 'leader'):
        #                     super(DataBase, self).rds = client
        #             except:
        #                 None

    def add_req(self, cli_id: str, req_time: int, req_id: str) -> None:
        time.sleep(np.random.default_rng().uniform(self.comm_lat[0], self.comm_lat[1])/1000)
        super(DataBase, self).add_req(cli_id, req_time, req_id)
        # while True:
        #     try:
        #         super(DataBase, self).add_req(cli_id, req_time, req_id)
        #         break
        #     except:
        #         for port in RAFT_PORTS:
        #             try:
        #                 client = Redis(host='localhost', port=port, db=0, decode_responses=False)
        #                 info = client.execute_command('INFO raft').decode().split('\n')
        #                 if (info[8].strip().split(':')[1] == 'leader'):
        #                     super(DataBase, self).rds = client
        #             except:
        #                 None
