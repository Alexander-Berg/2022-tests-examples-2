import pytest

COMPARISON_EPS = 1


@pytest.mark.dispatch_settings(
    settings=[
        {
            'zone_name': '__default__',
            'tariff_name': '__default__base__',
            'parameters': [
                {
                    'values': {
                        'QUERY_LIMIT_FREE_PREFERRED': 5,
                        'QUERY_LIMIT_LIMIT': 20,
                        'MAX_ROBOT_DISTANCE': 15000,
                        'MAX_ROBOT_TIME': 900,
                        'QUERY_LIMIT_MAX_LINE_DIST': 10000,
                        'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 15000,
                        'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 10800,
                        'PEDESTRIAN_MAX_SEARCH_RADIUS': 2000,
                    },
                },
            ],
        },
    ],
)
async def test_basic(taxi_cargo_orders):
    response = await taxi_cargo_orders.post('v1/order/search-limits')
    assert response.status_code == 200

    sorted_result = response.json()['settings']
    sorted_result.sort(key=lambda x: x['tariff'] + x['zone_id'])

    _assert_result(
        response,
        [
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 15000,
                    'max_route_time': 900,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': '__default__base__',
                'zone_id': '__default__',
            },
        ],
    )


async def test_zone_tariff(
        taxi_cargo_orders, load_json, dispatch_settings_mocks,
):
    #
    dispatch_settings_mocks.set_settings(
        settings=load_json('dispatch_settings.json'),
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post('v1/order/search-limits')
    assert response.status_code == 200

    actual_result = response.json()['settings']
    actual_result.sort(key=lambda x: x['zone_id'] + x['tariff'])

    assert actual_result[2]['limits']['max_route_distance'] == 5880

    _assert_result(
        response,
        [
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 5880,
                    'max_route_time': 1007,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': '__default__base__',
                'zone_id': '__default__',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 5880,
                    'max_route_time': 1007,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'business',
                'zone_id': '__default__',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 5880,
                    'max_route_time': 1007,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'child_tariff',
                'zone_id': '__default__',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 9600,
                    'max_route_time': 1512,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': '__default__base__',
                'zone_id': 'ekb',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 9600,
                    'max_route_time': 1512,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'business',
                'zone_id': 'ekb',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 9600,
                    'max_route_time': 1512,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'child_tariff',
                'zone_id': 'ekb',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 7200,
                    'max_route_time': 1120,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': '__default__base__',
                'zone_id': 'moscow',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 12000,
                    'max_route_time': 1200,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'business',
                'zone_id': 'moscow',
            },
            {
                'limits': {
                    'free_preferred': 5,
                    'limit': 20,
                    'max_line_distance': 10000,
                    'max_route_distance': 7200,
                    'max_route_time': 1120,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'child_tariff',
                'zone_id': 'moscow',
            },
        ],
    )


def _assert_result(response, expected_result):
    actual_result = response.json()['settings']
    actual_result.sort(key=lambda x: x['zone_id'] + x['tariff'])
    assert len(actual_result) == len(expected_result)

    for actual, expected in zip(actual_result, expected_result):
        for field in ['max_route_distance', 'max_route_time']:
            assert field in actual['limits']
            assert field in expected['limits']

            assert (
                abs(actual['limits'][field] - expected['limits'][field])
                <= COMPARISON_EPS
            )
            expected['limits'][field] = actual['limits'][field]

    assert actual_result == expected_result
