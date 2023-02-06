from datetime import timedelta, datetime
from decimal import Decimal
from operator import itemgetter

import pytest
from mock import patch, MagicMock
from psycopg2.sql import Identifier
from psycopg2.sql import SQL

import dmp_suite.yt.table as yt
import dmp_suite.greenplum.table as gp_table
from connection import greenplum as gp
from connection.ctl import get_ctl
from dmp_suite import datetime_utils as dtu
from dmp_suite import scales
from dmp_suite.ctl import CTL_LAST_LOAD_DATE, CTL_LAST_SYNC_DATE
from dmp_suite.datetime_utils import utcnow
from dmp_suite.greenplum import GPMeta
from dmp_suite.greenplum import Int as GpInt, Datetime as GpDatetime
from dmp_suite.greenplum import String, GPTable
from dmp_suite.greenplum.connection import EtlConnection
from dmp_suite.greenplum.hnhm import HnhmEntity
from dmp_suite.greenplum.hnhm.utils import ActualEntityCte
from dmp_suite.greenplum.task import cli, validators
from dmp_suite.greenplum.task.transformations import (
    ExternalTaskSource, snapshot, delete_insert, period_snapshot, scd2,
    replace_by_key,
    StgTableTaskSource, SqlTaskSource, YtTableTaskSource,
    TempTableError, TempTable,
)
from dmp_suite.table import DdsLayout, CdmLayout
from dmp_suite.task.args import use_arg, use_ctl_last_load_date, utcnow_arg, use_period_arg
from dmp_suite.task.cli import StartEndDate
from dmp_suite.task.execution import run_task
from dmp_suite.yt import YTMeta, etl
from dmp_suite.yt.task.etl.external_transform import external_source
from dmp_suite.yt.task.etl.transform import replace_by_snapshot
from test_dmp_suite.greenplum.task.tables import YTSourceTable, GPTargetTable
from test_dmp_suite.greenplum.utils import TestLayout
from test_dmp_suite.yt.utils import random_yt_table


@pytest.mark.slow('gp')
def test_snapshot_stg_table():
    yt_meta = YTMeta(YTSourceTable)
    yt_data = [dict(id=1, value='abc'), dict(id=2, value='def')]
    etl.init_target_table(yt_meta)
    etl.write_serialized_data(yt_meta.target_path(), yt_meta, yt_data)

    task = snapshot(
        'test_snapshot_stg_table',
        source=StgTableTaskSource(YTSourceTable),
        target=GPTargetTable
    )
    run_task(task)

    expected = [
        dict(id=1, value='abc', value_2=None),
        dict(id=2, value='def', value_2=None),
    ]

    actual = sorted((dict(row) for row in gp.connection.select_all(GPTargetTable)), key=itemgetter('id'))
    assert expected == actual


@pytest.mark.slow('gp')
def test_snapshot_with_ctl_stg_table():
    yt_meta = YTMeta(YTSourceTable)
    yt_data = [dict(id=1, value='abc'), dict(id=2, value='def')]
    etl.init_target_table(yt_meta)
    etl.write_serialized_data(yt_meta.target_path(), yt_meta, yt_data)

    ctl = get_ctl().gp
    old_ctl = utcnow() + timedelta(days=-2)
    ctl.set_param(GPTargetTable, CTL_LAST_LOAD_DATE, old_ctl)

    task = snapshot(
        'test_snapshot_with_ctl_stg_table',
        source=YtTableTaskSource(YTSourceTable),
        target=GPTargetTable
    ).arguments(
        period=StartEndDate.from_ctl(
            start=use_ctl_last_load_date(GPTargetTable),
            end=utcnow_arg()
        )
    ).set_ctl()

    run_task(task)

    expected = [
        dict(id=1, value='abc', value_2=None),
        dict(id=2, value='def', value_2=None),
    ]

    actual = sorted((dict(row) for row in gp.connection.select_all(GPTargetTable)), key=itemgetter('id'))
    assert expected == actual

    new_ctl = ctl.get_param(GPTargetTable, CTL_LAST_LOAD_DATE)
    assert old_ctl < new_ctl


