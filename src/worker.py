import logging
import itertools
import glob
import os
from typing import Any
import pandas as pd
from process import Process
from apiServer import ApiServer
from database import DataBase


# This is the a worker fetching requests from an APIServer, deciding their rate and writing to commong redis database
class Worker(Process):
    def run(self, **kwargs: Any) -> None:
        apiServer: ApiServer = kwargs['apiServer']
        database: DataBase = kwargs['database']

        # TODO: Implement task of workers, fetch requests from api server's redis-stream and process

        logging.info("Exiting")
