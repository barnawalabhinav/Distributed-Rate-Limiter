import logging
import os
import signal
import sys
import time
from threading import current_thread

from constants import *
from database import DataBase
from rate_limiter import RateLimiter

rate_limiters = []
# clients = []
# forks = []


def sig_handler(signum, frame):
    for rl in rate_limiters:
        rl.kill()
    # for client in clients:
    #     client.kill()
    # for pid in forks:
    #     os.kill(pid, signal.SIGKILL)
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
    # os.system(
    #     f"redis-cli -p {LB_PORT} SHUTDOWN; redis-server --port {LB_PORT} --daemonize yes --server_cpulist 0-0")
    os.system(
        f"redis-cli -p {DB_PORT} SHUTDOWN; redis-server --port {DB_PORT} --daemonize yes --server_cpulist 1-1")
    for i in range(N_SERVERS):
        os.system(
            f"redis-cli -p {START_PORT + i} SHUTDOWN; redis-server --port {START_PORT + i} --daemonize yes --server_cpulist {i+2}-{i+2}")
    # os.system(f"bash configure.sh {N_SERVERS} {START_PORT}")

    if COMMON_DB:
        os.system(f"bash configure_raft.sh {' '.join(RAFT_PORTS)}")
        time.sleep(1)

    # load_bal = LoadBal(LB_PORT)
    database = DataBase(DB_PORT) if COMMON_DB else None

    idx = 0
    for ser_id in range(N_SERVERS):
        rate_limiters.append(RateLimiter(port=START_PORT + ser_id,
                             listen_port=REQUEST_PORTS[idx], cpu=[ser_id + 2], db=database))
        idx += 1

    # pid = os.fork()
    # if pid == 0:
    #     load_bal.run()
    # else:
        # forks.append(pid)
        # for i in range(N_CLIENTS):
        #     print(f'Creating client {i}')
        #     clients.append(Client())
        #     clients[-1].create_and_run(gap=1)
        # pid = os.fork()
        # if pid == 0:

    '''
    clients = set()
    while len(clients) < N_CLIENTS:
        for rl in rate_limiters:
            clients.update(rl.rds.fetch_clients())

    client_ids = []
    for cli in clients:
        cli = cli.decode().split(':')[1]
        client_ids.append(cli)

    while True:
        # TODO: divyanka, for each client, no of reqs accepted in the past REQ_EXPIRY_TIME seconds
        time.sleep(REQ_EXPIRY_TIME)
        for cli_id in client_ids:
            if COMMON_DB:
                cnt = database.get_req_count(cli_id)
            else:
                cnt = 0
                for rl in rate_limiters:
                    cnt += rl.rds.get_req_count(cli_id)
            print(
                f'Accepted {cnt} requests for client {cli_id} in past {REQ_EXPIRY_TIME} seconds')
    '''
        # else:
        #     forks.append(pid)
        #     load_bal.dist_request(rate_limiters)
    
    while True:
        try:
            pid_killed, status = os.wait()
            print(pid_killed, status)
        except:
            break


if __name__ == "__main__":
    dist_rate_limiter()
