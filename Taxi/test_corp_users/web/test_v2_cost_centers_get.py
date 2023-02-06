import pytest


@pytest.mark.parametrize(
    ['cost_center_options_id', 'expected_result'],
    [
        pytest.param(
            'some_cc_options_id',
            {
                'client_id': 'some_client_id',
                'default': True,
                'field_settings': [
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'cost_center',
                        'required': True,
                        'services': ['eats', 'taxi', 'drive'],
                        'title': 'Центр затрат',
                        'values': ['командировка', 'в центральный офис'],
                    },
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'ride_purpose',
                        'required': True,
                        'services': ['eats', 'taxi'],
                        'title': 'Цель поездки',
                        'values': ['цель 1', 'цель 2', 'фиолетовая цель'],
                    },
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'custom_field_uuid_id',
                        'required': True,
                        'services': ['taxi', 'drive'],
                        'title': 'Кастомное поле',
                        'values': ['Дело №123/01/2021', 'Дело №124/02/2021'],
                    },
                    {
                        'format': 'mixed',
                        'hidden': True,
                        'id': 'hidden_field_uuid_id',
                        'required': True,
                        'services': ['taxi', 'drive'],
                        'title': 'Скрытое поле',
                        'values': ['значение 1', 'значение 2'],
                    },
                ],
                'id': 'some_cc_options_id',
                'name': 'Основной',
            },
        ),
        pytest.param(
            'other_cc_options_id',
            {
                'client_id': 'some_client_id',
                'default': False,
                'field_settings': [
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'cost_center',
                        'required': True,
                        'services': ['eats', 'taxi', 'drive'],
                        'title': 'Центр затрат',
                        'values': [
                            'запасная командировка',
                            'из центрального офиса',
                        ],
                    },
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'ride_purpose',
                        'required': True,
                        'services': ['eats', 'taxi'],
                        'title': 'Цель поездки',
                        'values': ['синяя цель'],
                    },
                    {
                        'format': 'mixed',
                        'hidden': False,
                        'id': 'other_field_uuid_id',
                        'required': True,
                        'services': ['taxi', 'drive'],
                        'title': 'Новое поле',
                        'values': ['Дело один', 'Дело два'],
                    },
                    {
                        'format': 'mixed',
                        'hidden': True,
                        'id': 'hidden_field_uuid_id',
                        'required': True,
                        'services': ['taxi', 'drive'],
                        'title': 'Скрытое поле',
                        'values': ['значение 111', 'значение 222'],
                    },
                ],
                'id': 'other_cc_options_id',
                'name': 'Запасной',
            },
        ),
    ],
)
async def test_get_one_cost_center(
        web_app_client, cost_center_options_id, expected_result,
):
    response = await web_app_client.get(
        '/v2/cost_centers',
        params={'cost_center_options_id': cost_center_options_id},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_result


@pytest.mark.parametrize(
    ['cost_center_options_id', 'expected_status'],
    [pytest.param('non-existed', 404)],
)
async def test_get_one_cost_center_fail(
        web_app_client, cost_center_options_id, expected_status,
):
    response = await web_app_client.get(
        '/v2/cost_centers',
        params={'cost_center_options_id': cost_center_options_id},
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'cost_center_options non-existed not found',
    }
