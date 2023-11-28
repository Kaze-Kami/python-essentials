# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

import inspect
import json
import os
import shutil
from datetime import datetime

import attrs

from essentials.gui.core import _CORE_LOGGER


class Config:
    """
    Base class for configs.
    Sub classes should be annotated with @attrs.define
    and provide default values for all members
    so load() can use cls() to construct a default config if loading fails
    """

    @staticmethod
    def load_or_defaults(
            cls, path: str,
            ignore_unknown_keys: bool = True,
            ignore_missing_keys: bool = True,
            backup: bool = True,
            backup_suffix: str = '.backup_%Y%m%dT%H%M%S%f',
    ):
        """
        Attempt to load config from (json at) given path
        If any key is missing in the json file the default value
        from the class definition will be used.
        If loading the config fails all default values will be used

        :param ignore_unknown_keys: omit keys present in json but not in class
        :param ignore_missing_keys: use default values for keys missing in json
        :param backup: do a backup if json keys mismatch config members
        :param backup_suffix: string appended to the original filepath if [backup] applies
                              It is passed to now.strftime so supports including date formatting.
                              If <filepath><backup_suffix> exists <filepath><backup_suffix>.N
                              is used instead where N = first integer so that the filename is unique
        """

        if not attrs.has(cls):
            raise RuntimeError('Config classes should be annotated with @attrs.define')

        defined_args = inspect.signature(cls).parameters.values()
        if any(p.default is p.empty for p in defined_args):
            raise RuntimeError('Config classes should provide default values for all members')

        arg_names = set(p.name for p in defined_args)

        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    data: dict = json.load(f)
                    cls_name = data.pop('__name__')

                    # sanity checks
                    if not cls.__name__ == cls_name:
                        raise RuntimeError(f'Cannot convert config of type {cls_name} to {cls.__name__}!')

                    found_names = set(data.keys())
                    if (missing := arg_names - found_names):
                        if ignore_missing_keys:
                            _CORE_LOGGER.warn(f'Missing config keys {missing}. Using defaults...')
                        else:
                            raise RuntimeError(f'Missing config keys {missing}')

                    if (unknown := found_names - arg_names):
                        if ignore_unknown_keys:
                            _CORE_LOGGER.warn(f'Unknown config keys {unknown}. Ignoring...')
                        else:
                            raise RuntimeError(f'Unknown config keys {unknown}')

                    if backup and missing | unknown:
                        Config.create_backup(path, backup_suffix)
                    # idk, this is a funny one
                    return cls(**{k: data[k] for k in arg_names & found_names})
            except (json.JSONDecodeError, TypeError) as e:
                _CORE_LOGGER.error(f'Failed to load config: {e} using fallback...')
                Config.create_backup(path, backup_suffix)
        else:
            _CORE_LOGGER.warn(f'No config found at {path} using default')
        return cls()

    @staticmethod
    def save(cls, path: str, config: 'Config'):
        try:
            data = attrs.asdict(config, recurse=True)
            data['__name__'] = cls.__name__

            with open(path, 'w') as f:
                json.dump(data, f)
        except (FileNotFoundError, TypeError) as e:
            _CORE_LOGGER.error(f'Failed to save config to {path}: {e}')

    @staticmethod
    def create_backup(path: str, backup_suffix: str):
        backup_suffix = datetime.now().strftime(backup_suffix)
        backup_path = f'{path}{backup_suffix}'
        i = 0
        while os.path.exists(backup_path):
            i += 1
            backup_path = f'{path}{backup_suffix}.{i}'
        _CORE_LOGGER.info(f'Backing up config at {backup_path}')
        shutil.copy(path, backup_path)
