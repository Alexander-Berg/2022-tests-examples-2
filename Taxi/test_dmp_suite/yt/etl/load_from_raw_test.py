from typing import List, Dict

import pytest

from nile.api.v1 import Record

from dmp_suite.yt import (
    YTTable, YTMeta,
    Date, Int, Any,
    DayPartitionScale, MonthPartitionScale,
    operation as op,
    split_to_partitions,
    etl,
)
from dmp_suite import datetime_utils as dtu
from dmp_suite import data_transform
from dmp_suite.exceptions import UnsupportedTableError
from test_dmp_suite.yt import utils


class RawTestTable(YTTable):
    dt = Date()
    doc = Any()


raw_test_table = utils.fixture_random_yt_table(RawTestTable)


class RawTestDailyTable(YTTable):
    __partition_scale__ = DayPartitionScale('dt')

    dt = Date()
    doc = Any()


raw_test_daily_table = utils.fixture_random_yt_table(RawTestDailyTable)


class TawTestMonthlyTable(YTTable):
    __partition_scale__ = MonthPartitionScale('dt')

    dt = Date()
    doc = Any()


raw_test_monthly_table = utils.fixture_random_yt_table(TawTestMonthlyTable)


class OdsTestTable(YTTable):
    dt = Date()
    count = Int()


ods_test_table = utils.fixture_random_yt_table(OdsTestTable)


class OdsTestDailyTable(YTTable):
    __partition_scale__ = DayPartitionScale('dt')

    dt = Date()
    count = Int()


ods_test_daily_table = utils.fixture_random_yt_table(OdsTestDailyTable)


class OdsTestMonthlyTable(YTTable):
    __partition_scale__ = MonthPartitionScale('dt')

    dt = Date()
    count = Int()


ods_test_monthly_table = utils.fixture_random_yt_table(OdsTestMonthlyTable)


def write_to_target(table, data):
    for partition, partition_data in split_to_partitions(table, data):
        partition_meta = YTMeta(table, partition=partition)

        etl.init_target_table(partition_meta, replace=False)
        op.write_yt_table(partition_meta.target_path(), partition_data)


def read_from_target(table):
    meta = YTMeta(table)

    if meta.has_partition_scale:
        for partition_path in op.get_yt_children(meta.target_folder_path):
            for row in op.read_yt_table(partition_path):
                yield row
    else:
        for row in op.read_yt_table(meta.target_path()):
            yield row


def sorted_records(records):
    return sorted(records, key=lambda row: sorted(row.items()))


