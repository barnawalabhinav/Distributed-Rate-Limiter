import logging
import os
import signal
import sys
from threading import current_thread

from client import Client
from constants import *
from database import DataBase
from loadBal import LoadBal
from rateLimiter import RateLimiter

servers = []
clients = []


def sig_handler(signum, frame):
    for proc in clients:
        proc.kill()
    for server in servers:
        server.kill()
    logging.info('Stopped!')
    sys.exit()

# This provides the interface to the web-dashboard where we display the results and perform experiments
# TODO: Decide the arguments that this function takes


def dist_rate_limiter():
    # Clear the log file
    open(LOGFILE, 'w').close()
    logging.basicConfig(filename=LOGFILE,
        level=logging.DEBUG,
        force=True,
        format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
    thread = current_thread()
    thread.name = "main"
    logging.debug('Done setting up loggers.')

    signal.signal(signal.SIGINT, sig_handler)

    # Set up redis-servers
    os.system(f"redis-cli -p {LB_PORT} SHUTDOWN; redis-server --port {LB_PORT} --daemonize yes --server_cpulist 0-0")
    os.system(f"redis-cli -p {DB_PORT} SHUTDOWN; redis-server --port {DB_PORT} --daemonize yes --server_cpulist 1-1")
    for i in range(N_SERVERS):
        os.system(f"redis-cli -p {START_PORT + i} SHUTDOWN; redis-server --port {START_PORT + i} --daemonize yes --server_cpulist {i+2}-{i+2}")
    # os.system(f"bash configure.sh {N_SERVERS} {START_PORT}")


    # TODO: Implement main file that stiches the processes and starts and ends the execution

    load_bal = LoadBal(LB_PORT)
    database = DataBase(DB_PORT)

    for ser_id in range(N_SERVERS):
        servers.append(RateLimiter(port=START_PORT + ser_id, cpu=[ser_id + 2], db=database))

    pid = os.fork()
    if pid == 0:
        load_bal.run()
    else:
        for _ in range(N_CLIENTS):
            clients.append(Client())
            clients[-1].create_and_run(gap=1000)
        load_bal.dist_request(servers)


if __name__ == "__main__":
    dist_rate_limiter()
