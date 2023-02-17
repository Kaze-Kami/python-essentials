# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""
from typing import Callable, TypeVar

_SPLIT_TYPE = TypeVar('_SPLIT_TYPE')


def split_parse(value: str, separator: str, parse: Callable[[str], _SPLIT_TYPE]) -> list[_SPLIT_TYPE]:
    return [parse(part) for part in value.split(separator)]
