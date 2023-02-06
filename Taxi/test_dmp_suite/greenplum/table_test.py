import mock
from collections import defaultdict
from unittest import TestCase

import pytest

import dmp_suite.datetime_utils as dtu
from dmp_suite.datetime_utils import Period
from dmp_suite.greenplum.exceptions import IncorrectTableIdentifier
from dmp_suite.exceptions import DWHError, DataOrStructureError
from dmp_suite.greenplum.table import (
    Array, Int, Double, Boolean, String, Json, Point, GPTable, GPLocation, GeoHash,
    ExternalGPLayout, ExternalGPLocation, split_table_identifier, RangePartitionItem, MonthPartitionScale,
    DayPartitionScale, YearPartitionScale, field_from_udt
)
from dmp_suite.table import LayeredLayout

from test_dmp_suite.domain.common import test_domain


def fake_prefix_resolver(prefix_key):
    d = defaultdict(lambda: 'prefix')
    d['custom'] = 'ct_prefix'
    return d[prefix_key]


class TestTable(TestCase):
    def test_array_serializer(self):
        arr = Array(Int)
        self.assertEqual(b'"{1,2,3}"', arr.serializer([1, 2, None, 3]))

        arr = Array(Double)
        self.assertEqual(b'"{-1,2.5,3.0}"', arr.serializer([-1, 2.5, None, 3.0]))

        arr = Array(Boolean)
        self.assertEqual(b'"{True,False}"', arr.serializer([True, False, None]))

        data = ['abc', '', 'abcasdf', None, r'"asdl"asd\"gfa']
        arr = Array(String)
        result = arr.serializer(data)
        self.assertEqual(br'"{\"abc\",\"\",\"abcasdf\",null,\"\\\"asdl\\\"asd\\\\\\\"gfa\"}"', result)

    def test_string_serializer(self):
        data = '"asdl"asd\ngfa'
        string = String()
        self.assertEqual(b'"\\"asdl\\"asd\ngfa"', string.serializer(data))
        self.assertEqual(b'', string.serializer(None))

    def test_json_serializer(self):
        json = Json()
        self.assertEqual(br'"{\"a\": 123}"', json.serializer({'a': 123}))
        self.assertEqual(br'"{\"b\": \"asd\\\"fa\\\"\"}"', json.serializer({'b': 'asd"fa"'}))
        self.assertEqual(br'"{\"c\": \"123\\\\\"}"', json.serializer({'c': '123\\'}))
        self.assertEqual(br'"{\"e\": null}"', json.serializer({'e': None}))
        self.assertEqual(br'"{\"o\\\"o\": 2.131, \"f\": \"kasd\\\"asda\\\"\"}"', json.serializer({'o"o': 2.131, 'f': 'kasd"asda"'}))
        self.assertEqual(b'', json.serializer(None))

    def test_point_serializer(self):
        point = Point()
        self.assertEqual('(39.39, 47.1)', point.serializer({'lat': 47.1, 'lon': 39.39}))
        self.assertEqual('(39.39, 47.1)', point.serializer({'lon': 39.39, 'lat': 47.1}))
        self.assertEqual('(39.39, 0.0)', point.serializer({'lon': 39.39, 'lat': 0.0}))
        self.assertEqual(None, point.serializer({'lon': 39.0, 'lat': 47}))
        self.assertEqual(None, point.serializer({'lon': '39.39', 'lat': '47.1'}))
        self.assertEqual(None, point.serializer({'lon': 39.39, 'wrong_key_name': 47.1}))
        self.assertEqual(None, point.serializer({'lon': 39.0, 'lat': None}))
        self.assertEqual(None, point.serializer({'lon': '', 'lat': 47.1}))
        self.assertEqual(None, point.serializer({'lon': [], 'lat': 47.1}))
        self.assertEqual(None, point.serializer({'lon': [39.39], 'lat': 47.1}))
        self.assertEqual(None, point.serializer({}))
        self.assertEqual(None, point.serializer([39.39, 47.1]))
        self.assertEqual(None, point.serializer('39.39, 47.1'))
        self.assertEqual(None, point.serializer(None))

    def test_geohash_serializer(self):
        geohash = GeoHash()
        self.assertEqual(
            'v94g1dutj',
            geohash.serializer({geohash.LATITUDE: 51.1683273, geohash.LONGITUDE: 71.439526})
        )
        self.assertEqual('v94g1dutj', geohash.serializer('v94g1dutj'))
        self.assertEqual(None, geohash.serializer(None))
        self.assertEqual(None, geohash.serializer([2, 3]))
        self.assertEqual(None, geohash.serializer((2, 3)))

        with self.assertRaises(DataOrStructureError):
            geohash.serializer('v94g1dutjaaaaaa')

        with self.assertRaises(DataOrStructureError):
            geohash.serializer('')

        with self.assertRaises(DataOrStructureError):
            geohash.serializer({geohash.LONGITUDE: 71.439526})

        with self.assertRaises(DataOrStructureError):
            geohash.serializer({geohash.LATITUDE: 71.439526})

        with self.assertRaises(DataOrStructureError):
            geohash.serializer({geohash.LATITUDE: '51.1683273', geohash.LONGITUDE: '71.439526'})

        geohash = GeoHash(precision=geohash.ACCURACY_4M)
        self.assertEqual(
            'v94g1dutj',
            geohash.serializer({geohash.LATITUDE: 51.1683273, geohash.LONGITUDE: 71.439526})
        )
        self.assertEqual('v94g1dutj', geohash.serializer('v94g1dutj'))

        geohash = GeoHash(precision=geohash.ACCURACY_70M)
        self.assertEqual(
            'v94g1du',
            geohash.serializer({geohash.LATITUDE: 51.1683273, geohash.LONGITUDE: 71.439526})
        )
        self.assertEqual('v94g1du', geohash.serializer('v94g1du'))


