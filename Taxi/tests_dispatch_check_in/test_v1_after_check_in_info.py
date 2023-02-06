import pytest


@pytest.mark.parametrize(
    'pickup_lines_config, expected_response_status, expected_error_code, '
    'order_id, exp3_enabled, card_title',
    [
        (
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            200,
            None,
            'order_id',
            False,
            'Пожалуйста ожидайте',
        ),
        (
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            200,
            None,
            'order_id',
            True,
            'Default user, пожалуйста ожидайте',
        ),
        (
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            200,
            None,
            'order_id2',
            True,
            'User 2, пожалуйста ожидайте',
        ),
        (
            {
                'svo_line_2': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            404,
            'PICKUP_LINE_NOT_FOUND',
            'order_id',
            True,
            '',
        ),
        (
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                },
            },
            500,
            'INVALID_PICKUP_LINE_SETTINGS',
            'order_id',
            True,
            '',
        ),
    ],
)
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_v1_after_check_in_info(
        taxi_config,
        taxi_dispatch_check_in,
        experiments3,
        load_json,
        pickup_lines_config,
        expected_response_status,
        expected_error_code,
        order_id,
        exp3_enabled,
        card_title,
):
    taxi_config.set(DISPATCH_CHECK_IN_PICKUP_LINES=pickup_lines_config)

    if exp3_enabled:
        experiments3.add_experiments_json(
            load_json('card_static_resources_experiments.json'),
        )

    headers = {'X-Request-Language': 'ru'}
    request_params = {'order_id': order_id, 'pickup_line': 'svo_line_1'}

    response = await taxi_dispatch_check_in.get(
        '/v1/after-check-in-info', params=request_params, headers=headers,
    )

    assert response.status == expected_response_status

    if expected_error_code is None:
        etalon = {
            'check_in_queue_info': {
                'check_in_zone': {
                    'geopoint': [10.0, 10.0],
                    'pickup_line_id': 'svo_line_1',
                },
            },
            'status_info': {
                'translations': {'card': {'title_template': card_title}},
            },
        }
        assert response.json() == etalon
    else:
        assert response.json()['code'] == expected_error_code
