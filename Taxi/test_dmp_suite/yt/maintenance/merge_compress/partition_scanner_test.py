from datetime import datetime, timedelta

import mock

from dmp_suite import datetime_utils as dtu
from dmp_suite.table import OdsLayout
from dmp_suite.yt import YTMeta, YTTable, Datetime, DayPartitionScale
from dmp_suite.yt.maintenance.merge_compress.content_revision_operation import (
    CONTENT_REVISION, DMP_MERGE_CONTENT_REVISION
)
from dmp_suite.yt.maintenance.merge_compress.partition_scanner import (
    select_dynamic_or_compressible_partitions,
    get_first_unmerged_partition,
    DEFAULT_TIMEDELTA
)


def test_get_first_unmerged_partition():
    class MyTable(YTTable):
        __layout__ = OdsLayout(name='random_layout', source='scooter')
        __partition_scale__ = DayPartitionScale(
            'utc_created_dttm',
            compression_delay_day_cnt=31
        )
        utc_created_dttm = Datetime()

    with mock.patch(
            'dmp_suite.yt.maintenance.merge_compress.partition_scanner.dtu.utcnow',
            return_value=datetime(2021, 1, 1)
    ):
        meta = YTMeta(MyTable)
        assert get_first_unmerged_partition(meta) == dtu.format_date(datetime(2020, 12, 1))


def test_get_first_unmerged_partition_wo_compression_delay_day_cnt():
    class MyTable(YTTable):
        __layout__ = OdsLayout(name='random_layout', source='scooter')
        __partition_scale__ = DayPartitionScale(
            'utc_created_dttm',
        )
        utc_created_dttm = Datetime()

    now = datetime(2021, 1, 1)

    with mock.patch(
            'dmp_suite.yt.maintenance.merge_compress.partition_scanner.dtu.utcnow',
            return_value=now
    ):
        meta = YTMeta(MyTable)
        assert get_first_unmerged_partition(meta) == dtu.format_date(now - DEFAULT_TIMEDELTA)


def test_select_dynamic_or_compressible_partitions():

    my_compression_delay_day_cnt = 10

    class MyTable(YTTable):
        __layout__ = OdsLayout(name='random_layout', source='scooter')
        __partition_scale__ = DayPartitionScale(
            'utc_created_dttm',
            compression_delay_day_cnt=my_compression_delay_day_cnt
        )
        utc_created_dttm = Datetime()

    utc_now = datetime(2021, 1, 1)

    class MyFakeNode:
        def __init__(self, title, attributes):
            self._title = title
            self._attributes = attributes

        def title(self):
            return self._title

        @property
        def attributes(self):
            return self._attributes

    fake_attrs = {
        'type': 'table',
        CONTENT_REVISION: 2,
        DMP_MERGE_CONTENT_REVISION: 1,
        'dynamic': False,
        'compression_codec': 'dog',
        'erasure_codec': 'cat',
        'resource_usage': {
            'chunk_count': 100500,
            'disk_space': 100500
        }
    }

    mock_utc_now = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_scanner.dtu.utcnow',
        return_value=utc_now
    )
    mock_get_yt_children = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_scanner.op.get_yt_children',
        return_value=[
            MyFakeNode(f'2020-12-{dd}', fake_attrs) for dd in range(10, 32)
        ]
    )
    mock_yt_path_exists = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_scanner.op.yt_path_exists',
        return_value=True
    )

    class YTClient:
        def get_attribute(self, *args, **kwargs):
            return None

    mock_yt_check_attr = mock.patch(
        'dmp_suite.yt.maintenance.merge_compress.partition_scanner.get_yt_client',
        return_value=YTClient()
    )

    with mock_utc_now, mock_get_yt_children, mock_yt_path_exists, mock_yt_check_attr:
        partition_nodes = list(select_dynamic_or_compressible_partitions(MyTable))
        assert len(partition_nodes) > 0
        corner_partition = dtu.format_date(utc_now - timedelta(my_compression_delay_day_cnt))

        for partition_node in partition_nodes:
            assert partition_node.meta.partition < corner_partition
