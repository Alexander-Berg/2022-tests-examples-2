import contextlib
import inspect

import mock
import pytest
from nile.api.v1 import extractors as ne, aggregators as na

from connection.yt import Pool
from dmp_suite.nile import cluster_utils as cu
from dmp_suite.yt import YTTable, Int, YTMeta, etl
from dmp_suite.yt import operation as yt
from dmp_suite.yt.task.etl import transform
from dmp_suite.yt.task.etl.external_transform import external_source
from dmp_suite.yt.task.etl.nile_transform import (
    nile_source,
    nile_config,
    filtered_date_range,
)
from dmp_suite.yt.task.etl.yql_transform import YqlTaskQuery
from test_dmp_suite.yt import utils
from test_dmp_suite.yt.task.etl.utils import (
    MockTask,
    Table,
    PartitionedTable,
    DttmTable,
    assert_filtered_date_range_partitioned,
    assert_filtered_date_range_non_partition,
)


table = utils.fixture_random_yt_table(Table)


@pytest.mark.slow
def test_nile_source(table):
    @nile_source(data=table)
    def accessor(args, data):
        return data.project(a='b', b='a')

    env = transform.TransformationEnvironment(
        task=MockTask(),
    )
    source = accessor.get_value(None, env)
    etl.init_target_table(table)
    yt.write_yt_table(YTMeta(table).target_path(), [dict(a=1, b=2)])
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as src:
        assert [dict(a=2, b=1)] == list(yt.read_yt_table(src))


@pytest.mark.slow
def test_nile_source_with_external_yt_table(table):
    table_path = YTMeta(table).target_path()

    @nile_source(data=table_path)
    def accessor(args, data):
        return data.project(a='b', b='a')

    env = transform.TransformationEnvironment(
        task=MockTask(),
    )
    source = accessor.get_value(None, env)
    etl.init_target_table(table)
    yt.write_yt_table(table_path, [dict(a=1, b=2)])
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as src:
        assert [dict(a=2, b=1)] == list(yt.read_yt_table(src))


class Table1(YTTable):
    p = Int()
    x = Int()


class Table2(YTTable):
    q = Int()
    y = Int()


table1 = utils.fixture_random_yt_table(Table1)
table2 = utils.fixture_random_yt_table(Table2)


@pytest.mark.slow
def test_nile_source_multiple_etl_sources(table, table1, table2):

    data0 = [dict(a=k, b=v) for k, v in zip(range(10), reversed(range(10)))]
    data1 = [dict(p=k, x=1) for k in [4, 1, 8, 0]]
    data2 = [dict(q=k, y=3) for k in [5, 3, 7, 1]]

    env = transform.TransformationEnvironment(
        task=MockTask(),
    )

    # Source 0: External source
    src0 = external_source(data0)

    # Source 1: Nile transformation
    etl.init_target_table(YTMeta(table1))
    yt.write_yt_table(YTMeta(table1).target_path(), data1)
    @nile_source(data=table1)
    def src1(args, data):
        return data.project(a='p')

    # Source 2: YQL transformation
    etl.init_target_table(YTMeta(table2))
    yt.write_yt_table(YTMeta(table2).target_path(), data2)
    query = 'INSERT INTO {target_path} FROM {data} SELECT q as a'
    src2 = YqlTaskQuery.from_string(query).add_tables(data=table2)

    # Multiple EtlSource task
    @nile_source(base=src0, stg1=src1, stg2=src2)
    def task(args, base, stg1, stg2):
        return base \
            .join(stg1, type='left_only', by='a') \
            .join(stg2, type='left_only', by='a') \
            .project(g=ne.const(1), b='a', a='b') \
            .groupby('g') \
            .aggregate(a=na.sum('a'), b=na.sum('b')) \
            .project('a', 'b')

    source = task.get_value(None, env)
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as path:
        assert [dict(a=10, b=17)] == list(yt.read_yt_table(path))


dttm_table = utils.fixture_random_yt_table(DttmTable)
partitioned_table = utils.fixture_random_yt_table(PartitionedTable)


@pytest.mark.slow
def test_filtered_date_range_partitioned(partitioned_table):
    @nile_source(data=filtered_date_range(partitioned_table))
    def accessor(args, data):
        return data.project('id')

    assert_filtered_date_range_partitioned(partitioned_table, accessor)


@pytest.mark.slow
def test_nile_filtered_date_range_non_partition(dttm_table):
    @nile_source(data=filtered_date_range(dttm_table, by_field='dttm'))
    def accessor(args, data):
        return data.project('id')

    assert_filtered_date_range_non_partition(dttm_table, accessor)


@pytest.mark.parametrize('config_first, config, expected', [
    (True, dict(pool='test_pool'), dict(pool='test_pool', name='Nile transformation task mock_task')),
    (False, dict(pool='test_pool'), dict(pool='test_pool', name='Nile transformation task mock_task')),
    (True, dict(pool='test_pool', name='test_task'), dict(pool='test_pool', name='test_task')),
    (False, dict(pool='test_pool', name='test_task'), dict(pool='test_pool', name='test_task')),
    (True, dict(), dict(name='Nile transformation task mock_task', pool=Pool.TAXI_DWH_PRIORITY)),
    (False, dict(), dict(name='Nile transformation task mock_task', pool=Pool.TAXI_DWH_PRIORITY)),
])
def test_nile_config(table, config_first, config, expected):
    table_path = YTMeta(table).target_path()

    def accessor(args, stream):
        return stream

    def get_source(func, env):
        config_decorator = nile_config(**config)
        source_decorator = nile_source(stream=table_path)
        if config_first:
            accessor = config_decorator(func)
            accessor = source_decorator(accessor)
        else:
            accessor = source_decorator(func)
            accessor = config_decorator(accessor)
        return accessor.get_value(None, env)

    env = transform.TransformationEnvironment(task=MockTask())
    env.task.name = 'mock_task'
    source = get_source(accessor, env)
    patch_job = mock.patch('dmp_suite.yt.task.etl.nile_transform.cu.get_job')
    patch_source_yt_etl = mock.patch('dmp_suite.yt.task.etl.transform.etl')
    with patch_job as job_mock, patch_source_yt_etl:
        with source.source_table(contextlib.nullcontext()) as src:
            # если декоратор с конфигами применяется первым, то у декорируемой
            # ф-ции появляется доп атрибут
            assert hasattr(accessor, '__task_source_config__') is config_first
            assert job_mock.call_args[1] == expected


def test_nile_config_args_diff():
    get_job_args = set(inspect.getfullargspec(cu.get_job).args)
    # что-то сомнительное
    get_job_args -= {'enable_legacy_live_preview'}
    nile_config_args = set(inspect.getfullargspec(nile_config).kwonlyargs)

    assert not nile_config_args.difference(get_job_args)
    assert not get_job_args.difference(nile_config_args)
