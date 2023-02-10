# -*- coding: utf-8 -*-

"""

Json compatible dictionary that supports
child access via 'path.to.child' as key

@author Kami-Kaze
"""

import json


class PathDict(dict):
    def pop(self, key: str):
        # FIXME
        item = self[key]
        del self[key]
        return item

    def __getitem__(self, path: str):
        path = path.split('.')
        item = self
        while 0 < len(path):
            item = item.__org_get__(path.pop(0))
        return item

    def __setitem__(self, path: str, item):
        path = path.split('.')
        parent = self
        while 1 < len(path):
            parent = parent.__org_get__(path.pop(0))
        parent.__org_set__(path[0], item)

    def __contains__(self, path: str):
        # FIXME: I'm lazy
        try:
            # noinspection PyStatementEffect
            self[path]
            return True
        except KeyError:
            return False

    def __delitem__(self, path: str):
        path = path.split('.')
        item = self
        while 1 < len(path):
            item = item[path.pop(0)]
        item.__org_del__(path[0])

    def __org_get__(self, key):
        return super(PathDict, self).__getitem__(key)

    def __org_set__(self, key, value):
        return super(PathDict, self).__setitem__(key, value)

    def __org_del__(self, key):
        return super(PathDict, self).__delitem__(key)

    def pstr(self):
        """
        Get a pretty string representation of [this]

        :return: pretty-printed json string representation of [this]
        """
        return json.dumps(self, indent=2, sort_keys=True)

    @staticmethod
    def default(d: 'PathDict'):
        """
        Method for json dumping

        :param d: object to dump
        :return: dictionary containing json data
        """
        return d.__dict__

    @staticmethod
    def load(f):
        """
        Load from json file

        :param f: file like object to read from
        :return: a "PathDict" containing the data from given json
        """
        return json.load(f, object_hook=PathDict)

    @staticmethod
    def loads(data: str | bytes):
        """
        Load from json string

        :param data: json string
        :return: a "PathDict" containing the data from given json
        """
        return json.loads(data, object_hook=PathDict)
