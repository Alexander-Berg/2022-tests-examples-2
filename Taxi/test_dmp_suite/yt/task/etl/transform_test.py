from datetime import timedelta, date
from decimal import Decimal as py_Decimal, ROUND_HALF_EVEN

import pytest
from mock import patch, MagicMock
from nile.api.v1 import with_hints
from pyspark.sql.types import DecimalType
from qb2.api.v1 import typing as qb2_typing
from qb2.utils.record import Record

from connection.ctl import get_ctl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE, CTL_LAST_SYNC_DATE
from dmp_suite.datetime_utils import Period, format_date
from dmp_suite.datetime_utils import utcnow
from dmp_suite.nile import NileBackend
from dmp_suite.task.execution import run_task
from dmp_suite.task.source import T_Source
from dmp_suite.yt import (
    table as yt,
    String,
    operation as op,
    YTMeta,
    ETLTable,
    Datetime,
    Date,
    DayPartitionScale, resolve_meta,
)
from dmp_suite.yt.task.etl import transform
from dmp_suite.yt.task.etl.external_transform import external_source
from dmp_suite.yt.task.etl.nile_transform import nile_source, nile_config
from dmp_suite.yt.task.etl.spark_transform import spark_source
from dmp_suite.yt.task.etl.transform import NamedStreamSourceAccessor
from dmp_suite.yt.task.processing import use_yt_complex_types
from test_dmp_suite.yt import utils

# Yt buffer table has expiration_time `utcnow() + 7 days`
# Therefore we can't use fixed time in the past for those tests
# We'll fix one value on launch and then use it

UTC_NOW = utcnow().replace(microsecond=0)
utc_now_mock = patch('dmp_suite.datetime_utils.utcnow', MagicMock(return_value=UTC_NOW))


class Table(ETLTable):
    __unique_keys__ = True

    id = String(sort_key=True, sort_position=0)
    name = String()


table = utils.fixture_random_yt_table(Table)


def read_actual_data(yt_table, partition=None):
    data = list(op.read_yt_table(YTMeta(yt_table, partition).target_path()))
    for d in data:
        d.pop('etl_updated')
    return data


