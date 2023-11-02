from __future__ import annotations

import logging
import time
from typing import Any, Iterable, Optional, Tuple

from redis.client import Redis

from constants import CLI_REQ, IDLE_TIME, LOAD, N_WORKERS, REQ_LIMIT, WRK_GRP
from base_redis import BaseRedis
from process import Process


class RLRedis(BaseRedis):
    def __init__(self, port: int):
        super(RLRedis, self).__init__(port)
        super(RLRedis, self).create_group()

    def add_request(self, cli_req: str):
        super(RLRedis, self).add_request(cli_req)

    def fetch_request(self, worker_name, cnt):
        return super(RLRedis, self).fetch_request(worker_name, cnt)
        # pending_msgs = super(RLRedis, self).rds.xpending(LOAD, WRK_GRP)
        # if (pending_msgs['pending'] == 0):
        #     return None
        # fileName = super(RLRedis, self).rds.xautoclaim(LOAD, WRK_GRP, worker_name, IDLE_TIME, 0, count=cnt)
        # if (len(fileName[1]) > 0):
        #     return fileName[1]
        # return None


class RLWorker(Process):
    def _process_req(self, cli_id: str, req_time: int, req_id: str, db: BaseRedis) -> Tuple[int, str]:
        if db.get_req_count(cli_id) >= REQ_LIMIT:
            print(
                f"Rejecting Request from time {req_time} at time {int(time.time() + 0.5)}")
            return -1, "refuted"

        db.add_req(cli_id, req_time, req_id)
        print(
            f"Accepting Request from time {req_time} at time {int(time.time() + 0.5)}")
        return -1, "accepted"

    # Implement task of workers, fetch requests from api server's redis-stream and process
    def run(self, **kwargs: Any) -> None:
        rl_redis: RLRedis = kwargs['rl_redis']
        database: BaseRedis = kwargs['database'] if kwargs['database'] is not None else rl_redis

        while True:
            reqs = rl_redis.fetch_request(self.name, cnt=2)
            if not reqs:
                time.sleep(1)
                continue
            result = []
            for (_, req) in reqs:
                req = req[CLI_REQ].decode()
                cli_id, req_time, req_id = req.split("-")
                rate, res = self._process_req(
                    cli_id, int(req_time), req_id, database)
                result.append((cli_id, str(rate)))
                result.append((req, res))
            
            for (key, arg) in result:
                database.set(key, arg)


# class RateLimiter:
#     def __init__(self, api_server: ApiServer, db: DataBase,
#                  cpu: Optional[int] = None):
#         self.rl_workers = []
#         for _ in range(N_WORKERS):
#             self.rl_workers.append(RLWorker(cpu=cpu))
#             self.rl_workers[-1].create_and_run(api_server=api_server, database=db)

#     def kill(self) -> None:
#         for worker in self.rl_workers:
#             worker.kill()


class RateLimiter:
    def __init__(self, port: int, db: Optional[BaseRedis] = None, cpu: Optional[Iterable[int]] = None):
        self.rds = RLRedis(port)
        # self.rate_limiter = RateLimiter(self, cpu=cpu, db=db)
        self.rl_workers = []
        for _ in range(N_WORKERS):
            self.rl_workers.append(RLWorker(cpu=cpu))
            self.rl_workers[-1].create_and_run(rl_redis=self.rds, database=db)

    def add_request(self, cli_req: str) -> None:
        self.rds.add_request(cli_req)

    def kill(self) -> None:
        # self.rate_limiter.kill()
        for worker in self.rl_workers:
            worker.kill()
