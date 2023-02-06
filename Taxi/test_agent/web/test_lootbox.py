import pytest

RU_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
RU_HEADERS1 = {'X-Yandex-Login': 'user2', 'Accept-Language': 'ru-RU'}
RU_403_HEADERS = {
    'X-Yandex-Login': 'user_without_permission',
    'Accept-Language': 'ru-RU',
}
RU_HEADERS_2 = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}


REQUEST_DATA1 = {
    'login': 'user1',
    'description': 'happy birthday',
    'coins': 12,
    'skin': 'gold confetti',
}

EXPECTED_DATA1 = {
    'description': 'happy birthday',
    'coins': 12,
    'skin': 'gold confetti',
}

EXPECTED_DATA2 = [
    {
        'id': '1234',
        'description': 'happy birthday1',
        'image': 'link1',
        'skin': 'gold confetti',
    },
    {
        'id': '1235',
        'description': 'happy birthday2',
        'coins': 12,
        'skin': 'gold confetti',
    },
    {'id': '1236', 'description': 'happy birthday3', 'skin': 'pink confetti'},
]


@pytest.mark.parametrize(
    'headers,body,status_code,response_content',
    [
        (RU_HEADERS, REQUEST_DATA1, 201, EXPECTED_DATA1),
        ({}, {}, 400, {}),
        (
            RU_403_HEADERS,
            {
                'login': 'justmark0',
                'description': 'happy birthday',
                'skin': 'gold',
            },
            403,
            {},
        ),
        (
            RU_HEADERS,
            {
                'login': 'no_such_username_in_db',
                'description': 'happy birthday',
                'coins': 12,
                'skin': 'gold',
            },
            400,
            {},
        ),
    ],
)
async def test_lootbox_cretion(
        web_app_client, headers, body, status_code, response_content,
):
    response = await web_app_client.post(
        '/lootbox/create', headers=headers, json=body,
    )
    assert response.status == status_code
    if response.status == 201:
        content = await response.json()
        identifier = content.pop('id')
        assert identifier is not None
        assert content == response_content


@pytest.mark.parametrize(
    'headers,body,status_code,response_content',
    [
        (RU_HEADERS, {'id': 'a111000222'}, 200, {}),
        (RU_HEADERS, {'id': 'key_that_is_not_in_db'}, 404, {}),
    ],
)
async def test_lootbox_as_viewed(
        web_app_client, headers, body, status_code, response_content,
):
    response = await web_app_client.post(
        '/lootbox/mark_as_viewed', headers=headers, json=body,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    'headers,status_code,response_content',
    [(RU_HEADERS1, 200, EXPECTED_DATA2)],
)
async def test_get_lootboxes(
        web_app_client, headers, status_code, response_content,
):
    response = await web_app_client.get('/lootboxes', headers=headers)
    assert response.status == status_code
    content = await response.json()
    assert content == response_content
