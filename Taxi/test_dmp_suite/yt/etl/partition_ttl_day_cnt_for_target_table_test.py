import pytest
from datetime import timedelta

from dmp_suite import datetime_utils as dtu
from dmp_suite.yt import etl
from dmp_suite.yt import operation as op
from dmp_suite.table import CustomPartition
from dmp_suite.yt.table import Date, Datetime, Int, MonthPartitionScale

from connection.yt import get_yt_client
from test_dmp_suite.yt import utils


class TestTableWithExpTime(etl.ETLTable):
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt', partition_ttl_day_cnt=100)

    dt = Date()
    dttm = Datetime(sort_key=True, sort_position=0)
    value = Int()


class TestTableWithoutExpTime(etl.ETLTable):
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt')

    dt = Date()
    dttm = Datetime(sort_key=True, sort_position=0)
    value = Int()


class TestTableWithExpTimeWOPart(etl.ETLTable):
    __unique_keys__ = True

    dt = Date()
    dttm = Datetime(sort_key=True, sort_position=0)
    value = Int()


class TestTableCustPart(etl.ETLTable):
    __unique_keys__ = True
    __partition_scale__ = CustomPartition(dtu.format_date)

    dt = Date()
    dttm = Datetime(sort_key=True, sort_position=0)
    value = Int()


test_table_with_exp_time = utils.fixture_random_yt_table(TestTableWithExpTime)
test_table_with_exp_time_wo_part = utils.fixture_random_yt_table(TestTableWithExpTimeWOPart)
test_table_without_exp_time = utils.fixture_random_yt_table(TestTableWithoutExpTime)
test_table_cust_part = utils.fixture_random_yt_table(TestTableCustPart)


@pytest.mark.slow
def test_expiration_time_in_rotation_to_target(test_table_with_exp_time):
    update_data = [
        dict(dt='2017-03-06', dttm='2017-03-06 02:02:02', value=3),
        dict(dt='2017-03-07', dttm='2017-03-07 00:00:00', value=4),
        dict(dt='2017-03-09', dttm='2017-03-09 16:16:16', value=5),
    ]
    current_date = dtu.format_date(dtu.utcnow().date())
    meta = etl.YTMeta(test_table_with_exp_time, partition=current_date)

    op.init_yt_table(
        meta.rotation_path(), meta.rotation_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.rotation_path(),
        update_data,
    )
    etl.rotation_to_target(
        meta
    )

    partition = meta.with_partition(current_date).target_path()
    partition_expiration_time = get_yt_client().get(partition + "/@expiration_time")
    partition_expiration_time_dt = dtu.parse_datetime(partition_expiration_time).date()
    actual_dt = (dtu.get_end_of_month(current_date) + timedelta(days=100)).date()

    assert partition_expiration_time_dt == actual_dt


@pytest.mark.slow
def test_no_expiration_time_in_rotation_to_target(test_table_without_exp_time):
    update_data = [
        dict(dt='2017-03-06', dttm='2017-03-06 02:02:02', value=3),
        dict(dt='2017-03-07', dttm='2017-03-07 00:00:00', value=4),
        dict(dt='2017-03-09', dttm='2017-03-09 16:16:16', value=5),
    ]
    current_date = dtu.format_date(dtu.utcnow().date())

    meta = etl.YTMeta(test_table_without_exp_time, partition=current_date)
    op.init_yt_table(
        meta.rotation_path(), meta.rotation_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.rotation_path(),
        update_data,
    )
    etl.rotation_to_target(
        meta
    )

    partition = meta.with_partition(current_date).target_path()

    partition_expiration_time = None

    try:
        partition_expiration_time = get_yt_client().get(partition + "/@expiration_time")
    except:
        pass

    if partition_expiration_time:
        raise AssertionError('Expiration_time must be None')


@pytest.mark.slow
def test_expiration_time_in_init_target_table(test_table_with_exp_time):
    current_date = dtu.format_date(dtu.utcnow().date())
    meta = etl.YTMeta(test_table_with_exp_time, partition=current_date)

    etl.init_target_table(meta)

    partition = meta.with_partition(current_date).target_path()
    partition_expiration_time = get_yt_client().get(partition + "/@expiration_time")
    partition_expiration_time_dt = dtu.parse_datetime(partition_expiration_time).date()
    actual_dt = (dtu.get_end_of_month(current_date) + timedelta(days=100)).date()

    assert partition_expiration_time_dt == actual_dt


@pytest.mark.slow
def test_no_expiration_time_in_init_target_table(test_table_without_exp_time):
    current_date = dtu.format_date(dtu.utcnow().date())
    meta = etl.YTMeta(test_table_without_exp_time, partition=current_date)

    etl.init_target_table(meta)

    partition = meta.with_partition(current_date).target_path()

    partition_expiration_time = None

    try:
        partition_expiration_time = get_yt_client().get(partition + "/@expiration_time")
    except:
        pass

    if partition_expiration_time:
        raise AssertionError('Expiration_time must be None')


@pytest.mark.slow
def test_no_expiration_time_in_init_target_table(test_table_with_exp_time_wo_part):
    meta = etl.YTMeta(test_table_with_exp_time_wo_part)

    etl.init_target_table(meta)

    target_path = meta.target_path()

    target_path_expiration_time = None

    try:
        target_path_expiration_time = get_yt_client().get(target_path + "/@expiration_time")
    except:
        pass

    if target_path_expiration_time:
        raise AssertionError('Expiration_time must be None')


@pytest.mark.slow
def test_no_expiration_time_in_init_target_table_cust_part(test_table_cust_part):
    current_date = dtu.format_date(dtu.utcnow().date())
    meta = etl.YTMeta(test_table_cust_part, partition=current_date)

    etl.init_target_table(meta)

    target_path = meta.target_path()

    target_path_expiration_time = None

    try:
        target_path_expiration_time = get_yt_client().get(target_path + "/@expiration_time")
    except:
        pass

    if target_path_expiration_time:
        raise AssertionError('Expiration_time must be None')