@pytest.mark.parametrize('params, result', (
    ({'prefix': '', 'layer': '', 'group': ''}, ''),
    ({'prefix': 'pfx', 'layer': '', 'group': ''}, 'pfx'),
    ({'prefix': '', 'layer': 'layer', 'group': 'group'}, 'layer_group'),
    ({'prefix': '__pfx', 'layer': '', 'group': 'lvl1_lvl2__lvl3'}, '__pfx_lvl1_lvl2__lvl3'),
))
def test_gp_location_format(params, result):
    assert GPLocation._format('{prefix}_{layer}_{group}', params) == result


@pytest.mark.parametrize('params, error_type', (
    ({'prefix': None, 'layer': 'layer', 'group': 'group'}, TypeError),
    ({'prefix': False, 'layer': 'layer', 'group': 'group'}, TypeError),
    ({'prefix': [], 'layer': 'layer', 'group': 'group'}, TypeError),
    ({'layer': 'layer', 'group': 'group'}, KeyError),
))
def test_gp_location_format_errors(params, error_type):
    with pytest.raises(error_type):
        GPLocation._format('{prefix}_{layer}_{group}', params)


@pytest.mark.parametrize('layout, expected_full', [
    (LayeredLayout('layer', 'name'), 'prefix_pfxvalue_layer.name'),
    (LayeredLayout('layer', 'name', 'group'), 'prefix_pfxvalue_layer_group.name'),
    (LayeredLayout('layer', 'name', 'l1_l2_l3'), 'prefix_pfxvalue_layer_l1_l2_l3.name'),
    (LayeredLayout('layer', 'name', domain=test_domain), 'prefix_pfxvalue_layer_test_domain_code.name'),
])
def test_gp_location(layout, expected_full):
    class Tab(GPTable):
        __layout__ = layout
    with mock.patch.object(Tab, 'get_layout_prefix', return_value='pfxvalue'):
        resolver = GPLocation(Tab, fake_prefix_resolver)
        assert resolver.full() == expected_full


def test_gp_location_custom_project():
    class Tab(GPTable):
        __layout__ = LayeredLayout('layer', 'name', prefix_key='custom')

    location = GPLocation(Tab, fake_prefix_resolver)
    assert location.full() == 'ct_prefix_pfxvalue_layer.name'


