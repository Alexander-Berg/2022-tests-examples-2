import pytest


@pytest.mark.parametrize(
    'login,body,status,expected_data',
    [
        (
            'user_admin',
            {
                'key': 'key_1',
                'base_permission': 'user_test',
                'ru_name': 'имя',
                'en_name': 'name',
                'piece': True,
                'use_reserves': True,
            },
            201,
            {
                'key': 'key_1',
                'base_permission': 'user_test',
                'ru_name': 'имя',
                'en_name': 'name',
                'piece': True,
                'use_reserves': True,
            },
        ),
        (
            'user_admin',
            {
                'key': 'key_2',
                'base_permission': 'user_test',
                'ru_name': 'имя',
                'en_name': 'name',
                'piece': True,
                'use_reserves': True,
            },
            400,
            {
                'code': 'error_team_with_key_already_exists',
                'message': 'General error',
            },
        ),
        (
            'user',
            {
                'key': 'key_4',
                'base_permission': 'user_test',
                'ru_name': 'имя',
                'en_name': 'name',
                'piece': True,
                'use_reserves': True,
            },
            403,
            {'code': 'access_denied', 'message': 'General error'},
        ),
    ],
)
async def test_team_create(
        web_context, web_app_client, login, body, status, expected_data,
):
    response = await web_app_client.post(
        '/v1/teams/create',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == status
    content = await response.json()
    assert expected_data == content


@pytest.mark.parametrize(
    'login,body,team_key,status,expected_data',
    [
        (
            'user_admin',
            {
                'base_permission': 'user_testa',
                'ru_name': 'Имя1',
                'en_name': 'Name',
                'piece': False,
                'use_reserves': False,
            },
            'key_2',
            200,
            {
                'key': 'key_2',
                'base_permission': 'user_testa',
                'ru_name': 'Имя1',
                'en_name': 'Name',
                'piece': False,
                'use_reserves': False,
            },
        ),
        (
            'user_admin',
            {},
            'key_3',
            200,
            {
                'key': 'key_3',
                'base_permission': 'user_test',
                'ru_name': 'name_ru',
                'en_name': 'name_en',
                'piece': False,
                'use_reserves': True,
            },
        ),
        (
            'user',
            {
                'base_permission': 'user_testa',
                'ru_name': 'Имя1',
                'en_name': 'Name',
                'piece': False,
                'use_reserves': False,
            },
            'key_2',
            403,
            {'code': 'access_denied', 'message': 'General error'},
        ),
        (
            'user_admin',
            {
                'key': 'key_2',
                'base_permission': 'user_testa',
                'ru_name': 'Имя1',
                'en_name': 'Name',
                'piece': True,
                'use_reserves': True,
            },
            'key_random',
            404,
            {
                'code': 'error_no_team_with_this_key',
                'message': 'General error',
            },
        ),
    ],
)
async def test_teams_update(
        web_app_client, login, team_key, body, status, expected_data,
):
    response = await web_app_client.post(
        f'/v1/teams/{team_key}/update',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == status
    content = await response.json()
    assert content == expected_data
