from dmp_suite import datetime_utils as dtu

from market_b2c_etl.layer.greenplum.dds.order.item import Item
from market_b2c_etl.layer.greenplum.ods.common.filters import partition_check, get_dds_partitions_start_dt


def test_filters():
    _partition_start_dt = get_dds_partitions_start_dt(Item())
    test_case_in_future = (dtu.datetime.now() + dtu.timedelta(days=2)).strftime(dtu.DATE_TIME_FORMAT)

    assert partition_check(dttm="2022-04-20 23:54:31", lower_bound=_partition_start_dt) is True
    assert partition_check(dttm="2017-04-20 23:54:31", lower_bound=_partition_start_dt) is True
    assert partition_check(dttm="2015-04-20 23:54:31", lower_bound=_partition_start_dt) is False
    assert partition_check(dttm=test_case_in_future, lower_bound=_partition_start_dt) is False
