import collections.abc
from typing import Mapping


class _NotNone:
    def __eq__(self, o):
        return o is not None


NotNone = _NotNone()  # pylint: disable=invalid-name


class SubDict(collections.abc.Mapping):
    def __init__(self, mapping: Mapping):
        self._mapping = mapping

    def __getitem__(self, item):
        return self._mapping.__getitem__(item)

    def __len__(self):
        return self._mapping.__len__()

    def __iter__(self):
        return self._mapping.__iter__()


def _assert_equals(outer, inner, path: str):
    if isinstance(inner, SubDict) and isinstance(outer, Mapping):
        for key in inner:
            _assert_equals(outer.get(key), inner.get(key), f'{path}.{key}')
        return

    assert outer == inner, f'values are not equal at: {path}'


def sub_dict(**kwargs):
    return SubDict(kwargs)


def assert_dict_contains(outer: Mapping, inner: Mapping):
    _assert_equals(outer, SubDict(inner), '')


def assert_dict_check(outer: Mapping, **kwargs):
    assert_dict_contains(outer, kwargs)
