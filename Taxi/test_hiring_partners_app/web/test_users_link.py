import pytest


@pytest.mark.parametrize(
    'yandex_login',
    ['have_invite_link_permission', 'not_have_invite_link_permission'],
)
async def test_v1_users_link(
        taxi_hiring_partners_app_web,
        yandex_login,
        load_json,
        mock_personal,
        mock_configs3,
):
    # arrange
    expected_response = load_json('responses.json')[yandex_login]
    mock_configs3(load_json('config3_response.json')[yandex_login])

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/users/link', headers={'X-Yandex-Login': yandex_login},
    )

    # assert
    assert response.status == expected_response['status_code']
    assert await response.json() == expected_response['body']


async def test_v1_users_link_user_without_code(
        taxi_hiring_partners_app_web, load_json, mock_personal, mock_configs3,
):
    # arrange
    mock_configs3(
        load_json('config3_response.json')['have_invite_link_permission'],
    )

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/users/link', headers={'X-Yandex-Login': 'user_without_code'},
    )

    # assert
    response_link = (await response.json())['link']
    assert response.status == 200
    assert len(response_link) == 68
    assert response_link[:36] == 'reg.eda.yandex.ru/?user_invite_code='
