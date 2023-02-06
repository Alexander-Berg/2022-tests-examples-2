import argparse

from dmp_suite.datetime_utils import Period
from dmp_suite.yt import YTTable, Int, YTMeta, etl, ETLTable, DayPartitionScale, \
    String, Datetime
from dmp_suite.yt import operation as yt
from dmp_suite.yt.task.etl import transform


class Table(YTTable):
    a = Int()
    b = Int()


class MockTask(transform.TransformationTask):
    target_table = Table

    def __init__(self):
        super(MockTask, self).__init__('mock_task', None, None, Table)


class DttmTable(YTTable):
    __unique_keys__ = True
    id = String(sort_key=True, sort_position=0)
    dttm = Datetime()
    name = String()


class PartitionedTable(ETLTable):
    __unique_keys__ = True
    __partition_scale__ = DayPartitionScale('dttm')

    id = String(sort_key=True, sort_position=0)
    dttm = Datetime()
    name = String()


def assert_filtered_date_range_partitioned(partitioned_table, source_accessor):
    etl.init_target_table(YTMeta(partitioned_table, '2010-10-09'))
    yt.write_yt_table(
        YTMeta(partitioned_table, '2010-10-09').target_path(),
        [dict(id='a', dttm='2010-10-09 10:00:00', name='a1')]
    )

    etl.init_target_table(YTMeta(partitioned_table, '2010-10-10'))
    yt.write_yt_table(
        YTMeta(partitioned_table, '2010-10-10').target_path(),
        [
            dict(id='b', dttm='2010-10-10 10:00:00', name='b1'),
            dict(id='c', dttm='2010-10-10 13:00:00', name='c1'),
            dict(id='d', dttm='2010-10-10 14:00:00', name='d1'),
            dict(id='f', dttm='2010-10-10 16:00:00', name='f1'),
        ]
    )

    args = argparse.Namespace(
        period=Period('2010-10-10 12:00:00', '2010-10-10 15:00:00')
    )
    env = transform.TransformationEnvironment(task=MockTask())
    source = source_accessor.get_value(args, env)

    with etl.temporary_path_factory() as path_factory:
        with source.source_table(path_factory) as src:
            assert [dict(id='c'), dict(id='d')] == list(yt.read_yt_table(src))


def assert_filtered_date_range_non_partition(yt_table, source_accessor):
    etl.init_target_table(YTMeta(yt_table))
    yt.write_yt_table(
        YTMeta(yt_table).target_path(),
        [
            dict(id='a', dttm='2010-10-09 10:00:00', name='a1'),
            dict(id='b', dttm='2010-10-10 10:00:00', name='b1'),
            dict(id='c', dttm='2010-10-10 13:00:00', name='c1'),
            dict(id='d', dttm='2010-10-10 14:00:00', name='d1'),
            dict(id='f', dttm='2010-10-10 16:00:00', name='f1'),
        ]
    )

    args = argparse.Namespace(
        period=Period('2010-10-10 12:00:00', '2010-10-10 15:00:00')
    )
    env = transform.TransformationEnvironment(task=MockTask())
    source = source_accessor.get_value(args, env)

    with etl.temporary_path_factory() as path_factory:
        with source.source_table(path_factory) as src:
            assert [dict(id='c'), dict(id='d')] == list(yt.read_yt_table(src))
