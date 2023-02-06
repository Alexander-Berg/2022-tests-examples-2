# TODO: Эти тесты больше не нужны, но тесткейсы понадобятся для https://st.yandex-team.ru/TAXIDWH-9618


# import pytest
#
# from dmp_suite import datetime_utils as dtu
# from dmp_suite.cohort_utils.impl import get_msk_dttm_expression, get_partition_filter_str
# from dmp_suite.greenplum import GPTable, MonthPartitionScale, Date, Datetime
# from dmp_suite.table import SummaryLayout, abstracttable
#
#
# @abstracttable
# class StubTable(GPTable):
#     __layout__ = SummaryLayout(group='test', service='test', name='stub')
#
#
# class EventWithUtcDatePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('utc_event_dt')
#     utc_event_dt = Date()
#
#
# class EventWithUtcDatetimePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('utc_event_dttm')
#     utc_event_dttm = Datetime()
#
#
# class EventWithMskDatePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('msk_event_dt')
#     msk_event_dt = Date()
#
#
# class EventWithMskDatetimePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('msk_event_dttm')
#     msk_event_dttm = Datetime()
#
#
# class EventWithMoscowDatePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('moscow_event_dt')
#     moscow_event_dt = Date()
#
#
# class EventWithMoscowDatetimePartition(StubTable):
#     __partition_scale__ = MonthPartitionScale('moscow_event_dttm')
#     moscow_event_dttm = Datetime()
#
#
# @pytest.mark.parametrize(
#     'gp_table, expected_filter_str',
#     (
#         (EventWithUtcDatePartition, "utc_event_dt >= '2020-10-22' AND utc_event_dt <= '2020-11-12'"),
#         (EventWithUtcDatetimePartition, "utc_event_dttm >= '2020-10-22 22:00:00' AND utc_event_dttm <= '2020-11-12 09:00:00'"),
#         (EventWithMskDatePartition, "msk_event_dt >= '2020-10-23' AND msk_event_dt <= '2020-11-12'"),
#         (EventWithMskDatetimePartition, "msk_event_dttm >= '2020-10-23 01:00:00' AND msk_event_dttm <= '2020-11-12 12:00:00'"),
#         (EventWithMoscowDatePartition, "moscow_event_dt >= '2020-10-23' AND moscow_event_dt <= '2020-11-12'"),
#         (EventWithMoscowDatetimePartition, "moscow_event_dttm >= '2020-10-23 01:00:00' AND moscow_event_dttm <= '2020-11-12 12:00:00'")
#     )
# )
# def test_get_partition_filter_str(gp_table, expected_filter_str):
#     msk_period = dtu.period('2020-10-23 01:00:00', '2020-11-12 12:00:00')
#     actual_filter_str = get_partition_filter_str(gp_table, msk_period=msk_period)
#     if expected_filter_str != actual_filter_str:
#         raise ValueError(f'Expected partition filter str is differed from actual: {expected_filter_str}, {actual_filter_str}.')
#
#
# @pytest.mark.parametrize(
#     'event_dttm_field, expected_msk_dttm_field',
#     (
#         ("utc_order_dttm", "((utc_order_dttm::TIMESTAMP) AT TIME ZONE 'UTC') AT TIME ZONE 'Europe/Moscow'"),
#         ("msk_order_dttm", "msk_order_dttm"),
#         ("moscow_order_dttm", "moscow_order_dttm")
#     )
# )
# def test_get_msk_dttm_field(event_dttm_field, expected_msk_dttm_field):
#     actual_msk_dttm_field = get_msk_dttm_expression(event_dttm_field)
#     if expected_msk_dttm_field != actual_msk_dttm_field:
#         raise ValueError(f'Expected msk dttm field str is differed from actual: {expected_msk_dttm_field}, {actual_msk_dttm_field}.')
#
#
# @pytest.mark.parametrize(
#     'event_dttm_field',
#     (
#         'utc_order_dt', 'msk_order_dt', 'utc_order_datetime', 'utc_order_time', 'utc_order_timestamp', 'dttm_event',
#         'local_order_dttm', 'order_dttm', 'cst_order_dttm'
#     )
# )
# def test_raise_get_msk_dttm_field(event_dttm_field):
#     with pytest.raises(ValueError):
#         get_msk_dttm_expression(event_dttm_field)
