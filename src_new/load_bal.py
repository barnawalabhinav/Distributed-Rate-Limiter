from __future__ import annotations

from typing import Final, List

from flask import Flask, jsonify, request
from redis.client import Redis

from constants import LOAD, N_SERVERS, PER_SERVER_REQ_CNT, REQUEST_PORTS
from rate_limiter import RateLimiter


class LoadBal:
    def __init__(self, port: int):
        self.rds = Redis(host='localhost', port=port, db=0, decode_responses=False)
        self.rds.flushall()
        self.app: Final = Flask(__name__)
        self.app.route('/add_request_to_queue', methods=['POST'])(self.add_request)

    def add_request(self):
        try:
            data = request.get_json()
            if 'request_data' in data:
                request_data = data['request_data']
                self.rds.rpush(LOAD, request_data)
                print(f"request = {request_data}")
                return jsonify({"message": "Request added to Redis queue successfully"})
            else:
                return jsonify({"error": "Missing 'request_data' in the request body"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def dist_request(self, rate_limiters: List[RateLimiter]):
        cur_server = 0
        req_id = 0
        while True:
            reqs = self.rds.lpop(LOAD, PER_SERVER_REQ_CNT)
            if reqs and len(reqs):
                for req in reqs:
                    req = req.decode() + '-' + str(req_id)
                    rate_limiters[cur_server].add_request(req)
                    req_id += 1

                cur_server = (cur_server + 1) % N_SERVERS

    def run(self):
        self.app.run(host='0.0.0.0', port=REQUEST_PORT)
