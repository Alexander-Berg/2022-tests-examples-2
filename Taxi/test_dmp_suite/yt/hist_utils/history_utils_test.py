import pytest
from unittest import TestCase

from dmp_suite import datetime_utils
from dmp_suite.datetime_utils import format_datetime
from dmp_suite.nile import cluster_utils
from dmp_suite.yt import YTMeta, etl, hist_utils
from dmp_suite.yt.hist_utils import (
    DeleteStrategy,
    _NoPartitionHistoryReducer,
    _PartitionHistoryReducer,
)
from test_dmp_suite.yt.hist_utils.data import EFFECTIVE_DATETIME, EFFECTIVE_START_DATETIME, change_ignore_expected, \
    change_ignore_records, change_new_expected, change_new_records, change_update_expected, change_update_records, \
    new_only_expected, new_only_records, old_history, old_only_expected_1, old_only_expected_2, old_only_records_1, \
    old_only_records_2, change_ignore_undeleted_records, change_ignore_undeleted_expected
from dmp_suite.yt.hist_table import MonthPartitionHistTable, DayPartitionHistTable
from test_dmp_suite.yt.hist_utils.table import BaseTestTable
from test_dmp_suite.yt.utils import random_yt_table


delete_track_builder = DeleteStrategy.create_history_builder(
    DeleteStrategy.TRACK,
    YTMeta(BaseTestTable),
    EFFECTIVE_DATETIME
)

delete_track_builder_with_start = DeleteStrategy.create_history_builder(
    DeleteStrategy.TRACK,
    YTMeta(BaseTestTable),
    EFFECTIVE_DATETIME,
    effective_start_datetime=EFFECTIVE_START_DATETIME
)

no_delete_track_builder = DeleteStrategy.create_history_builder(
    DeleteStrategy.NO_TRACK,
    YTMeta(BaseTestTable),
    EFFECTIVE_DATETIME
)


CLUSTER_READ_OPTIONS = dict(bytes_decode_mode='strict')


class TestHistoryBuilder(TestCase):

    def test_only_new(self):
        actual = list(delete_track_builder.build_history(new_only_records))
        self.assertListEqual(actual, new_only_expected)

    def test_only_old(self):
        actual = list(delete_track_builder.build_history(old_only_records_1))
        self.assertListEqual(actual, old_only_expected_1)

        actual = list(delete_track_builder.build_history(old_only_records_2))
        self.assertListEqual(actual, old_only_expected_2)

        actual = list(no_delete_track_builder.build_history(old_only_records_1))
        self.assertListEqual(actual, old_only_records_1)

    def test_change(self):
        # Test NEW
        actual = list(delete_track_builder.build_history(change_new_records))
        self.assertListEqual(actual, change_new_expected)

        # Test UPDATE
        actual = list(delete_track_builder.build_history(change_update_records))
        self.assertListEqual(actual, change_update_expected)

        # Test IGNORE
        actual = list(delete_track_builder.build_history(change_ignore_records))
        self.assertListEqual(actual, change_ignore_expected)

        # Test IGNORE for a previously deleted record.
        actual = list(delete_track_builder.build_history(change_ignore_undeleted_records))
        self.assertListEqual(actual, change_ignore_undeleted_expected)

    def test_reduce(self):
        groups = [
            (1, new_only_records),
            (2, old_only_records_1),
            (3, old_only_records_2),
            (4, change_new_records),
            (5, change_update_records),
            (6, change_ignore_records),
            (7, change_ignore_undeleted_records)
        ]

        delete_track_expected = new_only_expected \
                                + old_only_expected_1 \
                                + old_only_expected_2 \
                                + change_new_expected \
                                + change_update_expected \
                                + change_ignore_expected \
                                + change_ignore_undeleted_expected

        reducer = _NoPartitionHistoryReducer(delete_track_builder)
        actual = list(reducer(groups))
        self.assertListEqual(delete_track_expected, actual)

        no_delete_track_expected = new_only_expected \
                                   + old_only_records_1 \
                                   + old_only_records_2 \
                                   + change_new_expected \
                                   + change_update_expected \
                                   + change_ignore_expected \
                                   + change_ignore_undeleted_expected

        reducer = _NoPartitionHistoryReducer(no_delete_track_builder)
        actual = list(reducer(groups))
        self.assertListEqual(no_delete_track_expected, actual)

        class StreamMock(list):
            def __call__(self, r):
                self.append(r)

        actual_expected = [
            r for r in delete_track_expected
            if hist_utils.is_actual_record(r)
        ]

        history_expected = [
            r for r in delete_track_expected
            if not hist_utils.is_actual_record(r)
        ]

        reducer = _PartitionHistoryReducer(delete_track_builder)
        actual, history = StreamMock(), StreamMock()
        reducer(groups, actual, history)
        self.assertListEqual(actual_expected, actual)
        self.assertListEqual(history_expected, history)

        actual_expected = [
            r for r in no_delete_track_expected
            if hist_utils.is_actual_record(r)
        ]

        history_expected = [
            r for r in no_delete_track_expected
            if not hist_utils.is_actual_record(r)
        ]

        reducer = _PartitionHistoryReducer(no_delete_track_builder)
        actual, history = StreamMock(), StreamMock()
        reducer(groups, actual, history)
        self.assertListEqual(actual_expected, actual)
        self.assertListEqual(history_expected, history)

    # noinspection PyMethodMayBeStatic
    def test_reduce_with_effective_start_dttm(self):
        groups = [
            (1, new_only_records),
            (2, old_only_records_1)
        ]

        reducer = _NoPartitionHistoryReducer(delete_track_builder_with_start)
        actual = list(reducer(groups))
        for row in actual:
            if row['a'] == 1:  # new record
                assert row['effective_from_dttm'] == format_datetime(EFFECTIVE_START_DATETIME)
            if row['a'] == 2:  # existing record
                assert row['effective_from_dttm'] == '2017-05-01 00:00:00'


