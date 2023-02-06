import pytest

AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'

PROJECT1_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'ru-ru',
}
PROJECT2_HEADERS: dict = {
    'X-Yandex-Login': 'user3',
    'Accept-Language': 'ru-ru',
}
PROJECT1_AND_2_HEADERS: dict = {
    'X-Yandex-Login': 'user2',
    'Accept-Language': 'ru-ru',
}


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'project1': {
            'enable_chatterbox': False,
            'main_permission': 'user_project1',
        },
        'project2': {
            'enable_chatterbox': False,
            'main_permission': 'user_project2',
        },
    },
)
@pytest.mark.parametrize(
    'headers,request_data,expected_result_data',
    [
        (
            PROJECT1_HEADERS,
            {'search_string': ' wEb  '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'owebalexlogin',
                        'login': 'owebalexlogin',
                        'first_name': 'Александр1',
                        'last_name': 'Иванов1',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'web',
                        'login': 'web',
                        'first_name': 'Александр2',
                        'last_name': 'Иванов2',
                    },
                    {
                        'avatar': (AVATAR_TEMPLATE % 'webalex'),
                        'login': 'webalex',
                        'first_name': 'Александр',
                        'last_name': 'Иванов',
                    },
                ],
            },
        ),
        (PROJECT2_HEADERS, {'search_string': ' wEb  '}, {'users': []}),
        (
            PROJECT1_HEADERS,
            {'search_string': ' нОв1  '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'owebalexlogin',
                        'login': 'owebalexlogin',
                        'first_name': 'Александр1',
                        'last_name': 'Иванов1',
                    },
                ],
            },
        ),
        (
            PROJECT1_HEADERS,
            {'search_string': ' ПОЛЬЗОВАТЕЛЬ  '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'user1',
                        'login': 'user1',
                        'first_name': 'Первый',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'user2',
                        'login': 'user2',
                        'first_name': 'Второй',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': (AVATAR_TEMPLATE % 'user4'),
                        'login': 'user4',
                        'first_name': 'Четвертый',
                        'last_name': 'Пользователь',
                    },
                ],
            },
        ),
        (
            PROJECT2_HEADERS,
            {'search_string': ' ПОЛЬЗОВАТЕЛЬ  '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'user2',
                        'login': 'user2',
                        'first_name': 'Второй',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': (AVATAR_TEMPLATE % 'user4'),
                        'login': 'user4',
                        'first_name': 'Четвертый',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'user3',
                        'login': 'user3',
                        'first_name': 'Третий',
                        'last_name': 'Пользователь',
                    },
                ],
            },
        ),
        (
            PROJECT1_AND_2_HEADERS,
            {'search_string': ' ПОЛЬзоВАТЕЛЬ  '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'user1',
                        'login': 'user1',
                        'first_name': 'Первый',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'user2',
                        'login': 'user2',
                        'first_name': 'Второй',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': (AVATAR_TEMPLATE % 'user4'),
                        'login': 'user4',
                        'first_name': 'Четвертый',
                        'last_name': 'Пользователь',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'user3',
                        'login': 'user3',
                        'first_name': 'Третий',
                        'last_name': 'Пользователь',
                    },
                ],
            },
        ),
    ],
)
async def test_user_project_suggest(
        web_app_client, headers, request_data, expected_result_data,
):
    response = await web_app_client.post(
        '/user_suggest/project', headers=headers, json=request_data,
    )
    assert response.status == 200
    content = await response.json()
    assert expected_result_data == content