def test_external_gp_location():
    class Tab(GPTable):
        __layout__ = ExternalGPLayout('schema', 'table')

    resolver = ExternalGPLocation(Tab, fake_prefix_resolver)
    assert resolver.full() == 'schema.table'


@pytest.mark.parametrize('table_identifier, expected', [
    ('', None),
    ('some_table', (None, 'some_table')),
    ('some_schema.some_table', ('some_schema', 'some_table')),
    ('some_schema.some_table.and_some_trash', None),
])
def test_split_table_identifier(table_identifier, expected):
    if not expected:
        with pytest.raises(IncorrectTableIdentifier):
            split_table_identifier(table_identifier)
    else:
        actual = split_table_identifier(table_identifier)
        assert actual == expected


class TestRangePartitionItem:
    DAY_PARTITION_SCALE = DayPartitionScale('test_key')
    MONTH_PARTITION_SCALE = MonthPartitionScale('test_key')
    YEAR_PARTITION_SCALE = YearPartitionScale('test_key')

    def test_eq(self):
        partition = RangePartitionItem('2021-02-01', '2021-03-01', '202102')
        assert partition == partition
        assert partition == RangePartitionItem('2021-02-01', '2021-03-01', '202102')
        assert not partition == RangePartitionItem('2021-02-01', '2021-03-01', '2021-02')

    def test_non_datetime(self):
        partition = RangePartitionItem('2021-02-01', dtu.MAX_DATETIME_STRING_PLUS_ONE_SECOND, '202102')
        assert partition.start == dtu.parse_datetime('2021-02-01')
        assert partition.end == dtu.MAX_DATETIME_STRING_PLUS_ONE_SECOND

    def test_hash(self):
        partitions = {
            RangePartitionItem('2021-02-01', '2021-03-01', '202102'),
            RangePartitionItem('2021-03-01', '2021-04-01', '202103')
        }

        assert RangePartitionItem('2021-02-01', '2021-03-01', '202102') in partitions
        assert RangePartitionItem('2021-02-01', '2021-03-01', '2021-02') not in partitions
        assert RangePartitionItem('2021-02-01', '2021-02-28', '2021-02') not in partitions
        assert RangePartitionItem('2021-01-01', '2021-02-01', '202101') not in partitions

    @pytest.mark.parametrize('partition_scale, period, expected', [
        (MONTH_PARTITION_SCALE,
         Period('2021-02-01', '2021-02-01'),
         [RangePartitionItem('2021-02-01', '2021-03-01', '202102')]),
        (MONTH_PARTITION_SCALE,
         Period('2021-02-01', '2021-03-01'),
         [
             RangePartitionItem('2021-02-01', '2021-03-01', '202102'),
             RangePartitionItem('2021-03-01', '2021-04-01', '202103'),
          ]),
        (DAY_PARTITION_SCALE,
         Period('2021-02-02', '2021-02-04'),
         [
             RangePartitionItem('2021-02-02', '2021-02-03', '20210202'),
             RangePartitionItem('2021-02-03', '2021-02-04', '20210203'),
             RangePartitionItem('2021-02-04', '2021-02-05', '20210204'),
         ]),
        (YEAR_PARTITION_SCALE,
         Period('2021-02-01', '2021-02-01'),
         [RangePartitionItem('2021-01-01', '2022-01-01', '2021')]),
    ])
    def test_by_period(self, partition_scale, period, expected):
        assert list(RangePartitionItem.by_period(partition_scale, period)) == expected


def test_field_from_udt_array():
    field = field_from_udt('_int4', 'n')
    assert isinstance(field, Array)
    assert field.name == 'n'
    assert field.alias == 'n'


def test_field_from_udt_wrong_array():
    with pytest.raises(DWHError):
        field_from_udt('_abc', 'n')


def test_field_from_udt_primitive():
    field = field_from_udt('int4', 'n')
    assert isinstance(field, Int)
    assert field.name == 'n'
    assert field.alias == 'n'


def test_field_from_udt_wrong_primitive():
    with pytest.raises(DWHError):
        field_from_udt('abc', 'n')
