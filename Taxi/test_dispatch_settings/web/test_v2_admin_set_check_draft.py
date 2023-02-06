import pytest


@pytest.mark.parametrize(
    'req,resp',
    [
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_1',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 5},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 4},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 6},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 5},
                ],
                'group_name': 'test',
            },
            {
                'data': {
                    'zone_name': 'test_zone_1',
                    'tariff_name': 'test_tariff_1',
                    'new_parameters': [
                        {'name': 'MAX_ROBOT_TIME', 'value': 6},
                        {'name': 'QUERY_LIMIT_LIMIT', 'value': 5},
                    ],
                    'group_name': 'test',
                },
                'diff': {
                    'new': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME', 'value': 6},
                            {'name': 'QUERY_LIMIT_LIMIT', 'value': 5},
                        ],
                    },
                    'current': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME', 'value': 5},
                            {'name': 'QUERY_LIMIT_LIMIT', 'value': 4},
                        ],
                    },
                },
                'lock_ids': [
                    {'custom': True, 'id': 'test_zone_1:test_tariff_1'},
                ],
            },
        ),
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_3',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 3},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 4},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 3},
                ],
                'group_name': 'test',
            },
            {
                'data': {
                    'zone_name': 'test_zone_1',
                    'tariff_name': 'test_tariff_3',
                    'new_parameters': [
                        {'name': 'MAX_ROBOT_TIME', 'value': 4},
                        {'name': 'QUERY_LIMIT_LIMIT', 'value': 3},
                    ],
                    'group_name': 'test',
                },
                'diff': {
                    'new': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME', 'value': 4},
                            {'name': 'QUERY_LIMIT_LIMIT', 'value': 3},
                        ],
                    },
                    'current': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME', 'value': 3},
                            {'name': 'QUERY_LIMIT_LIMIT', 'value': 2},
                        ],
                    },
                },
                'lock_ids': [
                    {'custom': True, 'id': 'test_zone_1:test_tariff_3'},
                ],
            },
        ),
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_1',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 5},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 4},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME'},
                    {'name': 'QUERY_LIMIT_LIMIT'},
                ],
                'group_name': 'test',
            },
            {
                'data': {
                    'zone_name': 'test_zone_1',
                    'tariff_name': 'test_tariff_1',
                    'new_parameters': [
                        {'name': 'MAX_ROBOT_TIME'},
                        {'name': 'QUERY_LIMIT_LIMIT'},
                    ],
                    'group_name': 'test',
                },
                'diff': {
                    'new': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME'},
                            {'name': 'QUERY_LIMIT_LIMIT'},
                        ],
                    },
                    'current': {
                        'settings': [
                            {'name': 'MAX_ROBOT_TIME', 'value': 5},
                            {'name': 'QUERY_LIMIT_LIMIT', 'value': 4},
                        ],
                    },
                },
                'lock_ids': [
                    {'custom': True, 'id': 'test_zone_1:test_tariff_1'},
                ],
            },
        ),
    ],
)
async def test_valid(taxi_dispatch_settings_web, req, resp):
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/check-draft', json=req,
    )
    assert response.status == 200
    content = await response.json()
    content['data']['new_parameters'].sort(key=lambda x: x['name'])
    content['diff']['new']['settings'].sort(key=lambda x: x['name'])
    content['diff']['current']['settings'].sort(key=lambda x: x['name'])
    assert content == resp


@pytest.mark.parametrize(
    'req,resp',
    [
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_1',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 5},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 4},
                    {'name': 'UNKNOWN_PARAMETER', 'value': 3},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 6},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 5},
                    {'name': 'UNKNOWN_PARAMETER', 'value': 4},
                ],
                'group_name': 'test',
            },
            {
                'code': 'settings_mismatch',
                'message': (
                    f'Old parameters length: 3, etalon settings length: 2. '
                    f'Refresh page, please'
                ),
            },
        ),
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_3',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 3},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 3},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 4},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 3},
                ],
                'group_name': 'test',
            },
            {
                'code': 'settings_mismatch',
                'message': (
                    f'QUERY_LIMIT_LIMIT parameter etalon value is 2, '
                    f'and old value in draft data is 3. Refresh page, please'
                ),
            },
        ),
        (
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_1',
                'old_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 5},
                    {'name': 'QUERY_LIMIT_LIMIT_2', 'value': 4},
                ],
                'new_parameters': [
                    {'name': 'MAX_ROBOT_TIME', 'value': 6},
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 5},
                ],
                'group_name': 'test',
            },
            {
                'code': 'settings_mismatch',
                'message': (
                    f'QUERY_LIMIT_LIMIT parameter not in draft data. '
                    f'Refresh page, please'
                ),
            },
        ),
    ],
)
async def test_invalid(taxi_dispatch_settings_web, req, resp):
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/check-draft', json=req,
    )
    assert response.status == 409
    content = await response.json()
    assert content == resp
