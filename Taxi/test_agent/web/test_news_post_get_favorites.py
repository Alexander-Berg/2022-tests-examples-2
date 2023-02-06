import pytest

JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
ROMFORD_HEADERS = {'X-Yandex-Login': 'romford', 'Accept-Language': 'ru-RU'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-EN'}
NO_ACCESS_USER_HEADERS = {
    'X-Yandex-Login': 'no_access_user',
    'Accept-Language': 'en-EN',
}

AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'

JUSTMARK0_EXPECTED_RESULT = [
    {
        'id': 'post_5',
        'author': {
            'first_name': 'Mark',
            'last_name': 'Nicholson',
            'login': 'justmark0',
            'avatar': AVATAR_TEMPLATE % 'justmark0',
        },
        'created': '2022-01-01T00:00:00+03:00',
        'channels': [
            {'channel_id': 'channel_2', 'channel_name': 'channel_2_name'},
        ],
        'images': [],
        'likes': 0,
        'views': 0,
        'text': 'text',
        'format': 'text',
        'can_manage': True,
        'liked': False,
        'viewed': False,
    },
    {
        'id': 'post_2',
        'author': {
            'first_name': 'Mark',
            'last_name': 'Nicholson',
            'login': 'justmark0',
            'avatar': AVATAR_TEMPLATE % 'justmark0',
        },
        'created': '2022-01-01T00:00:00+03:00',
        'channels': [
            {'channel_id': 'channel_1', 'channel_name': 'channel_1_name'},
        ],
        'likes': 0,
        'views': 0,
        'text': 'text',
        'format': 'text',
        'can_manage': True,
        'liked': False,
        'viewed': False,
        'images': [
            {
                'file_id': 'image_1',
                'url': 'https://s3.mds.yandex.net/taxiagent/image_1',
            },
        ],
    },
    {
        'id': 'post_1',
        'author': {
            'first_name': 'Mark',
            'last_name': 'Nicholson',
            'login': 'justmark0',
            'avatar': AVATAR_TEMPLATE % 'justmark0',
        },
        'created': '2022-01-01T00:00:00+03:00',
        'channels': [
            {'channel_id': 'channel_1', 'channel_name': 'channel_1_name'},
            {'channel_id': 'channel_2', 'channel_name': 'channel_2_name'},
        ],
        'images': [],
        'likes': 1,
        'views': 1,
        'text': 'text',
        'format': 'text',
        'can_manage': True,
        'liked': True,
        'viewed': True,
    },
]

WEBALEX_EXPECTED_RESULT = [
    {
        'id': 'post_1',
        'author': {
            'first_name': 'Mark',
            'last_name': 'Nicholson',
            'login': 'justmark0',
            'avatar': AVATAR_TEMPLATE % 'justmark0',
        },
        'created': '2022-01-01T00:00:00+03:00',
        'channels': [
            {'channel_id': 'channel_1', 'channel_name': 'channel_1_name'},
            {'channel_id': 'channel_2', 'channel_name': 'channel_2_name'},
        ],
        'images': [],
        'likes': 1,
        'views': 1,
        'text': 'text',
        'format': 'text',
        'can_manage': False,
        'liked': False,
        'viewed': False,
    },
    {
        'id': 'post_5',
        'author': {
            'first_name': 'Mark',
            'last_name': 'Nicholson',
            'login': 'justmark0',
            'avatar': AVATAR_TEMPLATE % 'justmark0',
        },
        'created': '2022-01-01T00:00:00+03:00',
        'channels': [
            {'channel_id': 'channel_2', 'channel_name': 'channel_2_name'},
        ],
        'images': [],
        'likes': 0,
        'views': 0,
        'text': 'text',
        'format': 'text',
        'can_manage': False,
        'liked': False,
        'viewed': False,
    },
]


@pytest.mark.parametrize(
    'headers,url,expected_data',
    [
        (JUSTMARK0_HEADERS, '/post/favorite', JUSTMARK0_EXPECTED_RESULT),
        (
            WEBALEX_HEADERS,
            '/post/favorite?start_post_id=post_3',
            WEBALEX_EXPECTED_RESULT,
        ),
        (ROMFORD_HEADERS, '/post/favorite', []),
        (NO_ACCESS_USER_HEADERS, '/post/favorite', []),
    ],
)
async def test_news_post_get_favorites(
        web_app_client, headers, url, expected_data,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == 200
    content = await response.json()
    assert content == expected_data