@pytest.mark.slow
class TestHistoryBuilderSlow(object):

    all_records = new_only_records \
                  + old_only_records_1 \
                  + old_only_records_2 \
                  + change_new_records \
                  + change_update_records \
                  + change_ignore_records \
                  + change_ignore_undeleted_records

    new_records = [
        r for r in all_records
        if not hist_utils._is_valid_history_record(r)
    ]

    old_records = [
        r for r in all_records
        if hist_utils._is_valid_history_record(r)
    ]

    expected = new_only_expected \
               + old_only_expected_1 \
               + old_only_expected_2 \
               + change_new_expected \
               + change_update_expected \
               + change_ignore_expected \
               + change_ignore_undeleted_expected

    expected = sorted(expected, key=lambda r: (r.effective_to_dttm, r.a))

    actual_expected = [
        r for r in expected
        if hist_utils.is_actual_record(r)
    ]

    history_expected = [
        r for r in expected
        if not hist_utils.is_actual_record(r)
    ]

    def test_one_partition_table(self):

        cluster = cluster_utils.get_cluster()

        # Test one partition table
        table = BaseTestTable
        yt_meta = YTMeta(table)
        etl.init_target_table(yt_meta)
        cluster.write(yt_meta.target_path(), self.old_records)
        hist_utils.load(
            table=table,
            data=self.new_records,
            effective_datetime=EFFECTIVE_DATETIME
        )

        actual = list(cluster.read(yt_meta.target_path(), **CLUSTER_READ_OPTIONS))
        assert self.expected == actual

    def test_month_partitions(self):

        @random_yt_table
        class MonthPartitionTestTable(BaseTestTable, MonthPartitionHistTable):
            pass

        cluster = cluster_utils.get_cluster()

        table = MonthPartitionTestTable
        yt_meta = YTMeta(table, datetime_utils.MAX_DATETIME)
        etl.init_target_table(yt_meta)
        cluster.write(yt_meta.target_path(), self.old_records)
        hist_utils.load(
            table=table,
            data=self.new_records,
            effective_datetime=EFFECTIVE_DATETIME
        )

        actual = list(cluster.read(yt_meta.target_path(), **CLUSTER_READ_OPTIONS))
        history = list(
            cluster.read(
                YTMeta(table, EFFECTIVE_DATETIME).target_path(),
                **CLUSTER_READ_OPTIONS
            )
        )
        assert self.actual_expected == actual
        assert self.history_expected == history

    def test_day_partitions(self):

        @random_yt_table
        class DayPartitionTestTable(BaseTestTable, DayPartitionHistTable):
            pass

        cluster = cluster_utils.get_cluster()

        table = DayPartitionTestTable
        yt_meta = YTMeta(table, datetime_utils.MAX_DATETIME)
        etl.init_target_table(yt_meta)
        cluster.write(yt_meta.target_path(), self.old_records)
        hist_meta = YTMeta(table, EFFECTIVE_DATETIME)
        etl.init_target_table(hist_meta)

        cluster.write(hist_meta.target_path(), old_history)
        hist_utils.load(
            table=table,
            data=self.new_records,
            effective_datetime=EFFECTIVE_DATETIME
        )

        actual = list(cluster.read(yt_meta.target_path(), **CLUSTER_READ_OPTIONS))
        history = list(cluster.read(hist_meta.target_path(), **CLUSTER_READ_OPTIONS))
        assert self.actual_expected == actual
        assert old_history + self.history_expected == history
