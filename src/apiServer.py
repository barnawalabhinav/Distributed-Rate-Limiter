from __future__ import annotations

import logging
import time
from typing import Iterable, Optional, Any
from redis.client import Redis

from constants import CLI_REQ, LOAD, WRK_GRP, IDLE_TIME, N_WORKERS
from src.database import DataBase
from src.process import Process


class RLWorker(Process):
    def run(self, **kwargs: Any) -> None:
        apiServer: ApiServer = kwargs['api_server']
        database: DataBase = kwargs['database']

        # TODO: Implement task of workers, fetch requests from api server's redis-stream and process

        def process_req(id: str, req: str):
            print('Rejecting Request')
            return -1, "refuted"

        while True:
            reqs = apiServer.fetch_request(self.name, cnt=2)
            if not reqs:
                time.sleep(1)
                continue
            result = []
            for (_, req) in reqs:
                req = req[CLI_REQ].decode()
                id = req.split("-")
                cli_id, req_id = id[0], id[1]
                rate, res = process_req(cli_id, req_id)
                result.append((cli_id, str(rate)))
                result.append((req, res))

            for (key, arg) in result:
                database.set(key, arg)

        logging.info("Exiting")


class RateLimiter:
    def __init__(self, api_server: ApiServer, db: DataBase,
                 cpu: Optional[int] = None):
        self.rl_workers = []
        for _ in range(N_WORKERS):
            self.rl_workers.append(RLWorker(cpu=cpu))
            self.rl_workers[-1].create_and_run(api_server=api_server, database=db)

    def kill(self) -> None:
        for worker in self.rl_workers:
            worker.kill()


# This is the redis client providing interface to interact with main rate limiters on api servers
class ApiServer:
    def __init__(self, port: int, db: DataBase, cpu: Optional[Iterable[int]] = None):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()
        self.rds.xgroup_create(LOAD, WRK_GRP, id="0", mkstream=True)
        self.rate_limiter = RateLimiter(self, cpu=cpu, db=db)

    # TODO: Implement read and write operations and other functionalities, need to make it fault tolerant

    def add_request(self, cli_req: str):
        self.rds.xadd(LOAD, {CLI_REQ: cli_req})

    def fetch_request(self, worker_name, cnt):
        fileName = self.rds.xreadgroup(WRK_GRP, worker_name, {LOAD: ">"}, count=cnt)
        if fileName:
            return fileName[0][1]
        pending_msgs = self.rds.xpending(LOAD, WRK_GRP)
        if (pending_msgs['pending'] == 0):
            return None
        fileName = self.rds.xautoclaim(LOAD, WRK_GRP, worker_name, IDLE_TIME, 0, count=cnt)
        if (len(fileName[1]) > 0):
            return fileName[1]
        return None

    def kill(self) -> None:
        self.rate_limiter.kill()