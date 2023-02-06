import urllib.parse

import pytest

PROJECT1_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'ru-ru',
}
PROJECT2_HEADERS: dict = {
    'X-Yandex-Login': 'user3',
    'Accept-Language': 'ru-ru',
}
PROJECT1_AND_1_HEADERS: dict = {
    'X-Yandex-Login': 'user2',
    'Accept-Language': 'ru-ru',
}


@pytest.mark.config(AGENT_find_project_user_MIN_CHARACTER=3)
@pytest.mark.parametrize(
    'path,headers,status_code,response',
    [
        (
            '/profile/find_project_user?text=webalex',
            PROJECT1_HEADERS,
            200,
            ['owebalexlogin', 'webalex'],
        ),
        ('/profile/find_project_user?text=webalex', PROJECT2_HEADERS, 200, []),
        ('/profile/find_project_user?text=f', PROJECT1_HEADERS, 200, []),
        ('/profile/find_project_user', PROJECT1_HEADERS, 400, []),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '@test_login'}),
            ),
            PROJECT1_HEADERS,
            200,
            ['webalex'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '@another_test'}),
            ),
            PROJECT1_HEADERS,
            200,
            ['webalex'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '@login_test'}),
            ),
            PROJECT1_HEADERS,
            200,
            ['owebalexlogin', 'web'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode(
                    {'text': '   Александр      Иванов3   @login_test     '},
                ),
            ),
            PROJECT1_HEADERS,
            200,
            ['web'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '     Пользователь   '}),
            ),
            PROJECT1_HEADERS,
            200,
            ['user1', 'user2', 'user4'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '     Пользователь   '}),
            ),
            PROJECT2_HEADERS,
            200,
            ['user2', 'user3', 'user4'],
        ),
        (
            '/profile/find_project_user?{}'.format(
                urllib.parse.urlencode({'text': '     Пользователь   '}),
            ),
            PROJECT1_AND_1_HEADERS,
            200,
            ['user1', 'user2', 'user3', 'user4'],
        ),
    ],
)
async def test_search_part(
        web_app_client, path, headers, status_code, response,
):
    res = await web_app_client.get(path, headers=headers)
    assert res.status == status_code
    if status_code == 200:
        content = await res.json()
        users_list = [x['login'] for x in content]
        users_list.sort()
        response.sort()
        assert response == users_list
