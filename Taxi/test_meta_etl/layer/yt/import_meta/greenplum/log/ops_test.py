import argparse

import pytest
from typing import Type

from dmp_suite.datetime_utils import Period
from dmp_suite.yt import operation as ytop, YTMeta, YTTable, join_path_parts
from meta_etl.layer.yt.import_meta.greenplum.log.ops import merge_by_day, _get_yt_table
from test_dmp_suite.yt.utils import random_yt_table
import mock


def _prepare_data(yt_folder: str):
    partitions = [
        '2020-12-31 00:00:00',
        '2020-12-31 01:00:00',
        '2020-12-31 02:00:00',
        '2021-01-01 01:00:00',
        '2021-01-01 02:00:00',
        '2021-01-02 02:00:00',
    ]

    for partition in partitions:
        partition_path = join_path_parts(yt_folder, partition)
        ytop.init_yt_table(
            path=partition_path,
            attributes=None
        )
        ytop.write_yt_table(
            table_path=partition_path,
            data=[{'data': partition}]
        )


@pytest.mark.slow
def test_merge_by_day():
    yt_table: Type[YTTable] = random_yt_table(_get_yt_table())
    period = Period('2020-12-31 00:00:00', '2021-01-02 23:59:59')
    with mock.patch('meta_etl.layer.yt.import_meta.greenplum.log.ops._get_yt_table', return_value=yt_table):
        yt_folder = YTMeta(yt_table).target_folder_path
        _prepare_data(yt_folder)
        merge_by_day(argparse.Namespace(period=period))

        expected_partitions = [
            '2020-12-31 00:00:00',
            '2021-01-01 00:00:00',
            '2021-01-02 00:00:00',
        ]

        result_partitions = list(ytop.get_yt_children(
            yt_folder,
            absolute=False
        ))

        assert expected_partitions == result_partitions

        def read_partition(partition):
            return list(
                ytop.read_yt_table(
                    join_path_parts(yt_folder, partition)
                )
            )

        expected_20201231 = [
            {'data': '2020-12-31 00:00:00'},
            {'data': '2020-12-31 01:00:00'},
            {'data': '2020-12-31 02:00:00'},
        ]
        assert expected_20201231 == read_partition('2020-12-31 00:00:00')

        expected_20210101 = [
            {'data': '2021-01-01 01:00:00'},
            {'data': '2021-01-01 02:00:00'},
        ]
        assert expected_20210101 == read_partition('2021-01-01 00:00:00')

        expected_20210102 = [
            {'data': '2021-01-02 02:00:00'},
        ]
        assert expected_20210102 == read_partition('2021-01-02 00:00:00')


