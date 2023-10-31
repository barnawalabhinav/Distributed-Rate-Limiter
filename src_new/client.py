import logging
import time
from typing import Any, Final

import requests

from constants import REQUEST_IP, REQUEST_PORT
from load_bal import LoadBal
from process import Process


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def run(self, **kwargs: Any) -> None:
        self.flask_url= f"http://{REQUEST_IP}:{REQUEST_PORT}/add_request_to_queue"
        # Number of milliseconds to wait before sending the next request
        time_gap: int = kwargs['gap']

        # TODO: Implement the task of clients, send requests at various frequency

        while True:
            data = {
                'request_data': (str(self.pid) + "-" + str(int(time.time() + 0.5)))
            }
            try:
                # Send a POST request to the Flask app
                response = requests.post(self.flask_url, json=data)
            except:
                logging.debug("Failed to add request to the queue")
                continue

            # Check the response
            if response.status_code == 200:
                logging.debug("Request successfully added to the queue")
            else:
                logging.debug(f"Failed to add request to the queue. Status code: {response.status_code}")
                logging.debug("Response content:", response.text)
            # loadBal.add_request(str(self.pid) + "-" + str(int(time.time() + 0.5)))
            time.sleep(time_gap/1000)

