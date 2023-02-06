import pytest
from dmp_suite.yt.table import \
    Date, Datetime, DatetimeMicroseconds, \
    Int, UInt, Double, Any, String, Boolean, \
    List, Dict, Struct, Optional, Tuple, \
    MonthPartitionScale, DayPartitionScale
from dmp_suite.yt.etl_yql import load_period_from_buffer
from dmp_suite.yt.etl import ETLTable, YTMeta
from dmp_suite.yt import COMPRESSION_ATTRIBUTES
import dmp_suite.yt.operation as op
import dmp_suite.datetime_utils as dtu
from connection.yt import get_yt_client
from test_dmp_suite.yt.utils import fixture_random_yt_table
from dmp_suite.exceptions import DWHError
from dmp_suite.yt.dyntable_operation import operations as dyntable_op, dynamic_table_loaders


def check_schema(table_path, table_meta):
    expected_schema = table_meta.yt_schema()
    real_schema = op.get_yt_table_schema(table_path)

    assert len(expected_schema) == len(real_schema)

    for i in range(0, len(real_schema)):
        for k in real_schema[i]:
            if k not in expected_schema[i]:
                continue
            assert real_schema[i][k] == expected_schema[i][k]


class Table01(ETLTable):
    __partition_scale__ = MonthPartitionScale(partition_key='partition_dt')
    __compression_level__ = 'heaviest'
    __unique_keys__ = True

    partition_dt = Date()
    order_int = Int(sort_key=True, sort_position=0)
    field_dt = Date()
    field_str = String()
    field_any = Any()


