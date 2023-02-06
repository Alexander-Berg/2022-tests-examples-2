import pytest


@pytest.mark.usefixtures('personal', 'mock_data_markup')
@pytest.mark.parametrize(
    'user_cases, status',
    [
        ('default', 200),
        ('user_v2', 200),
        ('not_active', 403),
        ('user_v2_to_v1', 403),
    ],
)
async def test_default_users_cases(
        taxi_hiring_partners_app_web,
        mock_configs3,
        load_json,
        user_cases,
        status,
):
    # arrange
    request_data = load_json('requests.json')[user_cases]
    expected_data = load_json('expected_data.json')[user_cases]
    config3 = mock_configs3(load_json('config3_response.json'))

    # act
    response = await taxi_hiring_partners_app_web.get(
        '/v1/users/me',
        params=request_data['params'],
        headers=request_data['headers'],
    )

    # assert
    assert config3.has_calls
    assert response.status == status
    body = await response.json()
    assert body == expected_data


@pytest.mark.config(
    HIRING_PARTNERS_APP_PERMISSIONS_SETTINGS=[
        {
            'consumer_name': 'hiring/permission_flags',
            'config3_name': 'hiring_partners_app_permission_flags',
        },
        {
            'consumer_name': 'hiring/permission_flags_2',
            'config3_name': 'hiring_partners_app_permission_flags_2',
        },
        {
            'consumer_name': 'hiring/permission_flags_dubl',
            'config3_name': 'hiring_partners_app_permission_flags_dubl',
        },
    ],
)
@pytest.mark.usefixtures('personal', 'mock_data_markup')
@pytest.mark.parametrize('user_origin', ['international', 'domestic'])
async def test_permission_flags(
        taxi_hiring_partners_app_web, mock_configs3, load_json, user_origin,
):
    # arrange
    request_data = load_json('requests.json')[user_origin]
    expected_data = load_json('expected_data.json')[user_origin]
    config3 = mock_configs3(load_json('config3_response.json')[user_origin])

    # act
    response = await taxi_hiring_partners_app_web.get(
        '/v1/users/me',
        params=request_data['params'],
        headers=request_data['headers'],
    )

    # assert
    assert config3.has_calls
    assert response.status == 200
    body = await response.json()
    assert body == expected_data
