# -*- coding: utf-8 -*-

"""
Formatting utilities (pretty-print)

@author Kami-Kaze
"""

import json
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
