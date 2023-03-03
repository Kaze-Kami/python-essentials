# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

import os


def open_or_create(path: str, mode: str, default: str = ''):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(default)

    return open(path, mode)


def join_path(p0, *args):
    return os.path.join(p0, *args)
