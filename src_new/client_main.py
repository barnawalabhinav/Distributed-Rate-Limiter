import logging
import signal
import sys
import os

from client import Client
from constants import N_CLIENTS, CLIENT_PORT_BEG, LOGFILE, CLIENT_RATES


def sig_handler(signum, frame):
    for client in clients:
        client.kill()
    logging.info('Stopped!')
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)

    open(LOGFILE, 'w').close()
    logging.basicConfig(filename=LOGFILE,
                        level=logging.DEBUG,
                        force=True,
                        format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
    logging.debug('Done setting up loggers.')

    clients = []
    for i in range(N_CLIENTS):
        print(f'Creating client {i}')
        clients.append(Client(id))
        rate = CLIENT_RATES[i]
        time_gap = 1000 // rate
        clients[-1].create_and_run(port=CLIENT_PORT_BEG + i, gap=time_gap)

    while True:
        try:
            pid_killed, status = os.wait()
        except:
            break
