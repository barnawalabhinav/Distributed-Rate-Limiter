import logging
import os
import time
import socket
import signal
from typing import Any, Final

from flask import Flask, jsonify, request
import requests

from constants import REQUEST_IPS, REQUEST_PORTS
from load_bal import LoadBal
from process import Process


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def _get_response(self):
        try:
            data = request.get_json()
            if 'response_data' in data:
                response_data = data['response_data']
                
                '''
                response_data = {
                    <self.pid>-
                    <client sent timestamp>-
                    <request id assigned by rate limiter>-
                    <rate limiters receipt timestamp>-
                    <rate limiters finish timstamp>-
                    <result (accepted/refuted)>
                }
                '''

                # TODO: Perform analysis on the response

                # print(f"response = {response_data}")
                return jsonify({"message": "Response received successfully"})
            else:
                return jsonify({"error": "Missing 'response_data' in the request body"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def run(self, **kwargs: Any) -> None:
        self.flask_urls = []
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = kwargs['port']
        for i in range(len(REQUEST_IPS)):
            self.flask_urls.append(
                f"http://{REQUEST_IPS[i]}:{REQUEST_PORTS[i]}/add_request_to_queue")

        # Number of milliseconds to wait before sending the next request
        time_gap: int = kwargs['gap']

        pid = os.fork()
        if pid == 0:
            app = Flask(__name__)
            app.route('/add_response', methods=['POST'])(self._get_response)
            app.run(host='0.0.0.0', port=self.port)
        else:
            self.forks.append(pid)
            ser_id = 0
            while True:
                data = {
                    'request_data': (str(self.ip) + '_' + str(self.port) + '_' + str(self.pid) + "-" + str(int(time.time()*1000)))
                }
                try:
                    # Send a POST request to the Flask app
                    response = requests.post(self.flask_urls[ser_id], json=data)
                    ser_id = (ser_id + 1) % len(self.flask_urls)
                except:
                    logging.debug("Failed to add request to the queue")
                    # time.sleep(time_gap/1000)
                    continue

                # Check the response
                if response != 200:
                    logging.debug(f"Failed to add request to the queue. Status code: {response.status_code}")
                    logging.debug(f"Response content: {response.text}")
                # else:
                #     logging.debug("Request successfully added to the queue")
                    
                # loadBal.add_request(str(self.pid) + "-" + str(int(time.time() + 0.5)))
                time.sleep(time_gap/1000)
