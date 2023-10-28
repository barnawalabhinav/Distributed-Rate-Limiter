from __future__ import annotations

from typing import List

from redis.client import Redis

from apiServer import ApiServer
from constants import LOAD, PER_SERVER_REQ_CNT, N_SERVERS


# This is the redis client providing interface to interact with the load balancer
class LoadBal:
    def __init__(self, port: int):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()

    # TODO: Implement read and write operations and other functionalities, decide if it has to be fault tolerant

    def add_request(self, cli_req: str):
        self.rds.lpush(LOAD, cli_req)

    def dist_request(self, servers: List[ApiServer]):
        cur_server = 0
        req_id = 0
        while True:
            reqs = self.rds.lpop(LOAD, PER_SERVER_REQ_CNT)
            if reqs and len(reqs):
                for req in reqs:
                    req = req.decode() + '-' + str(req_id)
                    servers[cur_server].add_request(req)
                    req_id += 1

            cur_server = (cur_server + 1) % N_SERVERS
