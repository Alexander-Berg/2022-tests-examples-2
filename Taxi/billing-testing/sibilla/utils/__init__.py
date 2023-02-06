# coding: utf8

import collections
import copy
import os
import re
import sys
import typing

sys.path = [
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '../../../../../library/python',
        ),
    ),
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../../backend-py3'),
    ),
] + sys.path

from taxi import discovery  # noqa  # pylint: disable=E0401,C0413


class UtilsError(Exception):
    """Base class for Sibilla error"""


class SubstitutionNotFoundError(UtilsError):
    """Object substitution error"""


def lookup_data(value, data):
    path = value.split('.')
    lookups = []

    def _lookup_data(current_path: list, data: typing.Any):
        if not current_path:
            lookups.append(data)
            return
        element = current_path[0]
        if element == '*' and isinstance(data, list):
            for item in data:
                _lookup_data(current_path[1:], item)
        elif isinstance(data, dict) and element in data:
            _lookup_data(current_path[1:], data[element])
        elif isinstance(data, list) and element.isnumeric():
            if int(element) < len(data):
                _lookup_data(current_path[1:], data[int(element)])
            else:
                raise SubstitutionNotFoundError(
                    {'dict': data, 'element': element, 'path': path},
                )
        elif isinstance(data, collections.abc.Mapping) and element in data:
            _lookup_data(current_path[1:], data[element])
        elif isinstance(data, object) and hasattr(data, element):
            _lookup_data(current_path[1:], getattr(data, element))
        else:
            raise SubstitutionNotFoundError(
                {'dict': data, 'element': element, 'path': path},
            )

    _lookup_data(path, data)
    return lookups


def build(source, data_dict, glob: dict = None):
    def _build(source, data_dict):
        if isinstance(source, dict):
            for k in source:
                source[k] = _build(source[k], data_dict)
        elif isinstance(source, list):
            source = list(map(lambda s: _build(s, data_dict), source))
        elif isinstance(source, str) and source[0:1] == '@':
            desc = re.match(r'^@([^(]+)\(([^)]+)\)$', source)
            if desc is not None:
                lookup = lookup_data(desc[2], data_dict)
                if len(lookup) != 1:
                    raise UtilsError('Wildcard source not supported')
                source = lookup[0]
                loc: dict = {'source': source}
                # pylint:disable=exec-used
                exec(
                    f'source = {desc[1]}(source)', glob if glob else None, loc,
                )
                source = loc['source']
            else:
                lookup = lookup_data(source[1:], data_dict)
                if len(lookup) != 1:
                    raise UtilsError('Wildcard source not supported')
                source = lookup[0]
        return source

    if source is None:
        return None
    data = copy.deepcopy(source)
    return _build(data, data_dict)


def contains(needle, hashstack):
    if not isinstance(needle, type(hashstack)):
        return False
    if isinstance(needle, dict):
        needle_set = set(needle)
        hashstack_set = set(hashstack)
        if not needle_set - hashstack_set:
            for k in needle_set:
                if not contains(needle[k], hashstack[k]):
                    return False
            return True
        return False
    if isinstance(needle, list):
        if len(needle) > len(hashstack):
            return False
        matched = set()
        length_needle = len(needle)
        length_hashstack = len(hashstack)
        for i in range(length_needle):
            for j in range(length_hashstack):
                if j in matched:
                    continue
                if contains(needle[i], hashstack[j]):
                    matched.add(j)
        # one element can match with many orhers
        # [{'a': 1}] mathch with all
        # from [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}, {'a': 1, 'b': 1}]
        return len(matched) >= len(needle)
    return needle == hashstack


def prepare_url(url_data):
    if isinstance(url_data, str):
        service = re.findall(r'^(@[-\w\d]+)(.*)', url_data)
        if not service:
            return url_data
        # convert url to object
        url_data = {'service': service[0][0], 'uri': service[0][1]}
    service_url = url_data['service']
    path = url_data['uri']
    if service_url[0:1] == '@':
        service_url = discovery.find_service(service_url[1:]).url
    return service_url + path


def not_none(obj: typing.Optional[typing.Any]) -> typing.Any:
    assert obj is not None
    return obj
