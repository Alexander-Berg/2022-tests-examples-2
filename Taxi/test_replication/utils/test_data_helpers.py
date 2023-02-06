import copy

import pytest

from replication.utils import data_helpers


@pytest.mark.parametrize(
    'doc, paths, expected',
    [
        (
            {
                'key1': {
                    'subkey1': [{'foo': 43, 'bar': 'value', 'extra': 12}],
                    'subkey2': {'foo2': 12, 'd': 'fd'},
                    'subkey3': [
                        {'id': None},
                        {'id': 123},
                        {'id': None},
                        {'id': '22f'},
                    ],
                },
                'key2': {'no': []},
                'key3': {'key': 1, 'another': 2},
            },
            [
                'key1.subkey1.foo',
                'key1.subkey1.nokey',
                'key1.subkey1.bar',
                'key1.subkey3.id',
                'key1.subkey2.d',
                'key2.no.key',
                'key2.no2.key2',
                'key3.key',
            ],
            {
                'key1': {
                    'subkey1': [{'foo': 43, 'bar': 'value'}],
                    'subkey2': {'d': 'fd'},
                    'subkey3': [{'id': 123}, {'id': '22f'}],
                },
                'key3': {'key': 1},
            },
        ),
    ],
)
@pytest.mark.nofilldb
def test_get_trimmed_structure_dict(doc, paths, expected):
    assert data_helpers.get_trimmed_structure_dict(doc, paths) == expected


@pytest.mark.parametrize(
    'doc, path, value, expected',
    [
        (
            {
                'key1': {'subkey1': {'foo': 43, 'bar': 'value', 'extra': 12}},
                'key2': 1,
            },
            'key1.subkey1.foo',
            42,
            {
                'key1': {'subkey1': {'foo': 42, 'bar': 'value', 'extra': 12}},
                'key2': 1,
            },
        ),
    ],
)
@pytest.mark.nofilldb
def test_set_field(doc, path, value, expected):
    doc_copy = copy.deepcopy(doc)
    data_helpers.set_field(doc_copy, path, value)
    assert doc_copy == expected
