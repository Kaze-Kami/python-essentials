# -*- coding: utf-8 -*-

"""

"""

import abc

from typing import TypeVar, Generic, Callable

_T = TypeVar('_T')


class Formatter(Generic[_T]):
    @abc.abstractmethod
    def format(self, item: _T, max_chars: int) -> list[str] or str:
        raise NotImplementedError()

    def __call__(self, item: _T, max_chars: int) -> list[str]:
        val = self.format(item, max_chars)
        if isinstance(val, str):
            val = [val]
        return val


class SimpleFormatter(Formatter[_T]):
    def __init__(self, *lines: Callable[[_T, int], str]):
        self._lines = lines

    def format(self, item: _T, max_chars: int) -> list[str]:
        return [l(item, max_chars) for l in self._lines]
