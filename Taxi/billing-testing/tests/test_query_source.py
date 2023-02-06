import json
import os

import pytest

from sibilla import query


def test_query_invalid_format():
    def _t(data):
        with pytest.raises(query.InvalidDataFormatError):
            query.load(data)

    _t(42)


def test_query_load_from_object():
    def _t(actual):
        result = query.load(actual)
        assert isinstance(result, query.Query)
        assert [actual] == list(result)

    _t({'some_name': 'some_val', 'array': [1, 2, 3]})


def test_query_load_from_array():
    def _t(actual):
        result = query.load(actual)
        assert isinstance(result, query.Query)
        assert actual == list(result)

    _t([{'some_data': 'some_value'}, {'another_query': 'another_data'}])


def test_query_load_from_file():
    def _t(filename):
        with open(filename) as file_descriptor:
            data = json.load(file_descriptor)
            result = query.load(filename)
            assert isinstance(result, query.Query)
            assert data == list(result)

    path = os.path.dirname(os.path.abspath(__file__))
    _t(f'{path}/_data/query_source/01-account_search.json')


def test_query_load_from_files():
    def _t(path):
        files = []
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                files.append(json.load(open(os.path.join(path, file_name))))
        result = query.load(path)
        assert isinstance(result, query.Query)
        assert files == list(result)

    _t(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '_data',
            'query_source',
        ),
    )