def test_sql_source_get_sources():
    class Entity(HnhmEntity):
        __layout__ = DdsLayout('test', prefix_key='test')

        k = String()
        v = String()

        __keys__ = [k]

    class Table(GPTable):
        __layout__ = CdmLayout('test', prefix_key='test')

        s = String()

    source = (
        SqlTaskSource.from_string('select 1')
        .add_cte(a=ActualEntityCte(Entity))
        .add_tables(t=Table)
    )

    source_tables = list(source.get_sources())
    assert len(source_tables) == 2
    assert set(source.get_sources()) == {Entity, Table}

    source = (
        SqlTaskSource.from_string('select 1')
        .add_temp_tables(a=ActualEntityCte(Entity))
        .add_tables(t=Table)
    )

    source_tables = list(source.get_sources())
    assert len(source_tables) == 2
    assert set(source.get_sources()) == {Entity, Table}


def test_temp_table_raise_without_name():
    class Entity(HnhmEntity):
        __layout__ = DdsLayout('test', prefix_key='test')

        k = String()
        v = String()

        __keys__ = [k]

    with pytest.raises(TempTableError):
        TempTable(statement=ActualEntityCte(Entity)).get_value(None, None)


@pytest.mark.slow('gp')
def test_temp_table_sql():
    class Entity(HnhmEntity):
        __layout__ = DdsLayout('test', prefix_key='test')

        k = String()
        v = String()

        __keys__ = [k]

    cte = ActualEntityCte(Entity)
    qte_sql = gp.connection.build_executable_string(cte.sql_desc).lower()

    temp_table = TempTable(statement=cte, name='a')
    sql = gp.connection.build_executable_string(
        temp_table.get_value(None, None)
    ).lower()

    assert b'analyze "a";' in sql
    assert b'distributed randomly;' in sql
    assert b'create temporary table "a" on commit drop as' in sql
    assert qte_sql in sql

    temp_table = TempTable(
        statement=cte,
        name='a',
        distributed_by='k',
        analyze=False,
        on_commit_drop=False,
    )
    sql = gp.connection.build_executable_string(
        temp_table.get_value(None, None)
    ).lower()

    assert b'analyze "a";' not in sql
    assert b'distributed by ("k");' in sql
    assert b'create temporary table "a"' in sql
    assert b'on commit drop as' not in sql
    assert qte_sql in sql


@pytest.mark.slow('gp')
def test_sql_task_source_sql():

    class Entity1(HnhmEntity):
        __layout__ = DdsLayout('test1', prefix_key='test')

        k1 = String()
        v1 = String()

        __keys__ = [k1]

    class Entity2(HnhmEntity):
        __layout__ = DdsLayout('test2', prefix_key='test')

        k2 = String()
        v2 = String()

        __keys__ = [k2]

    class Table(GPTable):
        __layout__ = DdsLayout('test', prefix_key='test')

        k3 = String()
        v3 = String()

    sql = (
        'create temporary table result_table on commit drop as\n'
        'select * from ('
        '{cte}'
        ')\n'
        'union all\n'
        'select * from temp_cte\n'
        'union all\n'
        'select * from {t} where v = %(v)s'
    )
    pre_sql = 'select %(v)s as v;'

    cte = ActualEntityCte(Entity1)
    temp_cte = ActualEntityCte(Entity2)

    source = SqlTaskSource.from_string(
        sql,
    ).add_cte(
        cte=cte,
    ).add_temp_tables(
        temp_cte=temp_cte,
    ).add_tables(
        t=Table,
    ).add_pre_sql_statement(
        pre_sql,
    ).add_params(
        v=use_arg('v'),
    )

    temp_table_sql = TempTable(temp_cte, name='temp_cte').get_value(None, None)

    # эмулируем инициализация параметрами в таске
    source = source.get_value(dict(v='a'), None)

    assert pre_sql in list(source.pre_sql)
    assert temp_table_sql in list(source.pre_sql)
    assert len(list(source.pre_sql)) == 2

    query_sql = SQL(sql).format(
        cte=cte.sql_desc,
        t=SQL('{schema}.{table}').format(
            schema=Identifier(GPMeta(Table).schema),
            table=Identifier(GPMeta(Table).table_name)
        )
    )

    # порядок выполнения pre_sql и temp tables не гарантируется, но по факту
    # сначала pre_sql
    expected_query = (
        SQL(pre_sql) + SQL('\n') + temp_table_sql + SQL('\n') + query_sql
    )
    expected = gp.connection.build_executable_string(expected_query, v='a')
    assert source.executable_query_string == expected

    # проверяем, что от запусков с разными аргументами ничего не ломается
    source = source.get_value(dict(v='b'), None)
    expected = gp.connection.build_executable_string(expected_query, v='b')
    assert source.executable_query_string == expected


