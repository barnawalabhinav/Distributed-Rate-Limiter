from typing import Final

LOGFILE: Final[str] = "temp.log"
DONE: Final[str] = "DONE"

# Number of API Servers; there are two additional redis-servers by default
N_SERVERS: Final[int] = 3

# Servers are ports on and after this consecutively. Two default servers are assigned ports consecutively preceeding this
START_PORT: Final[int] = 7000

LOAD: Final[bytes] = b"LOAD"
SER_GRP: Final[str] = "SERVER"
CLI_GRP: Final[str] = "CLIENT"
WRK_GRP: Final[str] = "WORKER"
CLI_REQ: Final[bytes] = b"REQUEST"
IDLE_TIME: Final[int] = 1000  # In milliseconds

N_CLIENTS: Final[int] = 1
N_WORKERS: Final[int] = 2

PER_SERVER_REQ_CNT: Final[int] = 1
REQ_LIMIT: Final[int] = 1
REQ_EXPIRY_TIME: Final[int] = 10

IPS = ["10.17.7.57", "10.17.7.208", "10.17.7.217"]
REQUEST_IP: Final[str] = 'localhost'
REQUEST_PORT: Final[int] = 8080
LB_IP: Final[str] = 'localhost'
LB_PORT: Final[int] = 6501
DB_IP: Final[str] = 'localhost'
DB_PORT: Final[int] = 6000

COMMON_DB: Final[bool] = True
RAFT_PORTS: Final = [str(DB_PORT), str(DB_PORT + 1), str(DB_PORT + 2)]
