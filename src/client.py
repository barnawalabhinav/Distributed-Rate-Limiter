import logging
import itertools
import glob
import os
from typing import Any
import pandas as pd
from process import Process
from loadBal import LoadBal


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def run(self, **kwargs: Any) -> None:
        loadBal: LoadBal = kwargs['loadBal']

        # TODO: Implement the task of clients, send requests at various frequency

        logging.info("Exiting")
