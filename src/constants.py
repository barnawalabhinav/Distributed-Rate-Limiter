from typing import Final, List

DEBUG: Final[bool] = False
LOGFILE: Final[str] = "temp.log"

# Number of API Servers
N_SERVERS: Final[int] = 3

# Servers are ports on and after this consecutively.
START_PORT: Final[int] = 7000

LOAD: Final[bytes] = b"LOAD"
DONE: Final[bytes] = b"DONE"
CLIENTS: Final[str] = "CLIENT_IDS"
WRK_GRP: Final[str] = "WORKER"
CLI_REQ: Final[bytes] = b"REQUEST"

N_CLIENTS: Final[int] = 4
CLIENT_RATES: Final[List[int]] = [20] * N_CLIENTS  # per second
N_WORKERS: Final[int] = 16

PER_SERVER_REQ_CNT: Final[int] = 100
REQ_LIMIT: Final[int] = 10
REQ_EXPIRY_TIME: Final[int] = 1

REQUEST_IP: Final[str] = 'localhost'
REQUEST_PORTS: Final = [8080, 8081, 8082]
CLIENT_PORT_BEG: Final = 9080

DB_IP: Final[str] = 'localhost'
DB_PORT: Final[int] = 6000

COMMON_DB: Final[bool] = False
RAFT_PORTS: Final = [str(DB_PORT), str(DB_PORT + 1), str(DB_PORT + 2)]

CLIENT_ANALYSIS_WINDOW_LEN: Final[int] = 100
RUNTIME: Final[int] = 20
TOTAL_CLIENT_REQUESTS: Final[List[int]] = [RUNTIME * rate for rate in CLIENT_RATES]
