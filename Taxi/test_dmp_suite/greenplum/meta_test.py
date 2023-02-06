import unittest

import mock
import pytest

from dmp_suite import data_transform
from dmp_suite.greenplum import (
    Int, String, Json, Datetime, GPMeta, resolve_meta, resolve_table_full_name,
)
from dmp_suite.greenplum.table import GPLocation, GPTable, TABLE_NAME_LENGTH_LIMIT
from dmp_suite.table import SummaryLayout, LayeredLayout


class SerializedTable(GPTable):
    __layout__ = SummaryLayout('test', prefix_key='test')

    int_field = Int()
    default_int_field = Int(default_value=42)
    string_field = String()
    json_field = Json()
    datetime_field = Datetime()


class TestGPSerializer(unittest.TestCase):
    def setUp(self):
        meta = GPMeta(SerializedTable)
        self.serializer = meta.serializer()

    def test_mapper_serializes_data(self):
        input_data = [
            dict(int_field='33',
                 default_int_field=None,
                 string_field='foo',
                 json_field={'key': ['some', 'value']},
                 datetime_field='2018-01-01 00:00:00')
        ]
        expected_output_data = [
            dict(int_field=33,
                 default_int_field=42,
                 string_field=b'"foo"',
                 json_field=br'"{\"key\": [\"some\", \"value\"]}"',
                 datetime_field='2018-01-01 00:00:00')
        ]

        self.assertEqual(list(self.serializer.map(input_data)),
                         expected_output_data)

    def test_mapper_validates_data(self):
        input_data = [
            dict(int_field='33a',
                 default_int_field=None,
                 string_field='foo',
                 any_field=[],
                 datetime_field='2018/01/01')
        ]

        with self.assertRaises(data_transform.TransformError):
            list(self.serializer.map(input_data))


class NoKeyTable(GPTable):
    __layout__ = SummaryLayout(group='test', name='no_key', prefix_key='test')

    f1 = String()
    f2 = String()


class KeyTable(GPTable):
    __layout__ = SummaryLayout(group='test', name='key', prefix_key='test')

    f1 = String(key=True)
    f2 = String()


class MultiKeyTable(GPTable):
    __layout__ = SummaryLayout(group='test', name='key', prefix_key='test')

    f1 = String(key=True)
    f2 = Int(key=True)
    f3 = String()


class WrongTableName(GPTable):
    __layout__ = SummaryLayout(group='test', name='n'*(TABLE_NAME_LENGTH_LIMIT-1), prefix_key='test')


def test_unique_key():
    assert not GPMeta(NoKeyTable).unique_key
    assert list(GPMeta(MultiKeyTable).unique_key) == ['f1', 'f2']
    assert list(GPMeta(KeyTable).unique_key) == ['f1']


def test_resolve_meta():
    assert isinstance(resolve_meta(KeyTable), GPMeta)
    assert isinstance(resolve_meta(KeyTable()), GPMeta)
    assert isinstance(resolve_meta(GPMeta(KeyTable)), GPMeta)

    with pytest.raises(ValueError):
        resolve_meta('asf')


def test_resolve_full_table_name():
    meta = GPMeta(KeyTable)
    expected = meta.table_full_name
    assert resolve_table_full_name(KeyTable) == expected
    assert resolve_table_full_name(KeyTable()) == expected
    assert resolve_table_full_name(meta) == expected
    assert resolve_table_full_name('test.test') == 'test.test'


@pytest.mark.parametrize('meta_method, resolver_method', [
    ('table_name', 'table_name'),
    ('schema', 'schema'),
    ('table_full_name', 'full'),
])
def test_call_location_methods(meta_method, resolver_method):
    class TestTableEntityName(GPTable):
        __layout__ = LayeredLayout('layer', 'name', prefix_key='test')
        __location_cls__ = mock.MagicMock(GPLocation)

    meta = GPMeta(TestTableEntityName)
    resolver = meta.location
    assert isinstance(getattr(meta, meta_method)(), mock.MagicMock)
    assert getattr(resolver, resolver_method).called