UTC_NOW = datetime(2021, 3, 24, 15)
utc_now_mock = patch('dmp_suite.datetime_utils.utcnow', MagicMock(return_value=UTC_NOW))

DEFAULT_HOOK = object()
CUSTOM_HOOK = use_period_arg().end.round_down(scales.day)
UTC_NOW_ROUNDED = datetime(2021, 3, 24, 0)


@pytest.mark.slow('gp')
@utc_now_mock
@pytest.mark.parametrize(
    'hook, expected_ctl_load, expected_ctl_sync', [
        (DEFAULT_HOOK, UTC_NOW + timedelta(days=-1), UTC_NOW),
        (CUSTOM_HOOK, UTC_NOW_ROUNDED + timedelta(days=-1), UTC_NOW),
    ]
)
def test_period_snapshot_with_ctl(hook, expected_ctl_load, expected_ctl_sync):

    class GpPeriodSnapshotTarget(GPTable):
        __layout__ = TestLayout(name="period_snapshot_test")
        dttm = GpDatetime()
        value = GpInt()

    data_before = [
        dict(dttm=datetime(2021, 3, 19, 13), value=335),
        dict(dttm=datetime(2021, 3, 21, 13), value=689),
        dict(dttm=datetime(2021, 3, 21, 17), value=527),
        dict(dttm=datetime(2021, 3, 22, 11), value=904),
        dict(dttm=datetime(2021, 3, 23, 21), value=512),
    ]

    data_new = [
        dict(dttm=datetime(2021, 3, 21, 16), value=421),
        dict(dttm=datetime(2021, 3, 22, 11), value=824),
        dict(dttm=datetime(2021, 3, 23, 13), value=321),
    ]

    data_after = [
        dict(dttm=datetime(2021, 3, 19, 13), value=335),
        dict(dttm=datetime(2021, 3, 21, 13), value=689),
        dict(dttm=datetime(2021, 3, 21, 16), value=421),
        dict(dttm=datetime(2021, 3, 22, 11), value=824),
        dict(dttm=datetime(2021, 3, 23, 13), value=321),
        dict(dttm=datetime(2021, 3, 23, 21), value=512),
    ]

    with gp.connection.transaction():
        gp.connection.create_table(GpPeriodSnapshotTarget)
        gp.connection.insert(GpPeriodSnapshotTarget, data_before)

    ctl = get_ctl().gp
    ctl.set_param(GpPeriodSnapshotTarget, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(GpPeriodSnapshotTarget, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    task = period_snapshot(
        name='test_period_snapshot_with_ctl',
        source=ExternalTaskSource(data_new),
        target=GpPeriodSnapshotTarget,
        period_column_name='dttm',
    ).arguments(
        period=StartEndDate.from_ctl(
            start=use_ctl_last_load_date(GpPeriodSnapshotTarget),
            end=utcnow_arg().offset(timedelta(days=-1)),
        )
    )

    if hook is not DEFAULT_HOOK:
        task = task.set_ctl(hook=CUSTOM_HOOK, force=True)

    assert task._with_ctl is True

    run_task(task)

    assert ctl.get_param(GpPeriodSnapshotTarget, CTL_LAST_LOAD_DATE) == expected_ctl_load
    assert ctl.get_param(GpPeriodSnapshotTarget, CTL_LAST_SYNC_DATE) == expected_ctl_sync

    actual = sorted((dict(row) for row in gp.connection.select_all(GpPeriodSnapshotTarget)), key=itemgetter('dttm'))
    assert actual == data_after


@pytest.mark.slow('gp')
@utc_now_mock
@pytest.mark.parametrize(
    'hook, expected_ctl_load, expected_ctl_sync', [
        (None, UTC_NOW + timedelta(days=-3), UTC_NOW),
        (DEFAULT_HOOK, UTC_NOW + timedelta(days=-1), UTC_NOW),
        (CUSTOM_HOOK, UTC_NOW_ROUNDED + timedelta(days=-1), UTC_NOW),
    ]
)
def test_snapshot_with_ctl(hook, expected_ctl_load, expected_ctl_sync):

    class GpSnapshotTarget(GPTable):
        __layout__ = TestLayout(name="snapshot_test")
        id = GpInt()
        value = GpInt()

    data_before = [
        dict(id=1, value=312),
        dict(id=2, value=453),
        dict(id=3, value=201),
        dict(id=4, value=519),
    ]

    data_new = [
        dict(id=1, value=312),
        dict(id=3, value=201),
        dict(id=4, value=519),
        dict(id=5, value=814),
    ]

    data_after = [
        dict(id=1, value=312),
        dict(id=3, value=201),
        dict(id=4, value=519),
        dict(id=5, value=814),
    ]

    with gp.connection.transaction():
        gp.connection.create_table(GpSnapshotTarget)
        gp.connection.insert(GpSnapshotTarget, data_before)

    ctl = get_ctl().gp
    ctl.set_param(GpSnapshotTarget, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(GpSnapshotTarget, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    task = snapshot(
        'test_snapshot_with_ctl',
        source=ExternalTaskSource(data_new),
        target=GpSnapshotTarget,
    )

    if hook is not None:
        task = task.arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GpSnapshotTarget),
                end=utcnow_arg().offset(timedelta(days=-1)),
            )
        )
        if hook is DEFAULT_HOOK:
            task = task.set_ctl()
        else:
            task = task.set_ctl(hook=CUSTOM_HOOK)

    should_be_with_ctl = hook is not None
    assert task._with_ctl == should_be_with_ctl

    run_task(task)

    assert ctl.get_param(GpSnapshotTarget, CTL_LAST_LOAD_DATE) == expected_ctl_load
    assert ctl.get_param(GpSnapshotTarget, CTL_LAST_SYNC_DATE) == expected_ctl_sync

    actual = sorted((dict(row) for row in gp.connection.select_all(GpSnapshotTarget)), key=itemgetter('id'))
    assert actual == data_after


@pytest.mark.slow('gp')
@utc_now_mock
@pytest.mark.parametrize(
    'hook, expected_ctl_load, expected_ctl_sync', [
        (None, UTC_NOW + timedelta(days=-3), UTC_NOW),
        (DEFAULT_HOOK, UTC_NOW + timedelta(days=-1), UTC_NOW),
        (CUSTOM_HOOK, UTC_NOW_ROUNDED + timedelta(days=-1), UTC_NOW),
    ]
)
def test_delete_insert_with_ctl(hook, expected_ctl_load, expected_ctl_sync):

    class GpDeleteInsertTarget(GPTable):
        __layout__ = TestLayout(name="delete_insert_test")
        id = GpInt(key=True)
        value = GpInt()

    data_before = [
        dict(id=1, value=312),
        dict(id=2, value=453),
        dict(id=3, value=201),
    ]

    data_new = [
        dict(id=1, value=312),
        dict(id=2, value=451),
        dict(id=4, value=519),
    ]

    data_after = [
        dict(id=1, value=312),
        dict(id=2, value=451),
        dict(id=3, value=201),
        dict(id=4, value=519),
    ]

    with gp.connection.transaction():
        gp.connection.create_table(GpDeleteInsertTarget)
        gp.connection.insert(GpDeleteInsertTarget, data_before)

    ctl = get_ctl().gp
    ctl.set_param(GpDeleteInsertTarget, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(GpDeleteInsertTarget, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    task = delete_insert(
        'test_delete_insert_with_ctl',
        source=ExternalTaskSource(data_new),
        target=GpDeleteInsertTarget,
    )

    if hook is not None:
        task = task.arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GpDeleteInsertTarget),
                end=utcnow_arg().offset(timedelta(days=-1)),
            )
        )
        if hook is DEFAULT_HOOK:
            task = task.set_ctl()
        else:
            task = task.set_ctl(hook=CUSTOM_HOOK)

    should_be_with_ctl = hook is not None
    assert task._with_ctl == should_be_with_ctl

    run_task(task)

    assert ctl.get_param(GpDeleteInsertTarget, CTL_LAST_LOAD_DATE) == expected_ctl_load
    assert ctl.get_param(GpDeleteInsertTarget, CTL_LAST_SYNC_DATE) == expected_ctl_sync

    actual = sorted((dict(row) for row in gp.connection.select_all(GpDeleteInsertTarget)), key=itemgetter('id'))
    assert actual == data_after