@pytest.mark.slow
@utc_now_mock
def test_replace_by_snapshot(table):

    ctl = get_ctl().yt
    ctl.set_param(table, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(table, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    data = [dict(id='a', name='b'), dict(id='b', name='a')]
    task = transform.replace_by_snapshot('test1', external_source(data), table)
    run_task(task)
    assert data == read_actual_data(table)

    assert ctl.get_param(table, CTL_LAST_LOAD_DATE) == UTC_NOW + timedelta(days=-3)
    assert ctl.get_param(table, CTL_LAST_SYNC_DATE) == UTC_NOW

    def func(args, env):
        for d in data:
            yield d

    task = transform.replace_by_snapshot('test2', external_source(func), table)
    run_task(task)
    assert data == read_actual_data(table)


@pytest.mark.slow
@utc_now_mock
def test_append_to_target(table):

    ctl = get_ctl().yt
    ctl.set_param(table, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(table, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    data_1 = [dict(id='a', name='b'), dict(id='b', name='a')]
    task = transform.append_to_target('test1', external_source(data_1), table)
    run_task(task)

    assert ctl.get_param(table, CTL_LAST_LOAD_DATE) == UTC_NOW + timedelta(days=-3)
    assert ctl.get_param(table, CTL_LAST_SYNC_DATE) == UTC_NOW

    data_2 = [dict(id='a', name='b'), dict(id='b', name='a')]
    task = transform.append_to_target('test2', external_source(data_2), table)
    run_task(task)
    expected = data_1 + data_2
    assert expected == read_actual_data(table)


class PartitionedTable(ETLTable):
    __unique_keys__ = True
    __partition_scale__ = DayPartitionScale('dttm')

    id = String(sort_key=True, sort_position=0)
    dttm = Datetime()
    name = String()


partitioned_table = utils.fixture_random_yt_table(PartitionedTable)


@pytest.mark.slow
@utc_now_mock
def test_append_to_target_partitioning(partitioned_table):

    ctl = get_ctl().yt
    ctl.set_param(partitioned_table, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(partitioned_table, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    data_1 = [dict(id='a', name='b', dttm='2020-01-01 00:00:00'), dict(id='b', name='a', dttm='2020-01-01 00:00:00')]
    task = transform.append_to_target('test1', external_source(data_1), partitioned_table, partition='2020-01-01')
    run_task(task)

    assert ctl.get_param(partitioned_table, CTL_LAST_LOAD_DATE) == UTC_NOW + timedelta(days=-3)
    assert ctl.get_param(partitioned_table, CTL_LAST_SYNC_DATE) == UTC_NOW

    data_2 = [dict(id='a', name='b', dttm='2020-01-01 00:00:00'), dict(id='b', name='a', dttm='2020-01-01 00:00:00')]
    task = transform.append_to_target('test2', external_source(data_2), partitioned_table, partition='2020-01-01')
    run_task(task)
    data_3 = [dict(id='b', name='c', dttm='2020-01-02 00:00:00'), dict(id='c', name='d', dttm='2020-01-02 00:00:00')]
    task = transform.append_to_target('test3', external_source(data_3), partitioned_table, partition='2020-01-02')
    run_task(task)
    expected = data_1 + data_2
    assert expected == read_actual_data(partitioned_table, partition='2020-01-01')
    assert data_3 == read_actual_data(partitioned_table, partition='2020-01-02')


@pytest.mark.slow
@utc_now_mock
def test_replace_by_key(table):

    ctl = get_ctl().yt
    ctl.set_param(table, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(table, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    data = [dict(id='a', name='a1'), dict(id='b', name='b1')]
    task = transform.replace_by_key(
        'test1',
        external_source(data),
        table,
        partition_period=None
    )

    run_task(task)

    assert data == read_actual_data(table)

    assert ctl.get_param(table, CTL_LAST_LOAD_DATE) == UTC_NOW + timedelta(days=-3)
    assert ctl.get_param(table, CTL_LAST_SYNC_DATE) == UTC_NOW

    data = [dict(id='a', name='a2'), dict(id='c', name='c1')]
    task = transform.replace_by_key(
        'test2',
        external_source(data),
        table,
        partition_period=None
    )

    run_task(task)
    expected = [
        dict(id='a', name='a2'),
        dict(id='b', name='b1'),
        dict(id='c', name='c1'),
    ]
    assert expected == read_actual_data(table)


@pytest.mark.slow
@utc_now_mock
def test_replace_by_period(partitioned_table):

    ctl = get_ctl().yt
    ctl.set_param(partitioned_table, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(partitioned_table, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    data = [
        dict(id='a', dttm='2010-10-10 10:00:00', name='a1'),
        dict(id='b', dttm='2010-10-10 10:00:10', name='b1'),
    ]
    task = transform.replace_by_period(
        'test1',
        external_source(data),
        partitioned_table,
        period=Period('2010-10-10 10:00:00', '2010-10-10 10:00:10'),
    )
    run_task(task)
    assert data == read_actual_data(partitioned_table, '2010-10-10')

    assert ctl.get_param(partitioned_table, CTL_LAST_LOAD_DATE) == UTC_NOW + timedelta(days=-3)
    assert ctl.get_param(partitioned_table, CTL_LAST_SYNC_DATE) == UTC_NOW

    data = [
        dict(id='b', dttm='2010-10-10 10:00:10', name='b2'),
        dict(id='c', dttm='2010-10-10 10:00:20', name='c1'),
    ]
    task = transform.replace_by_period(
        'test2',
        external_source(data),
        partitioned_table,
        period=Period('2010-10-10 10:00:10', '2010-10-10 10:00:20'),
    )
    run_task(task)
    expected = [
        dict(id='a', dttm='2010-10-10 10:00:00', name='a1'),
        dict(id='b', dttm='2010-10-10 10:00:10', name='b2'),
        dict(id='c', dttm='2010-10-10 10:00:20', name='c1'),
    ]
    assert expected == read_actual_data(partitioned_table, '2010-10-10')


class PeriodicSnapshotTable(ETLTable):
    __unique_keys__ = True

    business_dt = Date(sort_key=True, sort_position=0)
    id = String(sort_key=True, sort_position=1)
    name = String()


snapshot_table = utils.fixture_random_yt_table(PeriodicSnapshotTable)


@pytest.mark.slow
@utc_now_mock
def test_replace_by_periodic_snapshot(snapshot_table):

    data = [
        dict(id='a', name='a1'),
        dict(id='b', name='b1'),
    ]
    expected = [
        dict(id='a', name='a1', business_dt='2022-03-01'),
        dict(id='b', name='b1', business_dt='2022-03-01'),
        dict(id='a', name='a1', business_dt='2022-03-02'),
        dict(id='b', name='b1', business_dt='2022-03-02'),
        dict(id='a', name='a1', business_dt='2022-03-03'),
        dict(id='b', name='b1', business_dt='2022-03-03'),
    ]

    # snapshot_date=date(2022, 3, 1)
    task = transform.periodic_snapshot(
        'test1_1',
        external_source(data),
        snapshot_table,
        snapshot_date_field='business_dt',
        snapshot_date=date(2022, 3, 1)
    )
    run_task(task)

    # snapshot_date=date(2022, 3, 2)
    task = transform.periodic_snapshot(
        'test1_2',
        external_source(data),
        snapshot_table,
        snapshot_date_field='business_dt',
        snapshot_date=date(2022, 3, 2)
    )
    run_task(task)

    # snapshot_date=date(2022, 3, 3)
    task = transform.periodic_snapshot(
        'test1_3',
        external_source(data),
        snapshot_table,
        snapshot_date_field='business_dt',
        snapshot_date=date(2022, 3, 3)
    )
    run_task(task)

    assert expected == read_actual_data(snapshot_table)

    data = [
        dict(id='c', name='c1'),
    ]
    expected = [
        dict(id='a', name='a1', business_dt='2022-03-01'),
        dict(id='b', name='b1', business_dt='2022-03-01'),
        dict(id='c', name='c1', business_dt='2022-03-02'),
        dict(id='a', name='a1', business_dt='2022-03-03'),
        dict(id='b', name='b1', business_dt='2022-03-03'),
    ]

    task = transform.periodic_snapshot(
        'test2',
        external_source(data),
        snapshot_table,
        snapshot_date_field='business_dt',
        snapshot_date=date(2022, 3, 2)
    )
    run_task(task)

    assert expected == read_actual_data(snapshot_table)

    data = [
        dict(id='b', name='b2'),
        dict(id='c', name='c1'),
    ]
    expected = [
        dict(id='a', name='a1', business_dt='2022-03-01'),
        dict(id='b', name='b1', business_dt='2022-03-01'),
        dict(id='c', name='c1', business_dt='2022-03-02'),
        dict(id='a', name='a1', business_dt='2022-03-03'),
        dict(id='b', name='b1', business_dt='2022-03-03'),
        dict(id='b', name='b2', business_dt=format_date(UTC_NOW)),
        dict(id='c', name='c1', business_dt=format_date(UTC_NOW)),
    ]
    task = transform.periodic_snapshot(
        'test3',
        external_source(data),
        snapshot_table,
        snapshot_date_field='business_dt'
    )
    run_task(task)
    assert expected == read_actual_data(snapshot_table)


class MockStreamAccessor(NamedStreamSourceAccessor):
    def get_value(self, args, env) -> T_Source:
        pass


def test_named_stream_source_accessor_func_validation():
    # это нормально, функция может теоретически и из "воздуха" вернуть данные
    def f():
        pass

    MockStreamAccessor(f, {})

    # первый аргумент будет интерпретирован, как аргумент таска
    def f(args):
        pass

    MockStreamAccessor(f, {})

    # первый аргумент будет интерпретирован, как аргументы таска
    def f(args, stream):
        pass

    MockStreamAccessor(f, dict(stream='//asd'))

    with pytest.raises(transform.TransformFuncError, match='{\'stream\'}'):
        def f(args, stream):
            pass

        MockStreamAccessor(f, {})

    with pytest.raises(transform.TransformFuncError, match='{\'stream\'}'):
        def f():
            pass

        MockStreamAccessor(f, dict(stream='//asd'))

    with pytest.raises(transform.TransformFuncError, match='{\'s2\'}'):
        def f(s1, s2, s3):
            pass

        MockStreamAccessor(f, dict(s1='//asd', s3='//asd'))

    with pytest.raises(transform.TransformFuncError, match='{\'s2\'}'):
        def f(args, s1, s2, s3):
            pass

        MockStreamAccessor(f, dict(s1='//asd', s3='//asd'))

    # s1 и s2 интерпретируются как стримы
    def f(s1, s2):
        pass

    MockStreamAccessor(f, dict(s1='//asd', s2='//asd'))

    # s1 и s2 интерпретируются как стримы, а args как аргументы таска
    def f(args, s1, s2):
        pass

    MockStreamAccessor(f, dict(s1='//asd', s2='//asd'))


def f1(args, s):
    assert args == args
    assert s == s
    f1.called = True


def f2(s):
    assert s == s
    f2.called = True


def f3():
    f3.called = True


def f4(args):
    assert args == args
    f4.called = True


@pytest.mark.parametrize(
    'func, streams',
    [
        (f1, dict(s='//path')),
        (f2, dict(s='//path')),
        (f3, {}),
        (f4, {}),
    ]
)
def test_named_stream_source_accessor_call(func, streams):
    args = object()
    func.called = False
    MockStreamAccessor(func, streams)(args, **streams)
    assert func.called


@pytest.mark.slow
@pytest.mark.parametrize(
    'data,expected',
    [
        # two rows in reversed order must be sorted in
        # date ascending order when loaded to table in
        # `replace_by_snapshot` transformation.
        (
            [
                {
                    'date': "1970-01-01T00:00:00.123654Z",
                    'datetime': "1970-01-01T00:00:00.123654Z",
                    'timestamp': "1970-01-01T00:00:00.123654Z",
                },
                {
                    'date': "1970-01-01T00:00:00.000000Z",
                    'datetime': "1970-01-01T00:00:00.000000Z",
                    'timestamp': "1970-01-01T00:00:00.000000Z",
                },
            ],
            [
                {
                    'date': 0,
                    'datetime': 0,
                    'timestamp': 0,
                },
                {
                    'date': 0,
                    'datetime': 0,
                    'timestamp': 123654,
                },
            ]
        ),
        # three rows in unsorted order must be sorted in
        # date ascending order when loaded to table in
        # `replace_by_snapshot` transformation.
        (
            [
                # Third
                {
                    'date': "1970-02-01T00:00:00.000000Z",
                    'datetime': "1970-02-01T00:00:00.000000Z",
                    'timestamp': "1970-02-01T00:00:00.000000Z",
                },
                # First
                {
                    'date': "1970-01-01T00:00:00.000100Z",
                    'datetime': "1970-01-01T00:00:00.000100",
                    'timestamp': "1970-01-01T00:00:00.000100Z",
                },
                # Second
                {
                    'date': "1970-01-02T00:00:00.000000Z",
                    'datetime': "1970-01-02T00:00:00.000000Z",
                    'timestamp': "1970-01-02T00:00:00.000000Z",
                },
            ],
            [
                {
                    'date': 0,
                    'datetime': 0,
                    'timestamp': 100,
                },
                {
                    'date': 1,
                    'datetime': 86_400,
                    'timestamp': 86_400_000_000,
                },
                {
                    'date': 31,
                    'datetime': 2_678_400,
                    'timestamp': 2_678_400_000_000,
                },
            ]
        ),
    ]
)
def test_snapshot_native_dates(data, expected):
    """
    Tests `replace_by_snapshot` transformation on a
    table with YT (native) date-time fields.
    """

    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = yt.NativeDate(sort_key=True, sort_position=0)
        datetime = yt.NativeDatetime(sort_key=True, sort_position=1)
        timestamp = yt.NativeTimestamp(sort_key=True, sort_position=2)

    task_snapshot = transform.replace_by_snapshot(
        name='test_snapshot_native_dates',
        source=external_source(data),
        target_table=_TestTable,
    )
    run_task(task_snapshot)
    assert expected == read_actual_data(_TestTable)


@pytest.mark.slow
def test_replace_by_period_with_native_dates():
    """
    Tests `replace_by_period` transformation on a
    table with YT (native) date-time fields. Note
    that table is NOT partitioned by those fields.
    """

    @utils.random_yt_table
    class _TestTable(ETLTable):
        str_date = yt.Date()
        date = yt.NativeDate(sort_key=True, sort_position=0)
        datetime = yt.NativeDatetime(sort_key=True, sort_position=1)
        timestamp = yt.NativeTimestamp(sort_key=True, sort_position=2)

    task_snapshot = transform.replace_by_snapshot(
        name='test_snapshot_prep_native_dates',
        source=external_source(
            [
                {
                    'str_date': "2020-01-01",
                    'date': "1970-01-01T00:00:00.000000Z",
                    'datetime': "1970-01-01T00:00:00.000000Z",
                    'timestamp': "1970-01-01T00:00:00.000000Z",
                },
                {
                    'str_date': "2020-01-03",
                    'date': "1970-01-02T00:00:00.000000Z",
                    'datetime': "1970-01-02T00:00:00.000000Z",
                    'timestamp': "1970-01-02T00:00:00.000000Z",
                },
            ],
        ),
        target_table=_TestTable,
    )
    run_task(task_snapshot)

    task_period = transform.replace_by_period(
        name='test_replace_by_period_with_native_dates',
        source=external_source(
            [
                {
                    'str_date': "2020-01-01",
                    'date': "1970-01-01T00:00:00.000500",
                    'datetime': "1970-01-01T00:00:00.000500",
                    'timestamp': "1970-01-01T00:00:00.000500",
                },
                {
                    'str_date': "2020-01-02",
                    'date': "1970-01-01T00:00:00.001000",
                    'datetime': "1970-01-01T00:00:00.001000",
                    'timestamp': "1970-01-01T00:00:00.001000Z",
                },
            ],
        ),
        target_table=_TestTable,
        by_field='str_date',
        period=Period("2020-01-01", "2020-01-02"),
    )
    run_task(task_period)

    # Трансформация должна заменить записи, (строковые)
    # даты которых попадают в период, на новые
    _expected = [
        {
            'str_date': "2020-01-01",
            'date': 0,
            'datetime': 0,
            'timestamp': 500,
        },
        {
            'str_date': "2020-01-02",
            'date': 0,
            'datetime': 0,
            'timestamp': 1000,
        },
        {
            'str_date': "2020-01-03",
            'date': 1,
            'datetime': 86_400,
            'timestamp': 86_400_000_000,
        },
    ]
    assert _expected == read_actual_data(_TestTable)


@pytest.mark.slow
def test_replace_by_key_with_native_dates():
    """
    Tests `replace_by_key` transformation on a
    table with YT (native) date-time fields. Note
    that table is NOT partitioned by those fields.
    """

    @utils.random_yt_table
    class _TestTable(ETLTable):
        __unique_keys__ = True
        date = yt.NativeDate(sort_key=True, sort_position=0)
        datetime = yt.NativeDatetime(sort_key=True, sort_position=1)
        timestamp = yt.NativeTimestamp(sort_key=True, sort_position=2)
        int_field = yt.Int()

    task_snapshot = transform.replace_by_snapshot(
        name='test_snapshot_prep_native_dates',
        source=external_source(
            [
                {
                    'date': "1970-01-01T00:00:00.000000Z",
                    'datetime': "1970-01-01T00:00:00.000000Z",
                    'timestamp': "1970-01-01T00:00:00.000000Z",
                    'int_field': 1,
                },
                {
                    'date': "1970-01-01T00:00:00.001000",
                    'datetime': "1970-01-01T00:00:00.001000",
                    'timestamp': "1970-01-01T00:00:00.001000Z",
                    'int_field': 2,
                },
            ],
        ),
        target_table=_TestTable,
    )
    run_task(task_snapshot)

    task_key = transform.replace_by_key(
        name='test_replace_by_key_with_native_dates',
        source=external_source(
            [
                {
                    'date': "1970-01-01T00:00:00.001000",
                    'datetime': "1970-01-01T00:00:00.001000",
                    'timestamp': "1970-01-01T00:00:00.001000Z",
                    'int_field': 3,
                },
                {
                    'date': "1970-01-01T00:00:00.000500",
                    'datetime': "1970-01-01T00:00:00.000500",
                    'timestamp': "1970-01-01T00:00:00.000500",
                    'int_field': 4,
                },
            ],
        ),
        target_table=_TestTable,
    )
    run_task(task_key)

    # Трансформация должна заменить записи с
    # пересекающимися ключами, и добавить новые.
    _expected = [
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 0,
           'int_field': 1,
        },
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 500,
           'int_field': 4,
        },
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 1000,
           'int_field': 3,
        },
    ]
    assert _expected == read_actual_data(_TestTable)


@pytest.mark.slow
def test_append_to_target_with_native_dates():
    """
    Tests `append_to_target` transformation on a
    table with YT (native) date-time fields. Note
    that table is NOT partitioned by those fields.
    """

    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = yt.NativeDate(sort_key=True, sort_position=0)
        datetime = yt.NativeDatetime(sort_key=True, sort_position=1)
        timestamp = yt.NativeTimestamp(sort_key=True, sort_position=2)

    task_snapshot = transform.replace_by_snapshot(
        name='test_snapshot_prep_native_dates',
        source=external_source(
            [
                {
                    'date': "1970-01-01T00:00:00.000000Z",
                    'datetime': "1970-01-01T00:00:00.000000Z",
                    'timestamp': "1970-01-01T00:00:00.000000Z",
                },
                {
                    'date': "1970-01-01T00:00:00.001000",
                    'datetime': "1970-01-01T00:00:00.001000",
                    'timestamp': "1970-01-01T00:00:00.001000Z",
                },
            ],
        ),
        target_table=_TestTable,
    )
    run_task(task_snapshot)

    task_append = transform.append_to_target(
        name='test_append_to_target_with_native_dates',
        source=external_source(
            [
                {
                    'date': "1970-01-01T00:00:00.001000",
                    'datetime': "1970-01-01T00:00:00.001000",
                    'timestamp': "1970-01-01T00:00:00.001000Z",
                    'int_field': 3,
                },
                {
                    'date': "1970-01-01T00:00:00.000500",
                    'datetime': "1970-01-01T00:00:00.000500",
                    'timestamp': "1970-01-01T00:00:00.000500",
                    'int_field': 4,
                },
            ],
        ),
        target_table=_TestTable,
    )
    run_task(task_append)

    # Трансформация должна добавить
    # новые строки в конец таблицы.
    _expected = [
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 0,
        },
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 1000,
        },
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 1000,
        },
        {
           'date': 0,
           'datetime': 0,
           'timestamp': 500,
        },
    ]
    assert _expected == read_actual_data(_TestTable)


@pytest.mark.slow
def test_transform_complex():

    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = yt.Date()
        decimal = yt.Decimal(5, 3)
        optional = yt.Optional(yt.Int)
        list = yt.List(String)
        struct = yt.Struct({'id': yt.Int, 'name': yt.String})
        tuple = yt.Tuple((yt.Bool, yt.Bool, yt.Int))
        variant_named = yt.VariantNamed({'id': yt.Int, 'name': yt.String})
        variant_unnamed = yt.VariantUnnamed((yt.String, yt.Int))
        dict = yt.Dict(yt.Int, yt.Bool)
        tagged = yt.Tagged('DummyTag', yt.Bool)

    data = [
        dict(
            date='2021-07-07', decimal="10.200", optional=42, list=['a', 'b', 'c'],
            struct={'id': 122, 'name': 'Jonny'}, tuple=(True, False, 55),
            variant_named=('id', 42), variant_unnamed=(1, 115),
            dict={15: True}, tagged=True,
        )
    ]
    expected = [
        dict(
            date='2021-07-07', decimal=b'\x80\x00\x27\xd8', optional=42, list=['a', 'b', 'c'],
            struct={'id': 122, 'name': 'Jonny'}, tuple=[True, False, 55],
            variant_named=['id', 42], variant_unnamed=[1, 115],
            dict=[[15, True]], tagged=True,
        )
    ]

    task_snapshot = transform.replace_by_snapshot(
        name='test_complex_rps',
        source=external_source(data),
        target_table=_TestTable,
    ).with_processing(
        use_yt_complex_types()
    )

    run_task(task_snapshot)

    assert expected == read_actual_data(_TestTable)

    data[0]['optional'] = 567
    expected[0]['optional'] = 567

    task_period = transform.replace_by_period(
        name='test_complex_rpp',
        source=external_source(data),
        target_table=_TestTable,
        by_field='date',
        period=Period(data[0]['date'], data[-1]['date']),
    ).with_processing(
        use_yt_complex_types()
    )

    run_task(task_period)

    assert expected == read_actual_data(_TestTable)


def _write_decimal_table(yt_table, table_rows):
    task_snapshot = transform.replace_by_snapshot(
        name='test_snapshot_prepare_decimal_table',
        source=external_source(table_rows),
        target_table=yt_table,
    )
    run_task(task_snapshot)


def _read_decimals_from(yt_table):
    return [
        yt_table.decimal.deserializer(r['decimal'])
        for r in op.read_yt_table(
            resolve_meta(yt_table).target_path()
        )
    ]


@pytest.mark.slow
def test_decimal_in_nile_over_yql_mapper():
    """ Тест проверяет возможность изменения Decimal поля в маппере Nile over YQL """

    @utils.random_yt_table
    class TestTableDecimal(yt.YTTable):
        decimal = yt.Decimal(5, 3)

    decimal_initial_data = [dict(decimal="10.123"), dict(decimal="5.3"), dict(decimal="-5"), dict(decimal="99.999")]
    decimal_expected_data = [py_Decimal("13.123"), py_Decimal("8.3"), py_Decimal("-2"), py_Decimal("+inf")]

    _decimal_rounder = yt.get_decimal_rounder(5, 3, rounding=ROUND_HALF_EVEN, round_infinity=True)

    # запись начальных данных
    _write_decimal_table(TestTableDecimal, decimal_initial_data)

    # маппер, увеличивающий значения на 3
    @nile_config(nile_backend_type=NileBackend.YQL)
    @nile_source(source_table=TestTableDecimal)
    def _increment_decimal_source(_, source_table):

        @with_hints(output_schema={'decimal': qb2_typing.YQLDecimal[5, 3]})
        def decimal_plus_three(records):
            for r in records:
                yield Record(decimal=_decimal_rounder(r.decimal + 3))

        return source_table.map(decimal_plus_three)

    # применение маппера
    task_snapshot = transform.replace_by_snapshot(
        name='test_incrementation_of_decimal',
        source=_increment_decimal_source,
        target_table=TestTableDecimal,
    ).with_processing(
        use_yt_complex_types()
    )
    run_task(task_snapshot)

    # assert
    assert decimal_expected_data == _read_decimals_from(TestTableDecimal)


@pytest.mark.slow
def test_decimal_in_nile_over_yt_mapper():
    """ Тест проверяет возможность изменения Decimal поля в маппере Nile over YT """

    @utils.random_yt_table
    class TestTableDecimal(yt.YTTable):
        decimal = yt.Decimal(5, 3)

    decimal_initial_data = [dict(decimal="10.123"), dict(decimal="5.3"), dict(decimal="-5"), dict(decimal="99.999")]
    decimal_expected_data = [py_Decimal("13.123"), py_Decimal("8.3"), py_Decimal("-2"), py_Decimal("+inf")]

    _decimal_rounder = yt.get_decimal_rounder(5, 3, rounding=ROUND_HALF_EVEN, round_infinity=True)

    # запись начальных данных
    _write_decimal_table(TestTableDecimal, decimal_initial_data)

    # маппер, увеличивающий значения на 3
    @nile_config(
        nile_backend_type=NileBackend.YT,
        # этот аргумент важен, иначе Nile ломается пытаясь
        # декодировать байтового значение Decimal
        bytes_decode_mode='never',
    )
    @nile_source(source_table=TestTableDecimal)
    def _increment_decimal_source(_, source_table):

        def decimal_plus_three(records):
            for r in records:
                yield Record(
                    decimal=TestTableDecimal.decimal.serializer(
                        _decimal_rounder(
                            3 + TestTableDecimal.decimal.deserializer(r.decimal)
                        )
                    )
                )

        return source_table.map(decimal_plus_three)

    # применение маппера
    task_snapshot = transform.replace_by_snapshot(
        name='test_incrementation_of_decimal',
        source=_increment_decimal_source,
        target_table=TestTableDecimal,
    )
    run_task(task_snapshot)

    # assert
    assert decimal_expected_data == _read_decimals_from(TestTableDecimal)


@pytest.mark.slow
def test_decimal_in_spark_mapper():
    """ Тест проверяет возможность изменения Decimal поля в маппере SPYT """

    @utils.random_yt_table
    class TestTableDecimal(yt.YTTable):
        decimal = yt.Decimal(5, 3)

    # NB! spark не умеет округлять значения до бесконечностей, а
    # кастомная функция округления не съедается через udf, поэтому
    # на данный момент не рассматриваем выход за крайние значения.
    decimal_initial_data = [dict(decimal="10.123"), dict(decimal="5.3"), dict(decimal="-5")]
    decimal_expected_data = [py_Decimal("13.123"), py_Decimal("8.3"), py_Decimal("-2")]

    # запись начальных данных.
    _write_decimal_table(TestTableDecimal, decimal_initial_data)

    # маппер, увеличивающий значения на 3
    @spark_source(source_table=TestTableDecimal)
    def _increment_decimal_source(_, source_table):

        return source_table.withColumn(
            'decimal',
            (source_table.decimal + 3).cast(DecimalType(precision=5, scale=3)),
        )

    # применение маппера
    task_snapshot = transform.replace_by_snapshot(
        name='test_incrementation_of_decimal',
        source=_increment_decimal_source,
        target_table=TestTableDecimal,
    ).with_processing(
        use_yt_complex_types()
    )
    run_task(task_snapshot)

    # assert
    assert decimal_expected_data == _read_decimals_from(TestTableDecimal)
