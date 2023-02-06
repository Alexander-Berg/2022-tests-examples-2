import operator

import pytest

from dmp_suite import exceptions
from dmp_suite import extract_utils as eu
from dmp_suite import yt
from dmp_suite.yt import etl
from dmp_suite.yt import operation as op
from dmp_suite.yt.dyntable_operation import dynamic_table_loaders
from dmp_suite.yt.dyntable_operation import operations as dyn_op

from test_dmp_suite.yt import utils as yt_test_utils


RAW_DATA = [
    {
        'id': 1,
        'doc': {
            'id': 1,
            'value': 'b',
            'utc_created_dttm': '2020-01-01 00:00:00',
            'utc_updated_dttm': '2020-01-01 00:00:00',
        },
        'utc_created_dttm': '2020-01-01 00:00:00',
    },
    {
        'id': 2,
        'doc': {
            'id': 2,
            'value': 'b',
            'utc_created_dttm': '2018-01-01 00:00:00',
            'utc_updated_dttm': '2019-01-01 00:00:00',
        },
        'utc_created_dttm': '2018-01-01 00:00:00',
    },
    {
        'id': 3,
        'doc': {
            'id': 3,
            'value': 'b',
            'utc_created_dttm': '1970-01-02 00:00:01',
            'utc_updated_dttm': '1975-01-02 00:00:01',
        },
        'utc_created_dttm': '1970-01-02 00:00:01',
    },
]


HISTORY_DATA = [
    {
        'utc_updated_dttm': '1975-01-02 00:00:01',
        'id': 3,
        'doc': {
            'id': 3,
            'value': 'b',
            'utc_created_dttm': '1970-01-02 00:00:01',
            'utc_updated_dttm': '1975-01-02 00:00:01',
        },
    },
    {
        'utc_updated_dttm': '2019-01-01 00:00:00',
        'id': 2,
        'doc': {
            'id': 2,
            'value': 'b',
            'utc_created_dttm': '2018-01-01 00:00:00',
            'utc_updated_dttm': '2019-01-01 00:00:00',
        },
    },
    {
        'utc_updated_dttm': '2020-01-01 00:00:00',
        'id': 1,
        'doc': {
            'id': 1,
            'value': 'b',
            'utc_created_dttm': '2020-01-01 00:00:00',
            'utc_updated_dttm': '2020-01-01 00:00:00',
        },
    },
]


@yt_test_utils.random_yt_table
class DummyRawTable(yt.YTTable):
    __unique_keys__ = True
    __dynamic__ = True
    __partition_scale__ = yt.ShortYearPartitionScale('utc_created_dttm')

    id = yt.Int(sort_key=True, sort_position=0)
    doc = yt.Any()
    utc_created_dttm = yt.Datetime()


@yt_test_utils.random_yt_table
class DummyRawHistoryTable(yt.YTTable):
    __unique_keys__ = True
    __dynamic__ = True
    __partition_scale__ = yt.ShortMonthPartitionScale('utc_updated_dttm')

    utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
    id = yt.Int(sort_key=True, sort_position=1)
    doc = yt.Any()


def assert_data_in_table(table, expected_data):
    def read(_meta):
        if _meta.has_partition_scale:
            for partition_path in op.get_yt_children(_meta.target_folder_path):
                for row in op.read_yt_table(partition_path):
                    yield row
        else:
            for row in op.read_yt_table(_meta.target_path()):
                yield row

    meta = yt.YTMeta(table)
    data = list(read(meta))

    expected_data = list(expected_data)  # shallow copy

    assert len(data) == len(expected_data)

    for sort_key in reversed(meta.sort_key_names()):
        data = sorted(data, key=operator.itemgetter(sort_key))
        expected_data = sorted(
            expected_data, key=operator.itemgetter(sort_key),
        )

    assert data == expected_data


def assert_partitions(table, expected_partitions):
    meta = yt.YTMeta(table)
    actual_partitions = list(
        sorted(op.get_yt_children(meta.target_folder_path, absolute=False))
    )
    assert sorted(expected_partitions) == actual_partitions


def fill_table(table, data):
    dynamic_table_loaders.upload(
        data=data,
        yt_table_or_meta=table,
        extractors={},
    )
    meta = yt.YTMeta(table)
    # dumps data on disk
    dyn_op.unmount_all_partitions(meta)
    dyn_op.mount_all_partitions(meta)


def cleanup_table(table):
    meta = yt.YTMeta(table)
    if not op.yt_path_exists(meta.target_folder_path):
        return
    dyn_op.unmount_all_partitions(meta)
    op.remove_yt_table(meta.target_folder_path, recursive=True)


@pytest.fixture()
def fill_raw():
    fill_table(DummyRawTable, RAW_DATA)


@pytest.fixture()
def cleanup_all():
    yield
    cleanup_table(DummyRawTable)
    cleanup_table(DummyRawHistoryTable)


@pytest.mark.slow
@pytest.mark.usefixtures('fill_raw')
@pytest.mark.usefixtures('cleanup_all')
def test_history_initialization():
    etl.initialize_history(
        source_table=DummyRawTable,
        target_table=DummyRawHistoryTable,
        extractors={
            'id': 'id',
            'doc': eu.raw_record_extractor,
            'utc_updated_dttm': 'utc_updated_dttm',
        }
    )

    assert_data_in_table(DummyRawHistoryTable, HISTORY_DATA)
    assert_partitions(DummyRawHistoryTable, [
        '1975-01',
        '2019-01',
        '2020-01',
    ])


@pytest.mark.slow
@pytest.mark.usefixtures('cleanup_all')
def test_fail_on_non_empty_history_dir():
    fill_table(DummyRawHistoryTable, HISTORY_DATA)
    with pytest.raises(exceptions.NotSupportedError):
        etl.initialize_history(
            source_table=DummyRawTable,
            target_table=DummyRawHistoryTable,
        )