@pytest.mark.slow('gp')
@utc_now_mock
@pytest.mark.parametrize(
    'hook, expected_ctl_load, expected_ctl_sync', [
        (None, UTC_NOW + timedelta(days=-3), UTC_NOW),
        (DEFAULT_HOOK, UTC_NOW + timedelta(days=-1), UTC_NOW),
        (CUSTOM_HOOK, UTC_NOW_ROUNDED + timedelta(days=-1), UTC_NOW),
    ]
)
def test_replace_by_key_with_ctl(hook, expected_ctl_load, expected_ctl_sync):

    class GpReplaceByKeyTarget(GPTable):
        __layout__ = TestLayout(name="replace_by_key_test")
        dttm = GpDatetime()
        value = GpInt()

    data_before = [
        dict(dttm=datetime(2021, 3, 19, 13), value=335),
        dict(dttm=datetime(2021, 3, 21, 13), value=689),
        dict(dttm=datetime(2021, 3, 21, 17), value=527),
        dict(dttm=datetime(2021, 3, 22, 11), value=904),
        dict(dttm=datetime(2021, 3, 23, 21), value=512),
        dict(dttm=datetime(2021, 3, 25, 15), value=107),
    ]

    data_new = [
        dict(dttm=datetime(2021, 3, 21, 16), value=421),
        dict(dttm=datetime(2021, 3, 22, 11), value=824),
        dict(dttm=datetime(2021, 3, 23, 13), value=321),
    ]

    data_after = [
        dict(dttm=datetime(2021, 3, 19, 13), value=335),
        dict(dttm=datetime(2021, 3, 21, 16), value=421),
        dict(dttm=datetime(2021, 3, 22, 11), value=824),
        dict(dttm=datetime(2021, 3, 23, 13), value=321),
        dict(dttm=datetime(2021, 3, 25, 15), value=107),
    ]

    with gp.connection.transaction():
        gp.connection.create_table(GpReplaceByKeyTarget)
        gp.connection.insert(GpReplaceByKeyTarget, data_before)

    ctl = get_ctl().gp
    ctl.set_param(GpReplaceByKeyTarget, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(GpReplaceByKeyTarget, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    task = replace_by_key(
        name='test_period_snapshot_with_ctl',
        source=ExternalTaskSource(data_new),
        target=GpReplaceByKeyTarget,
    ).with_partition_key(
        'dttm'
    )

    if hook is not None:
        task = task.arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GpReplaceByKeyTarget),
                end=utcnow_arg().offset(timedelta(days=-1)),
            )
        )
        if hook is DEFAULT_HOOK:
            task = task.set_ctl()
        else:
            task = task.set_ctl(hook=CUSTOM_HOOK)

    should_be_with_ctl = hook is not None
    assert task._with_ctl == should_be_with_ctl

    run_task(task)

    assert ctl.get_param(GpReplaceByKeyTarget, CTL_LAST_LOAD_DATE) == expected_ctl_load
    assert ctl.get_param(GpReplaceByKeyTarget, CTL_LAST_SYNC_DATE) == expected_ctl_sync

    actual = sorted((dict(row) for row in gp.connection.select_all(GpReplaceByKeyTarget)), key=itemgetter('dttm'))
    assert actual == data_after


