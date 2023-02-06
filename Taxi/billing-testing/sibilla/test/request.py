# coding: utf8

import collections
import typing

from sibilla import utils


class Query(collections.abc.Mapping):
    def __init__(self, data=None, expected=None, json=None):
        self.__expected = expected
        self.__data = data
        self.__json = json

    @property
    def expected(self):
        return self.__expected

    def keys(self):
        return ['data', 'json']

    def __getitem__(self, item):
        if item == 'json':
            return self.__json
        if item == 'data':
            return self.__data
        return None

    def isexpected(self, query_data: collections.abc.Mapping) -> bool:
        return utils.contains(
            query_data['json'], self['json'],
        ) and utils.contains(query_data['data'], self['data'])

    def __len__(self) -> int:
        return len(self.keys())

    def __iter__(self) -> typing.Iterator:
        return iter(self.keys())

    def __contains__(self, item) -> bool:
        return item in self.keys()

    def __repr__(self) -> str:
        return 'Query(data={data}, expected={expected}, json={json})'.format(
            data=str(self.__data),
            expected=str(self.__expected),
            json=str(self.__json),
        )

    def __str__(self) -> str:
        return repr(self)
