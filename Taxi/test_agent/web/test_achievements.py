import pytest


TRANSLATE = {
    'access_denied': {'ru': 'Ошибка доступа', 'en': 'Access denied'},
    'achievement.key_2.name': {
        'ru': 'Название ачивки',
        'en': 'Name achievement',
    },
    'achievement.key_2.description': {
        'ru': 'Описание ачивки',
        'en': 'Description achievement',
    },
    'key_not_unuq': {'ru': 'Ключ уже существует', 'en': 'Key exists'},
    'error.achievements_not_found': {
        'ru': 'Ачивка отсутствует',
        'en': 'Achievements not found',
    },
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'login,body,status,expected_data',
    [
        (
            'login_1',
            {
                'key': 'key_1',
                'img_active': 'active_link_1',
                'img_inactive': 'inactive_link_1',
                'is_hidden': False,
            },
            403,
            {'code': 'access_denied', 'message': 'Ошибка доступа'},
        ),
        (
            'login_2',
            {
                'key': 'key_2',
                'img_active': 'active_link_2',
                'img_inactive': 'inactive_link_2',
                'is_hidden': False,
            },
            201,
            {
                'key': 'key_2',
                'name_tanker_key': 'achievement.key_2.name',
                'name': 'Название ачивки',
                'description_tanker_key': 'achievement.key_2.description',
                'description': 'Описание ачивки',
                'img_active': 'active_link_2',
                'img_inactive': 'inactive_link_2',
                'is_hidden': False,
            },
        ),
        (
            'login_2',
            {
                'key': 'key_3',
                'name': 'name_3',
                'description': 'description_3',
                'img_active': 'active_link_3',
                'img_inactive': 'inactive_link_3',
                'is_hidden': False,
            },
            400,
            {'code': 'key_not_unuq', 'message': 'Ключ уже существует'},
        ),
    ],
)
async def test_achievement_add(
        web_context, web_app_client, login, body, status, expected_data,
):
    response = await web_app_client.post(
        '/v1/achievements/create',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == status
    content = await response.json()

    if status == 201:
        expected_data['created'] = content['created']
        if content.get('updated'):
            expected_data['updated'] = content['updated']
    assert expected_data == content


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'login,type_rows,status,expected_data',
    [
        (
            'login_1',
            'all',
            403,
            {'code': 'access_denied', 'message': 'Ошибка доступа'},
        ),
        (
            'login_2',
            'all',
            200,
            [
                {
                    'key': 'key_3',
                    'description_tanker_key': 'achievement.key_3.description',
                    'description': 'achievement.key_3.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'name_tanker_key': 'achievement.key_3.name',
                    'name': 'achievement.key_3.name',
                },
                {
                    'key': 'key_4',
                    'description_tanker_key': 'achievement.key_4.description',
                    'description': 'achievement.key_4.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'name_tanker_key': 'achievement.key_4.name',
                    'name': 'achievement.key_4.name',
                },
                {
                    'key': 'key_5',
                    'description_tanker_key': 'achievement.key_5.description',
                    'description': 'achievement.key_5.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': True,
                    'name_tanker_key': 'achievement.key_5.name',
                    'name': 'achievement.key_5.name',
                },
            ],
        ),
        (
            'login_2',
            'active',
            200,
            [
                {
                    'key': 'key_3',
                    'description_tanker_key': 'achievement.key_3.description',
                    'description': 'achievement.key_3.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'name_tanker_key': 'achievement.key_3.name',
                    'name': 'achievement.key_3.name',
                },
                {
                    'key': 'key_4',
                    'description_tanker_key': 'achievement.key_4.description',
                    'description': 'achievement.key_4.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'name_tanker_key': 'achievement.key_4.name',
                    'name': 'achievement.key_4.name',
                },
            ],
        ),
        (
            'login_2',
            'hidden',
            200,
            [
                {
                    'key': 'key_5',
                    'description_tanker_key': 'achievement.key_5.description',
                    'description': 'achievement.key_5.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': True,
                    'name_tanker_key': 'achievement.key_5.name',
                    'name': 'achievement.key_5.name',
                },
            ],
        ),
    ],
)
async def test_achievements_list(
        web_context, web_app_client, login, type_rows, status, expected_data,
):
    response = await web_app_client.get(
        f'/v1/achievements/list?type={type_rows}',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:

        content_results = [
            {
                'key': row['key'],
                'description_tanker_key': row['description_tanker_key'],
                'description': row['description'],
                'img_active': row['img_active'],
                'img_inactive': row['img_inactive'],
                'is_hidden': row['is_hidden'],
                'name_tanker_key': row['name_tanker_key'],
                'name': row['name'],
            }
            for row in await response.json()
        ]

        assert content_results == expected_data

    else:
        assert await response.json() == expected_data


@pytest.mark.parametrize(
    'login,achievement_id,body,status,expected_data',
    [
        (
            'login_1',
            'key_3',
            {'is_hidden': False},
            403,
            {'code': 'access_denied', 'message': 'Ошибка доступа'},
        ),
        (
            'login_2',
            'key_777',
            {'is_hidden': False},
            400,
            {
                'code': 'error.achievements_not_found',
                'message': 'Ачивка отсутствует',
            },
        ),
        (
            'login_2',
            'key_3',
            {'is_hidden': False},
            201,
            {
                'key': 'key_3',
                'description_tanker_key': 'achievement.key_3.description',
                'description': 'achievement.key_3.description',
                'img_active': 'img_active',
                'img_inactive': 'img_inactive',
                'is_hidden': False,
                'name_tanker_key': 'achievement.key_3.name',
                'name': 'achievement.key_3.name',
            },
        ),
        (
            'login_2',
            'key_3',
            {'is_hidden': False, 'img_active': 'img_active_new'},
            201,
            {
                'key': 'key_3',
                'description_tanker_key': 'achievement.key_3.description',
                'description': 'achievement.key_3.description',
                'img_active': 'img_active_new',
                'img_inactive': 'img_inactive',
                'is_hidden': False,
                'name_tanker_key': 'achievement.key_3.name',
                'name': 'achievement.key_3.name',
            },
        ),
        (
            'login_2',
            'key_3',
            {
                'is_hidden': False,
                'img_active': 'img_active_new',
                'img_inactive': 'img_inactive_new',
            },
            201,
            {
                'key': 'key_3',
                'description_tanker_key': 'achievement.key_3.description',
                'description': 'achievement.key_3.description',
                'img_active': 'img_active_new',
                'img_inactive': 'img_inactive_new',
                'is_hidden': False,
                'name_tanker_key': 'achievement.key_3.name',
                'name': 'achievement.key_3.name',
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
async def test_achievements_update(
        web_context,
        web_app_client,
        login,
        achievement_id,
        body,
        status,
        expected_data,
):
    response = await web_app_client.post(
        f'/v1/achievements/{achievement_id}/update',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == status
    content = await response.json()

    if response.status == 201:

        expected_data.update(
            {'created': content['created'], 'updated': content['updated']},
        )
        assert content == expected_data
    else:
        assert content == expected_data


async def test_collections_list(web_context, web_app_client):
    response = await web_app_client.get(
        '/v1/achievements/collections/list',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'id': '2c04b547a3da476e85b50ead69db1970',
            'name': 'Первая коллекция',
            'items': [
                {
                    'created': '2021-01-01T00:00:00Z',
                    'description': 'achievement.key_3.description',
                    'description_tanker_key': 'achievement.key_3.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'key': 'key_3',
                    'name': 'achievement.key_3.name',
                    'name_tanker_key': 'achievement.key_3.name',
                    'coins': 0,
                    'lootbox_skin': 'rare_card',
                },
                {
                    'created': '2021-01-01T00:00:01Z',
                    'description': 'achievement.key_4.description',
                    'description_tanker_key': 'achievement.key_4.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'key': 'key_4',
                    'name': 'achievement.key_4.name',
                    'name_tanker_key': 'achievement.key_4.name',
                    'coins': 0,
                    'lootbox_skin': 'common_card',
                },
                {
                    'created': '2021-01-01T00:00:02Z',
                    'description': 'achievement.key_5.description',
                    'description_tanker_key': 'achievement.key_5.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': True,
                    'key': 'key_5',
                    'name': 'achievement.key_5.name',
                    'name_tanker_key': 'achievement.key_5.name',
                    'coins': 0,
                    'lootbox_skin': 'immortal_card',
                },
            ],
        },
        {
            'id': '2c04b547a3da476e85b50ead88njff',
            'name': 'Вторая коллекция',
            'items': [
                {
                    'created': '2021-01-01T00:00:00Z',
                    'description': 'achievement.key_3.description',
                    'description_tanker_key': 'achievement.key_3.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'key': 'key_3',
                    'name': 'achievement.key_3.name',
                    'name_tanker_key': 'achievement.key_3.name',
                    'coins': 0,
                    'lootbox_skin': 'common_card',
                },
                {
                    'created': '2021-01-01T00:00:01Z',
                    'description': 'achievement.key_4.description',
                    'description_tanker_key': 'achievement.key_4.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': False,
                    'key': 'key_4',
                    'name': 'achievement.key_4.name',
                    'name_tanker_key': 'achievement.key_4.name',
                    'coins': 0,
                    'lootbox_skin': 'common_card',
                },
                {
                    'created': '2021-01-01T00:00:02Z',
                    'description': 'achievement.key_5.description',
                    'description_tanker_key': 'achievement.key_5.description',
                    'img_active': 'img_active',
                    'img_inactive': 'img_inactive',
                    'is_hidden': True,
                    'key': 'key_5',
                    'name': 'achievement.key_5.name',
                    'name_tanker_key': 'achievement.key_5.name',
                    'coins': 0,
                    'lootbox_skin': 'common_card',
                },
            ],
        },
        {
            'id': '1791fd06c11b46d5a08f1fb32ded99b2',
            'name': 'Третья пустая коллекция',
            'items': [],
        },
    ]


@pytest.mark.parametrize('body', [({'name': 'Первая коллекция'})])
async def test_collections_create(web_context, web_app_client, body):
    response = await web_app_client.post(
        '/v1/achievements/collections/create',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == 200
    content = await response.json()
    assert content['name'] == body['name']


@pytest.mark.parametrize(
    'collection_id,body,expected_response',
    [
        (
            '2c04b547a3da476e85b50ead69db1970',
            {
                'name': 'Updated name :)',
                'items': [
                    {
                        'achievement_id': 'key_3',
                        'coins': 10,
                        'lootbox_skin': 'immortal_card',
                    },
                    {
                        'achievement_id': 'key_4',
                        'coins': 15,
                        'lootbox_skin': 'rare_card',
                    },
                ],
            },
            {
                'id': '2c04b547a3da476e85b50ead69db1970',
                'name': 'Updated name :)',
                'items': [
                    {
                        'created': '2021-01-01T00:00:00Z',
                        'description': 'achievement.key_3.description',
                        'description_tanker_key': (
                            'achievement.key_3.description'
                        ),
                        'img_active': 'img_active',
                        'img_inactive': 'img_inactive',
                        'is_hidden': False,
                        'key': 'key_3',
                        'name': 'achievement.key_3.name',
                        'name_tanker_key': 'achievement.key_3.name',
                        'coins': 10,
                        'lootbox_skin': 'immortal_card',
                    },
                    {
                        'created': '2021-01-01T00:00:01Z',
                        'description': 'achievement.key_4.description',
                        'description_tanker_key': (
                            'achievement.key_4.description'
                        ),
                        'img_active': 'img_active',
                        'img_inactive': 'img_inactive',
                        'is_hidden': False,
                        'key': 'key_4',
                        'name': 'achievement.key_4.name',
                        'name_tanker_key': 'achievement.key_4.name',
                        'coins': 15,
                        'lootbox_skin': 'rare_card',
                    },
                ],
            },
        ),
        (
            '2c04b547a3da476e85b50ead69db1970',
            {'name': 'Updated name :)', 'items': []},
            {
                'id': '2c04b547a3da476e85b50ead69db1970',
                'name': 'Updated name :)',
                'items': [],
            },
        ),
    ],
)
async def test_collections_update(
        web_context, web_app_client, collection_id, body, expected_response,
):
    response = await web_app_client.post(
        f'/v1/achievements/collections/{collection_id}/update',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
        json=body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
