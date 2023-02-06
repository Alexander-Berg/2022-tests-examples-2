import pytest

RU_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}


@pytest.mark.parametrize(
    'body,headers,status,response_content',
    [
        (
            {'type_action': 'add', 'key': 'channel_1', 'logins': ['webalex']},
            {},
            400,
            {},
        ),
        ({}, {}, 400, {}),
        (
            {'type_action': 'add', 'key': 'chatterbox', 'logins': ['webalex']},
            RU_HEADERS,
            201,
            {'logins': ['liambaev', 'webalex']},
        ),
        (
            {
                'type_action': 'add',
                'key': 'chatterbox',
                'logins': ['liambaev'],
            },
            RU_HEADERS,
            201,
            {'logins': ['liambaev']},
        ),
        (
            {
                'type_action': 'replace',
                'key': 'chatterbox',
                'logins': ['webalex'],
            },
            RU_HEADERS,
            201,
            {'logins': ['webalex']},
        ),
        (
            {
                'type_action': 'clear',
                'key': 'chatterbox',
                'logins': ['webalex'],
            },
            RU_HEADERS,
            201,
            {'logins': []},
        ),
        (
            {
                'type_action': 'remove',
                'key': 'chatterbox',
                'logins': ['liambaev'],
            },
            RU_HEADERS,
            201,
            {'logins': []},
        ),
        (
            {'type_action': 'add', 'key': 'chatterbox', 'logins': ['webalex']},
            RU_HEADERS,
            201,
            {'logins': ['liambaev', 'webalex']},
        ),
        (
            {
                'type_action': 'replace',
                'key': 'chatterbox',
                'logins': ['webalex'],
            },
            RU_HEADERS,
            201,
            {'logins': ['webalex']},
        ),
        (
            {
                'type_action': 'clear',
                'key': 'chatterbox',
                'logins': ['webalex'],
            },
            RU_HEADERS,
            201,
            {'logins': []},
        ),
        (
            {
                'type_action': 'remove',
                'key': 'chatterbox',
                'logins': ['liambaev'],
            },
            RU_HEADERS,
            201,
            {'logins': []},
        ),
        (
            {
                'type_action': 'abracadabra',
                'key': 'chatterbox',
                'logins': ['liambaev'],
            },
            RU_HEADERS,
            400,
            {},
        ),
    ],
)
async def test_responsible(
        web_app_client, body, headers, status, response_content,
):
    res = await web_app_client.post(
        '/channel/responsible', json=body, headers=headers,
    )
    assert res.status == status
    if res.status == 201:
        content = await res.json()
        assert content == response_content
