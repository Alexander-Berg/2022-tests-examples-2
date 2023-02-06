import itertools
from contextlib import contextmanager
from datetime import datetime
from functools import partial

import pytest
from mock import patch, call, Mock

from dmp_suite.greenplum import (
    Distribution, MonthPartitionScale,
    String, Datetime, GPTable, PartitionList, ListPartitionItem,
    GPMeta, DayPartitionScale, Tablespace
)
from dmp_suite.greenplum.query import GreenplumQuery
from dmp_suite.greenplum import GPMeta
from dmp_suite.greenplum.maintenance.partition.expired import (
    _get_partition_ttl_rules as get_partition_ttl_rules,
    ttl_by_attr, ExpiredPartitionMaintenanceTask, ExpiredPartition
)
from connection import greenplum as gp
from test_dmp_suite.greenplum.utils import TestLayout


class NonPartitionTable(GPTable):
    __layout__ = TestLayout(name='non_partition')
    data_id = String(key=True)


class NonTtlPartitionTable(GPTable):
    __layout__ = TestLayout(name='non_ttl_partition')
    __distributed_by__ = Distribution('data_id')
    __partition_scale__ = MonthPartitionScale(
        partition_key='utc_start_dttm',
        start='2020-05-01',
        end='2020-07-01',
    )
    data_id = String(key=True)
    utc_start_dttm = Datetime()
    value = String()


class TtlPartitionTable(GPTable):
    __layout__ = TestLayout(name='ttl_partition')
    __distributed_by__ = Distribution('data_id')
    __partition_scale__ = MonthPartitionScale(
        partition_key='utc_start_dttm',
        start='2020-05-01',
        end='2020-07-01',
        partition_ttl_day_cnt=10
    )
    data_id = String(key=True)
    utc_start_dttm = Datetime()
    value = String()


class TtlSubpartitionTable(GPTable):
    __layout__ = TestLayout(name='ttl_subpartition')
    __distributed_by__ = Distribution('data_id')
    __partition_scale__ = PartitionList(
        partition_key='scale_name',
        partition_list=[
            ListPartitionItem(name='yearly', value='yearly'),
            ListPartitionItem(name='monthly', value='monthly'),
        ],
        default_partition=ListPartitionItem(name='other', value=None),
        subpartition=MonthPartitionScale(
            partition_key='utc_start_dttm',
            start='2020-05-01',
            end='2020-07-01',
            is_subpartition=True,
            partition_ttl_day_cnt=10
        )
    )
    data_id = String(key=True)
    utc_start_dttm = Datetime()
    scale_name = String()
    value = String()


# довольно странный случай, но пусть будет для полноты
class MultiTtlTable(GPTable):
    __layout__ = TestLayout(name='multi_ttl')
    __distributed_by__ = Distribution('data_id')
    __partition_scale__ = MonthPartitionScale(
        partition_key='utc_start_dttm',
        start='2020-05-01',
        end='2020-05-31',
        partition_ttl_day_cnt=10,
        subpartition=DayPartitionScale(
            partition_key='utc_end_dttm',
            start='2020-05-01',
            end='2020-05-31',
            is_subpartition=True,
            partition_ttl_day_cnt=10
        )
    )
    data_id = String(key=True)
    utc_start_dttm = Datetime()
    utc_end_dttm = Datetime()
    value = String()


@pytest.mark.parametrize('gp_table, expected', [
    (NonPartitionTable, []),
    (NonTtlPartitionTable, []),
    (TtlPartitionTable, [(0, datetime(year=2020, month=9, day=20))]),
    (TtlSubpartitionTable, [(1, datetime(year=2020, month=9, day=20))]),
    (
        MultiTtlTable,
        [
            (0, datetime(year=2020, month=9, day=20)),
            (1, datetime(year=2020, month=9, day=20)),
        ]
    ),
])
def test_get_partition_ttl_rules(gp_table, expected):
    def to_rules(gp_table, level, dt):
        meta = GPMeta(gp_table)
        return {
            'schema_name': meta.schema,
            'table_name': meta.table_name,
            'partition_level': level,
            'upper_bound_by_partition': dt,
            'upper_bound_by_created': dt
        }

    expected = [to_rules(gp_table, *i) for i in expected]
    now = datetime(year=2020, month=9, day=30)
    assert list(get_partition_ttl_rules(now, gp_table, ttl_by_attr('partition_ttl_day_cnt'))) == expected


