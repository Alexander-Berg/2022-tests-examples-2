import mock
import pytest
from yt.wrapper.errors import YtHttpResponseError

from connection.yt import Pool, Cluster
from dmp_suite.exceptions import DWHError
from dmp_suite.yt.maintenance.merge_compress.common import PartitionNode
from dmp_suite.yt.maintenance.merge_compress.task import find_and_compress_tables
from dmp_suite.yt.maintenance.merge_compress.partition_priority import MAX_ERROR_COUNT
from dmp_suite.yt import RawHistoryLayout, MonthPartitionScale, Date, ETLTable, YTMeta


class TestTable(ETLTable):
    __layout__ = RawHistoryLayout('test', 'test')
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt')

    dt = Date(sort_key=True, sort_position=0)


def _do_raise(*args, **kwargs):
    raise YtHttpResponseError(
        {'message': 'test'}, 'url', {}, {}
    )


def _do_nothing(*args, **kwargs):
    return


PARTITION_ATTRS = {
    'resource_usage': {
        'disk_space': 100500,
        'chunk_count': 2
    },
    'dynamic': False,
    'content_revision': 500100,
    'compression_codec': 'zlib_9',
    'erasure_codec': 'none'
}

@pytest.mark.skip(reason='DMPDEV-4669')
def test_threshold_find_and_compress_tables():
    mock_get_partitions = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.task.get_all_available_partitions',
        mock.MagicMock(
            return_value=[PartitionNode(YTMeta(TestTable), PARTITION_ATTRS) for _ in range(2 * MAX_ERROR_COUNT + 1)]
        )
    )

    mock_merge_and_compress_partition = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.task.merge_and_compress_partition',
        _do_raise
    )

    mock_logger = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_priority.logger.warning',
    )

    # Независимо от кол-ва воркеров всегда происходит одно и то же
    for max_workes in range(1, 15):
        with mock_get_partitions, mock_merge_and_compress_partition, mock_logger as warn:
            with pytest.raises(DWHError):
                find_and_compress_tables('root_etl', 'task_name', Pool.RESEARCH, cluster=Cluster.HAHN,
                                         max_workers=max_workes)

                assert MAX_ERROR_COUNT <= warn.call_count < 2 * MAX_ERROR_COUNT


def test_success_find_and_compress_tables():
    mock_get_partitions = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.task.get_all_available_partitions',
        mock.MagicMock(
            return_value=[PartitionNode(YTMeta(TestTable), PARTITION_ATTRS) for _ in range(2 * MAX_ERROR_COUNT + 1)]
        )
    )

    mock_merge_and_compress_partition = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.task.merge_and_compress_partition',
        _do_nothing
    )

    mock_logger = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_priority.logger.warning',
    )

    # Независимо от кол-ва воркеров всегда происходит одно и то же
    for max_workes in range(1, 2):
        with mock_get_partitions, mock_merge_and_compress_partition, mock_logger as warn:
            # Вызов функии должен завершиться успешно
            find_and_compress_tables('root_etl', 'task_name', Pool.RESEARCH, cluster=Cluster.HAHN,
                                     max_workers=max_workes)

            assert warn.call_count == 0
