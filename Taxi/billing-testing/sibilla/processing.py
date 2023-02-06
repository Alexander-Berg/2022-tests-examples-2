# coding: utf8

import copy
import logging
import re

from taxi import secdist


logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Storage error object"""


class DataNotFoundError(StorageError):
    """Error when no success execution"""


class SubstitutionNotFoundError(StorageError):
    """Could not resolve path"""


class Storage:
    def __init__(self, source: dict = None):
        if source:
            self.__internal_storage = copy.deepcopy(source)
        else:
            self.__internal_storage = {}

    def get(self, item):
        if item == 'secdist':
            yield secdist.load_secdist()
        elif item in self.__internal_storage:
            yield from self.__internal_storage[item]
        else:
            logger.error(f'{item} not found')
            raise DataNotFoundError(f'{item} not found')

    def put(self, item, value):
        if item not in self.__internal_storage:
            self.__internal_storage[item] = []
        self.__internal_storage[item].append(value)


class Source:
    def __init__(self, template, storage: Storage):
        self.__required: set = set()
        self.__storage = storage
        self.__template = template
        self.__parse(template)

    def __parse(self, template):
        if isinstance(template, str):
            # fn_name(@value) or @value
            matches = re.findall(
                r'(?:(?:^([\w]+)\(@([-.\w]+)\)$)|(?:^@([-.\w]+)$))', template,
            )
            if not matches:
                return
            path = ''
            if matches[0][0]:
                path = matches[0][1]
            else:
                path = matches[0][2]
            value = path.split('.', 1)[0]
            if value != '':
                self.__required.add(value)
        elif isinstance(template, dict):
            for k in template:
                self.__parse(template[k])
        elif isinstance(template, list):
            for element in template:
                self.__parse(element)

    @property
    def require(self):
        return self.__required

    def __generate(self, body, required, pos=0):
        if pos == len(required):
            yield body
        else:
            for new_body in self.__generate(body, required, pos + 1):
                yield from self.__insert_value(new_body, required[pos])

    def __insert_value(self, source, name):
        def _lookup_value(value, path):
            data_dict = {name: value}
            path_elements = path.split('.')
            for element in path_elements:
                if isinstance(data_dict, dict) and element in data_dict:
                    data_dict = data_dict[element]
                elif (
                    element.isnumeric()
                    and isinstance(data_dict, list)
                    and 0 <= int(element) < len(data_dict)
                ):
                    data_dict = data_dict[int(element)]
                else:
                    logger.error(f'Substitution for {path} not found')
                    raise SubstitutionNotFoundError()
            return data_dict

        def _build(source, value):
            if isinstance(source, dict):
                for k in source:
                    source[k] = _build(source[k], value)
            elif isinstance(source, list):
                source = list(map(lambda s: _build(s, value), source))
            elif isinstance(source, str) and re.match('@' + name, source):
                source = _lookup_value(value, source[1:])
            return source

        for value in self.__storage.get(name):
            data = copy.deepcopy(source)
            yield _build(data, value)

    def __iter__(self):
        return self.__generate(self.__template, list(self.__required))
