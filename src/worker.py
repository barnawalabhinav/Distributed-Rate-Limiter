import os
import time
import glob
import logging
import itertools
import pandas as pd
from typing import Any

from process import Process
from database import DataBase
from apiServer import ApiServer
from constants import CLI_REQ

# This is the a worker fetching requests from an APIServer, deciding their rate and writing to commong redis database
class Worker(Process):
    def run(self, **kwargs: Any) -> None:
        apiServer: ApiServer = kwargs['apiServer']
        database: DataBase = kwargs['database']

        # TODO: Implement task of workers, fetch requests from api server's redis-stream and process

        def process_req(id: str, req: str):
            return -1, "refuted"

        while (True):
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