class Table02(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dt')
    __unique_keys__ = True

    partition_dt = Date()
    order_uint = UInt(sort_key=True, sort_position=0)
    field_double = Double()
    field_dttm_micro = DatetimeMicroseconds(required=False)


class Table03(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dttm')

    partition_dttm = Datetime()
    order_str = String(sort_key=True, sort_position=0)
    timestamp = Datetime()
    field_bool = Boolean()
    field_str_null = String()


class Table04(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dttm_micro')
    __unique_keys__ = True

    partition_dttm_micro = DatetimeMicroseconds()
    order_int = Int(sort_key=True, sort_position=0)
    field_any = Any()
    field_str = String()


class Table05(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dttm')
    __compression_level__ = 'lightest'
    __unique_keys__ = True

    partition_dttm = Datetime(sort_key=True, sort_position=0)
    order_int = Int(sort_key=True, sort_position=1, required=True)
    field_str = String()
    field_dt = Date()
    field_any = Any()
    field_uint = UInt()


class Table06(ETLTable):
    partition_dt = Date()
    __compression_level__ = 'heaviest'
    order_int = Int(sort_key=True, sort_position=0)
    field_str = String()


class Table07(ETLTable):
    order_int = Int(sort_key=True, sort_position=0)
    partition_dttm = DatetimeMicroseconds(sort_key=True, sort_position=1)
    field_str = String()


class Table08(ETLTable):
    order_int = Int(sort_key=True, sort_position=0)
    partition_dttm_micro = DatetimeMicroseconds()
    field_str = String(required=False)


class Table09(ETLTable):
    __dynamic__ = True
    __unique_keys__ = True
    order_int = Int(sort_key=True, sort_position=0)
    partition_dttm = Datetime()
    field_str = String()


class Table10(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dt')

    partition_dt = Date()
    order_int = Int(sort_key=True, sort_position=0)
    field_list_string_1 = List(String)
    field_list_string_2 = List(Optional[String])
    field_list_string_3 = Optional(List[String])
    field_list_string_4 = Optional(List[Optional[String]])
    field_any = Any()


class Table11(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dt')
    __unique_keys__ = True
    partition_dt = Date()
    order_int = Int(sort_key=True, sort_position=0)
    field_dict_1 = Dict(String, Int)
    field_dict_2 = Optional(Dict[String, Optional[Double]])
    field_list_string_4 = Optional(List[Optional[String]])


class Table12(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dt')
    partition_dt = Date()
    field_list_str = Optional(List[Optional[String]])
    field_list_double = List[Double]
    field_dict_1 = Optional(Dict[String, Optional[UInt]])
    field_dict_2 = Optional(Dict[String, Optional[List[Optional[String]]]])
    field_any = Any()
    field_bool = Boolean()
    field_int = Int()
    field_uint = UInt()
    field_double = Double()
    field_str = String()
    field_tuple = Tuple([Optional[String], Boolean, Double, Optional[Int]])
    field_struct = Optional(Struct[{'id': String, 'values': List[String]}])


class Table13(ETLTable):
    __partition_scale__ = DayPartitionScale(partition_key='partition_dt')
    partition_dt = Date()
    order_int = Int(sort_key=True, sort_position=0)
    field_nested_list = Optional(List[Optional[List[Optional[String]]]])
    field_dict_1 = Optional(Dict[String, Optional[Int]])
    field_dict_2 = Optional(Dict[String, List[String]])
    field_tuple = Optional(Tuple[(Optional[String], Boolean, Double, Optional[Int])])
    field_struct = Optional(Struct[{'id': String, 'values': List[String]}])


test_table_01 = fixture_random_yt_table(Table01)
test_table_02 = fixture_random_yt_table(Table02)
test_table_03 = fixture_random_yt_table(Table03)
test_table_04 = fixture_random_yt_table(Table04)
test_table_05 = fixture_random_yt_table(Table05)
test_table_06 = fixture_random_yt_table(Table06)
test_table_07 = fixture_random_yt_table(Table07)
test_table_08 = fixture_random_yt_table(Table08)
test_table_09 = fixture_random_yt_table(Table09)
test_table_10 = fixture_random_yt_table(Table10)
test_table_11 = fixture_random_yt_table(Table11)
test_table_12 = fixture_random_yt_table(Table12)
test_table_13 = fixture_random_yt_table(Table13)


def _drop_etl_updated(records):
    for r in records:
        del r['etl_updated']
    return records


@pytest.mark.slow
def test_modify_second_partition(test_table_01):
    meta = YTMeta(test_table_01)

    op.init_yt_table(
        meta.with_partition('2017-01-01').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2017-01-01').target_path(),
        [
            dict(partition_dt='2017-01-01', order_int=1, field_dt='1985-08-01', field_str='тест', field_any=[1, 2, 3]),
            dict(partition_dt='2017-01-02', order_int=2, field_dt='1985-08-02', field_str=None, field_any={'k': 'v'}),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2017-02-01').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2017-02-01').target_path(),
        [
            dict(partition_dt='2017-02-03', order_int=3, field_dt='1985-08-01', field_str='', field_any=['1', '2']),
            dict(partition_dt='2017-02-04', order_int=4, field_dt='1985-08-02', field_str=None, field_any=1000),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(partition_dt='2017-02-01', order_int=5, field_dt=None, field_str='', field_any=['1', '2']),
            dict(partition_dt='2017-02-02', order_int=6, field_dt='2019-01-01', field_str='xxxx', field_any=9000),
            dict(partition_dt='2017-02-03', order_int=7, field_dt='2020-01-01', field_str='\t\n', field_any='123'),
        ]
    )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2017-01-01', '2017-02-02')
        )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2017-02-02', '2017-02-04')
        )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2017-02-01', '2017-02-03'),
        by_field='partition_dt',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2017-01-01').target_path()
    ))) == [
               dict(partition_dt='2017-01-01', order_int=1, field_dt='1985-08-01', field_str='тест',
                    field_any=[1, 2, 3]),
               dict(partition_dt='2017-01-02', order_int=2, field_dt='1985-08-02', field_str=None,
                    field_any={'k': 'v'}),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2017-02-01').target_path()
    ))) == [
               dict(partition_dt='2017-02-04', order_int=4, field_dt='1985-08-02', field_str=None, field_any=1000),
               dict(partition_dt='2017-02-01', order_int=5, field_dt=None, field_str='', field_any=['1', '2']),
               dict(partition_dt='2017-02-02', order_int=6, field_dt='2019-01-01', field_str='xxxx', field_any=9000),
               dict(partition_dt='2017-02-03', order_int=7, field_dt='2020-01-01', field_str='\t\n', field_any='123'),
           ]

    assert get_yt_client().get_attribute(
        meta.with_partition('2017-01-01').target_path(), 'compression_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['compression_codec']

    assert get_yt_client().get_attribute(
        meta.with_partition('2017-01-01').target_path(), 'erasure_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['erasure_codec']

    assert get_yt_client().get_attribute(
        meta.with_partition('2017-02-01').target_path(), 'compression_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['compression_codec']

    assert get_yt_client().get_attribute(
        meta.with_partition('2017-02-01').target_path(), 'erasure_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['erasure_codec']

    check_schema(meta.with_partition('2017-01-01').target_path(), meta)
    check_schema(meta.with_partition('2017-02-01').target_path(), meta)


@pytest.mark.slow
def test_many_partitions(test_table_02):
    meta = YTMeta(test_table_02)

    op.init_yt_table(
        meta.with_partition('2021-08-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2021-08-10').target_path(),
        [
            dict(
                partition_dt='2021-08-10', order_uint=1, field_double=3.14,
                field_dttm_micro='2010-01-01 00:00:00.000000',
            ),
            dict(
                partition_dt='2021-08-10', order_uint=2, field_double=None,
                field_dttm_micro='2010-01-01 00:00:00.000001',
            ),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2021-08-11').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2021-08-11').target_path(),
        [
            dict(
                partition_dt='2021-08-11', order_uint=100, field_double=3.,
                field_dttm_micro=None,
            ),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2021-08-15').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2021-08-15').target_path(),
        [
            dict(
                partition_dt='2021-08-15', order_uint=5, field_double=-9e6,
                field_dttm_micro='2014-05-01 00:03:00.123456',
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2021-08-12', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-12', order_uint=14, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-13', order_uint=16, field_double=1234.99,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-14', order_uint=17, field_double=888.0,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-15', order_uint=15, field_double=None,
                field_dttm_micro=None,
            ),
            dict(
                partition_dt='2021-08-16', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-20', order_uint=4, field_double=-5.5,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]
    )
    load_period_from_buffer(
        meta,
        period=dtu.Period('2021-08-11', '2021-08-22')
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-10').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-10', order_uint=1, field_double=3.14,
                   field_dttm_micro='2010-01-01 00:00:00.000000',
               ),
               dict(
                   partition_dt='2021-08-10', order_uint=2, field_double=None,
                   field_dttm_micro='2010-01-01 00:00:00.000001',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-11').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-12').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-12', order_uint=4, field_double=None,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
               dict(
                   partition_dt='2021-08-12', order_uint=14, field_double=None,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-13').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-13', order_uint=16, field_double=1234.99,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-14').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-14', order_uint=17, field_double=888.0,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-15').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-15', order_uint=15, field_double=None,
                   field_dttm_micro=None,
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-16').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-16', order_uint=4, field_double=None,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-17').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-18').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-19').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-20').target_path()
    ))) == [
               dict(
                   partition_dt='2021-08-20', order_uint=4, field_double=-5.5,
                   field_dttm_micro='2014-05-01 00:00:00.00000',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-21').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2021-08-22').target_path()
    ))) == []


