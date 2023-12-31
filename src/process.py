from __future__ import annotations

import logging
import os
import signal
import sys
from abc import ABC, abstractmethod
from threading import current_thread
from typing import Any


# Creation of a new process; this class inherited by both workers and clients
class Process(ABC):
    def __init__(self, **kwargs: Any):
        self.name = "worker-?"
        self.pid = -1
        self.cpu = kwargs['cpu'] if 'cpu' in kwargs else None
        self.forks = []

    def create_and_run(self, **kwargs: Any) -> None:
        pid = os.fork()
        assert pid >= 0
        if pid == 0:
            if sys.platform.startswith('linux') and self.cpu is not None:
                try:
                    os.sched_setaffinity(pid, self.cpu)
                except AttributeError:
                    print("os.sched_setaffinity not available on this platform.")
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
        for pid in self.forks:
            os.kill(pid, signal.SIGKILL)
        os.kill(self.pid, signal.SIGKILL)
