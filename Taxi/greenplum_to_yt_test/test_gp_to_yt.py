import argparse
import datetime
import json
from contextlib import contextmanager
from decimal import Decimal

import pytest
from mock import Mock, patch
from psycopg2.extras import RealDictCursor

from connection import ctl, greenplum as gp
from connection.yt import get_yt_client
from dmp_suite import datetime_utils as dtu, yt
from dmp_suite.ctl import CTL_LAST_LOAD_DATE_MICROSECONDS
from dmp_suite.ctl.storage import DictStorage
from dmp_suite.export.greenplum_to_yt.greenplum_to_yt import (
    GpToYtTsvMode, _copy_data_to_stg_table, copy_gp_to_yt, get_partitions_by_data
)
from dmp_suite.export.greenplum_to_yt.tasks import GpToYtDynamicIncrementTask
from dmp_suite.greenplum import GPMeta
from dmp_suite.task.execution import _expand_value_accessors
from dmp_suite.yt import etl
from dmp_suite.yt.dyntable_operation.operations import insert_chunk_in_dynamic_table, unmount_table
from .tables import (GPCommonTest, GPCommonTestPartTest, YTCommonDynamicPartTest, YTCommonDynamicTest, YTCommonTest)

gptransfer_params = {'seconds_to_sleep': 3, 'timeout': 60 * 5}

table_empty_values = dict(col_json=None, col_point=None, col_array_int=None, col_array_str=None, col_array_dt=None,
                          col_array_dttm=None, col_array_bool=None, col_uuid=None, col_smallint=None, col_double=None)


@contextmanager
def _prepare_gp_table(cls, data):
    gp_meta = GPMeta(cls)
    with gp.connection.transaction():
        gp.connection.create_table(gp_meta)
        gp.connection.insert(cls, data)
    yield gp_meta


@pytest.mark.slow('gp')
def test_get_partitions_by_data():
    def get_row(col_dttm):
        return dict(col_int=5, col_boolean=True, col_bigint=1, col_numeric=1, col_varchar="str", col_text="text",
                    col_dt='2020-02-02', col_dttm=col_dttm, **table_empty_values)

    test_data = [get_row('2020-02-02 00:00:00'), get_row('2020-02-28 00:00:00'), get_row('2020-03-28 00:00:00'),
                 get_row('2021-02-02 00:00:00'), get_row('2020-12-28 00:00:00')]

    expected = ['2020-02-01', '2020-03-01', '2020-12-01', '2021-02-01']

    with _prepare_gp_table(GPCommonTest, test_data) as gp_meta:
        actual = get_partitions_by_data(gp_meta)
    assert actual == expected


@pytest.mark.slow('gp')
@pytest.mark.parametrize('period', (
    dtu.date_period('2020-02-01 00:00:00', '2020-02-02'),
    None,
))
def test_copy_filtered_data(period):

    test_data = [
        dict(col_int=5, col_boolean=True, col_bigint=2147483649, col_numeric=Decimal('0.1'),
             col_varchar="str", col_text="text", col_dt=dtu.parse_date('2020-02-02').date(),
             col_dttm=dtu.parse_datetime('2020-01-02 02:02:59'), **table_empty_values),
        dict(col_int=10, col_boolean=True, col_bigint=-2147483649, col_numeric=Decimal(1.123),
             col_varchar="str", col_text="text", col_dt=dtu.parse_date('2020-02-02').date(),
             col_dttm=dtu.parse_datetime('2020-02-02 02:02:59'), **table_empty_values),
        dict(col_int=20, col_boolean=False, col_bigint=0, col_numeric=Decimal(0), col_varchar='', col_text='',
             col_dt=dtu.parse_date('2020-02-02').date(), col_dttm=dtu.parse_datetime('2020-03-02 02:02:59'),
             **table_empty_values),
    ]

    with _prepare_gp_table(GPCommonTest, test_data) as gp_meta:
        with _copy_data_to_stg_table(gp_meta, period, 'col_dttm', add_etl_id=False) as (stg_meta, rows_count):
            with gp.connection.transaction():
                with gp.connection.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('SELECT * FROM {} ORDER BY col_int'.format(stg_meta.table_full_name))
                    actual = [dict(r) for r in cur]
            if period:
                assert rows_count == 1
                assert actual == test_data[1:2]
            else:
                assert rows_count == 3
                assert actual == test_data

    assert not gp.connection.table_exists(stg_meta)


def direct_loader(**kw):
    copy_gp_to_yt(kw['gmeta'], kw['target_path'], kw['period'], kw['partition_key'], kw['fields'],
                  gptransfer_params=kw['gptp'])


def tsv_table_loader(**kw):
    loader = GpToYtTsvMode(kw['gmeta'], kw['target_path'], kw['fields'], kw['ymeta'], kw['period'], kw['partition_key'],
                           gptransfer_params=kw['gptp'], chunk_size=3)
    loader.run()


