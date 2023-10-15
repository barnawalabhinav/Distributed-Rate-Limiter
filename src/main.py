import os
import sys
import time
import glob
import signal
import logging
from threading import current_thread

from constants import *
from client import Client
from worker import Worker
from loadBal import LoadBal
from database import DataBase
from apiServer import ApiServer
from process import Process


servers = []
clients = []
workers = []

def sig_handler(signum, frame):
    for proc in clients:
        proc.kill()
    for proc in servers:
        proc.kill()
    logging.info('Stopped!')
    sys.exit()

# This provides the interface to the web-dashboard where we display the results and perform experiments
# TODO: Decide the arguments that this function takes


def dist_rate_limiter():
    # Clear the log file
    open(LOGFILE, 'w').close()
    logging.basicConfig(  # filename=LOGFILE,
        level=logging.DEBUG,
        force=True,
        format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
    thread = current_thread()
    thread.name = "main"
    logging.debug('Done setting up loggers.')

    signal.signal(signal.SIGINT, sig_handler)

    # Set up redis-servers
    os.system(f"bash configure.sh {N_SERVERS} {START_PORT}")

    # TODO: Implement main file that stiches the processes and starts and ends the execution

    load_bal = LoadBal(START_PORT - 1)
    database = DataBase(START_PORT - 2)

    for ser_id in range(N_SERVERS):
        servers.append(ApiServer(START_PORT + ser_id))
        for _ in range(N_WORKERS):
            workers.append(Worker(cpu = ser_id + 2))

    for idx, worker in enumerate(workers):
        worker.create_and_run(apiServer = servers[idx // N_WORKERS], database = database)

    for _ in range(N_CLIENTS):
        clients.append(Client())
        clients[-1].create_and_run(loadBal = load_bal)

    server_id = 0
    while (True):
        load_bal.dist_request(servers[server_id], cnt=1)
        server_id = (server_id + 1) % N_SERVERS

if __name__ == "__main__":
    dist_rate_limiter()
