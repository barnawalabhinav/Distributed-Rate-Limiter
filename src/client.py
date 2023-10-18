import time
import logging
from typing import Any

from process import Process
from loadBal import LoadBal


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def run(self, **kwargs: Any) -> None:
        loadBal: LoadBal = kwargs['loadBal']
        
        # Number of milliseconds to wait before sending the next request
        time_gap: int = kwargs['gap']

        # TODO: Implement the task of clients, send requests at various frequency

        while True:
            loadBal.add_request(str(self.pid) + "-" + str(time.time()))
            time.sleep(time_gap/1000)

        logging.info("Exiting")
