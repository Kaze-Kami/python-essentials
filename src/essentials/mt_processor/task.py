# -*- coding: utf-8 -*-

"""

"""

import abc
import time

from enum import Enum
from threading import Lock
from typing import Generic, TypeVar

_T = TypeVar('_T')


class TaskStatus(Enum):
    NOT_STARTED = 0,
    PREPARING = 10,
    IN_PROGRESS = 20,
    COMPLETED = 30,
    FAILED = 40


class Task(Generic[_T]):
    def __init__(self, name: str):
        self._name = name

        self._status = TaskStatus.NOT_STARTED
        self._result = None
        self._error = None

        # progress monitoring
        self._lock = Lock()
        self._progress = 0
        self._message = ''
        self._start = 0
        self._end = 0

    def execute(self):
        try:
            self._status = TaskStatus.PREPARING
            self._start = time.perf_counter()
            self.prepare()
            self._status = TaskStatus.IN_PROGRESS
            self._result = self.run()
            self._end = time.perf_counter()
            self._status = TaskStatus.COMPLETED
        except Exception as e:
            self._end = time.perf_counter()
            self._error = e
            self._status = TaskStatus.FAILED

    def update_progress(self, progress: float, message: str = ''):
        with self._lock:
            self._progress = progress
            self._message = message

    def prepare(self):
        pass

    @abc.abstractmethod
    def run(self) -> _T:
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> TaskStatus:
        # todo: do we need to use a lock here?
        return self._status

    @property
    def error(self) -> Exception or None:
        return self._error

    @property
    def result(self) -> _T or None:
        return self._result

    @property
    def progress(self) -> float:
        with self._lock:
            return self._progress

    @property
    def message(self) -> str:
        with self._lock:
            return self._message

    @property
    def start(self) -> float:
        return self._start

    @property
    def end(self) -> float:
        return self._end

    @property
    def eta(self):
        if not self.status == TaskStatus.IN_PROGRESS or self._progress == 0:
            return 0
        elif self._progress == 1:
            return 0
        return (time.perf_counter() - self._start) * (1.0 / self._progress - 1.0)
