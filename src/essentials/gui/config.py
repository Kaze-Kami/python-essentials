# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

import json
import os
from typing import Callable

from essentials.gui.core import _CORE_LOGGER


class Config:
    def __init__(self, **kwargs):
        pass

    @classmethod
    def load(cls, path: str, fallback: Callable[[], 'Config'] | None = None):
        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    data: dict = json.load(f)
                    cls_name = data.pop('__name__')
                    if not cls.__name__ == cls_name:
                        raise RuntimeError(f'Cannot convert config of type {cls_name} to {cls.__name__}!')
                    return cls(**data)
            except (json.JSONDecodeError or TypeError) as e:
                _CORE_LOGGER.error(f'Failed to load config: {e} using fallback...')
        else:
            _CORE_LOGGER.warn(f'No config found at {path} using fallback...')
        if fallback is not None:
            return fallback()
        raise RuntimeError(f'No fallback factory for config given!')

    @classmethod
    def save(cls, path: str, config: 'Config'):
        try:
            data = config.__dict__
            data['__name__'] = cls.__name__
            with open(path, 'w') as f:
                json.dump(data, f)
        except (FileNotFoundError or TypeError) as e:
            _CORE_LOGGER.error(f'Failed to save config to {path}: {e}')