@pytest.mark.slow
def test_dttm_in_day_partitions_with_nulls(test_table_03):
    meta = YTMeta(test_table_03)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dttm='2019-10-10 02:02:02', order_str='a1', timestamp='1985-08-01 10:00:00', field_bool=True
            ),
            dict(
                partition_dttm='2019-10-10 01:01:01', order_str='a2', timestamp='1985-08-02 11:00:00', field_bool=False
            ),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2019-10-12').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-12').target_path(),
        [
            dict(
                partition_dttm='2019-10-12 12:02:02', order_str='b1', timestamp='1985-08-01 10:00:00',
            ),
            dict(partition_dttm='2019-10-12 11:01:01', order_str='b2', field_bool=False),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2019-10-08 08:00:00', order_str='d1', timestamp='1985-08-01 10:00:00', field_bool=True
            ),
            dict(
                partition_dttm='2019-10-08 12:02:02', order_str='c1',
            ),
            dict(
                partition_dttm='2019-10-10 12:02:02', order_str='e1', timestamp='1985-08-01 10:00:00', field_bool=False
            ),
        ]
    )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-10-08 08:00:01', '2019-12-31 07:00:00')
        )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-10-10 12:02:03', '2019-12-31 07:00:00')
        )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-08 00:00:00', '2019-10-10 23:59:59')
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-08').target_path()
    ))) == [
               dict(
                   partition_dttm='2019-10-08 12:02:02', order_str='c1', timestamp=None, field_bool=None,
                   field_str_null=None,
               ),
               dict(
                   partition_dttm='2019-10-08 08:00:00', order_str='d1', timestamp='1985-08-01 10:00:00',
                   field_bool=True, field_str_null=None,
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-09').target_path()
    ))) == []

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-10').target_path()
    ))) == [
               dict(
                   partition_dttm='2019-10-10 12:02:02', order_str='e1', timestamp='1985-08-01 10:00:00',
                   field_bool=False, field_str_null=None,
               ),
           ]


