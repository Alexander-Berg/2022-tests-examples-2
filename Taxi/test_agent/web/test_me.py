import pytest


AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'help': 'http://wiki.yandex-team.ru',
        },
    },
)
@pytest.mark.parametrize(
    'headers,status_code,response_content',
    [
        ({}, 400, {}),
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'},
            200,
            {
                'login': 'webalex',
                'avatar': AVATAR_TEMPLATE % 'webalex',
                'first_name': 'Александр',
                'last_name': 'Иванов',
                'permissions': [
                    'approve_piecework',
                    'approve_piecework_logistic',
                    'dismiss_users',
                    'naim_users',
                ],
            },
        ),
        (
            {'X-Yandex-Login': 'liam', 'Accept-Language': 'ru-RU'},
            200,
            {
                'login': 'liam',
                'avatar': AVATAR_TEMPLATE % 'liam',
                'first_name': 'liam',
                'last_name': 'liam',
                'permissions': ['user_calltaxi'],
                'project': 'calltaxi',
                'help': 'http://wiki.yandex-team.ru',
            },
        ),
        (
            {
                'X-Yandex-Login': 'login_not_in_system',
                'Accept-Language': 'ru-RU',
            },
            404,
            {},
        ),
    ],
)
async def test_me(web_app_client, headers, status_code, response_content):
    response = await web_app_client.get('/me', headers=headers)
    assert response.status == status_code
    if response.status == 200:
        content = await response.json()
        content['permissions'] = sorted(content['permissions'])
        response_content['permissions'] = sorted(
            response_content['permissions'],
        )
        assert content == response_content
