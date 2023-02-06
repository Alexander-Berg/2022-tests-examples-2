import multiprocessing as mp
from datetime import datetime
from concurrent import futures

import pytest
import mock
from qb2.typing.simple import (
    String as QB2String,
    Bool as QB2Bool,
    NoneType as QB2NonType,
)
from qb2.typing.yson import Yson as QB2Yson
from qb2.typing.union import Union as QB2Union

from dmp_suite import data_transform
from dmp_suite.table import Table
from dmp_suite import datetime_utils as dtu, global_state
from dmp_suite.yt import meta as yt_meta

import unittest
from dmp_suite.exceptions import DWHError
from dmp_suite.table import LayeredLayout
from dmp_suite.yt import YTTable, DayPartitionScale, String, MonthPartitionScale, \
    Date, YTMeta, full_path, join_path_parts, Datetime, ShortMonthPartitionScale, Int, Any, \
    COMPRESSION_ATTRIBUTES, resolve_meta, DeprecatedYTLocation, Boolean, NotLayeredYtTable, NotLayeredYtLayout
from nile.api.v1 import Record


class T(Table):
    pass


class TestTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test')
    __unique_keys__ = True

    id = String(sort_key=True, sort_position=1)
    dt = Date(sort_key=True, sort_position=0)
    name = String(name='name_abc')


class PartitionedTestTable(TestTable):
    __partition_scale__ = DayPartitionScale("dt")


