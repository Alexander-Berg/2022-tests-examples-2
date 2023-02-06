import pytest

NOW = '2021-01-29T00:00:00+00:00'
NOW_PLUS_TTL = '2021-01-29T00:10:00+00:00'


@pytest.mark.now(NOW)
async def test_surge_points_cache(taxi_umlaas_pricing, testpoint):
    content = None

    @testpoint('surge-points-data')
    def _set_cache_content(data_json):
        nonlocal content
        content = data_json

    await taxi_umlaas_pricing.invalidate_caches()
    assert sorted(content, key=lambda x: x['id']) == [
        {
            'pins': 5,
            'pins_order': 4,
            'pins_driver': 3,
            'free': 2,
            'total': 6,
            'radius': 1000,
            'value_raw': 1.5,
            'value_smooth': 2.5,
            'created_ts': '2021-01-28T14:00:00+00:00',
            'active_till': NOW_PLUS_TTL,
            'category': '__default__',
            'point': [11.0, 10.0],
            'surge_value_in_tariff': 7.7,
            'ps_shift_past_raw': 0.23,
            'deviation_from_target_abs': 0.314,
            'id': '',
            'point_b_adj_percentiles': [0.1, 0.2],
            'value_raw_graph': 1.4,
            'cost': 199,
        },
        {
            'pins': 5,
            'pins_order': 4,
            'pins_driver': 3,
            'free': 2,
            'total': 6,
            'radius': 1000,
            'value_raw': 1.5,
            'value_smooth': 2.5,
            'created_ts': '2021-01-28T14:00:00+00:00',
            'active_till': NOW_PLUS_TTL,
            'category': '__default__',
            'point': [11.0, 10.0],
            'surge_value_in_tariff': 7.7,
            'ps_shift_past_raw': 0.23,
            'deviation_from_target_abs': 0.314,
            'id': '6010bde7eb37e20aaa602576',
            'point_b_adj_percentiles': [0.3, 0.4],
            'value_raw_graph': 0,
            'cost': 0,
        },
    ]