@pytest.mark.slow
def test_micro_in_day_partitions_whole_days(test_table_04):
    meta = YTMeta(test_table_04)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dttm_micro='2019-10-10 22:22:22.222222', order_int=1, field_any='555', field_str=None,
            ),
            dict(
                partition_dttm_micro='2019-10-10 22:22:22.555555', order_int=2, field_any={}, field_str='STR',
            ),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2019-10-11').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-11').target_path(),
        [
            dict(
                partition_dttm_micro='2019-10-11 23:00:00.000000', order_int=10, field_any=[], field_str='123 321',
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm_micro='2019-10-11 23:59:59.999999',
                order_int=20, field_any={'a': {'1': 123}}, field_str='',
            ),
            dict(
                partition_dttm_micro='2019-10-11 00:00:00.000000',
                order_int=15, field_any=[[1, 2], [3, 4], [5, 6]], field_str='F',
            ),
            dict(
                partition_dttm_micro='2019-10-11 14:00:00.134645', order_int=5, field_any=None, field_str='Юникод',
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-11 00:00:00.000000', '2019-10-11 23:59:59.999999')
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-10').target_path()
    ))) == [
               dict(
                   partition_dttm_micro='2019-10-10 22:22:22.222222', order_int=1, field_any='555', field_str=None,
               ),
               dict(
                   partition_dttm_micro='2019-10-10 22:22:22.555555', order_int=2, field_any={}, field_str='STR',
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-11').target_path()
    ))) == [
               dict(
                   partition_dttm_micro='2019-10-11 14:00:00.134645', order_int=5, field_any=None, field_str='Юникод',
               ),
               dict(
                   partition_dttm_micro='2019-10-11 00:00:00.000000',
                   order_int=15, field_any=[[1, 2], [3, 4], [5, 6]], field_str='F',
               ),
               dict(
                   partition_dttm_micro='2019-10-11 23:59:59.999999', order_int=20, field_any={'a': {'1': 123}},
                   field_str=''
               ),
           ]


@pytest.mark.slow
def test_micro_in_day_partitions_shifted_period(test_table_04):
    meta = YTMeta(test_table_04)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dttm_micro='2019-10-10 22:22:22.222222', order_int=1, field_any='555', field_str=None,
            ),
            dict(
                partition_dttm_micro='2019-10-10 22:22:22.555555', order_int=2, field_any={}, field_str='STR',
            ),
        ]
    )

    op.init_yt_table(
        meta.with_partition('2019-10-11').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-11').target_path(),
        [
            dict(
                partition_dttm_micro='2019-10-11 23:00:00.000000', order_int=10, field_any=[], field_str='123 321',
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm_micro='2019-10-11 14:00:00.134645', order_int=5, field_any=None, field_str='Юникод',
            ),
        ]
    )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-10-11 14:00:00.000000', '2019-10-11 14:00:00.134644')
        )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-10-11 14:00:00.134646', '2019-10-11 14:00:59.999999')
        )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10 22:22:22.555555', '2019-10-11 22:59:59.999999')
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-10').target_path()
    ))) == [
               dict(
                   partition_dttm_micro='2019-10-10 22:22:22.222222', order_int=1, field_any='555', field_str=None,
               ),
           ]

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-11').target_path()
    ))) == [
               dict(
                   partition_dttm_micro='2019-10-11 14:00:00.134645', order_int=5, field_any=None, field_str='Юникод',
               ),
               dict(
                   partition_dttm_micro='2019-10-11 23:00:00.000000', order_int=10, field_any=[], field_str='123 321',
               ),
           ]

    check_schema(meta.with_partition('2019-10-11').target_path(), meta)


