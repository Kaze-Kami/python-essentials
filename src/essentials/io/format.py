# -*- coding: utf-8 -*-

"""
Formatting utilities (pretty-print)

@author Kami-Kaze
"""

import json
from datetime import timedelta
from typing import Any


def pformat(obj: Any, sink=None, prefix=''):
    if obj is None:
        obj = {}

    if isinstance(obj, str):
        pretty = obj
    else:
        pretty = json.dumps(obj, indent=4, sort_keys=True)
    if sink is not None:
        for line in pretty.split('\n'):
            sink(f'{prefix}{line}')
    else:
        return pretty


__TIME_INDEX = [
    ('s', 60),
    ('m', 60),
    ('h', 24),
    ('d', 7),
    ('w', 52),
    ('y', 1)
]

__FORMATS = [
    '.0f',
    '1.0f',
    '1.0f',
    '1.0f',
    '1.0f',
    '1.0f',
    '3.0f'
]


def duration(value: timedelta or float, millis=True):
    if isinstance(value, timedelta):
        value = value.total_seconds()
    parts = []

    if millis:
        parts.append(((value % 1) * 1000, 'ms'))

    value = int(value)
    for (unit, div) in __TIME_INDEX:
        v = value % div
        value //= div
        parts.append((v, unit))

    strs = []
    required = False
    for ((v, u), f) in zip(reversed(parts), __FORMATS[:len(parts)]):
        if required or 0 < v:
            required = True
            strs.append(f'{v:{f}}{u}')

    return ' '.join(strs
