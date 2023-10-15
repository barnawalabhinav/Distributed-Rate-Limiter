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


# This is the a worker fetching requests from an APIServer, deciding their rate and writing to commong redis database
class Worker(Process):
    def run(self, **kwargs: Any) -> None:
        apiServer: ApiServer = kwargs['apiServer']
        database: DataBase = kwargs['database']

        # TODO: Implement task of workers, fetch requests from api server's redis-stream and process

        def process_req(self, id: str, req: str):
            return -1, "refuted"

        while (True):
            req = apiServer.fetch_request(cnt=1)
            if not req:
                time.sleep(1)
                continue
            id = req.split("-")
            cli_id, req_id = id[0], id[1]
            rate, result = process_req(cli_id, req_id)
            database.set(cli_id, str(rate))
            database.set(req, result)

        logging.info("Exiting")
