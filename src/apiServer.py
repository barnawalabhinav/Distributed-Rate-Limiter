from __future__ import annotations

import logging
import time
from typing import Iterable, Optional, Any, Tuple
from redis.client import Redis

from constants import CLI_REQ, LOAD, WRK_GRP, IDLE_TIME, N_WORKERS, REQ_LIMIT
from src.database import DataBase
from src.process import Process


class RLWorker(Process):
    def _process_req(self, cli_id: str, req_time: int, db: DataBase) -> Tuple[int, str]:
        if db.get_req_count(cli_id) > REQ_LIMIT:
            print(f"Rejecting Request from time {req_time}")
            return -1, "refuted"

        db.add_req(cli_id, req_time)
        print(f"Accepting Request from time {req_time}")
        return -1, "accepted"

    def run(self, **kwargs: Any) -> None:
        apiServer: ApiServer = kwargs['api_server']
        database: DataBase = kwargs['database']

        # TODO: Implement task of workers, fetch requests from api server's redis-stream and process

        while True:
            reqs = apiServer.fetch_request(self.name, cnt=2)
            if not reqs:
                time.sleep(1)
                continue
            result = []
            for (_, req) in reqs:
                req = req[CLI_REQ].decode()
                cli_id, req_time = req.split("-")
                rate, res = self._process_req(cli_id, int(req_time), database)
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