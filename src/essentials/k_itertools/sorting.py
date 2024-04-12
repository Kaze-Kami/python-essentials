# -*- coding: utf-8 -*-

"""

"""

from typing import TypeVar, Generic, Callable

_T = TypeVar('_T')
_K = TypeVar('_K')


class SortBy(Generic[_T, _K]):
    def __init__(self, prop: Callable[[_T], _K], priorities: list[_K] = None):
        self._property = prop
        self._priorities = priorities

    def __call__(self, item):
        val = self._property(item)
        # sort by value
        if self._priorities is None:
            return val
        # sort by priorities
        try:
            return self._priorities.index(val)
        except ValueError:
            # sort unknown to end
            return len(self._priorities) + 1
