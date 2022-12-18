# -*- coding: utf-8 -*-

"""
Self-Updating Spinner

@author Kami-Kaze
"""

import sys
import time
from threading import Thread
from typing.io import IO


class Spinner:
    _STATES = ['|', '/', '-', '\\']

    def __init__(self, msg='', sink: IO = sys.stdout, flush: bool = False):
        self._msg = msg
        self._state = 0
        self._running = False

        self._sink = sink
        self._flush = flush
        self._daemon: Thread = None

    def __enter__(self):
        self._state = 0
        self._running = True
        self._daemon = Thread(target=self._print)
        self._daemon.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False
        self._daemon.join()
        return False

    def update(self, msg: str):
        self._msg = msg

    def _print(self):
        while self._running:
            state = Spinner._STATES[self._state]
            self._state = (self._state + 1) % len(Spinner._STATES)

            text = ''
            if self._msg:
                text = f' {self._msg}'

            print(f'\r{state}{text}', file=self._sink, flush=self._flush, end='')

            time.sleep(.25)

        # FIXME: I think we need to 'blank the line' (e.g. print a lot of spaces)
        print('\r')
