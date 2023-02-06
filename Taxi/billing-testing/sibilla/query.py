# coding: utf8
import abc
import json
import os
import time


class QueryError(Exception):
    """Module errors"""


class InvalidDataFormatError(QueryError):
    """Query format error"""


class Query(abc.ABC):
    def __iter__(self):
        return self._make_iter()

    @abc.abstractmethod
    def _make_iter(self):
        raise NotImplementedError


class QueryFromObject(Query):
    def __init__(self, data):
        self.__data = data

    def _make_iter(self):
        return iter([self.__data])


class QueryFromArray(Query):
    def __init__(self, data):
        self.__data = data

    def _make_iter(self):
        return iter(self.__data)


class QueryFromFile(Query):
    def __init__(self, filename):
        with open(filename) as fdesc:
            self.__data = json.load(fdesc)

    def _make_iter(self):
        return iter(self.__data)


class QueryFromDir(Query):
    def __init__(self, dirname):
        self.__dirname = dirname

    def file_iter(self):
        for fpath in os.listdir(self.__dirname):
            fname = os.path.join(self.__dirname, fpath)
            if not os.path.isfile(fname):
                continue
            yield json.load(open(fname))

    def _make_iter(self):
        return iter(self.file_iter())


def load(data):
    if isinstance(data, dict):
        return QueryFromObject(data)
    if isinstance(data, list):
        return QueryFromArray(data)
    if isinstance(data, str) and os.path.isdir(data):
        return QueryFromDir(data)
    if isinstance(data, str) and os.path.isfile(data):
        return QueryFromFile(data)
    if isinstance(data, str):
        return QueryFromObject(data)
    raise InvalidDataFormatError


class WaitForSuccess:
    def __init__(self, **kargs):
        self.__first_query = time.time()
        self.__last_query = None
        self.__timeout = 0
        self.__try_limit = 1
        self.__retry_attempt = 0
        if 'retry_count' in kargs:
            self.__try_limit = kargs['retry_count']
        if 'timeout' in kargs:
            self.__timeout = kargs['timeout']

    @property
    def timeout(self):
        return self.__timeout

    @property
    def retry_count(self):
        return self.__try_limit

    def register_attempt(self):
        self.__retry_attempt += 1
        self.__last_query = time.time()
        return self

    def __bool__(self):
        if self.__try_limit > 0 and self.__try_limit <= self.__retry_attempt:
            return False
        if self.__timeout:
            last_time = time.time()
            if self.__last_query:
                last_time = self.__last_query
            return last_time - self.__first_query < self.__timeout
        return True
