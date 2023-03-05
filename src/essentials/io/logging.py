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
from functools import wraps
from typing import Type, Callable, Any

import spdlog
from spdlog import LogLevel
_log_file_name_fallback = 'log.txt'
_log_level_name_fallback = 'info'
_log_file_level_name_fallback = 'debug'
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
_log_file = os.environ.get('log_file', _log_file_name_fallback)
_log_file_level_name = os.environ.get('log_file_level', _log_file_level_name_fallback)
_log_level = _name_to_level_map.get(_log_level_name.lower())
_log_file_level = _name_to_level_map.get(_log_file_level_name.lower())

if _log_level is None:
    print(f'ERROR: Unknown log level {_log_level_name}!', file=sys.stderr)
    print(f'Using fallback: {_log_level_name_fallback}', file=sys.stderr)
    _log_level = _name_to_level_map[_log_level_name_fallback]

_console_sink = spdlog.stdout_sink_mt()
_console_sink.set_level(_log_level)

if _log_file_level is None and _log_file is not None:
    print(f'ERROR: Unknown log file level {_log_file_level_name}!', file=sys.stderr)
    print(f'Using fallback: {_log_file_level_name_fallback}', file=sys.stderr)
    _log_file_level = _name_to_level_map[_log_file_level_name_fallback]

if _log_file == '':
    _file_sink = spdlog.null_sink_mt()
else:
    _file_sink = spdlog.basic_file_sink_mt(_log_file, truncate=True)
_file_sink.set_level(LogLevel.DEBUG)


def get_logger(*name: str or Type) -> spdlog.Logger:
    parts = []

    for part in name:
        if isinstance(part, Type):
            part = part.__name__
        parts.append(part)

    name = ':'.join(parts)

    if name not in _loggers:
        # FIXME: colored=False is required for spdlog to work on windows
        sinks = [_console_sink]
        if _file_sink is not None:
            sinks.append(_file_sink)
        logger = spdlog.SinkLogger(name, sinks)
        logger.set_pattern('%T [%n|%l]: %v', spdlog.PatternTimeType.local)
        logger.set_level(LogLevel.TRACE)
        _loggers[name] = logger

    return _loggers[name]


def drop_logger(logger: spdlog.Logger) -> None:
    name = logger.name()
    spdlog.drop(name)
    _loggers.pop(name)


def log_call(logger: spdlog.Logger | str, log_level=LogLevel.DEBUG, name: str | None = None):
    if isinstance(logger, str):
        logger = get_logger(logger)

    def decorator(f: Callable[..., Any]):
        f_name = name or f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            logger.log(log_level, f'{f_name}')
            r = f(*args, **kwargs)
            return r

        return wrapper

    return decorator


_core_logger = get_logger('core')
_core_logger.debug('Logging initialized')
