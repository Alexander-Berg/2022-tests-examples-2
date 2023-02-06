import os
from typing import Any

import bson
import pytest

from sampling.pipeline import fixture_generator
from sampling.pipeline import generators


class SeqGenerator(generators.Generator):
    def __init__(self):
        generators.Generator.__init__(self)
        self._start = 1

    def fetch(self) -> Any:
        data = self._start
        self._start += 1
        return data


@pytest.mark.parametrize(
    'input_data, items, expected',
    [
        ('{"$seq": null}', 3, [1, 2, 3]),
        (
            '{"a": {"$seq": null}, "b": {"$seq": null}}',
            3,
            [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}],
        ),
        (  # use different generators
            (
                '{"a": {"$seq": {"__id__": "seq1"}}, '
                '"b": {"$seq": {"__id__": "seq2"}}}'
            ),
            3,
            [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}, {'a': 3, 'b': 3}],
        ),
        (  # to json str
            '{"$json_string": {"data": {"a": {"$seq": null}}}}',
            3,
            ['{"a": 1}', '{"a": 2}', '{"a": 3}'],
        ),
    ],
)
def test_sample_seq(input_data, items, expected, patch):
    additional_generators = {'$seq': SeqGenerator}
    generator = iter(
        fixture_generator.fixture_pipeline(
            input_data, additional_generators=additional_generators,
        ),
    )
    result = []
    for _ in range(items):
        result.append(next(generator))
    assert result == expected


def test_oid():
    input_data = '{"$oid": null}'
    generator = iter(fixture_generator.fixture_pipeline(input_data))
    assert bson.objectid.ObjectId.is_valid(next(generator)['$oid'])


@pytest.mark.parametrize(
    'filters, lookup, expected',
    [
        ({}, 'zone', {'ekb', 'moscow', 'spb'}),
        ({'zone': 'moscow', 'payment_type': 'cash'}, 'tariff_id', {'101112'}),
        ({'zone': 'ekb', 'tariffs.*': 'courier'}, 'tariff_id', {'123'}),
        ({'zone': 'moscow', 'tariffs.*': 'courier'}, 'tariff_id', []),
    ],
)
def test_collection_lookup(search_path, filters, lookup, expected):
    path = str(list(search_path('lookup.json'))[0])
    os.chdir(os.path.dirname(path))
    generator = generators.CollectionLookup('lookup.json', filters, lookup)
    actual_data = set(generator.fetch())
    assert actual_data == set(expected)
