import copy

import unittest
import datetime
import pytest

import utils.common as common


class TestSetDefaultValues(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.defaults = {
            'A': 'default',
            'B': 'default',
            'C': 'default',
            'D': None
        }
        super(TestSetDefaultValues, self).__init__(*args, **kwargs)

    def test_main(self):
        source = [{
            'A': 1,
            'B': '2'
        }]
        expected = [{
            'A': 1,
            'B': '2',
            'C': 'default',
            'D': None
        }]
        self.assertEqual(common.set_default_values(source, **self.defaults), expected)

    def test_extended_source(self):
        source = [{
            'A': '1',
            'B': None,
            'E': 'value'
        }]
        expected = [{
            'A': '1',
            'B': None,
            'C': 'default',
            'D': None,
            'E': 'value'
        }]
        self.assertEqual(common.set_default_values(source, **self.defaults), expected)

    def test_extended_source_dict(self):
        source = {
            'A': '1',
            'B': None,
            'E': 'value'
        }
        expected = {
            'A': '1',
            'B': None,
            'C': 'default',
            'D': None,
            'E': 'value'
        }
        self.assertEqual(common.set_default_values(source, **self.defaults), expected)

    def test_empty_source(self):
        source = []
        self.assertEqual(common.set_default_values(source, **self.defaults), [])

    def test_empty_source_empty_dict(self):
        source = [{}]
        self.assertEqual(common.set_default_values(source, **self.defaults), [self.defaults])

    def test_empty_source_dict(self):
        source = {}
        self.assertEqual(common.set_default_values(source, **self.defaults), self.defaults)

    def test_empty_defaults(self):
        source = {'A': 1}
        self.assertEqual(common.set_default_values(source, **{}), source)
        self.assertEqual(common.set_default_values([source], **{}), [source])
        self.assertEqual(common.set_default_values(source, kwargs=None), source)
        self.assertEqual(common.set_default_values([source], kwargs=None), [source])


class TestGetChunks(object):
    def test_smoke(self):
        a = [1, 2, 3, 4, 5]
        expected_result = [[1, 2], [3, 4], [5]]
        chunks = list(common.get_chunks(a, 2))
        assert chunks == expected_result

    def test_int_division(self):
        a = [1, 2, 3, 4]
        expected_result = [[1, 2], [3, 4]]
        chunks = list(common.get_chunks(a, 2))
        assert chunks == expected_result


class TestDatetimeToTimestampConverter(object):
    def test_datetime_to_timestamp(self):
        utc_datetime = datetime.datetime(2011, 2, 28, 23, 59, 59)

        assert utc_datetime == datetime.datetime.utcfromtimestamp(
            common.datetime_to_timestamp(utc_datetime)
        )


@pytest.mark.parametrize(
    'value,expected',
    [
        ({'a': 1}, {'a': 1}),
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
        ({'a': 1, 'b': {'c': 2, 'd': 5}}, {'a': 1, 'b.c': 2, 'b.d': 5}),
        ({'a': 1, 'b': {'c': {'e': [1, 2, 3]}, 'd': 5}}, {'a': 1, 'b.c.e': [1, 2, 3], 'b.d': 5}),
        ({'a': {'b': {'c': {'d': {'e': 1}}}}}, {'a.b.c.d.e': 1}),
        ({'a': '1'}, {'a': '1'}),
        (
            {'a': {'b': '1', 'c': '2'}, 'b': {'d': {'c': '5', 'f': '100'}, 'a': {'e': '2', 'f': '5'}}},
            {'a.b': '1', 'a.c': '2', 'b.d.c': '5', 'b.d.f': '100', 'b.a.e': '2', 'b.a.f': '5'}
        )
    ]
)
def test_flatten_nested_dicts(value, expected):
    original_value = copy.deepcopy(value)
    result = common.flatten_nested_dicts(value)
    assert value == original_value, 'should not modify inputs'
    assert result == expected


def test_flatten_nested_dicts_dot_names_collision():
    dct = {'a.b': {'c': 1}, 'a': {'b': {'c': 2}}}
    with pytest.raises(RuntimeError):
        common.flatten_nested_dicts(dct)
