from __future__ import absolute_import, division, print_function

import pytest

import six

from sandbox.projects.yabs.sandbox_task_tracing.util import frozendict

from sandbox.projects.yabs.sandbox_task_tracing.info import jsonified


@pytest.mark.parametrize(
    'value',
    [None, False, True, 0, 1, 1.5, float('inf'), '', 'test'],
    ids=repr,
)
def test_jsonified_immutable(value):
    assert jsonified(value) == value


@pytest.mark.parametrize(
    'value',
    [
        dict(a=1, b=2),
        frozendict(a=1, b=2),
    ],
    ids=repr,
)
def test_jsonified_dict(value):
    result = jsonified(value)
    assert result == dict(value)
    assert result is not value
    assert type(result) is dict


@pytest.mark.parametrize(
    'value',
    [
        [1, 2],
        (1, 2),
    ],
    ids=repr,
)
def test_jsonified_list(value):
    result = jsonified(value)
    assert result == list(value)
    assert result is not value
    assert type(result) is list


@pytest.mark.parametrize(
    'value',
    [
        {1, 2},
        frozenset({1, 2}),
        six.viewkeys(dict(a=1, b=2)),
        six.viewvalues(dict(a=1, b=2)),
    ],
    ids=repr,
)
def test_jsonified_set(value):
    result = jsonified(value)
    assert sorted(result) == sorted(value)
    assert result is not value
    assert type(result) is list


@pytest.mark.parametrize(
    'value',
    [
        six.viewitems(dict(a=1, b=2)),
    ],
    ids=repr,
)
def test_jsonified_items(value):
    result = jsonified(value)
    assert sorted(result) == sorted(map(list, value))
    assert result is not value
    assert type(result) is list
    assert type(next(iter(result))) is list


@pytest.mark.parametrize(
    'value',
    [
        object(),
        iter((1, 2)),
        six.iteritems(dict(a=1, b=2)),
        six.iterkeys(dict(a=1, b=2)),
        six.itervalues(dict(a=1, b=2)),
    ],
    ids=lambda value: type(value).__name__,
)
def test_jsonified_object(value):
    result = jsonified(value)
    assert type(result) is dict
    assert 'repr' in result
    assert 'type' in result


def test_jsonified_nested():
    assert jsonified({1: [({2},)]}) == {'1': [[[2]]]}