@pytest.mark.slow('gp')
@pytest.mark.parametrize('loader, yt_table, gp_table, period, partition_key', (
        (tsv_table_loader, YTCommonTest, GPCommonTest, None, None),
        (tsv_table_loader, YTCommonTest, GPCommonTest, dtu.period('2020-02-01 00:00:00', '2020-03-01 00:00:00'), None),
        (tsv_table_loader, YTCommonTest, GPCommonTest, dtu.period('2020-02-01', '2020-03-01'), 'col_dt'),
        (direct_loader, YTCommonTest, GPCommonTest, None, None),
        (direct_loader, YTCommonTest, GPCommonTest, dtu.period('2020-02-01 00:00:00', '2021-03-01 00:00:00'), None),
        (direct_loader, YTCommonDynamicTest, GPCommonTest, None, None),
        (direct_loader, YTCommonDynamicTest, GPCommonTest,
         dtu.period('2020-02-01 00:00:00', '2020-03-01 00:00:00'), None),
))
def test_copy_gp_to_yt_base_case(loader, yt_table, gp_table, period, partition_key):
    yt_meta = yt.YTMeta(yt_table)
    fields = [f.name for f in yt_meta.fields() if f.name != '_etl_id']
    test_data = [
        dict(col_int=5, col_boolean=True, col_smallint=123, col_bigint=2147483649, col_numeric=0.1, col_double=0.2,
             col_varchar='\ta\nbc\rd\\\"', col_text="text",
             col_dt='2020-02-02', col_dttm='2020-01-02 02:02:59', col_uuid='2e39a5fa-8590-41e3-b2b9-cbeda0585413',
             col_json={"t": "t", "l": [1, None]}, col_point={'lon': 1.123, 'lat': 2.12},
             col_array_int=[1, 2], col_array_str=['3', '4'], col_array_dt=['2020-02-02', '2020-02-02'],
             col_array_dttm=['2020-01-02 02:02:59', '2020-01-02 02:03:59'], col_array_bool=[True, False]),
        dict(col_int=10, col_boolean=True, col_smallint=-12, col_bigint=-2147483649, col_numeric=1.123, col_double=1.0,
             col_varchar='\ta\nbc\rd\\\"', col_text="text", col_dt='2020-01-02', col_dttm='2020-02-02 02:02:59',
             col_uuid=None, col_json={}, col_point=None, col_array_int=[], col_array_str=[], col_array_dt=[],
             col_array_dttm=[], col_array_bool=[]),
        dict(col_int=20, col_boolean=False, col_smallint=-12, col_bigint=0, col_numeric=0.0, col_double=0.0,
             col_varchar='\ta\nbc\rd\\\"', col_text='',
             col_dt='2020-02-29', col_dttm='2020-03-02 02:02:59',
             col_uuid=None, col_json=None, col_point=None, col_array_int=None, col_array_str=None, col_array_dt=None,
             col_array_dttm=None, col_array_bool=None),
        dict(col_int=30, col_boolean=None, col_smallint=None, col_bigint=None, col_numeric=None, col_double=None,
             col_varchar='\ta\nbc\rd\\\"', col_text=None, col_dt='2020-03-05', col_dttm='2020-03-05 02:02:59',
             col_uuid=None, col_json=None, col_point=None, col_array_int=None, col_array_str=None, col_array_dt=None,
             col_array_dttm=None, col_array_bool=None),
    ]

    etl.init_target_table(yt_meta)
    gp_prepared_data = []
    for row in test_data:
        prep_row = dict(row)
        prep_row['col_array_dt'] = None if row['col_array_dt'] is None else list(map(dtu.parse_date,
                                                                                     row['col_array_dt']))
        prep_row['col_array_dttm'] = None if row['col_array_dttm'] is None else list(map(dtu.parse_datetime,
                                                                                         row['col_array_dttm']))
        prep_row['col_json'] = None if row['col_json'] is None else json.dumps(row['col_json'])
        prep_row['col_point'] = '({lon},{lat})'.format(**prep_row['col_point']) if prep_row['col_point'] else None
        gp_prepared_data.append(prep_row)

    with _prepare_gp_table(gp_table, gp_prepared_data) as gp_meta:
        loader(gmeta=gp_meta, target_path=yt_meta.target_path(), period=period, fields=fields, ymeta=yt_meta,
               gptp=gptransfer_params, partition_key=partition_key)

        if yt_meta.is_dynamic:
            get_yt_client().freeze_table(yt_meta.target_path(), sync=True)  # дождемся записи измений в таблицу

        actual = list(get_yt_client().read_table(yt_meta.target_path()))
        actual.sort(key=lambda i: i['col_int'])

        expected = test_data

        if loader is tsv_table_loader:
            # todo сейчас отличается поведение: табличный сериализатор в etl преобразует None -> False в булевых полях,
            # а gptransfer этого не делает
            expected[-1]['col_boolean'] = False

        if period:
            st, end = dtu.format_datetime(period.start), dtu.format_datetime(period.end)
            expected = list(filter(lambda r: st < r[partition_key or 'col_dttm'] < end, test_data))

        assert actual == expected


