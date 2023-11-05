import logging
import os
import time
import socket
from typing import Any, Dict, List, Final

import pandas as pd
from flask import Flask, jsonify, request
import requests

from constants import REQUEST_IP, REQUEST_PORTS, CLIENT_ANALYSIS_WINDOW_LEN, TOTAL_CLIENT_REQUESTS
from process import Process


# This is the a client requesting accesses to the API, interacts with the load balancer
class Client(Process):
    def __init__(self):
        super(Client, self).__init__()
        self.start_time: Final[int] = int(time.time())

        '''
        self.data stores the results of requests in the given format
        key: start_time-end_time
        value: [accepted_count, rejected_count, cum_latency, cum_rtt]
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
                    <result (accepted/refuted)>-
                    <rate limiter response send timestamp>
                }
                '''

                # TODO: Perform analysis on the response
                response_time = int(time.time() * 1000)
                _, sent_time, _, rl_recv_time, rl_end_time, res, rl_response_send_time = response_data.split('-')

                rtt = (response_time - int(rl_response_send_time)) + (int(rl_recv_time) - int(sent_time))
                processing_latency = int(rl_end_time) - int(rl_recv_time)

                req_window_start = ((int(sent_time) // 1000 - self.start_time) // CLIENT_ANALYSIS_WINDOW_LEN) \
                                   * CLIENT_ANALYSIS_WINDOW_LEN
                req_window = f'{req_window_start}-{req_window_start + CLIENT_ANALYSIS_WINDOW_LEN - 1}'

                print(f'{req_window}:[{res}, {processing_latency}, {rtt}]')

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
        # self.ip = socket.gethostbyname(socket.gethostname())
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

                i += 1
                print(i)

                # Check the response
                if response != 200:
                    logging.debug(f"Failed to add request to the queue. Status code: {response.status_code}")
                    logging.debug(f"Response content: {response.text}")
                # else:
                #     logging.debug("Request successfully added to the queue")

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

            while True:
                try:
                    _, _ = os.wait()
                except:
                    break
