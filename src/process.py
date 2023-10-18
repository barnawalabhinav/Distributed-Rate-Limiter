from __future__ import annotations

import os
import sys
import signal
import logging
from typing import Any
from abc import abstractmethod, ABC
from threading import current_thread


# Creation of a new process; this class inherited by both workers and clients
class Process(ABC):
    def __init__(self, **kwargs: Any):
        self.name = "worker-?"
        self.pid = -1
        self.cpu = kwargs['cpu'] if 'cpu' in kwargs else None
        # self.crash = kwargs['crash'] if 'crash' in kwargs else False
        # self.slow = kwargs['slow'] if 'slow' in kwargs else False
        # self.cpulimit = kwargs['limit'] if 'slow' in kwargs and 'limit' in kwargs else 100

    def create_and_run(self, **kwargs: Any) -> None:
        pid = os.fork()
        assert pid >= 0
        if pid == 0:
            if self.cpu is not None:
                os.sched_setaffinity(pid, self.cpu)
            # Child worker process
            self.pid = os.getpid()
            self.name = f"process-{self.pid}"
            thread = current_thread()
            thread.name = self.name
            logging.info(f"Starting")
            self.run(**kwargs)
            sys.exit()
        else:
            self.pid = pid
            self.name = f"process-{pid}"

    @abstractmethod
    def run(self, **kwargs: Any) -> None:
        raise NotImplementedError

    def kill(self) -> None:
        logging.info(f"Killing {self.name}")
        os.kill(self.pid, signal.SIGKILL)