@pytest.mark.slow
def test_dttm_sorted_by_dttm_within_a_day(test_table_05):
    meta = YTMeta(test_table_05)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dttm='2019-10-10 02:02:02', order_int=90, field_dt='2021-01-21',
                field_str='', field_any=None, field_uint=180,
            ),
            dict(
                partition_dttm='2019-10-10 02:02:02', order_int=100, field_dt='1985-08-01',
                field_str='XXX', field_any=True, field_uint=999999,
            ),
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
            dict(
                partition_dttm='2019-10-10 12:00:00', order_int=1, field_dt='2016-01-01',
                field_str=None, field_any={'a': [{'k': [1, 2, 3], 'm': 15}]}, field_uint=10000000000000,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=12, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
            dict(
                partition_dttm='2019-10-10 03:50:01', order_int=5, field_dt=None,
                field_str='', field_any='', field_uint=None,
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10 03:00:00', '2019-10-10 03:59:59')
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(
        meta.with_partition('2019-10-10').target_path()
    ))) == [
               dict(
                   partition_dttm='2019-10-10 02:02:02', order_int=90, field_dt='2021-01-21',
                   field_str='', field_any=None, field_uint=180,
               ),
               dict(
                   partition_dttm='2019-10-10 02:02:02', order_int=100, field_dt='1985-08-01',
                   field_str='XXX', field_any=True, field_uint=999999,
               ),
               dict(
                   partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                   field_str='\n\n', field_any='\n\n', field_uint=None,
               ),
               dict(
                   partition_dttm='2019-10-10 03:03:03', order_int=12, field_dt=None,
                   field_str='\n\n', field_any='\n\n', field_uint=None,
               ),
               dict(
                   partition_dttm='2019-10-10 03:50:01', order_int=5, field_dt=None,
                   field_str='', field_any='', field_uint=None,
               ),
               dict(
                   partition_dttm='2019-10-10 12:00:00', order_int=1, field_dt='2016-01-01',
                   field_str=None, field_any={'a': [{'k': [1, 2, 3], 'm': 15}]}, field_uint=10000000000000,
               ),
           ]

    assert get_yt_client().get_attribute(
        meta.with_partition('2019-10-10').target_path(), 'schema'
    ).attributes['unique_keys']

    assert get_yt_client().get_attribute(
        meta.with_partition('2019-10-10').target_path(), 'compression_codec'
    ) == COMPRESSION_ATTRIBUTES['lightest']['compression_codec']

    assert get_yt_client().get_attribute(
        meta.with_partition('2019-10-10').target_path(), 'erasure_codec'
    ) == COMPRESSION_ATTRIBUTES['lightest']['erasure_codec']


