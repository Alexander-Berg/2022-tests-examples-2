import pytest


@pytest.mark.parametrize('user_cases', ('default', 'international'))
async def test_users_me(
        taxi_hiring_partners_app_web, mock_configs3, load_json, user_cases,
):
    # arrange
    request_data = load_json('requests.json')[user_cases]
    expected_data = load_json('expected_data.json')[user_cases]
    config3 = mock_configs3(load_json('config3_response.json')[user_cases])

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/internal/v1/users/me', json=request_data['body'],
    )

    # assert
    assert config3.has_calls
    assert response.status == 200
    body = await response.json()
    assert body == expected_data


@pytest.mark.parametrize(
    'user_cases, status', [('not_active', 403), ('not_found', 404)],
)
async def test_users_me_error(
        taxi_hiring_partners_app_web,
        mock_configs3,
        load_json,
        user_cases,
        status,
):
    # arrange
    request_data = load_json('requests.json')[user_cases]
    expected_data = load_json('expected_data.json')[user_cases]
    config3 = mock_configs3(load_json('config3_response.json')['default'])

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/internal/v1/users/me', json=request_data['body'],
    )

    # assert
    assert not config3.has_calls
    assert response.status == status
    body = await response.json()
    assert body == expected_data