# вместо таблицы gpdb.object_meta готовим синтетику сами:
# 1. gpdb.object_meta обновляется раз в несколько часов,
#    что неприемлемо для тестов
# 2. нужна возможность проверить различные сценарии:
#   - первичная инициализация/создание таблицы
#   - исторический пересчет
def prepare_gpdb_object_meta(conn, gp_tables, create_dttm):
    sql_create_table = """
    CREATE TEMP TABLE test_meta_table (
        object_schema_name VARCHAR,
        object_name  VARCHAR,
        actual_flg BOOLEAN,
        create_dttm TIMESTAMP,
        gp_tablespace VARCHAR
    ) ON COMMIT DROP
    """
    GreenplumQuery.from_string(sql_create_table, conn).execute()

    sql_insert = """
    insert into test_meta_table
    select
      partitionschemaname as object_schema_name,
      partitiontablename as object_name,
      TRUE as actual_flg,
      %(create_dttm)s as create_dttm,
      %(gp_tablespace)s as gp_tablespace
     from pg_partitions
    where tablename = %(table_name)s
      and schemaname = %(schema_name)s
    """

    for gp_table in gp_tables:
        meta = GPMeta(gp_table)
        gp_tablespace = Tablespace.NVME.value
        GreenplumQuery.from_string(
            sql_insert
        ).add_params(
            table_name=meta.table_name,
            schema_name=meta.schema,
            create_dttm=create_dttm,
            gp_tablespace=gp_tablespace
        ).execute()

    temp_schema = GreenplumQuery.from_string(
        'select nspname from pg_namespace where oid  =  pg_my_temp_schema()'
    ).get_data()
    temp_schema = next(temp_schema)[0]
    return dict(
        object_meta_schema=temp_schema,
        object_meta_name='test_meta_table'
    )


@contextmanager
def patch_prepare_partitions(create_dttm):
    gpdb_object_meta_table_mock = dict()
    orig_prepare_partitions = ExpiredPartitionMaintenanceTask._prepare_partitions

    def _prepare_partitions_(self, conn, gp_tables, dt):
        # реальная дата создания партиций будет зависеть от даты запуска тестов
        # поэтому создаем спец таблицу с метаданными о создании партиций
        with conn.transaction():
            gpdb_object_meta_table = prepare_gpdb_object_meta(
                conn, gp_tables, create_dttm
            )
            gpdb_object_meta_table_mock.update(**gpdb_object_meta_table)
            return orig_prepare_partitions(self, conn, gp_tables, dt)

    patch_object_meta_table = patch(
        'dmp_suite.greenplum.maintenance.partition.expired._GPDB_OBJECT_META_TABLE',
        gpdb_object_meta_table_mock
    )
    patch_prepare_partitions = patch(
        'dmp_suite.greenplum.maintenance.partition.expired.ExpiredPartitionMaintenanceTask._prepare_partitions',
        _prepare_partitions_
    )
    with patch_object_meta_table, patch_prepare_partitions:
        yield


def _to_expected_call(expected):
    return [
        call(ExpiredPartition(
            schema_name=GPMeta(i['table']).schema,
            table_name=GPMeta(i['table']).table_name,
            partition_name=i['partition_name'],
            parent_partition_name=i['parent_partition_name'],
            partition_level=int(i['parent_partition_name'] is not None)
        ))
        for i in expected
    ]


def create_expected(base):
    def get_expected(*partition_names):
        return _to_expected_call([
            dict(b, partition_name=p)
            for b, p in itertools.product(base, partition_names)
        ])
    return get_expected


def create_expected_multi_ttl(gp_table, parent_partition):
    def get_expected_multi_ttl(start, end, with_parent):
        expected = []
        for partition in range(start, end + 1):
            expected.append(
                dict(table=gp_table,
                     parent_partition_name=parent_partition,
                     partition_name=f'{partition}')
            )
        if with_parent:
            expected.append(
                dict(table=gp_table,
                     parent_partition_name=None,
                     partition_name=parent_partition)
            )
        return _to_expected_call(expected)
    return get_expected_multi_ttl


