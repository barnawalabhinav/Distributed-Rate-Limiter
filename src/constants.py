from typing import Final, List


# *********************** TUNE THESE CONSTANT AS NEEDED *********************** #

N_SERVERS: Final[int] = 3 # Number of API Servers
RUNTIME: Final[int] = 20 # Total Runtime
N_CLIENTS: Final[int] = 4 # Number of Clients to be run on this machine
CLIENT_RATES: Final[List[int]] = [20] * N_CLIENTS # List of client rates (number of requests per second)
N_WORKERS: Final[int] = 8 # Number of workers per server
REQ_LIMIT: Final[int] = 10 # Global Rate Limit for each client (number of requests per second)
REQUEST_IP: Final[str] = 'localhost' # IP address of the API Servers
COMMON_DB: Final[bool] = True # Whether to use a shared DataBase or not
DB_IP: Final[str] = 'localhost' # IP address of the shared DataBase

# ***************************************************************************** #

START_PORT: Final[int] = 7000 # Servers are ports on and after this consecutively.
DB_PORT: Final[int] = 6000
RAFT_PORTS: Final = [str(DB_PORT), str(DB_PORT + 1), str(DB_PORT + 2)]
REQUEST_PORTS: Final = [8080, 8081, 8082]
CLIENT_PORT_BEG: Final = 9080

LOAD: Final[bytes] = b"LOAD"
DONE: Final[bytes] = b"DONE"
CLIENTS: Final[str] = "CLIENT_IDS"
WRK_GRP: Final[str] = "WORKER"
CLI_REQ: Final[bytes] = b"REQUEST"

PER_SERVER_REQ_CNT: Final[int] = 100
REQ_EXPIRY_TIME: Final[int] = 1
CLIENT_ANALYSIS_WINDOW_LEN: Final[int] = 100
TOTAL_CLIENT_REQUESTS: Final[List[int]] = [RUNTIME * rate for rate in CLIENT_RATES]

DEBUG: Final[bool] = False
LOGFILE: Final[str] = "temp.log"
