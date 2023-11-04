import logging
import os
import time
import socket
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify, request
import requests

from constants import REQUEST_IPS, REQUEST_PORTS, CLIENT_ANALYSIS_WINDOW_LEN, TOTAL_CLIENT_REQUESTS
from process import Process


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def __init__(self):
        super(Client, self).__init__()
        self.start_time = time.time() * 1000

        '''
        self.data stores the results of requests in the given format
        key: start_time-end_time
        value: [accepted_count, rejected_count, latency, rtt]
        '''
        self.data: Dict[str, List[int, int, int, int]] = {}

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
                    <rate limiter response send timestamp>-
                    <result (accepted/refuted)>
                }
                '''

                # TODO: Perform analysis on the response
                response_time = time.time() * 1000
                _, sent_time, _, rl_recv_time, rl_end_time, rl_response_send_time, res = response_data.split('-')

                rtt = (response_time - int(rl_response_send_time)) + (int(rl_recv_time) - int(sent_time))
                processing_latency = int(rl_end_time) - int(rl_recv_time)

                req_window_start = (sent_time // 1000 - self.start_time) // CLIENT_ANALYSIS_WINDOW_LEN
                req_window = f'{req_window_start}-{req_window_start + CLIENT_ANALYSIS_WINDOW_LEN}'

                if req_window in self.data:
                    self.data[req_window][2] += processing_latency
                    self.data[req_window][3] += rtt
                else:
                    self.data[req_window] = [0, 0, processing_latency, rtt]

                if res == 'accepted':
                    self.data[req_window][0] += 1
                else:
                    self.data[req_window][1] += 1

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
            i = 0
            while i < TOTAL_CLIENT_REQUESTS:
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
                else:
                    i += 1
                #     logging.debug("Request successfully added to the queue")
                    
                # loadBal.add_request(str(self.pid) + "-" + str(int(time.time() + 0.5)))
                time.sleep(time_gap/1000)

            df = pd.DataFrame(columns=['Window', 'Latency', 'RTT', 'Accepted', 'Rejected'], index=None)
            for i, (key, value) in enumerate(self.data.items()):
                accepted_count, rejected_count, latency, rtt = value
                df.loc[i] = {'Window': key,
                             'Latency': latency / (accepted_count + rejected_count),
                             'RTT': rtt / (accepted_count + rejected_count),
                             'Accepted': accepted_count,
                             'Rejected': rejected_count}

            df.to_csv(f'../data/Client_{self.pid}_data.csv', index=False)