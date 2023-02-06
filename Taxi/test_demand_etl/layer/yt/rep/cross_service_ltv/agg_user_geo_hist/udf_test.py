from collections import namedtuple
from os import environ
from demand_etl.layer.yt.rep.ltv_personal_data.agg_user_geo_hist.impl import fill_null_geo

GmvRecord = namedtuple('GmvRecord', [
    'user_id',
    'phone_number_md5',
    'utc_week_start_dt',
    'geobase_region_id',
    'taxi_agglomeration_node_id',
    'sort_column',
])

def test_fill_null_geo():
    environ['UDF_END_DATE'] = '2021-07-05'
    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-28', None, None, 1),
        GmvRecord(b'user1', b'phone1', b'2021-06-28', 213, b'br_moscow', 2),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-14', None, None, 1),
        GmvRecord(b'user1', b'phone1', b'2021-06-14', 213, b'br_moscow', 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', 63, b'br_irkutsk', 2),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-14', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-21', 213, b'br_moscow', 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-28', None, None, 1),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-21', None, None, 1),
        GmvRecord(b'user1', b'phone1', b'2021-06-28', 213, b'br_moscow', 2),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': None,
         'taxi_agglomeration_node_id': None, 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-14', 213, b'br_moscow', 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', 63, b'br_irkutsk', 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-28', None, None, 1),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-14', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-14', 213, b'br_moscow', 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', None, None, 1),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', 63, b'br_irkutsk', 2),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-14', 'geobase_region_id': 213,
         'taxi_agglomeration_node_id': b'br_moscow', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': 63,
         'taxi_agglomeration_node_id': b'br_irkutsk', 'user_id': b'user1'},
    ]

    assert list(fill_null_geo(b'user1', [
        GmvRecord(b'user1', b'phone1', b'2021-06-14', None, None, 2),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', None, None, 1),
        GmvRecord(b'user1', b'phone1', b'2021-06-21', None, None, 2),
    ])) == [
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-14', 'geobase_region_id': None,
         'taxi_agglomeration_node_id': None, 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-21', 'geobase_region_id': None,
         'taxi_agglomeration_node_id': None, 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-06-28', 'geobase_region_id': None,
         'taxi_agglomeration_node_id': None, 'user_id': b'user1'},
        {'phone_number_md5': b'phone1', 'utc_week_start_dt': b'2021-07-05', 'geobase_region_id': None,
         'taxi_agglomeration_node_id': None, 'user_id': b'user1'},
    ]