@pytest.mark.slow('gp')
@utc_now_mock
@pytest.mark.parametrize(
    'hook, expected_ctl_load, expected_ctl_sync', [
        (None, UTC_NOW + timedelta(days=-3), UTC_NOW),
        (DEFAULT_HOOK, UTC_NOW + timedelta(days=-1), UTC_NOW),
        (CUSTOM_HOOK, UTC_NOW_ROUNDED + timedelta(days=-1), UTC_NOW),
    ]
)
def test_scd2_with_ctl(hook, expected_ctl_load, expected_ctl_sync):

    class GpScd2Target(GPTable):
        __layout__ = TestLayout(name="scd2_test")
        id = GpInt(key=True)
        value = GpInt()
        valid_from = GpDatetime()
        valid_to = GpDatetime()

    data_before = [
        dict(id=1, value=312, valid_from=datetime(2021, 3, 19, 13), valid_to=datetime(2021, 3, 21, 14)),
        dict(id=1, value=793, valid_from=datetime(2021, 3, 21, 15), valid_to=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value=3, valid_from=datetime(2021, 3, 25), valid_to=datetime(2021, 4, 23, 23)),
        dict(id=3, value=4, valid_from=datetime(2021, 4, 24), valid_to=datetime(2021, 5, 21, 23)),
        dict(id=3, value=2145, valid_from=datetime(2021, 5, 22), valid_to=datetime(9999, 12, 31, 23, 59, 59)),
    ]

    data_new = [
        dict(id=1, value=451, valid_from=datetime(2021, 3, 23, 15)),
        dict(id=2, value=814, valid_from=datetime(2021, 3, 23, 15)),
        dict(id=3, value=4, valid_from=datetime(2021, 5, 7)),
        dict(id=3, value=4, valid_from=datetime(2021, 5, 22)),
    ]

    data_after = [
        dict(id=1, value=312, valid_from=datetime(2021, 3, 19, 13), valid_to=datetime(2021, 3, 21, 14)),
        dict(id=1, value=793, valid_from=datetime(2021, 3, 21, 15), valid_to=datetime(2021, 3, 23, 14)),
        dict(id=1, value=451, valid_from=datetime(2021, 3, 23, 15), valid_to=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value=814, valid_from=datetime(2021, 3, 23, 15), valid_to=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value=3, valid_from=datetime(2021, 3, 25), valid_to=datetime(2021, 4, 23, 23)),
        dict(id=3, value=4, valid_from=datetime(2021, 4, 24), valid_to=datetime(9999, 12, 31, 23, 59, 59)),
    ]

    with gp.connection.transaction():
        gp.connection.create_table(GpScd2Target)
        gp.connection.insert(GpScd2Target, data_before)

    ctl = get_ctl().gp
    ctl.set_param(GpScd2Target, CTL_LAST_LOAD_DATE, UTC_NOW + timedelta(days=-3))
    ctl.set_param(GpScd2Target, CTL_LAST_SYNC_DATE, UTC_NOW + timedelta(days=-2))

    task = scd2(
        name='test_scd2_with_ctl',
        source=ExternalTaskSource(data_new),
        target=GpScd2Target,
        valid_from_column='valid_from',
        valid_to_column='valid_to',
        append_only=False
    ).with_recording_interval(
        'hour'
    )

    if hook is not None:
        task = task.arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GpScd2Target),
                end=utcnow_arg().offset(timedelta(days=-1)),
            )
        )
        if hook is DEFAULT_HOOK:
            task = task.set_ctl()
        else:
            task = task.set_ctl(hook=CUSTOM_HOOK)

    should_be_with_ctl = hook is not None
    assert task._with_ctl == should_be_with_ctl

    run_task(task)

    assert ctl.get_param(GpScd2Target, CTL_LAST_LOAD_DATE) == expected_ctl_load
    assert ctl.get_param(GpScd2Target, CTL_LAST_SYNC_DATE) == expected_ctl_sync

    actual = sorted((dict(row) for row in gp.connection.select_all(GpScd2Target)),
                    key=lambda r: (r['id'], r['valid_from']))
    assert actual == data_after