@pytest.mark.slow
def test_dt_single_partition(test_table_06):
    meta = YTMeta(test_table_06)

    op.init_yt_table(
        meta.target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.target_path(),
        [
            dict(
                partition_dt='2019-10-10', order_int=10, field_str='aaa',
            ),
            dict(
                partition_dt='2019-10-01', order_int=15, field_str='october',
            ),
            dict(
                partition_dt='2019-10-10', order_int=20, field_str='aaaaaaa',
            ),
            dict(
                partition_dt='2019-05-10', order_int=30, field_str='MMM',
            ),
            dict(
                partition_dt='2019-12-01', order_int=31, field_str=None,
            ),
            dict(
                partition_dt='2021-12-31', order_int=32, field_str=None,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2019-10-05', order_int=6, field_str='aaaa',
            ),
            dict(
                partition_dt='2019-10-10', order_int=33, field_str='bbbb',
            ),
        ]
    )

    with pytest.raises(DWHError, match='Data has the row'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-01-01', '2019-03-31'),
            by_field='partition_dt',
        )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-04', '2019-10-10'),
        by_field='partition_dt',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.target_path()))) == [
        dict(
            partition_dt='2019-10-05', order_int=6, field_str='aaaa',
        ),
        dict(
            partition_dt='2019-10-01', order_int=15, field_str='october',
        ),
        dict(
            partition_dt='2019-05-10', order_int=30, field_str='MMM',
        ),
        dict(
            partition_dt='2019-12-01', order_int=31, field_str=None,
        ),
        dict(
            partition_dt='2021-12-31', order_int=32, field_str=None,
        ),
        dict(
            partition_dt='2019-10-10', order_int=33, field_str='bbbb',
        ),
    ]

    assert get_yt_client().get_attribute(
        meta.target_path(), 'compression_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['compression_codec']

    assert get_yt_client().get_attribute(
        meta.target_path(), 'erasure_codec'
    ) == COMPRESSION_ATTRIBUTES['heaviest']['erasure_codec']


@pytest.mark.slow
def test_dttm_single_partition(test_table_07):
    meta = YTMeta(test_table_07)

    op.init_yt_table(
        meta.target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.target_path(),
        [
            dict(
                partition_dttm='2021-03-10 04:50:01', order_int=-100, field_str='',
            ),
            dict(
                partition_dttm='2021-03-13 19:22:26', order_int=100, field_str='FFF',
            ),
            dict(
                partition_dttm='2021-03-14 23:00:01', order_int=200, field_str='0',
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2021-03-14 11:08:40', order_int=50, field_str='',
            ),
            dict(
                partition_dttm='2021-03-14 11:08:40', order_int=201, field_str=None,
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2021-03-14 00:00:00', '2021-03-14 23:59:59'),
        by_field='partition_dttm',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.target_path()))) == [
        dict(
            partition_dttm='2021-03-10 04:50:01', order_int=-100, field_str='',
        ),
        dict(
            partition_dttm='2021-03-14 11:08:40', order_int=50, field_str='',
        ),
        dict(
            partition_dttm='2021-03-13 19:22:26', order_int=100, field_str='FFF',
        ),
        dict(
            partition_dttm='2021-03-14 11:08:40', order_int=201, field_str=None,
        ),
    ]

    check_schema(meta.target_path(), meta)


@pytest.mark.slow
def test_micro_single_partition(test_table_08):
    meta = YTMeta(test_table_08)

    op.init_yt_table(
        meta.target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.target_path(),
        [
            dict(
                partition_dttm_micro='2021-05-01 04:50:01.997808', order_int=0, field_str='',
            ),
            dict(
                partition_dttm_micro='2021-05-01 19:22:26.891234', order_int=1, field_str='FFF',
            ),
            dict(
                partition_dttm_micro='2021-05-02 23:00:01.000000', order_int=4, field_str='0',
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm_micro='2021-05-01 06:10:00.123431', order_int=3, field_str='ЙЦУКЕН',
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2021-05-01 00:00:00.000000', '2021-05-01 06:59:59.999999'),
        by_field='partition_dttm_micro',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.target_path()))) == [
        dict(
            partition_dttm_micro='2021-05-01 19:22:26.891234', order_int=1, field_str='FFF',
        ),
        dict(
            partition_dttm_micro='2021-05-01 06:10:00.123431', order_int=3, field_str='ЙЦУКЕН',
        ),
        dict(
            partition_dttm_micro='2021-05-02 23:00:01.000000', order_int=4, field_str='0',
        ),
    ]

    check_schema(meta.target_path(), meta)

@pytest.mark.slow
def test_dyntable_single_partition(test_table_09):
    meta = YTMeta(test_table_09)

    op.init_yt_table(
        meta.target_path(),
        meta.attributes(),
        replace=True,
    )

    dynamic_table_loaders.upload(
        data=[
            dict(
                partition_dttm='2021-05-01 04:50:01', order_int=0, field_str='',
            ),
            dict(
                partition_dttm='2021-05-01 19:22:26', order_int=1, field_str='FFF',
            ),
            dict(
                partition_dttm='2021-05-02 23:00:01', order_int=4, field_str='0',
            ),
        ],
        yt_table_or_meta=meta,
        extractors={},
    )
    dyntable_op.unmount_all_partitions(meta)
    dyntable_op.mount_all_partitions(meta)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2021-05-01 06:10:00.123431', order_int=3, field_str=None,
            ),
        ]
    )

    with pytest.raises(NotImplementedError, match='Dynamic tables are not supported in replace_by_period'):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2021-05-01 00:00:00', '2021-05-01 06:59:59'),
            by_field='partition_dttm',
        )


