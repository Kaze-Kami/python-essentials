# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

from dataclasses import dataclass

import requests

from essentials.util.text_utils import split_parse


@dataclass
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    def __gt__(self, other: 'Version'):
        return self.to_tuple() > other.to_tuple()

    def __ge__(self, other: 'Version'):
        return self.to_tuple() >= other.to_tuple()

    def __lt__(self, other: 'Version'):
        return self.to_tuple() < other.to_tuple()

    def __le__(self, other: 'Version'):
        return self.to_tuple() <= other.to_tuple()

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'

    def __repr__(self):
        return f'Version(major={self.major}, minor={self.minor} patch={self.patch})'

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def to_tuple(self):
        return self.major, self.minor, self.patch

    @staticmethod
    def parse_version(version_str: str) -> 'Version':
        """
        Parse a version string in the format major[.minor?[.patch?]]
        """
        return Version(*split_parse(version_str, '.', int))


def check_version(version: str or Version, reference_url: str) -> Version or None:
    """
    Check version against given target
    :param version: version to check, either a version string or [Version]
    :param reference_url: url to a file containing a version string
    :return: the latest version if its newer than the current one, None otherwise
    """
    if isinstance(version, str):
        version = Version.parse_version(version)

    r = requests.get(reference_url)

    # todo: try catch + check status code
    ref = Version.parse_version(r.text)
    return ref if version < ref else None
