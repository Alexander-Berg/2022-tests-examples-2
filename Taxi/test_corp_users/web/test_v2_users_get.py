import pytest


@pytest.mark.parametrize(
    ['user_id', 'status_code', 'expected_response'],
    [
        pytest.param(
            'test_user_1',
            200,
            {
                'client_id': 'client3',
                'cost_centers': {
                    'format': 'select',
                    'required': True,
                    'values': [
                        'Деловая поездка 3',
                        'Поездка по личным делам 3',
                    ],
                },
                'cost_centers_id': 'cost_center_0',
                'department_id': 'dep1',
                'email': 'example@yandex-team.ru',
                'fullname': 'good user',
                'id': 'test_user_1',
                'is_active': True,
                'is_deleted': False,
                'limits': [
                    {'limit_id': 'drive_limit', 'service': 'drive'},
                    {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                    {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
                    {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
                ],
                'phone': '+79654646541',
                'role': {'role_id': 'old_role'},
                'created': '2021-02-28T12:30:00+03:00',
            },
            id='get full user',
        ),
        pytest.param(
            'test_user_3',
            200,
            {
                'client_id': 'client3',
                'cost_centers_id': 'cost_center_1',
                'department_id': 'dep1_1',
                'email': 'example@yandex-team.ru',
                'fullname': 'fullname',
                'id': 'test_user_3',
                'is_active': True,
                'is_deleted': False,
                'limits': [
                    {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
                ],
                'phone': '+79654646543',
            },
            id='get simple user',
        ),
    ],
)
async def test_get_user_success(
        web_app_client, mock_personal, user_id, status_code, expected_response,
):
    response = await web_app_client.get(
        '/v2/users', params={'user_id': user_id},
    )
    assert response.status == status_code
    response_data = await response.json()
    response_data['limits'] = sorted(
        response_data['limits'], key=lambda x: x['service'],
    )
    assert response_data == expected_response


@pytest.mark.parametrize(
    ['user_id', 'status_code'],
    [pytest.param('not_existed_user', 404, id='not found')],
)
async def test_get_user_fail(web_app_client, user_id, status_code):
    response = await web_app_client.get(
        '/v2/users', params={'user_id': user_id},
    )
    assert response.status == status_code
    response_data = await response.json()
    assert response_data == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'User not_existed_user not found',
    }
