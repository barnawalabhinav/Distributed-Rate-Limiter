import logging
import os
import time
import socket
from typing import Any, Dict, List, Final

import pandas as pd
from flask import Flask, jsonify, request
import requests

from constants import REQUEST_IP, REQUEST_PORTS, CLIENT_ANALYSIS_WINDOW_LEN, TOTAL_CLIENT_REQUESTS, COMMON_DB
from process import Process


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def __init__(self, **kwargs: Any):
        super(Client, self).__init__()
        self.start_time: Final[int] = int(time.time())
        self.id: Final[int] = kwargs['id']
        self.filename = None
        if COMMON_DB:
            self.filename = f'../data/client_{self.id}_common_db.csv'
        else:
            self.filename = f'../data/client_{self.id}.csv'

        # clear the contents of the output file
        open(self.filename, 'w').close()

    def _get_response(self):
        try:
            data = request.get_json()
            response_time = int(time.time() * 1000)
            if 'response_data' in data:
                response_data = data['response_data']

                '''
                response_data = {
                    <self.pid>-
                    <client sent timestamp>-
                    <request id assigned by rate limiter>-
                    <rate limiters receipt timestamp>-
                    <rate limiters finish timstamp>-
                    <result (accepted/refuted)>-
                    <rate limiter response time>
                }
                '''

                # TODO: Perform analysis on the response
                _, sent_time, _, rl_recv_time, rl_end_time, res, rl_response_time = response_data.split('-')
                processing_latency = int(rl_end_time) - int(rl_recv_time)
                rtt = (response_time - int(rl_response_time)) + (int(rl_recv_time) - int(sent_time))

                req_window_start = ((int(sent_time) // 1000 - self.start_time) // CLIENT_ANALYSIS_WINDOW_LEN) * \
                                   CLIENT_ANALYSIS_WINDOW_LEN
                req_window = f'{req_window_start}-{req_window_start + CLIENT_ANALYSIS_WINDOW_LEN - 1}'

                with open(self.filename, 'a') as file:
                    print(f'{req_window}:{res}-{processing_latency}-{rtt}', file=file)

                # print(f"response = {response_data}")
                return jsonify({"message": "Response received successfully"})
            else:
                return jsonify({"error": "Missing 'response_data' in the request body"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def run(self, **kwargs: Any) -> None:
        self.flask_urls = []
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        self.port = kwargs['port']
        for i in range(len(REQUEST_PORTS)):
            self.flask_urls.append(
                f"http://{REQUEST_IP}:{REQUEST_PORTS[i]}/add_request_to_queue")

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
            while i < TOTAL_CLIENT_REQUESTS[self.id]:
                data = {
                    'request_data': (str(self.ip) + '_' + str(self.port) + '_' + str(self.pid) + "-" + str(
                        int(time.time() * 1000)))
                }
                try:
                    # Send a POST request to the Flask app
                    response = requests.post(
                        self.flask_urls[ser_id], json=data)
                    ser_id = (ser_id + 1) % len(self.flask_urls)
                except:
                    logging.debug("Failed to add request to the queue")
                    # time.sleep(time_gap/1000)
                    continue

                # Check the response
                if response != 200:
                    logging.debug(f"Failed to add request to the queue. Status code: {response.status_code}")
                    logging.debug(f"Response content: {response.text}")

                i += 1
                # print(i)
                # logging.debug("Request successfully added to the queue")

                # loadBal.add_request(str(self.pid) + "-" + str(int(time.time() + 0.5)))
                time.sleep(time_gap / 1000)

            # print(f'Waiting 10 seconds before outputting data in csv file')
            # time.sleep(10)
            #
            # print(self.data)
            #
            # df = pd.DataFrame(columns=['Window', 'Latency', 'RTT', 'Accepted', 'Rejected'], index=None)
            # for i, (key, value) in enumerate(self.data.items()):
            #     accepted_count, rejected_count, latency, rtt = value
            #     df.loc[i] = {'Window': key,
            #                  'Latency': latency / (accepted_count + rejected_count),
            #                  'RTT': rtt / (accepted_count + rejected_count),
            #                  'Accepted': accepted_count,
            #                  'Rejected': rejected_count}
            #
            # df.to_csv(f'../data/Client_{self.pid}_data.csv', index=False)
            #
            # print('Data written to csv')

            print(f'Client {self.id} is done!!')

            while True:
                try:
                    _, _ = os.wait()
                except:
                    break
