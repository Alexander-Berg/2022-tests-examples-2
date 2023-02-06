import pytest

from dmp_suite.yt import YTMeta
from dmp_suite.yt.etl import ETLTable
from dmp_suite.yt.maintenance.merge_compress.common import PartitionNode
from dmp_suite.yt.maintenance.merge_compress.content_revision_operation import CONTENT_REVISION
from dmp_suite.yt.maintenance.merge_compress.partition_priority import (
    MAX_ERROR_COUNT, PartitionOrderByPriorityIterator
)
from dmp_suite.yt.table import Date, MonthPartitionScale, RawHistoryLayout


class TestTable(ETLTable):
    __layout__ = RawHistoryLayout('test', 'test')
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt')

    dt = Date(sort_key=True, sort_position=0)


PARTITIONS = [
    PartitionNode(
        YTMeta(TestTable, '2021-01-01'),
        {
            CONTENT_REVISION: 100500,
            'compression_codec': 'zlib_9',
            'erasure_codec': 'none',
            'resource_usage': {
                'disk_space': 2,
                'chunk_count': 2
            },
            'dynamic': True
        }
    ),
    PartitionNode(
        YTMeta(TestTable, '2021-02-01'),
        {
            CONTENT_REVISION: 100500,
            'compression_codec': 'zlib_9',
            'erasure_codec': 'none',
            'resource_usage': {
                'disk_space': 100500,
                'chunk_count': 2
            },
            'dynamic': False
        }
    ),
    PartitionNode(
        YTMeta(TestTable, '2021-03-01'),
        {
            CONTENT_REVISION: 100500,
            'compression_codec': 'zlib_9',
            'erasure_codec': 'none',
            'resource_usage': {
                'disk_space': 12,
                'chunk_count': 100500
            },
            'dynamic': False
        }
    ),
    PartitionNode(
        YTMeta(TestTable, '2021-04-01'),
        {
            CONTENT_REVISION: 100500,
            'compression_codec': 'zlib_9',
            'erasure_codec': 'none',
            'resource_usage': {
                'disk_space': 1,
                'chunk_count': 1
            },
            'dynamic': True
        }
    ),
]


@pytest.mark.skip(reason="Подкручивааем приоритеты: DMPDEV-4647")
def test_just_work():
    expected_oreder = ['2021-01-01', '2021-04-01', '2021-03-01', '2021-02-01']

    assert len(list(PartitionOrderByPriorityIterator(PARTITIONS))) == 4

    for partition, expected in zip(PartitionOrderByPriorityIterator(PARTITIONS), expected_oreder):
        assert partition.meta.partition == expected


@pytest.mark.skip(reason="Подкручивааем приоритеты: DMPDEV-4647")
def test_black_list():
    partition_iter = PartitionOrderByPriorityIterator(PARTITIONS)

    count = 0
    while True:
        try:
            partition = next(partition_iter)
            partition_iter.add_to_blacklist(partition.meta.table_class)
            count += 1
        except StopIteration:
            break
    assert count == MAX_ERROR_COUNT
