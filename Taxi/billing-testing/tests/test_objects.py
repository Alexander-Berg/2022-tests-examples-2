# coding: utf8

import pytest

from sibilla import processing
from sibilla import test
from sibilla import utils

__SAMPLE_TEST = {
    'name': 'sample',
    'query': {'value': 'foo', 'array': ['bar']},
    'url': 'https://example.com',
    'result': {'code': 200, 'response': '@request'},
}

__SAMPLE_TEST_WITH_ALIAS = {
    'name': 'sample',
    'alias': 'some-alias',
    'query': {},
    'url': 'https://example.com',
    'result': {},
}

__SAMPLE_TEST_USE_ALIAS = {
    'name': 'sample',
    'require': 'some-alias',
    'query': '@some-alias',
    'url': 'https://example.com',
    'result': {},
}


def test_query_collection_function():
    query1 = test.Query(json={'a': 123, 'b': 456})
    query2 = test.Query(json={'a': 123})
    assert query1.isexpected(query2)


def test_sibilla_query_str_default():
    query = test.Query()
    assert str(query) == 'Query(data=None, expected=None, json=None)'


def test_sibilla_query_str():
    query = test.Query(
        data={'foo': 123, 'bar': [4, 5, 6]},
        expected=True,
        json={'status': 200},
    )
    assert str(query) == (
        'Query(data={\'foo\': 123, \'bar\': [4, 5, 6]}, '
        'expected=True, '
        'json={\'status\': 200})'
    )


def test_responses_collection():
    result = processing.Storage()
    result.put('a', 42)
    assert list(result.get('a')) == [42]


def test_response_exception():
    result = processing.Storage()
    with pytest.raises(processing.DataNotFoundError):
        list(result.get('a'))


def test_data_source_parser():
    def _t(data, expected):
        source = processing.Source(data, processing.Storage())
        assert source.require == expected

    _t('@test', {'test'})
    _t({'code': '@secdist.settings_override'}, {'secdist'})
    _t(
        {'code': '@secdist.settings_override', 'value': '@response'},
        {'secdist', 'response'},
    )
    _t(
        {'code': '@secdist.settings_override', 'value': ['@response']},
        {'secdist', 'response'},
    )


def test_data_source_generator():
    def _t(body, storage: processing.Storage, expected):
        source = processing.Source(body, storage)
        matched = 0
        for item in source:
            for exp in expected:
                try:
                    assert item == exp
                    matched += 1
                except AssertionError:
                    # don't care if objects are not equals
                    pass
        assert matched == len(expected)

    _t('1234', processing.Storage(), ['1234'])
    _t('@raw', processing.Storage({'raw': ['456', '123']}), ['123', '456'])
    _t(
        '@raw.f',
        processing.Storage({'raw': [{'f': '456'}, {'f': '123'}]}),
        ['123', '456'],
    )
    _t(
        ['@one.f', '@two', 'some-val'],
        processing.Storage({'one': [{'f': 1}, {'f': 2}], 'two': [3, 4]}),
        [
            [1, 3, 'some-val'],
            [1, 4, 'some-val'],
            [2, 3, 'some-val'],
            [2, 4, 'some-val'],
        ],
    )


def test_object_as_datasource():
    class TestObj:
        def __init__(self):
            self.json = {'123': '456'}
            self.text = 'foo'

    def _t(body, storage: object, expected):
        source = utils.build(body, storage)
        assert source == expected

    _t({'a': '@json'}, TestObj(), {'a': {'123': '456'}})
