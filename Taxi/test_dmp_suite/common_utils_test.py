from collections import defaultdict

import pytest

from nile.api.v1 import stream as ns
from dmp_suite.common_utils import one_or_several, lazy_min, flatten_dict, deep_update_dict


def test_one_or_several():
    assert list(one_or_several(14)) == [14]
    assert list(one_or_several([3, 14, 15])) == [3, 14, 15]
    assert list(one_or_several("abc")) == ["abc"]
    assert list(one_or_several(["a", "b", "c"])) == ["a", "b", "c"]
    assert list(one_or_several(ns.BatchStream([None, None]))) == [None, None]


@pytest.mark.parametrize("given_iterable", [[2, 1, 3], [2, 3, 1], [1, 2, 3]])
def test_lazy_min_wo_key(given_iterable):
    assert lazy_min(given_iterable) == min(given_iterable)


@pytest.mark.parametrize("given_iterable", [[2, 1, 3], [1, 2, 3]])
def test_lazy_min_w_key(given_iterable):
    key = lambda x: -x
    assert lazy_min(given_iterable, key=key) == min(given_iterable, key=key)


def test_lazy_min_wo_default():
    with pytest.raises(ValueError):
        lazy_min([])


def test_lazy_min_w_default():
    assert lazy_min([], default=-1) == -1


def test_lazy_min_w_default_none():
    assert lazy_min([], default=None) is None


@pytest.mark.parametrize("given_iterable, expect_key_calls", [([2, 2, 1], 3), ([2], 0)])
def test_lazy_min_is_lazy(given_iterable, expect_key_calls):
    key_calls = []

    def key(value):
        key_calls.append(1)
        return value

    lazy_min(given_iterable, key=key)
    assert len(key_calls) == expect_key_calls


def test_flatten_dict():
    source = {
        'foo': {
            'bar': {'name': 'Bob', 'age': 32},
            'blah': 'minor',
            'tags': ['one', 'two'],
        }
    }

    result = flatten_dict(source)
    assert result == {
        'foo bar name': 'Bob',
        'foo bar age': 32,
        'foo blah': 'minor',
        'foo tags': ['one', 'two'],
    }

    result = flatten_dict(source, delimiter='.')
    assert result == {
        'foo.bar.name': 'Bob',
        'foo.bar.age': 32,
        'foo.blah': 'minor',
        'foo.tags': ['one', 'two'],
    }


@pytest.mark.parametrize(
    "dest,upd,expected",
    [
        ({'a': 5}, {10: 10}, {'a': 5, 10: 10}),
        ({'a': {'b': 15}}, {'a': {'c': 41}}, {'a': {'b': 15, 'c': 41}}),
        ({'a': 10}, {'a': {'b': 100}}, {'a': {'b': 100}}),
    ]
)
def test_deep_update_dict(dest, upd, expected):
    deep_update_dict(dest, upd)
    assert dest == expected
