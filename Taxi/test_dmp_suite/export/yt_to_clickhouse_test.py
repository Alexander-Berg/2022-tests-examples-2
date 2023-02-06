# coding: utf-8
import uuid
import pytest

from dmp_suite import yt, clickhouse
from dmp_suite.datetime_utils import date_period
from dmp_suite.export import yt_to_clickhouse as y2c
from dmp_suite.yt import YTMeta, NotLayeredYtTable, NotLayeredYtLayout, operation as yt_op
from dmp_suite.clickhouse import CHTable, CHMeta, operation as clickhouse_op, CHLayout


# Automated ClickHouse integration tests are currently outlawed.
@pytest.mark.manual
@pytest.mark.slow
def test_export_partition_increment(source_table, destination_table):
    source_partition = yt.YTMeta(source_table, partition="2019-03-01")
    destination_partition = CHMeta(destination_table, partition="2019-03-01")

    old_data = [
        "2019-03-03\told_value_3\n",
        "2019-03-04\told_value_4\n",
        "2019-03-05\told_value_5\n",
        "2019-03-06\told_value_6\n",
    ]
    increment_data = [
        {"dt": "2019-03-03", "value": "new_value_3"},
        {"dt": "2019-03-04", "value": "new_value_4"},
        {"dt": "2019-03-05", "value": "new_value_5"},
        {"dt": "2019-03-06", "value": "new_value_6"},
    ]
    expected_new_data = [
        ["2019-03-03", "old_value_3"],
        ["2019-03-04", "new_value_4"],
        ["2019-03-05", "new_value_5"],
        ["2019-03-06", "old_value_6"],
    ]

    clickhouse_op.create_table(destination_partition)
    clickhouse_op.insert_to_target(destination_partition, old_data)

    yt_op.init_yt_table(source_partition.target_path(), source_partition.attributes())
    yt_op.write_yt_table(source_partition.target_path(), increment_data)

    y2c.export_partition_increment(
        source_partition,
        destination_partition,
        period=date_period("2019-03-04", "2019-03-05"),
    )

    actual_new_data = get_table_data(destination_partition)
    assert list(sorted(actual_new_data)) == list(sorted(expected_new_data))


def get_table_data(meta):
    return clickhouse_op.impl.run_query(
        "SELECT * FROM {table_name}".format(table_name=meta.table_full_name()),
        ignore_result=False,
    )


@pytest.fixture
def source_table():
    entity_name = uuid.uuid4().hex

    class SourceTable(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('test', entity_name)
        __partition_scale__ = yt.MonthPartitionScale("dt")

        dt = yt.Date()
        value = yt.String()

    try:
        yield SourceTable
    finally:
        yt_op.remove_yt_node(YTMeta(SourceTable).target_path())
        yt_op.remove_yt_node(YTMeta(SourceTable).rotation_path())
        yt_op.remove_yt_node(YTMeta(SourceTable).buffer_path())


@pytest.fixture
def destination_table():
    # Adding a first letter to make a valid name.
    table_name = "t" + uuid.uuid4().hex

    class DestinationTable(CHTable):
        __layout__ = CHLayout(table_name, db='test', prefix_key='test')
        __engine__ = clickhouse.MergeTreeEngine(
            partition_key="dt"
        )

        dt = clickhouse.Date()
        value = clickhouse.String()

    try:
        yield DestinationTable
    finally:
        clickhouse_op.drop_table(CHMeta(DestinationTable))
        clickhouse_op.drop_rotation_table(CHMeta(DestinationTable))
