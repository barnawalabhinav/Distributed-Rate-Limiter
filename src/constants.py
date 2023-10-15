from typing import Final

LOGFILE: Final[str] = "/tmp/wc.log"
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

N_CLIENTS: Final[int] = 8
N_WORKERS: Final[int] = 2
