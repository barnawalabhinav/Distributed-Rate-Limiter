import logging
import os
import time
import socket
from typing import Any, Final

from flask import Flask, jsonify, request
import requests

from constants import REQUEST_IP, REQUEST_PORTS, CLIENT_ANALYSIS_WINDOW_LEN, TOTAL_CLIENT_REQUESTS, COMMON_DB, DEBUG
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
        
        # with open(self.filename, 'a') as file:
        #     print(f'Processing Latency,RTT,Acceptence Rate', file=file)

        self.avg_rtt = 0
        self.accept_rate = 0
        self.avg_proc_lat = 0
        self.cnt_responses = 0

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
                # # Excluding Queueing Time
                # rtt = (response_time - int(rl_response_time)) + (int(rl_recv_time) - int(sent_time))
                
                # Including Queueing Time
                total_rtt = (response_time - int(sent_time)) - processing_latency

                req_window_start = ((int(sent_time) // 1000 - self.start_time) // CLIENT_ANALYSIS_WINDOW_LEN) * CLIENT_ANALYSIS_WINDOW_LEN
                req_window = f'{req_window_start}-{req_window_start + CLIENT_ANALYSIS_WINDOW_LEN - 1}'

                # with open(self.filename, 'a') as file:
                #     print(f'{req_window}:{res}-{processing_latency}-{rtt}', file=file)

                self.avg_proc_lat = (self.avg_proc_lat * self.cnt_responses + processing_latency) / (self.cnt_responses + 1)
                self.avg_rtt = (self.avg_rtt * self.cnt_responses + total_rtt) / (self.cnt_responses + 1)
                self.accept_rate = (self.accept_rate * self.cnt_responses + (res == 'accepted')) / (self.cnt_responses + 1)
                self.cnt_responses += 1
                if (self.cnt_responses % 300) == 0:
                    # with open(self.filename, 'a') as file:
                    # #     print(f'{self.avg_proc_lat},{self.avg_rtt},{self.accept_rate}', file=file)
                    #     print(f'{self.accept_rate}', file=file)

                    print(f'Client {self.id} - Average Processing Latency = {self.avg_proc_lat} ms')
                    print(f'Client {self.id} - Average RTT = {self.avg_rtt} ms')
                    print(f'Client {self.id} - Acceptance Rate = {self.accept_rate}')

                    # self.avg_rtt = 0
                    # self.accept_rate = 0
                    # self.avg_proc_lat = 0
                    # self.cnt_responses = 0

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
        for num_attempts in range(len(REQUEST_PORTS)):
            self.flask_urls.append(
                f"http://{REQUEST_IP}:{REQUEST_PORTS[num_attempts]}/add_request_to_queue")

        # Number of milliseconds to wait before sending the next request
        time_gap: int = kwargs['gap']

        pid = os.fork()
        if pid == 0:
            app = Flask(__name__)
            app.route('/add_response', methods=['POST'])(self._get_response)
            app.run(host='0.0.0.0', port=self.port)
        else:
            success_rate = 0
            num_attempts = 0
            self.forks.append(pid)
            ser_id = 0
            prev_time = int(time.time() * 1000)
            while num_attempts < TOTAL_CLIENT_REQUESTS[self.id]:
                data = {
                    'request_data': (str(self.ip) + '_' + str(self.port) + '_' + str(self.pid) + "-" + str(
                        int(time.time() * 1000)))
                }
                try:
                    response = requests.post(self.flask_urls[ser_id], json=data)
                    ser_id = (ser_id + 1) % len(self.flask_urls)
                    # print("Gap: ", int(time.time() * 1000) - prev_time)
                except:
                    if DEBUG:
                        logging.debug("Failed to add request to the queue")
                    continue

                # Check the response
                if response != 200:
                    if DEBUG:
                        logging.debug(f"Failed to add request to the queue. Status code: {response.status_code}")
                        logging.debug(f"Response content: {response.text}")

                success_rate = (success_rate * num_attempts + (response.status_code == 200)) / (num_attempts + 1)
                if (num_attempts + 1) % 300 == 0:
                    print(f'Client {self.id} Request Success rate = {success_rate}')

                num_attempts += 1
                curr_gap = int(time.time() * 1000) - prev_time
                prev_time = int(time.time() * 1000)
                if curr_gap < time_gap:
                    time.sleep((time_gap - curr_gap) / 10000)

            print(f'Client {self.id} is done!!')

            while True:
                try:
                    _, _ = os.wait()
                except:
                    break