@pytest.mark.slow
def test_duplicate_keys(test_table_05):
    meta = YTMeta(test_table_05)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dttm='2019-10-10 02:02:02', order_int=90, field_dt='2021-01-21',
                field_str='', field_any=None, field_uint=180,
            ),
            dict(
                partition_dttm='2019-10-10 02:02:02', order_int=91, field_dt='1985-08-01',
                field_str='XXX', field_any=True, field_uint=999999,
            ),
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
            dict(
                partition_dttm='2019-10-10 12:00:00', order_int=1, field_dt='2016-01-01',
                field_str=None, field_any={'a': [{'k': [1, 2, 3], 'm': 15}]}, field_uint=10000000000000,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
            dict(
                partition_dttm='2019-10-10 03:03:03', order_int=11, field_dt=None,
                field_str='\n\n', field_any='\n\n', field_uint=None,
            ),
        ]
    )

    with pytest.raises(RuntimeError):
        load_period_from_buffer(
            meta,
            period=dtu.Period('2019-10-10 03:00:00', '2019-10-10 03:59:59')
        )


@pytest.mark.slow
def test_complex_types_nonunique_stringlists(test_table_10):
    meta = YTMeta(test_table_10)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=10,
                field_list_string_1=['a1', 'b1'],
                field_list_string_2=[],
                field_list_string_3=[],
                field_list_string_4=None,
                field_any=None,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=3,
                field_list_string_1=['a3', 'b3', 'c3'],
                field_list_string_2=[None, 'bb3'],
                field_list_string_3=['aaa3'],
                field_list_string_4=None,
                field_any=None,
            ),
            dict(
                partition_dt='2019-10-10',
                order_int=4,
                field_list_string_1=[],
                field_list_string_2=['aa4', 'bb4'],
                field_list_string_3=None,
                field_list_string_4=[None, 'bbbb4'],
                field_any='aaa',
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10', '2019-10-10'),
        by_field='partition_dt',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.with_partition('2019-10-10').target_path()))) == [
        dict(
            partition_dt='2019-10-10',
            order_int=3,
            field_list_string_1=['a3', 'b3', 'c3'],
            field_list_string_2=[None, 'bb3'],
            field_list_string_3=['aaa3'],
            field_list_string_4=None,
            field_any=None,
        ),
        dict(
            partition_dt='2019-10-10',
            order_int=4,
            field_list_string_1=[],
            field_list_string_2=['aa4', 'bb4'],
            field_list_string_3=None,
            field_list_string_4=[None, 'bbbb4'],
            field_any='aaa',
        ),
    ]

    check_schema(meta.with_partition('2019-10-10').target_path(), meta)


@pytest.mark.slow
def test_complex_types_unique_dicts(test_table_11):
    meta = YTMeta(test_table_11)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=10,
                field_dict_1=[['a', 1]],
                field_dict_2=[['a', 1.1]],
                field_list_string_4=None,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=3,
                field_dict_1=[['a3', 1]],
                field_dict_2=None,
                field_list_string_4=None,
            ),
            dict(
                partition_dt='2019-10-10',
                order_int=4,
                field_dict_1=[['a4', 1]],
                field_dict_2=[['aa4', 2.2]],
                field_list_string_4=[None, 'bbbb4'],
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10', '2019-10-11'),
        by_field='partition_dt',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.with_partition('2019-10-10').target_path()))) == [
        dict(
            partition_dt='2019-10-10',
            order_int=3,
            field_dict_1=[['a3', 1]],
            field_dict_2=None,
            field_list_string_4=None,
        ),
        dict(
            partition_dt='2019-10-10',
            order_int=4,
            field_dict_1=[['a4', 1]],
            field_dict_2=[['aa4', 2.2]],
            field_list_string_4=[None, 'bbbb4'],
        ),
    ]

    check_schema(meta.with_partition('2019-10-10').target_path(), meta)
    check_schema(meta.with_partition('2019-10-11').target_path(), meta)


@pytest.mark.slow
def test_empty_tables(test_table_12):
    meta = YTMeta(test_table_12)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10', '2019-10-11'),
        by_field='partition_dt',
    )

    check_schema(meta.with_partition('2019-10-10').target_path(), meta)
    check_schema(meta.with_partition('2019-10-11').target_path(), meta)


