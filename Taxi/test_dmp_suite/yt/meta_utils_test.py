import pytest

from dmp_suite.table import RawLayout
from dmp_suite.yt import (
    etl,
    YTMeta,
    NotLayeredYtTable,
    MonthPartitionScale,
    Datetime,
    YTTable)
from dmp_suite import datetime_utils as dtu
from dmp_suite.yt.partitions_utils import range_partitions, Partition
from dmp_suite.yt.partitions_utils import period_from_table_partitions
from test_dmp_suite.yt import utils
from dmp_suite.yt import operation as op


class PartitionTable(NotLayeredYtTable):
    __partition_scale__ = MonthPartitionScale('partition_key')
    partition_key = Datetime()


class NotPartitionedTable(YTTable):
    __layout__ = RawLayout('test', 'test')
    just_date = Datetime()


partition_test_table = utils.fixture_random_yt_table(PartitionTable)


@pytest.mark.slow
def test_range_partitions(partition_test_table):
    partition = '2017-11-01'
    link = '2017-12-01'

    meta = YTMeta(partition_test_table)
    partition_meta = meta.with_partition(partition)

    partition_path = partition_meta.target_path()
    link_path = partition_meta.target_folder_path + '/' + link

    op.init_yt_table(partition_path, partition_meta.attributes())
    op.create_link(partition_meta.target_path(), link_path)

    assert [p.name for p in range_partitions(meta, '2017-11-07 12:12:12', '2017-11-07 12:12:16')] == [partition]
    assert [p.name for p in range_partitions(meta, '2017-12-07 12:12:12', '2017-12-07 12:12:16')] == [link]
    assert [p.name for p in range_partitions(meta, '2017-11-07 12:12:12')] == [partition, link]

    assert not [p.name for p in range_partitions(meta, '2017-10-07 12:12:12', '2017-10-07 12:12:16')]
    assert not [p.name for p in range_partitions(meta, '2018-01-07 12:12:12', '2018-01-07 12:12:16')]

    # Test 'extra_attrs'
    # No period
    actual_partition_nodes = range_partitions(meta, extra_attrs=['dynamic'])
    assert list(map(lambda p: p.name, actual_partition_nodes)) == [partition, link]

    is_dynamic = next(
        map(
            lambda t: t.attributes['dynamic'],
            actual_partition_nodes
        )
    )
    assert not is_dynamic

    # With a period
    actual_partition_nodes_period = range_partitions(
        meta,
        '2017-11-07 12:12:12',
        '2017-12-07 12:12:16',
        extra_attrs=['dynamic']
    )

    assert actual_partition_nodes_period == actual_partition_nodes
    for partition in actual_partition_nodes:
        assert partition.attributes.get('type') == 'table'
        assert not partition.attributes['dynamic']


@pytest.mark.slow
def test_period_from_table_partitions(partition_test_table):
    partitions = ['2017-11-01', '2017-10-01', '2017-12-01']

    meta = YTMeta(partition_test_table)

    for partition in partitions:
        etl.init_target_table(meta.with_partition(partition))

    assert period_from_table_partitions(meta) == dtu.Period(
        '2017-10-01 00:00:00.000000',
        '2017-12-31 23:59:59.999999',
    )


@pytest.mark.slow
def test_all_partitions(partition_test_table):
    partitions = [
        '2017-10-01',
        # Эта партиция специально пропущена. Её создавать не будем
        # и all_partitions не должен её возвращать, так как он
        # возвращает только то, что реально есть в YT, в случае партиционированных
        # таблиц:
        # '2017-11-01',
        '2017-12-01',
    ]

    meta = YTMeta(partition_test_table)

    for partition in partitions:
        etl.init_target_table(meta.with_partition(partition))

    expected_paths = [
        meta.with_partition(partition).target_path()
        for partition in partitions
    ]

    assert meta.all_partition_paths == expected_paths


@pytest.mark.slow
def test_all_partitions_for_non_partitioned_table():
    meta = YTMeta(NotPartitionedTable)

    # Так как all_partitions гарантирует, что таблички существуют в YT,
    # а мы пока таблицу не проинициализировали, то ждём, что метод отдаст
    # пустой список:
    assert meta.all_partition_paths == []

    # После инициализации он должен отдавать список с одной только таргетной таблицей:
    etl.init_target_table(meta)

    assert meta.all_partition_paths == [meta.target_path()]