def assert_dropped_by_tables(gp_tables, create_dttm, validation_dttm, expected):
    with patch_prepare_partitions(create_dttm):
        mock_action = Mock()
        ExpiredPartitionMaintenanceTask(
            pymodule='test',
            name='test',
            maintenance_action=mock_action,
            ttl='partition_ttl_day_cnt'
        ).do_partitions_maintenance(
            gp_tables, validation_dttm
        )
        assert mock_action.call_count == len(expected)
        mock_action.assert_has_calls(expected, any_order=True)


def create_tables(conn, gp_tables):
    with conn.transaction():
        for gp_table in gp_tables:
            conn.create_table(gp_table)


@pytest.mark.slow('gp')
def test_cleanup_partition_by_tables():
    conn = gp.connection
    # создадим таблицы, чтобы информация о них появилась в системном словаре GP

    # для end='2020-07-01'
    # будут созданы партиции 202005, 202006, 202007
    gp_tables = [
        NonPartitionTable,
        NonTtlPartitionTable,
        TtlPartitionTable,
        TtlSubpartitionTable,
    ]

    create_tables(conn, gp_tables)

    assert_dropped = partial(assert_dropped_by_tables, gp_tables)
    expected = create_expected([
            dict(table=TtlPartitionTable, parent_partition_name=None),
            dict(table=TtlSubpartitionTable, parent_partition_name='monthly'),
            dict(table=TtlSubpartitionTable, parent_partition_name='yearly'),
            # не нашел как, но это видимо создалась дефолтная партиция
            dict(table=TtlSubpartitionTable, parent_partition_name='other'),
    ])

    # на каждый parametrize создавалась бы отдельная схема и все таблицы
    # что как-то дорого

    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=8, day=5),
        expected=expected('202005', '202006')
    )

    # партиция 202007 не удаляется
    # так ttl должен отсчитываться от даты окончания партиции
    # 2020-08-01 + 10 дней
    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=8, day=10),
        expected=expected('202005', '202006')
    )

    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=8, day=12),
        expected=expected('202005', '202006', '202007')
    )

    # удаляются только существующие партиции
    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=11, day=11),
        expected=expected('202005', '202006', '202007')
    )

    # сценарии пересоздания исторических партиций

    # ничего не удаляем,
    assert_dropped(
        create_dttm=datetime(year=2020, month=8, day=10),
        validation_dttm=datetime(year=2020, month=8, day=11),
        expected=[]
    )

    # удаляем, ttl превышает дату создания партиции и дату действия партиции
    assert_dropped(
        create_dttm=datetime(year=2020, month=8, day=10),
        validation_dttm=datetime(year=2020, month=8, day=21),
        expected=expected('202005', '202006', '202007')
    )


@pytest.mark.slow('gp')
def test_cleanup_partition_by_tables_multi_ttl():
    conn = gp.connection

    gp_tables = [
        MultiTtlTable
    ]

    # создадим таблицы, чтобы информация о них появилась в системном словаре GP
    create_tables(conn, gp_tables)

    assert_dropped = partial(assert_dropped_by_tables, gp_tables)
    expected_multi_ttl = create_expected_multi_ttl(MultiTtlTable, '202005')

    # на каждый parametrize создавалась бы отдельная схема и все таблицы
    # что как-то дорого

    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=5, day=5),
        expected=[]
    )

    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=5, day=15),
        expected=expected_multi_ttl(20200501, 20200504, False)
    )

    assert_dropped(
        create_dttm=datetime(year=2020, month=3, day=1),
        validation_dttm=datetime(year=2020, month=6, day=15),
        expected=expected_multi_ttl(20200501, 20200531, True)
    )

    # сценарии пересоздания исторических партиций

    assert_dropped(
        create_dttm=datetime(year=2020, month=8, day=1),
        validation_dttm=datetime(year=2020, month=8, day=5),
        expected=[]
    )

    assert_dropped(
        create_dttm=datetime(year=2020, month=8, day=1),
        validation_dttm=datetime(year=2020, month=8, day=17),
        expected=expected_multi_ttl(20200501, 20200531, True)
    )