@pytest.mark.slow
class TestLoadFromRaw(object):
    def test_creates_table(self, raw_test_table, ods_test_table):
        RAW_DATA = [
            {'dt': None, 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-05', 'count': 43}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_table, raw_test_table, RAW_DATA
        )
        self.assertTargetDataEqual(
            ods_test_table, EXPECTED_DATA
        )

    def test_reloads_table(self, raw_test_table, ods_test_table):
        RAW_DATA = [
            {'dt': None, 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        OLD_TARGET_DATA = [
            {'dt': '2018-12-04', 'count': 42}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-05', 'count': 43}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_table, raw_test_table, RAW_DATA,
            old_target_data=OLD_TARGET_DATA
        )
        self.assertTargetDataEqual(
            ods_test_table, EXPECTED_DATA
        )

    def test_updates_table(self, raw_test_table, ods_test_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-06 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '44'}},
            {'dt': '2018-12-06', 'doc': {'dt': '2018-12-06', 'count': '48'}}
        ]
        OLD_TARGET_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 43}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 44},
            {'dt': '2018-12-06', 'count': 48}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_table, raw_test_table, RAW_DATA,
            old_target_data=OLD_TARGET_DATA, period=PERIOD, by_field='dt'
        )
        self.assertTargetDataEqual(
            ods_test_table, EXPECTED_DATA
        )

    def test_creates_one_partition(
            self, raw_test_daily_table, ods_test_daily_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '44'}}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-05', 'count': 44}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_daily_table, raw_test_daily_table, RAW_DATA,
            period=PERIOD
        )
        self.assertTargetDataEqual(
            ods_test_daily_table, EXPECTED_DATA
        )

    def test_reloads_one_partition_and_creates_one_partition(
            self, raw_test_daily_table, ods_test_daily_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-06 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '44'}},
            {'dt': '2018-12-06', 'doc': {'dt': '2018-12-06', 'count': '48'}}
        ]
        OLD_TARGET_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 43}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 44},
            {'dt': '2018-12-06', 'count': 48}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_daily_table, raw_test_daily_table, RAW_DATA,
            old_target_data=OLD_TARGET_DATA, period=PERIOD
        )
        self.assertTargetDataEqual(
            ods_test_daily_table, EXPECTED_DATA
        )

    def test_updates_one_partition_from_smaller_scale_partition(
            self, raw_test_daily_table, ods_test_monthly_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '44'}},
            {'dt': '2018-12-06', 'doc': {'dt': '2018-12-06', 'count': '48'}}
        ]
        OLD_TARGET_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 43},
            {'dt': '2018-12-06', 'count': 51}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 44},
            {'dt': '2018-12-06', 'count': 51}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_monthly_table, raw_test_daily_table, RAW_DATA,
            old_target_data=OLD_TARGET_DATA, period=PERIOD
        )
        self.assertTargetDataEqual(
            ods_test_monthly_table, EXPECTED_DATA
        )

    def test_updates_one_partition_from_partition_fragment(
            self, raw_test_monthly_table, ods_test_monthly_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '44'}},
            {'dt': '2018-12-06', 'doc': {'dt': '2018-12-06', 'count': '48'}}
        ]
        OLD_TARGET_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 43},
            {'dt': '2018-12-06', 'count': 51}
        ]
        EXPECTED_DATA = [
            {'dt': '2018-12-04', 'count': 42},
            {'dt': '2018-12-05', 'count': 44},
            {'dt': '2018-12-06', 'count': 51}
        ]

        self.prepare_tables_and_load_from_raw(
            ods_test_monthly_table, raw_test_monthly_table, RAW_DATA,
            old_target_data=OLD_TARGET_DATA, period=PERIOD
        )
        self.assertTargetDataEqual(
            ods_test_monthly_table, EXPECTED_DATA
        )

    def test_validates_period(self, raw_test_daily_table, ods_test_daily_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-04', 'doc': {'dt': '2018-12-04', 'count': '41'}},
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-06', 'count': '44'}}
        ]
        with pytest.raises(Exception):
            self.prepare_tables_and_load_from_raw(
                ods_test_daily_table, raw_test_daily_table, RAW_DATA,
                period=PERIOD
            )

    def test_requires_by_field_when_both_unpartitioned(
            self, raw_test_table, ods_test_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        with pytest.raises(UnsupportedTableError):
            self.prepare_tables_and_load_from_raw(
                ods_test_table, raw_test_table, RAW_DATA,
                period=PERIOD
            )

    def test_requires_unpartitioned_source_table(
            self, raw_test_daily_table, ods_test_table):
        RAW_DATA = [
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        with pytest.raises(UnsupportedTableError):
            self.prepare_tables_and_load_from_raw(
                ods_test_table, raw_test_daily_table, RAW_DATA
            )

    def test_requires_unpartitioned_destination_table(
            self, raw_test_table, ods_test_daily_table):
        RAW_DATA = [
            {'dt': None, 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        with pytest.raises(UnsupportedTableError):
            self.prepare_tables_and_load_from_raw(
                ods_test_daily_table, raw_test_table, RAW_DATA
            )

    def test_requires_partitioned_source_table(
            self, raw_test_table, ods_test_daily_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': None, 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        with pytest.raises(UnsupportedTableError):
            self.prepare_tables_and_load_from_raw(
                ods_test_daily_table, raw_test_table, RAW_DATA,
                period=PERIOD
            )

    def test_requires_partitioned_destination_table(
            self, raw_test_daily_table, ods_test_table):
        PERIOD = dtu.Period('2018-12-05 00:00:00', '2018-12-05 23:59:59')
        RAW_DATA = [
            {'dt': '2018-12-05', 'doc': {'dt': '2018-12-05', 'count': '43'}}
        ]
        with pytest.raises(UnsupportedTableError):
            self.prepare_tables_and_load_from_raw(
                ods_test_table, raw_test_daily_table, RAW_DATA,
                period=PERIOD
            )

    def prepare_tables_and_load_from_raw(
            self,
            target_table, raw_table,
            raw_data, old_target_data=None, period=None, by_field=None
    ):
        write_to_target(raw_table, raw_data)

        if old_target_data is not None:
            write_to_target(target_table, old_target_data)

        etl.load_from_raw(
            target_table=target_table,
            raw_table=raw_table,
            period=period,
            by_field=by_field
        )

    def assertTargetDataEqual(self, table, expected_data):
        actual_data = list(read_from_target(table))
        assert sorted_records(actual_data) == sorted_records(expected_data)


class Table(YTTable):
    id = Int()
    val = Int()


def assert_mapper(
    mapper: etl.FromRawMapper,
    records: List[Dict],
    expected: List[Dict],
):
    assert list(mapper(records)) == list(map(Record.from_dict, expected))


class TestFromRawMapper:
    def test_from_raw_mapper_defaults(self):
        mapper = etl.FromRawMapper(Table)
        assert_mapper(
            mapper,
            [dict(doc=dict(id=1, val=2))],
            [dict(id=1, val=2)],
        )

    def test_from_raw_mapper_doc_field_none(self):
        mapper = etl.FromRawMapper(Table, doc_field=None)
        assert_mapper(
            mapper,
            [dict(id=1, val=2)],
            [dict(id=1, val=2)],
        )

    def test_from_raw_mapper_doc_field_custom(self):
        mapper = etl.FromRawMapper(Table, doc_field='df')
        assert_mapper(
            mapper,
            [dict(df=dict(id=1, val=2))],
            [dict(id=1, val=2)],
        )

    def test_from_raw_mapper_with_extractors(self):
        extractors = dict(val='v')
        mapper = etl.FromRawMapper(Table, extractors=extractors)
        assert_mapper(
            mapper,
            [dict(doc=dict(id=1, v=2))],
            [dict(id=1, val=2)],
        )

    def test_from_raw_mapper_with_extractors_and_transform(self):
        extractors = dict(val='v')
        tramsform = data_transform.UnfoldDictList('a')
        mapper = etl.FromRawMapper(
            table=Table,
            extractors=extractors,
            transform=tramsform
        )
        assert_mapper(
            mapper,
            [dict(doc=dict(a=[dict(id=1, v=2), dict(id=2, v='3')]))],
            [dict(id=1, val=2), dict(id=2, val=3)],
        )