@pytest.mark.slow('gp')
def test_everything_use_one_connection():
    class TestTable(GPTable):
        __layout__ = TestLayout(name="everything_use_one_connection")

        a = GpInt()

    class FailAnyUsageError(RuntimeError):
        pass

    class ConnectionMock:
        def __getattribute__(self, item):
            raise FailAnyUsageError('I fail on any usage!!!111')

    fail_any_usage_connection = ConnectionMock()
    real_connection = EtlConnection(**gp.get_default_connection_conf())
    real_connection.THIS_TEST_CONNECTION = True

    class ConnectionManagerMock:
        def get_connection(self, connection=None):
            if getattr(connection, 'THIS_TEST_CONNECTION', None):
                return connection

            if connection == 'high':
                return real_connection

            return fail_any_usage_connection

    source = SqlTaskSource.from_string('''
        CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
        SELECT 1 AS a
    ''')

    def get_task():
        return snapshot(
            'test',
            source=source,
            source_validation=validators.validate_nulls('a'),
            target=TestTable,
        )

    # мокаем manager, а не get_connection, чтобы не думать об импортах: модуль
    # или фукнция get_connection из config
    get_connection_patch = patch(
        'connection.greenplum._manager',
        ConnectionManagerMock(),
    )

    with get_connection_patch:
        with pytest.raises(FailAnyUsageError):
            task = get_task().arguments(
                resource_group=cli.ResourceGroup.low(),
            )
            run_task(task)

    with get_connection_patch:
        with pytest.raises(FailAnyUsageError):
            task = get_task()
            run_task(task)

    with get_connection_patch:
        task = get_task().arguments(
            resource_group=cli.ResourceGroup.high(),
        )
        run_task(task)

    assert list(map(dict, gp.connection.select_all(TestTable))) == [dict(a=1)]