class TestTable2(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test')

    id = String(required=True)
    flag = Boolean()
    data = Any()


class TestDynamicTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test')
    __unique_keys__ = True
    __dynamic__ = True

    id = String(sort_key=True, sort_position=0)
    text_field = String()


class TestEnableDynamicStoreReadTable(TestDynamicTable):
    __enable_dynamic_store_read__ = True


class ChildTable1(TestTable):
    __layout__ = NotLayeredYtLayout('test1', 'test1')

    s = String()


class ChildTable2(ChildTable1):
    __layout__ = NotLayeredYtLayout('test2', 'test2')


class DayTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('folder', 'name')
    __partition_scale__ = DayPartitionScale('pkey')

    pkey = Datetime()


class OtherDayTable(YTTable):
    __partition_scale__ = DayPartitionScale('pkey')

    pkey = Datetime()


class MonthTable(NotLayeredYtTable):
    __partition_scale__ = MonthPartitionScale('pkey')
    __layout__ = NotLayeredYtLayout('path', 'en')
    pkey = Datetime()


class ShortMonthTable(NotLayeredYtTable):
    __partition_scale__ = ShortMonthPartitionScale('pkey')
    __layout__ = NotLayeredYtLayout('path', 'en')
    pkey = Datetime()


class NoScaleTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('folder', 'entity')
    pkey = String()


class OtherNoScaleTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('folder', 'entity')
    pkey = String()


class NoPartitionKeyTable(NotLayeredYtTable):
    __partition_scale__ = DayPartitionScale(None)
    __layout__ = NotLayeredYtLayout('path', 'en')
    pkey = String()


class WrongPartitionKeyTable(NotLayeredYtTable):
    __partition_scale__ = DayPartitionScale('abc')
    __layout__ = NotLayeredYtLayout('path', 'en')
    pkey = String()


class HeaviestTable(YTTable):
    __compression_level__ = 'heaviest'

    column = String()


class SerializedTable(YTTable):
    int_field = Int()
    default_int_field = Int(default_value=42)
    string_field = String()
    any_field = Any()
    datetime_field = Datetime()


class TestYTMeta(unittest.TestCase):
    def test_has_field(self):
        meta = YTMeta(TestTable)

        self.assertTrue(meta.has_field('dt'))
        self.assertTrue(meta.has_field('name_abc'))
        self.assertFalse(meta.has_field('name'))
        self.assertFalse(meta.has_field('abc'))

        t1 = YTMeta(ChildTable1)
        t2 = YTMeta(ChildTable2)

        self.assertTrue(t1.has_field('id'))
        self.assertTrue(t1.has_field('dt'))
        self.assertTrue(t1.has_field('name_abc'))
        self.assertTrue(t1.has_field('s'))

        self.assertTrue(t2.has_field('id'))
        self.assertTrue(t2.has_field('dt'))
        self.assertTrue(t2.has_field('name_abc'))
        self.assertTrue(t2.has_field('s'))

    def test_target_path(self):
        meta = YTMeta(TestTable)
        self.assertEqual(meta.target_path(), '//dummy/test/test')
        self.assertEqual(['dt', 'id'], meta.unique_key_names())

    def test_target_wo_partition(self):
        meta = YTMeta(TestTable)
        self.assertEqual(meta.target_path_wo_partition, '//dummy/test/test')

        meta = YTMeta(DayTable)
        self.assertEqual(meta.target_path_wo_partition, '//dummy/folder/name')

    def test_rel_path(self):
        meta = YTMeta(TestTable)
        self.assertEqual(meta.rel_path(), 'test/test')

        meta = YTMeta(ChildTable1)
        self.assertEqual(meta.rel_path(), 'test1/test1')

        meta = YTMeta(MonthTable, '2019-01-01')
        self.assertEqual(meta.rel_path(), 'path/en/2019-01-01')

    def test_fields_for_sort(self):
        meta = YTMeta(TestTable)

        expected = [
            Date(name='dt', alias='dt', sort_key=True, sort_position=0),
            String(name='id', alias='id', sort_key=True, sort_position=1)
        ]
        actual = meta.sort_key_fields()
        self.assertEqual(expected, actual)

    def test_full_path(self):
        self.assertRaises(ValueError, full_path, path=None)
        self.assertRaises(ValueError, full_path, path='//home//test')

        actual = full_path('tst')
        expected = '//tst'
        self.assertEqual(expected, actual)

        actual = full_path('/tst')
        expected = '//tst'
        self.assertEqual(expected, actual)

        actual = full_path('//tst')
        expected = '//tst'
        self.assertEqual(expected, actual)

        actual = full_path(path='tst', prefix='home')
        expected = '//home/tst'
        self.assertEqual(expected, actual)

        actual = full_path(path='/tst', prefix='//home')
        expected = '//home/tst'
        self.assertEqual(expected, actual)

        actual = full_path(path='tst', suffix='ctl')
        expected = '//tst/ctl'
        self.assertEqual(expected, actual)

        actual = full_path(path='tst', prefix='home', suffix='ctl')
        expected = '//home/tst/ctl'
        self.assertEqual(expected, actual)

        actual = full_path(
            path='tst',
            prefix='home',
            suffix='ctl',
            partition='orders'
        )
        expected = '//home/tst/ctl/orders'
        self.assertEqual(expected, actual)

    def test_join_path_parts(self):
        self.assertRaises(AttributeError, join_path_parts, None)
        self.assertRaises(AttributeError, join_path_parts, '//home', None)

        actual = join_path_parts('//tst')
        expected = '//tst'
        self.assertEqual(expected, actual)

        actual = join_path_parts('tst/')
        expected = 'tst/'
        self.assertEqual(expected, actual)

        actual = join_path_parts('//home', '/test/')
        expected = '//home/test/'
        self.assertEqual(expected, actual)

        actual = join_path_parts('//home', '/test')
        expected = '//home/test'
        self.assertEqual(expected, actual)

        actual = join_path_parts('//home/', '/test')
        expected = '//home/test'
        self.assertEqual(expected, actual)

        actual = join_path_parts('//home', '/lvl0', '/lvl1/lvl2/', '/lvl3/')
        expected = '//home/lvl0/lvl1/lvl2/lvl3/'
        self.assertEqual(expected, actual)

        actual = join_path_parts('//home', '/lvl0', '', 'lvl1')
        expected = '//home/lvl0/lvl1'
        self.assertEqual(expected, actual)

    def test_has_partition_scale(self):
        meta = YTMeta(DayTable)
        self.assertTrue(meta.has_partition_scale)
        meta = YTMeta(NoScaleTable)
        self.assertFalse(meta.has_partition_scale)

    def test_partition_scale_extract_partition(self):
        meta = YTMeta(DayTable)
        record = dict(pkey='2017-05-03 15:23:23')
        self.assertEqual(
            meta.partition_scale.extract_partition(record),
            '2017-05-03'
        )

        meta = YTMeta(MonthTable)
        record = dict(pkey='2017-05-03 15:23:23')
        self.assertEqual(
            meta.partition_scale.extract_partition(record),
            '2017-05-01'
        )

        record = dict(a=1)
        self.assertRaises(
            ValueError,
            meta.partition_scale.extract_partition,
            record
        )

    def test_partition_scale_partitions_by_period(self):
        meta = YTMeta(MonthTable)

        period = dtu.period('2017-09-12', '2017-11-23')
        self.assertEqual(
            meta.partition_scale.split_in_partitions(period),
            ['2017-09-01', '2017-10-01', '2017-11-01']
        )
        period = dtu.period('2017-12-12', '2018-01-23')
        self.assertEqual(
            meta.partition_scale.split_in_partitions(period),
            ['2017-12-01', '2018-01-01']
        )
        period = dtu.period('2017-11-12', '2017-11-23')
        self.assertEqual(
            meta.partition_scale.split_in_partitions(period),
            ['2017-11-01']
        )
        period = dtu.period('2017-11-12', '2017-11-12')
        self.assertEqual(
            meta.partition_scale.split_in_partitions(period),
            ['2017-11-01']
        )
        period = dtu.period('2017-11-12 12:12:12', '2017-11-12 12:13:13')
        self.assertEqual(
            meta.partition_scale.split_in_partitions(period),
            ['2017-11-01']
        )

    def test_init(self):
        self.assertRaises(ValueError, YTMeta, T)
        self.assertRaises(AttributeError, YTMeta, NoPartitionKeyTable)
        self.assertRaises(AttributeError, YTMeta, WrongPartitionKeyTable)
        self.assertRaises(ValueError, YTMeta, DayTable, 'abc')
        self.assertRaises(ValueError, YTMeta, DayTable, '2017-1')

    def test_partition(self):

        dt = dtu.parse_datetime('2017-04-04')
        meta = YTMeta(TestTable, dt)
        with pytest.raises(DWHError):
            self.assertEqual(meta.partition, dt)

        meta = YTMeta(DayTable, '2017-10-10 23:12:12')
        self.assertEqual(meta.partition, '2017-10-10')

        meta = YTMeta(DayTable, datetime(2017, 10, 10, 23, 12, 12))
        self.assertEqual(meta.partition, '2017-10-10')

        meta = YTMeta(MonthTable, '2017-10-10 23:12:12')
        self.assertEqual(meta.partition, '2017-10-01')

        meta = YTMeta(ShortMonthTable, '2017-10-10 23:12:12')
        self.assertEqual(meta.partition, '2017-10')

        meta = YTMeta(ShortMonthTable, '2017-10')
        self.assertEqual(meta.partition, '2017-10')

    def test_with_partition(self):
        meta = YTMeta(DayTable, partition='2017-10-10')
        new_meta = meta.with_partition('2018-10-10')

        self.assertIs(new_meta.table_class, meta.table_class)
        self.assertEqual(new_meta.target_folder_path, meta.target_folder_path)
        self.assertEqual(new_meta.partition, '2018-10-10')

    @mock.patch('connection.yt.get_bundle_value',
                mock.MagicMock(return_value='dummy'))
    def test_dynamic(self):
        static_meta = YTMeta(TestTable)
        self.assertFalse(static_meta.is_dynamic)
        self.assertFalse(static_meta.enable_dynamic_store_read)
        self.assertFalse(static_meta.attributes()['dynamic'])
        self.assertFalse('tablet_cell_bundle' in static_meta.attributes())
        self.assertFalse(static_meta.attributes()['enable_dynamic_store_read'])
        self.assertFalse(static_meta.rotation_attributes()['dynamic'])
        self.assertFalse('tablet_cell_bundle' in static_meta.rotation_attributes())
        self.assertFalse(static_meta.rotation_attributes()['enable_dynamic_store_read'])
        self.assertFalse(static_meta.buffer_attributes()['dynamic'])
        self.assertFalse('tablet_cell_bundle' in static_meta.buffer_attributes())
        self.assertFalse(static_meta.buffer_attributes()['enable_dynamic_store_read'])

        dynamic_meta = YTMeta(TestDynamicTable)
        self.assertTrue(dynamic_meta.is_dynamic)
        self.assertFalse(dynamic_meta.enable_dynamic_store_read)
        self.assertTrue(dynamic_meta.attributes()['dynamic'])
        self.assertEqual(dynamic_meta.attributes()['tablet_cell_bundle'],
                         'dummy')
        self.assertFalse(dynamic_meta.attributes()['enable_dynamic_store_read'])
        self.assertFalse(dynamic_meta.rotation_attributes()['dynamic'])
        self.assertEqual(
            dynamic_meta.rotation_attributes()['tablet_cell_bundle'],
            'dummy'
        )
        self.assertFalse(dynamic_meta.rotation_attributes()['enable_dynamic_store_read'])
        self.assertFalse(dynamic_meta.buffer_attributes()['dynamic'])
        self.assertEqual(dynamic_meta.buffer_attributes()['tablet_cell_bundle'],
                         'dummy')
        self.assertFalse(dynamic_meta.buffer_attributes()['enable_dynamic_store_read'])

    def test_enable_dynamic_store_read(self):
        meta = YTMeta(TestEnableDynamicStoreReadTable)
        self.assertTrue(meta.enable_dynamic_store_read)
        self.assertTrue(meta.attributes()['enable_dynamic_store_read'])
        self.assertTrue(meta.rotation_attributes()['enable_dynamic_store_read'])

    def test_default_compression(self):
        meta = YTMeta(TestTable)
        normal_compression = COMPRESSION_ATTRIBUTES['normal']

        assert meta.compression_level == 'normal'

        self.assertIsSubdict(normal_compression, meta.attributes())
        self.assertIsSubdict(normal_compression, meta.rotation_attributes())
        self.assertIsSubdict(normal_compression, meta.buffer_attributes())

    def test_heaviest_compression(self):
        meta = YTMeta(HeaviestTable)
        heaviest_compression = COMPRESSION_ATTRIBUTES['heaviest']

        assert meta.compression_level == 'heaviest'

        self.assertIsSubdict(heaviest_compression, meta.attributes())
        self.assertIsSubdict(heaviest_compression, meta.rotation_attributes())
        self.assertIsSubdict(heaviest_compression, meta.buffer_attributes())

    def test_schema(self):
        meta = YTMeta(TestTable)

        target_schema = meta.attributes()['schema']
        assert list(target_schema) == [
            {'name': 'dt', 'sort_order': 'ascending', 'type': 'string', 'required': False},
            {'name': 'id', 'sort_order': 'ascending', 'type': 'string', 'required': False},
            {'name': 'name_abc', 'type': 'string', 'required': False}
        ]
        assert target_schema.attributes['strict']
        assert target_schema.attributes['unique_keys']

        rotation_schema = meta.rotation_attributes()['schema']
        assert list(rotation_schema) == [
            {'name': 'dt', 'sort_order': 'ascending', 'type': 'string', 'required': False},
            {'name': 'id', 'sort_order': 'ascending', 'type': 'string', 'required': False},
            {'name': 'name_abc', 'type': 'string', 'required': False}
        ]
        assert rotation_schema.attributes['strict']
        assert rotation_schema.attributes['unique_keys']

        buffer_schema = meta.buffer_attributes()['schema']
        assert list(buffer_schema) == [
            {'name': 'dt', 'type': 'string', 'required': False},
            {'name': 'id', 'type': 'string', 'required': False},
            {'name': 'name_abc', 'type': 'string', 'required': False}
        ]
        assert buffer_schema.attributes['strict']
        assert not buffer_schema.attributes['unique_keys']

    def test_schema_with_required(self):
        meta = YTMeta(TestTable2)
        target_schema = meta.attributes()['schema']
        assert list(target_schema) == [
            {'name': 'data', 'type': 'any', 'required': False},
            {'name': 'flag', 'type': 'boolean', 'required': False},
            {'name': 'id', 'type': 'string', 'required': True},
        ]

    def test_qb2_schema(self):
        meta = YTMeta(TestTable2)
        assert meta.qb2_schema == {
            'data': QB2Union[QB2NonType, QB2Yson],
            'flag': QB2Union[QB2Bool, QB2NonType],
            'id': QB2String,
        }

    def assertIsSubdict(self, subdictionary, dictionary):
        for key, value in subdictionary.items():
            assert dictionary[key] == value


class TestYTSerializer(unittest.TestCase):
    def setUp(self):
        meta = YTMeta(SerializedTable)
        self.serializer = meta.serializer()

    def test_mapper_serializes_data(self):
        mapper = self.serializer.mapper()

        input_data = [
            Record(int_field='33',
                   default_int_field=None,
                   string_field=u'foo',
                   any_field=[],
                   datetime_field=u'2018-01-01')
        ]
        expected_output_data = [
            Record(int_field=33,
                   default_int_field=42,
                   string_field=b'foo',
                   any_field=[],
                   # QUESTION: это нормально, что строка для Datetime
                   #           остаётся юникодной?
                   #           Может она должна преобразовываться в bytes?
                   datetime_field=u'2018-01-01 00:00:00')
        ]

        result = list(mapper(input_data))
        self.assertEqual(result, expected_output_data)

    def test_mapper_validates_data(self):
        mapper = self.serializer.mapper()

        input_data = [
            Record(int_field='33a',
                   default_int_field=None,
                   string_field='foo',
                   any_field=[],
                   datetime_field='2018/01/01')
        ]

        with self.assertRaises(data_transform.TransformError):
            list(mapper(input_data))


def test_resolve_meta():
    with pytest.raises(ValueError):
        resolve_meta('asdf')

    assert isinstance(resolve_meta(TestTable), YTMeta)
    assert isinstance(resolve_meta(TestTable()), YTMeta)
    assert isinstance(resolve_meta(YTMeta(TestTable)), YTMeta)


def test_resolve_meta_with_partition():
    # Проверим, разные варианты, когда в resolve_meta
    # передаётся partition.

    # По умолчанию партиция не задана, и попытка доступа к атрибуту
    # вызывает ошибку:
    with pytest.raises(DWHError):
        resolve_meta(PartitionedTestTable).partition

    # То же самое должно происходить, если
    # в resolve_meta мы передаём None:
    with pytest.raises(DWHError):
        resolve_meta(PartitionedTestTable, None).partition

    assert resolve_meta(PartitionedTestTable, '2020-07-15').partition == '2020-07-15'
    assert resolve_meta(PartitionedTestTable(), '2020-07-15').partition == '2020-07-15'
    assert resolve_meta(YTMeta(PartitionedTestTable), '2020-07-15').partition == '2020-07-15'

    # Если в resolve_meta передана мета с partition:
    old_meta = resolve_meta(PartitionedTestTable, '2020-07-15')
    # то, её можно переопределить
    new_meta = resolve_meta(old_meta, '2020-01-01')
    # при этом не только партиция изменится:
    assert new_meta.partition == '2020-01-01'
    # но и оригинальный объект meta не должен поменяться
    assert old_meta.partition == '2020-07-15'

    # Передача None должна сбрасывать партишен, как-будто его и не было
    with pytest.raises(DWHError):
        resolve_meta(old_meta, None).partition


@pytest.mark.parametrize('meta_method, location_method', [
    ('target_path', 'full'),
    ('rel_path', 'rel'),
    ('target_folder_path', 'folder'),
    ('rel_folder', 'rel_folder'),
    ('buffer_path', 'buffer'),
    ('rotation_path', 'rotation'),
    ('partition', 'table_name'),
    ('target_path_wo_partition', 'wo_partition'),
])
def test_call_location_methods(meta_method, location_method):
    """
    этот тест проверяет что мета вызывает нужные методы location
    """
    class TestTableEntityName(YTTable):
        __layout__ = LayeredLayout('layer', 'name')
        __location_cls__ = mock.MagicMock(DeprecatedYTLocation)

    meta = YTMeta(TestTableEntityName)
    resolver = meta.location
    assert isinstance(getattr(meta, meta_method)(), mock.MagicMock)
    assert getattr(resolver, location_method).called
