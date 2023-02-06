from collections import namedtuple
from demand_etl.layer.yt.rep.user_features.geo.yandex_uid.impl import prepare_features
from os import environ

GeoOrderRecord = namedtuple('GeoOrderRecord', [
    'yandex_uid',
    'taxi_agglomeration_node_id',
    'geobase_region_id',
    'geobase_country_name_ru',
    'geobase_city_name_ru',
    'utc_order_created_dttm',
    'order_gmv_w_vat_rub'
])


def test_prepare_features():
    environ['START'] = '2021-10-14 00:00:00'
    environ['END'] = '2021-10-16 23:59:59'

    dict1 = {
        'first_city_name': b'Moscow',
        'first_country_name': b'Russia',
        'first_taxi_agglomeration_node_id': b'br_moscow',
        'last_city_name': b'Moscow',
        'last_country_name': b'Russia',
        'last_taxi_agglomeration_node_id': b'br_moscow',
        'all_time_most_spent_city_name': b'Moscow',
        'week_13_most_spent_city_name': b'Moscow',
        'week_6_most_spent_city_name': b'Moscow',
        'week_1_most_spent_city_name': b'Moscow',
        'all_time_most_spent_country_name': b'Russia',
        'week_13_most_spent_country_name': b'Russia',
        'week_6_most_spent_country_name': b'Russia',
        'week_1_most_spent_country_name': b'Russia',
        'all_time_most_spent_geobase_region_id': 213,
        'week_13_most_spent_geobase_region_id': 213,
        'week_6_most_spent_geobase_region_id': 213,
        'week_1_most_spent_geobase_region_id': 213,
        'all_time_most_spent_taxi_agglomeration_node_id': b'br_moscow',
        'week_13_most_spent_taxi_agglomeration_node_id': b'br_moscow',
        'week_6_most_spent_taxi_agglomeration_node_id': b'br_moscow',
        'week_1_most_spent_taxi_agglomeration_node_id': b'br_moscow',
        'all_time_most_used_city_name': b'Moscow',
        'week_13_most_used_city_name': b'Moscow',
        'week_6_most_used_city_name': b'Moscow',
        'week_1_most_used_city_name': b'Moscow',
        'all_time_most_used_country_name': b'Russia',
        'week_13_most_used_country_name': b'Russia',
        'week_6_most_used_country_name': b'Russia',
        'week_1_most_used_country_name': b'Russia',
        'all_time_most_used_geobase_region_id': 213,
        'week_13_most_used_geobase_region_id': 213,
        'week_6_most_used_geobase_region_id': 213,
        'week_1_most_used_geobase_region_id': 213,
        'all_time_most_used_taxi_agglomeration_node_id': b'br_moscow',
        'week_13_most_used_taxi_agglomeration_node_id': b'br_moscow',
        'week_6_most_used_taxi_agglomeration_node_id': b'br_moscow',
        'week_1_most_used_taxi_agglomeration_node_id': b'br_moscow',
        'yandex_uid': b'1'
    }

    dict2 = {
        'last_city_name': b'Grodno',
        'last_country_name': b'Belarus',
        'last_taxi_agglomeration_node_id': b'br_grodno',
        'all_time_most_spent_city_name': b'Grodno',
        'week_13_most_spent_city_name': b'Grodno',
        'week_6_most_spent_city_name': b'Grodno',
        'week_1_most_spent_city_name': b'Grodno',
        'all_time_most_spent_country_name': b'Belarus',
        'week_13_most_spent_country_name': b'Belarus',
        'week_6_most_spent_country_name': b'Belarus',
        'week_1_most_spent_country_name': b'Belarus',
        'all_time_most_spent_geobase_region_id': 10274,
        'week_13_most_spent_geobase_region_id': 10274,
        'week_6_most_spent_geobase_region_id': 10274,
        'week_1_most_spent_geobase_region_id': 10274,
        'all_time_most_spent_taxi_agglomeration_node_id': b'br_grodno',
        'week_13_most_spent_taxi_agglomeration_node_id': b'br_grodno',
        'week_6_most_spent_taxi_agglomeration_node_id': b'br_grodno',
        'week_1_most_spent_taxi_agglomeration_node_id': b'br_grodno',
        'week_1_most_used_city_name': b'Grodno',
        'week_1_most_used_country_name': b'Belarus',
        'week_1_most_used_geobase_region_id': 10274,
        'week_1_most_used_taxi_agglomeration_node_id': b'br_grodno',
        'yandex_uid': b'1'
    }

    dict_week_none = {
        x: None for x in dict1 if x.startswith('week_1_')
    }

    assert list(prepare_features(b'1', [
        GeoOrderRecord(b'1', b'br_moscow', 213, b'Russia', b'Moscow', b'2021-10-01 00:00:00', 1050),
    ])) == [
               {
                   'report_dt': b'2021-10-14',
                   **dict1,
                   **dict_week_none
               },
               {
                   'report_dt': b'2021-10-15',
                   **dict1,
                   **dict_week_none
               },
               {
                   'report_dt': b'2021-10-16',
                   **dict1,
                   **dict_week_none
               },
           ]

    assert list(prepare_features(b'1', [
        GeoOrderRecord(b'1', b'br_moscow', 213, b'Russia', b'Moscow', b'2021-10-01 10:00:00', 1050),
        GeoOrderRecord(b'1', b'br_moscow', 213, b'Russia', b'Moscow', b'2021-10-02 12:00:00', 300),
        GeoOrderRecord(b'1', b'br_grodno', 10274, b'Belarus', b'Grodno', b'2021-10-15 13:00:00', 2040),
    ])) == [
               {
                   'report_dt': b'2021-10-14',
                   **dict1,
                   **dict_week_none
               },
               {
                   'report_dt': b'2021-10-15',
                   **dict1,
                   **dict2
               },
               {
                   'report_dt': b'2021-10-16',
                   **dict1,
                   **dict2
               },

           ]

    dict3 = {
        'last_city_name': b'Tambov',
        'last_taxi_agglomeration_node_id': b'br_tambov',
        'week_13_most_spent_city_name': b'Tambov',
        'week_6_most_spent_city_name': b'Tambov',
        'week_1_most_spent_city_name': b'Tambov',
        'week_13_most_spent_geobase_region_id': 13,
        'week_6_most_spent_geobase_region_id': 13,
        'week_1_most_spent_geobase_region_id': 13,
        'week_13_most_spent_taxi_agglomeration_node_id': b'br_tambov',
        'week_6_most_spent_taxi_agglomeration_node_id': b'br_tambov',
        'week_1_most_spent_taxi_agglomeration_node_id': b'br_tambov',
        'all_time_most_used_city_name': b'Tambov',
        'week_13_most_used_city_name': b'Tambov',
        'week_6_most_used_city_name': b'Tambov',
        'week_1_most_used_city_name': b'Tambov',
        'all_time_most_used_geobase_region_id': 13,
        'week_13_most_used_geobase_region_id': 13,
        'week_6_most_used_geobase_region_id': 13,
        'week_1_most_used_geobase_region_id': 13,
        'all_time_most_used_taxi_agglomeration_node_id': b'br_tambov',
        'week_13_most_used_taxi_agglomeration_node_id': b'br_tambov',
        'week_6_most_used_taxi_agglomeration_node_id': b'br_tambov',
        'week_1_most_used_taxi_agglomeration_node_id': b'br_tambov',
        'yandex_uid': b'1'
    }

    dict4 = {
        'last_city_name': b'Sochi',
        'last_taxi_agglomeration_node_id': b'br_sochi',
        'all_time_most_spent_city_name': b'Sochi',
        'week_13_most_spent_city_name': b'Sochi',
        'week_6_most_spent_city_name': b'Sochi',
        'week_1_most_spent_city_name': b'Sochi',
        'all_time_most_spent_geobase_region_id': 239,
        'week_13_most_spent_geobase_region_id': 239,
        'week_6_most_spent_geobase_region_id': 239,
        'week_1_most_spent_geobase_region_id': 239,
        'all_time_most_spent_taxi_agglomeration_node_id': b'br_sochi',
        'week_13_most_spent_taxi_agglomeration_node_id': b'br_sochi',
        'week_6_most_spent_taxi_agglomeration_node_id': b'br_sochi',
        'week_1_most_spent_taxi_agglomeration_node_id': b'br_sochi',
        'all_time_most_used_city_name': b'Sochi',
        'week_13_most_used_city_name': b'Sochi',
        'week_6_most_used_city_name': b'Sochi',
        'week_1_most_used_city_name': b'Sochi',
        'all_time_most_used_geobase_region_id': 239,
        'week_13_most_used_geobase_region_id': 239,
        'week_6_most_used_geobase_region_id': 239,
        'week_1_most_used_geobase_region_id': 239,
        'all_time_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_13_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_6_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_1_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'yandex_uid': b'1'
    }

    assert list(prepare_features(b'1', [
        GeoOrderRecord(b'1', b'br_moscow', 213, b'Russia', b'Moscow', b'2021-06-10 10:00:00', 1050),
        GeoOrderRecord(b'1', b'br_tambov', 13, b'Russia', b'Tambov', b'2021-10-14 12:00:00', 300),
        GeoOrderRecord(b'1', b'br_sochi', 239, b'Russia', b'Sochi', b'2021-10-16 13:00:00', 2040),
    ])) == [
               {
                   'report_dt': b'2021-10-14',
                   **dict1,
                   **dict3
               },
               {
                   'report_dt': b'2021-10-15',
                   **dict1,
                   **dict3
               },
               {
                   'report_dt': b'2021-10-16',
                   **dict1,
                   **dict4
               },
           ]

    dict5 = {
        'last_city_name': b'Sochi',
        'last_taxi_agglomeration_node_id': b'br_sochi',
        'all_time_most_used_city_name': b'Sochi',
        'week_13_most_used_city_name': b'Sochi',
        'week_6_most_used_city_name': b'Sochi',
        'week_1_most_used_city_name': b'Sochi',
        'all_time_most_used_geobase_region_id': 239,
        'week_13_most_used_geobase_region_id': 239,
        'week_6_most_used_geobase_region_id': 239,
        'week_1_most_used_geobase_region_id': 239,
        'all_time_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_13_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_6_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'week_1_most_used_taxi_agglomeration_node_id': b'br_sochi',
        'yandex_uid': b'1'
    }

    assert list(prepare_features(b'1', [
        GeoOrderRecord(b'1', b'br_moscow', 213, b'Russia', b'Moscow', b'2021-10-10 10:00:00', 1000),
        GeoOrderRecord(b'1', b'br_sochi', 239, b'Russia', b'Sochi', b'2021-10-11 13:00:00', 500),
    ])) == [
               {
                   'report_dt': b'2021-10-14',
                   **dict1,
                   **dict5
               },
               {
                   'report_dt': b'2021-10-15',
                   **dict1,
                   **dict5
               },
               {
                   'report_dt': b'2021-10-16',
                   **dict1,
                   **dict5
               }

           ]
