from collections import namedtuple
from scooter_etl.layer.yt.ods.scooter_analytics.drive_areas_hist.impl import reduce_areas

AreaRecord = namedtuple('AreaRecord', [
    'area_id',
    'country_name_en',
    'city_name_en',
    'area_title',
    'area_agg_type',
    'area_coords',
    'node_level',
    'parent_area_id',
    'utc_business_dt',
    'polygon_area_m2_value'
])


def test_reduce_areas():
    assert list(reduce_areas(b'parking_1', [
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1]]', 1, b'ch_1',
                   b'2021-10-01', 22233.23),
    ])) == [
               {'area_agg_type': b'parking', 'area_coords': b'[[0,1],[1,1]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_1', 'utc_valid_from_dt': b'2021-10-01', 'utc_valid_to_dt': b'9999-12-31',
                'polygon_area_m2_value': 22233.23}
           ]

    assert list(reduce_areas(b'parking_1', [
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1]]', 1, b'ch_1',
                   b'2021-10-01', 889.3),
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1]]', 1, b'ch_1',
                   b'2021-10-02', 889.3),
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1],[1,2]]', 1, b'ch_1',
                   b'2021-10-03', 1222.22),
    ])) == [
               {'area_agg_type': b'parking', 'area_coords': b'[[0,1],[1,1]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_1', 'utc_valid_from_dt': b'2021-10-01', 'utc_valid_to_dt': b'2021-10-02',
                'polygon_area_m2_value': 889.3},
               {'area_agg_type': b'parking', 'area_coords': b'[[0,1],[1,1],[1,2]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_1', 'utc_valid_from_dt': b'2021-10-03', 'utc_valid_to_dt': b'9999-12-31',
                'polygon_area_m2_value': 1222.22}
           ]

    assert list(reduce_areas(b'parking_1', [
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1]]', 1, b'ch_1',
                   b'2022-01-12', 123.123),
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[0,1],[1,1]]', 1, b'ch_180',
                   b'2022-01-13', 123.123),
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[100,1],[1,1]]', 1, b'ch_100',
                   b'2022-01-14', 1423.11),
        AreaRecord(b'parking_1', b'Russia', b'Moscow', b'parking_1', b'parking', b'[[100,1],[1,1]]', 1, b'ch_100',
                   b'2022-01-15', 1423.11),
    ])) == [
               {'area_agg_type': b'parking', 'area_coords': b'[[0,1],[1,1]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_1', 'utc_valid_from_dt': b'2022-01-12', 'utc_valid_to_dt': b'2022-01-12',
                'polygon_area_m2_value': 123.123},
               {'area_agg_type': b'parking', 'area_coords': b'[[0,1],[1,1]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_180', 'utc_valid_from_dt': b'2022-01-13', 'utc_valid_to_dt': b'2022-01-13',
                'polygon_area_m2_value': 123.123},
               {'area_agg_type': b'parking', 'area_coords': b'[[100,1],[1,1]]', 'area_id': b'parking_1',
                'area_title': b'parking_1', 'city_name_en': b'Moscow', 'country_name_en': b'Russia', 'node_level': 1,
                'parent_area_id': b'ch_100', 'utc_valid_from_dt': b'2022-01-14', 'utc_valid_to_dt': b'9999-12-31',
                'polygon_area_m2_value': 1423.11}
           ]
