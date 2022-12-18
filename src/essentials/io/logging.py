# -*- coding: utf-8 -*-

"""
TODO: Document logging configuration

Simple wrapper around (py-) spdlog
https://github.com/bodgergely/spdlog-python
https://github.com/gabime/spdlog

@author Kami-Kaze
"""

import os
import sys

import spdlog
from spdlog import LogLevel
_log_level_name_fallback = 'info'
_name_to_level_map = {
    'critical': LogLevel.CRITICAL,
    'error'   : LogLevel.ERR,
    'warning' : LogLevel.WARN,
    'info'    : LogLevel.INFO,
    'debug'   : LogLevel.DEBUG,
    'trace'   : LogLevel.TRACE,
    'none'    : LogLevel.OFF,
}

# initialize logging
_loggers: dict[str, spdlog.Logger] = {}
_log_level_name = os.environ.get('log_level', _log_level_name_fallback)
_log_level = _name_to_level_map.get(_log_level_name.lower())

if _log_level is None:
    print(f'ERROR: Unknown log level {_log_level_name}!', file=sys.stderr)
    print(f'Using fallback: {_log_level_name_fallback}', file=sys.stderr)
    _log_level = _name_to_level_map[_log_level_name_fallback]


def get_logger(name: str) -> spdlog.Logger:
    if name not in _loggers:
        # FIXME: colored=False is required for spdlog to work on windows
        logger = spdlog.ConsoleLogger(name, colored=False)
        logger.set_pattern('%T [%l | %n]: %v', spdlog.PatternTimeType.local)
        logger.set_level(_log_level)
        _loggers[name] = logger

    return _loggers[name]


_core_logger = get_logger('core')
_core_logger.info('Logging initialized')