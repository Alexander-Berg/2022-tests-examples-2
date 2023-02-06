import pytest


@pytest.mark.parametrize(
    ['headers', 'query_params', 'expected_response'],
    [
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client1'},
            {},
            {
                'limit': 100,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'cc_options_id_1',
                        'default': True,
                        'field_settings': [
                            {
                                'format': 'mixed',
                                'id': 'cost_center',
                                'required': True,
                                'services': ['eats', 'taxi', 'drive'],
                                'title': 'Центр затрат',
                                'values': [
                                    'командировка',
                                    'в центральный офис',
                                ],
                                'hidden': False,
                            },
                        ],
                        'name': 'Основной',
                    },
                    {
                        'id': 'cc_options_id_2',
                        'default': False,
                        'field_settings': [
                            {
                                'format': 'mixed',
                                'id': 'cost_center',
                                'required': True,
                                'services': ['eats', 'taxi', 'drive'],
                                'title': 'Центр затрат',
                                'values': [
                                    'запасная командировка',
                                    'из центрального офиса',
                                ],
                                'hidden': False,
                            },
                        ],
                        'name': 'Запасной',
                    },
                ],
            },
            id='empty query',
        ),
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client1'},
            {'limit': 1},
            {
                'limit': 1,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'cc_options_id_1',
                        'default': True,
                        'field_settings': [
                            {
                                'format': 'mixed',
                                'id': 'cost_center',
                                'required': True,
                                'services': ['eats', 'taxi', 'drive'],
                                'title': 'Центр затрат',
                                'values': [
                                    'командировка',
                                    'в центральный офис',
                                ],
                                'hidden': False,
                            },
                        ],
                        'name': 'Основной',
                    },
                ],
            },
            id='test limit',
        ),
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client1'},
            {'offset': 1},
            {
                'limit': 100,
                'offset': 1,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'cc_options_id_2',
                        'default': False,
                        'field_settings': [
                            {
                                'format': 'mixed',
                                'id': 'cost_center',
                                'required': True,
                                'services': ['eats', 'taxi', 'drive'],
                                'title': 'Центр затрат',
                                'values': [
                                    'запасная командировка',
                                    'из центрального офиса',
                                ],
                                'hidden': False,
                            },
                        ],
                        'name': 'Запасной',
                    },
                ],
            },
            id='test offset',
        ),
    ],
)
async def test_cost_centers_list(
        web_app_client, headers, query_params, expected_response,
):
    response = await web_app_client.get(
        '/integration/v2/cost_centers/list',
        params=query_params,
        headers=headers,
    )
    response_data = await response.json()
    assert response_data == expected_response