@pytest.mark.slow
def test_complex_types_unusual(test_table_13):
    meta = YTMeta(test_table_13)

    op.init_yt_table(
        meta.with_partition('2019-10-10').target_path(),
        meta.attributes(),
        replace=True,
    )
    get_yt_client().write_table(
        meta.with_partition('2019-10-10').target_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=10,
            ),
        ]
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2019-10-10',
                order_int=3,
                field_nested_list=[[None, 's'], ['aa', 'bb', 'cc']],
                field_dict_1=[['aaa', 111]],
                field_dict_2=[['Ключ1', ['Элемент1', 'Элемент2']]],
                field_tuple=['str', False, -3.0, None],
                field_struct={'id': 'ididid', 'values': ['values1', 'values2']},
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2019-10-10', '2019-10-10'),
        by_field='partition_dt',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.with_partition('2019-10-10').target_path()))) == [
        dict(
            partition_dt='2019-10-10',
            order_int=3,
            field_nested_list=[[None, 's'], ['aa', 'bb', 'cc']],
            field_dict_1=[['aaa', 111]],
            field_dict_2=[['Ключ1', ['Элемент1', 'Элемент2']]],
            field_tuple=['str', False, -3.0, None],
            field_struct={'id': 'ididid', 'values': ['values1', 'values2']},
        ),
    ]

    check_schema(meta.with_partition('2019-10-10').target_path(), meta)


@pytest.mark.slow
def test_single_partition_absent_target(test_table_07):
    meta = YTMeta(test_table_07)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dttm='2021-03-14 11:08:40', order_int=50, field_str='',
            ),
            dict(
                partition_dttm='2021-03-14 19:22:26', order_int=100, field_str='FFF',
            ),
            dict(
                partition_dttm='2021-03-14 11:08:40', order_int=201, field_str=None,
            ),
        ]
    )

    load_period_from_buffer(
        meta,
        period=dtu.Period('2021-03-14 00:00:00', '2021-03-14 23:59:59'),
        by_field='partition_dttm',
    )

    assert _drop_etl_updated(list(get_yt_client().read_table(meta.target_path()))) == [
        dict(
            partition_dttm='2021-03-14 11:08:40', order_int=50, field_str='',
        ),
        dict(
            partition_dttm='2021-03-14 19:22:26', order_int=100, field_str='FFF',
        ),
        dict(
            partition_dttm='2021-03-14 11:08:40', order_int=201, field_str=None,
        ),
    ]

    check_schema(meta.target_path(), meta)


@pytest.mark.slow
def test_multi_partition_absent_target(test_table_02):
    params = [
        ('2021-08-11', []),
        ('2021-08-12', [
            dict(
                partition_dt='2021-08-12', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-12', order_uint=14, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]),
        ('2021-08-13', [
            dict(
                partition_dt='2021-08-13', order_uint=16, field_double=1234.99,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]),
        ('2021-08-14', [
            dict(
                partition_dt='2021-08-14', order_uint=17, field_double=888.0,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]),
        ('2021-08-15', [
            dict(
                partition_dt='2021-08-15', order_uint=15, field_double=None,
                field_dttm_micro=None,
            ),
        ]),
        ('2021-08-16', [
            dict(
                partition_dt='2021-08-16', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]),
        ('2021-08-17', []),
        ('2021-08-18', []),
        ('2021-08-19', []),
        ('2021-08-20', [
            dict(
                partition_dt='2021-08-20', order_uint=4, field_double=-5.5,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]),
        ('2021-08-21', []),
        ('2021-08-22', []),
    ]

    meta = YTMeta(test_table_02)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        [
            dict(
                partition_dt='2021-08-12', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-12', order_uint=14, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-13', order_uint=16, field_double=1234.99,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-14', order_uint=17, field_double=888.0,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-15', order_uint=15, field_double=None,
                field_dttm_micro=None,
            ),
            dict(
                partition_dt='2021-08-16', order_uint=4, field_double=None,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
            dict(
                partition_dt='2021-08-20', order_uint=4, field_double=-5.5,
                field_dttm_micro='2014-05-01 00:00:00.00000',
            ),
        ]
    )
    load_period_from_buffer(
        meta,
        period=dtu.Period('2021-08-11', '2021-08-22')
    )

    for partition, expected in params:
        actual = _drop_etl_updated(list(get_yt_client().read_table(
            meta.with_partition(partition).target_path()
        )))
        assert actual == expected
