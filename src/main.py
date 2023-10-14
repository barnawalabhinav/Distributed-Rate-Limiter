import glob
import logging
import os
import signal
import sys
import time
from threading import current_thread
from constants import *

processes = []


def sig_handler(signum, frame):
    for w in processes:
        w.kill()
    logging.info('Bye!')
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


if __name__ == "__main__":
    dist_rate_limiter()
