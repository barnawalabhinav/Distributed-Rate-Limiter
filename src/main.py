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


def sig_handler(signum, frame):
    for rl in rate_limiters:
        rl.kill()
    logging.info('Stopped!')
    sys.exit()


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
    # # With Pinned CPUs
    # os.system(f"redis-cli -p {DB_PORT} SHUTDOWN; redis-server --port {DB_PORT} --daemonize yes --server_cpulist 0-0")
    # for i in range(N_SERVERS):
    #     os.system(f"redis-cli -p {START_PORT + i} SHUTDOWN; redis-server --port {START_PORT + i} --daemonize yes --server_cpulist {i+1}-{i+1}")
    #     # if not COMMON_DB:
    #     #     os.system(f"redis-cli -p {START_PORT + N_SERVERS + i} SHUTDOWN; redis-server --port {START_PORT + N_SERVERS + i} --daemonize yes --server_cpulist {i+1}-{i+1}")

    # Without Pinned CPUs
    os.system(f"redis-cli -p {DB_PORT} SHUTDOWN; redis-server --port {DB_PORT} --daemonize yes")
    for i in range(N_SERVERS):
        os.system(f"redis-cli -p {START_PORT + i} SHUTDOWN; redis-server --port {START_PORT + i} --daemonize yes")
        # if not COMMON_DB:
        #     os.system(f"redis-cli -p {START_PORT + N_SERVERS + i} SHUTDOWN; redis-server --port {START_PORT + N_SERVERS + i} --daemonize yes")

    # if COMMON_DB:
    #     os.system(f"bash configure_raft.sh {' '.join(RAFT_PORTS)}")

    database = DataBase(DB_PORT) if COMMON_DB else None

    if COMMON_DB:
        print("Database is common")
    else:
        print("Database is not common")

    idx = 0
    for ser_id in range(N_SERVERS):
        # if not common_database:
        #     database = BaseRedis(START_PORT + N_SERVERS + ser_id)
        # With Pinned CPUs
        # rate_limiters.append(RateLimiter(port=START_PORT + ser_id, listen_port=REQUEST_PORTS[idx], cpu=[ser_id + 2], db=database))
        
        # Without Pinned CPUs
        rate_limiters.append(RateLimiter(port=START_PORT + ser_id, listen_port=REQUEST_PORTS[idx], db=database))
        idx += 1
    
    while True:
        try:
            pid_killed, status = os.wait()
            print(pid_killed, status)
        except:
            break


if __name__ == "__main__":
    dist_rate_limiter()
