# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""


class CircularBuffer:
    def __init__(self, container):
        self._data = container
        self._size = len(container)
        self._offset = 0

    def __len__(self):
        return self._size

    def push(self, value):
        self._data[self._offset] = value
        self._offset = (self._offset + 1) % self._size

    def __iter__(self):
        for i in range(self._size):
            yield self._data[(self._offset + i) % self._size]

    @property
    def offset(self):
        return self._offset

    @property
    def size(self):
        return self._size