@pytest.mark.slow('gp')
def test_type_v3_yt_to_gp():

    @random_yt_table
    class TestYTTypeV3Source(yt.YTTable):
        tst_int = yt.Int(sort_key=True)
        tst_decimal = yt.Decimal(5, 3)
        tst_date = yt.NativeDate()
        tst_datetime = yt.NativeDatetime()
        tst_timestamp = yt.NativeTimestamp()

    class TestGPTypeV3Target(gp_table.GPTable):
        __layout__ = TestLayout(
            name='yt_to_gp_transfer_snapshot_test',
        )

        tst_int = gp_table.Int(key=True)
        tst_decimal = gp_table.Numeric()
        tst_date = gp_table.Date()
        tst_datetime = gp_table.Datetime()
        tst_timestamp = gp_table.Datetime()

    conn = gp.connection

    with conn.transaction():
        if conn.table_exists(TestGPTypeV3Target):
            conn.drop_table(TestGPTypeV3Target)

        conn.create_table(TestGPTypeV3Target)

    task_snapshot = replace_by_snapshot(
        name='dmp_suite_yt_to_gp_type_v3_data',
        source=external_source(
            [
                {
                    'tst_int': 0,
                    'tst_decimal': '12.345',
                    'tst_date': '1970-01-01',
                    'tst_datetime': '1970-01-01 00:00:00',
                    'tst_timestamp': '1970-01-01 00:00:00.000000',
                },
                {
                    'tst_int': 1,
                    'tst_decimal': '0.94',
                    'tst_date': '2010-10-10',
                    'tst_datetime': '2010-10-10 10:10:10',
                    'tst_timestamp': '2010-10-10 10:10:10.000010',
                },
                {
                    'tst_int': 2,
                    'tst_decimal': '1.5',
                    'tst_date': '2010-10-10',
                    'tst_datetime': '2010-10-10',
                    'tst_timestamp': '2010-10-10',
                },
            ]
        ),
        target_table=TestYTTypeV3Source,
    )

    run_task(task_snapshot)

    task_snapshot = snapshot(
        name='dmp_suite_yt_to_gp_type_v3_transfer',
        source=YtTableTaskSource(TestYTTypeV3Source),
        target=TestGPTypeV3Target
    )

    run_task(task_snapshot)

    expected = [
        {
            'tst_int': 0,
            'tst_decimal': Decimal('12.345'),
            'tst_date': dtu._to_datetime('1970-01-01').date(),
            'tst_datetime': dtu._to_datetime('1970-01-01 00:00:00.000000'),
            'tst_timestamp': dtu._to_datetime('1970-01-01 00:00:00.000000'),
        },
        {
            'tst_int': 1,
            'tst_decimal': Decimal('0.94'),
            'tst_date': dtu._to_datetime('2010-10-10').date(),
            'tst_datetime': dtu._to_datetime('2010-10-10 10:10:10.000000'),
            'tst_timestamp': dtu._to_datetime('2010-10-10 10:10:10.000010'),
        },
        {
            'tst_int': 2,
            'tst_decimal': Decimal('1.5'),
            'tst_date': dtu._to_datetime('2010-10-10').date(),
            'tst_datetime': dtu._to_datetime('2010-10-10 00:00:00.000000'),
            'tst_timestamp': dtu._to_datetime('2010-10-10 00:00:00.000000'),
        },
    ]

    actual = sorted(
        (dict(row) for row in gp.connection.select_all(TestGPTypeV3Target)),
        key=itemgetter('tst_int')
    )
    assert expected == actual
