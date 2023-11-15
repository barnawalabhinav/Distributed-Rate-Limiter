from __future__ import annotations

import logging
import os
import signal
import time
from typing import Any, Iterable, Optional, Tuple, Final

from flask import Flask, jsonify, request
import requests

from constants import CLI_REQ, N_WORKERS, REQ_LIMIT, DONE, PER_SERVER_REQ_CNT, DEBUG
from base_redis import BaseRedis
from process import Process


class RLRedis(BaseRedis):
    def __init__(self, port: int):
        super(RLRedis, self).__init__(port)
        super(RLRedis, self).create_group()

    def add_to_response_queue(self, req: str, resp: str):
        msg = req + '-' + str(int(time.time()*1000)) + '-' + resp
        self.rds.rpush(DONE, msg)

    def fetch_responses_from_queue(self):
        return self.rds.lpop(DONE, 10000)

    def add_request(self, cli_req: str):
        super(RLRedis, self).add_request(cli_req)

    def fetch_request(self, worker_name, cnt):
        return super(RLRedis, self).fetch_request(worker_name, cnt)


class RLWorker(Process):
    def _process_req(self, cli_id: str, req_time: int, req_id: str, db: BaseRedis, my_rds: BaseRedis) -> Tuple[int, str]:
        try:
            if db.get_req_count(cli_id) >= REQ_LIMIT:
                return "refuted"
            db.add_req(cli_id, req_time, req_id)
            return "accepted"
        except:
            if my_rds.get_req_count(cli_id) >= REQ_LIMIT:
                return "refuted"
            my_rds.add_req(cli_id, req_time, req_id)
            return "accepted"

    # Implement task of workers, fetch requests from api server's redis-stream and process
    def run(self, **kwargs: Any) -> None:
        rl_redis: RLRedis = kwargs['rl_redis']
        database: BaseRedis = kwargs['database']

        while True:
            reqs = rl_redis.fetch_request(self.name, cnt=PER_SERVER_REQ_CNT)
            if not reqs:
                continue
            for (_, req) in reqs:
                req = req[CLI_REQ].decode()
                cli_id, _, req_id, req_time = req.split("-")
                res = self._process_req(cli_id, int(req_time), req_id, database, rl_redis)
                
                # Try to send response to client
                msg = req + '-' + str(int(time.time()*1000)) + '-' + res
                ip, port, msg = msg.split('_')
                flask_url = f'http://{ip}:{int(port)}/add_response'
                data = {
                    'response_data': f'{msg}-{int(time.time() * 1000)}'
                }
                try:
                    response = requests.post(flask_url, json=data)
                except:
                    if DEBUG:
                        logging.debug("Failed to send response")
                    rl_redis.add_to_response_queue(req, res)
                    continue

                # Check the response
                if response.status_code == 200:
                    continue
                else:
                    if DEBUG:
                        logging.debug(f"Failed to respond to client. Status code: {response.status_code}")
                        logging.debug(f"Response content: {response.text}")

                rl_redis.add_to_response_queue(req, res)


class RateLimiter:
    def __init__(self, port: int, listen_port: int, db: Optional[BaseRedis] = None, cpu: Optional[Iterable[int]] = None):
        self.rds = RLRedis(port)
        self.rl_workers = []
        self.listen_port = listen_port
        if db == None:
            db = self.rds

        for _ in range(N_WORKERS):
            self.rl_workers.append(RLWorker(cpu=cpu))
            self.rl_workers[-1].create_and_run(rl_redis=self.rds, database=db)

        self.req_id = 0
        self.app: Final = Flask(__name__)
        self.app.route('/add_request_to_queue', methods=['POST'])(self.add_request)
        self.forks = [self.listen(), self.send_responses()]

    def add_request(self):
        try:
            data = request.get_json()
            if 'request_data' in data:
                request_data = data['request_data']
                cli_id = request_data.split('-')[0] + '@primary'
                if self.rds.get_req_count(cli_id) >= REQ_LIMIT:
                    # print(f"Rejecting Request from client {cli_id}")
                    return jsonify({"error": "Request limit exceeded"}), 400
                req_time = int(time.time() * 1000)
                req = request_data + '-' + str(self.req_id) + '-' + str(req_time)
                self.rds.add_request(req)
                self.rds.add_req(cli_id, req_time, str(self.req_id))
                self.req_id += 1
                return jsonify({"message": "Request added to Queue successfully"})
            else:
                return jsonify({"error": "Missing 'request_data' in the request body"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def send_responses(self):
        pid = os.fork()
        if pid != 0:
            return pid
        while True:
            msgs = self.rds.fetch_responses_from_queue()
            if msgs and len(msgs):
                for msg in msgs:
                    msg = msg.decode()
                    ip, port, msg = msg.split('_')
                    flask_url = f'http://{ip}:{int(port)}/add_response'
                    data = {
                        'response_data': f'{msg}-{int(time.time() * 1000)}'
                    }
                    try:
                        response = requests.post(flask_url, json=data)
                    except:
                        if DEBUG:
                            logging.debug("Failed to send response")
                        continue

                    # Check the response
                    if response.status_code != 200:
                        if DEBUG:
                            logging.debug(f"Failed to respond to client. Status code: {response.status_code}")
                            logging.debug(f"Response content: {response.text}")

    def listen(self):
        pid = os.fork()
        if pid == 0:
            print(f'listening at port {self.listen_port}')
            self.app.run(host='0.0.0.0', port=self.listen_port)
        return pid

    def kill(self) -> None:
        for worker in self.rl_workers:
            worker.kill()
        for pid in self.forks:
            os.kill(pid, signal.SIGKILL)
