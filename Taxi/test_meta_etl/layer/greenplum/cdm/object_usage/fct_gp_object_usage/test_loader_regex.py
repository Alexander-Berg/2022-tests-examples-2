import re
import pytest

from meta_etl.layer.greenplum.cdm.object_usage.fct_gp_object_usage.loader import (
    REGEX_TABLE_FROM_ATTRIBUTE_DDS, REGEX_TABLE_DDS_PRT, REGEX_TABLE_PRT
)

REGEX_TABLE_FROM_ATTRIBUTE_DDS_CPL = re.compile(REGEX_TABLE_FROM_ATTRIBUTE_DDS)
REGEX_TABLE_DDS_PRT_CPL = re.compile(REGEX_TABLE_DDS_PRT)
REGEX_TABLE_PRT_CPL = re.compile(REGEX_TABLE_PRT)


@pytest.mark.parametrize(
    "table_gp,table_dmp", [
        ('a__geo__node_id__key', 'geo'),
        ('a__order_candidate__previous_order_left_time_sec___2_prt_202008', 'order_candidate'),
        ('a__cancel_reason_group__name_h_2', 'cancel_reason_group'),
    ]
)
def test_regex_table_from_attribute_dds(table_gp, table_dmp):
    result = REGEX_TABLE_FROM_ATTRIBUTE_DDS_CPL.match(table_gp).group(1)
    assert table_dmp == result


@pytest.mark.parametrize(
    "table_gp,table_dmp", [
        ('h__communication_1_prt_202008', 'communication'),
        ('h__phone_hash', 'phone_hash'),
        ('h__office', 'office'),
        ('h__schedule_redefined_date', 'schedule_redefined_date'),
        ('l__courier_shift__courier_shift_parent', 'courier_shift__courier_shift_parent'),
        ('l__communication_took__operator_by__phone_via', 'communication_took__operator_by__phone_via'),
        ('l__order__payment', 'order__payment'),
        ('l__place__place_schedule_1_prt_historical', 'place__place_schedule'),
        ('l__call_belong__task_has', 'call_belong__task_has'),
    ]
)
def test_regex_table_dds_prt(table_gp, table_dmp):
    result = REGEX_TABLE_DDS_PRT_CPL.match(table_gp).group(1)
    assert table_dmp == result


@pytest.mark.parametrize(
    "table_gp,table_dmp", [
        ('agg_tariff_zone_1_prt_monthly_2_prt_2015', 'agg_tariff_zone'),
        ('agg_car_branding_2_prt_201909', 'agg_car_branding'),
        ('mminnekaev_subsidy_report_orders_1_prt_35', 'mminnekaev_subsidy_report_orders'),
        ('dm_order_1_prt', 'dm_order'),
        ('dm_order_10_prt', 'dm_order'),
    ]
)
def test_regex_table_prt(table_gp, table_dmp):
    result = REGEX_TABLE_PRT_CPL.sub('', table_gp)
    assert table_dmp == result