def ctl_getter(obj):
    return obj

# внутри тестируемого GpToYtDynamicIncrementTask используется пул процессов
# при создании нового подпроцесса были проблемы с pickling объектов MagicMock/Mock
# переопределение метода используеися как замена mock.patch
class GpToYtDynamicIncrementTaskHelper(GpToYtDynamicIncrementTask):
    def _select_max(self, meta):
        return datetime.datetime(2020, 3, 5, 2, 2, 1)


class PickableMock(Mock):
    def __reduce__(self):
        return (Mock, ())


@pytest.mark.slow('gp')
@pytest.mark.parametrize('period', [
    None,
    dtu.period('2020-02-01 00:00:00', '2020-03-05 02:02:58')
])
def test_increment_loader_base_case(period):
    yt_meta = yt.YTMeta(YTCommonDynamicPartTest, partition='2020-02-01')
    gp_table = GPCommonTestPartTest
    yt_data = [
        dict(col_int=5, col_boolean=True, col_bigint=2147483649, col_numeric=0.1, col_varchar="str", col_text="text",
             col_dt='2020-02-02', col_dttm='2020-02-02 02:02:59', **table_empty_values),  # сохраняется
        dict(col_int=10, col_boolean=False, col_bigint=1, col_numeric=0.0, col_varchar="str", col_text="text",
             col_dt='2020-02-02', col_dttm='2020-02-02 02:02:59', **table_empty_values),
    ]

    gp_data = [
        dict(col_int=1, col_boolean=True, col_bigint=2147483649, col_numeric=0.1, col_varchar="str", col_text="text",
             col_dt='2020-01-02', col_dttm='2020-01-01 02:02:59', **table_empty_values),  # не обновляется вне ctl
        dict(col_int=10, col_boolean=True, col_bigint=-2147483649, col_numeric=1.123, col_varchar="\ta'b\"cd\\",
             col_text="text", col_dt='2020-02-02', col_dttm='2020-02-02 02:02:59', **table_empty_values),  # обновляет
        dict(col_int=20, col_boolean=False, col_bigint=0, col_numeric=0.0, col_varchar='', col_text='',
             col_dt='2020-03-02', col_dttm='2020-03-02 02:02:59', **table_empty_values),  # добавляет + значение для ctl
        dict(col_int=30, col_boolean=None, col_bigint=None, col_numeric=None, col_varchar=None, col_text=None,
             col_dt='2020-03-05', col_dttm='2020-03-05 02:02:59', **table_empty_values),  # не попадает в период
    ]
    expected = {
        '2020-02-01': [
            dict(col_int=5, col_boolean=True, col_bigint=2147483649, col_numeric=0.1, col_varchar="str",
                 col_text="text",  # сохраняет
                 col_dt='2020-02-02', col_dttm='2020-02-02 02:02:59', **table_empty_values),
            dict(col_int=10, col_boolean=True, col_bigint=-2147483649, col_numeric=1.123, col_varchar="\ta'b\"cd\\",
                 col_text="text", col_dt='2020-02-02', col_dttm='2020-02-02 02:02:59',
                 **table_empty_values),  # обновляет
        ],
        '2020-03-01': [
            dict(col_int=20, col_boolean=False, col_bigint=0, col_numeric=0.0, col_varchar='', col_text='',
                 col_dt='2020-03-02', col_dttm='2020-03-02 02:02:59',
                 **table_empty_values),  # добавляет + значение для ctl
        ],
    }

    client = get_yt_client()
    insert_chunk_in_dynamic_table(yt_meta, yt_data, yt_client=client)

    with patch('connection.ctl.get_ctl', return_value=ctl.WrapCtl(DictStorage())), \
         _prepare_gp_table(gp_table, gp_data) as gp_meta:

        ctl.get_ctl().yt.set_param(
            yt_meta.table, CTL_LAST_LOAD_DATE_MICROSECONDS, datetime.datetime(2020, 2, 1, second=0))

        task = GpToYtDynamicIncrementTaskHelper(
            'name', gp_meta.table, yt_meta.table,
            updated_field='col_dttm',
        )

        if period:
            args = argparse.Namespace(period=period)
        else:
            args = argparse.Namespace()
            task._arguments['period'].post_parse(name='period', args=args)

        # частично эмулируем деятельность runner-а
        _expand_value_accessors(args)
        args = list(task.split_args(args))[0]
        task._run_task(args)

        new_ctl = ctl.get_ctl().yt.get_param(yt_meta.table, CTL_LAST_LOAD_DATE_MICROSECONDS)
        assert new_ctl == datetime.datetime(2020, 3, 5, 2, 2, 1)

        actual = {}
        for partition in ('2020-02-01', '2020-03-01'):
            yt_meta = yt_meta.with_partition(partition)
            path = yt_meta.target_path()
            unmount_table(path, sync=True)
            actual[partition] = list(client.read_table(path))
            actual[partition].sort(key=lambda i: i['col_int'])

        assert actual == expected
