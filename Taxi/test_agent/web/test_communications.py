import pytest


@pytest.mark.parametrize(
    'url,headers,expected_response',
    [
        (
            '/communications',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {
                'notifications': [
                    {
                        'id': '72691367106446e48815f31894274405',
                        'title': 'Test 5',
                        'body': 'Test 5',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:05+0000',
                        'type': 'warning',
                    },
                    {
                        'id': '72691367106446e48815f31894274404',
                        'title': 'Test 4',
                        'body': 'Test 4',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:04+0000',
                        'type': 'warning',
                    },
                    {
                        'id': '72691367106446e48815f31894274403',
                        'title': 'Test 3',
                        'body': 'Test 3',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:03+0000',
                        'type': 'warning',
                    },
                    {
                        'id': '72691367106446e48815f31894274402',
                        'title': 'Test 2',
                        'body': 'Test 2',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:02+0000',
                        'type': 'warning',
                    },
                    {
                        'id': '72691367106446e48815f31894274401',
                        'title': 'Test 1',
                        'body': 'Test 1',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:01+0000',
                        'type': 'warning',
                    },
                ],
            },
        ),
        (
            '/communications?limit=100&last_created_at=2021-01-02T00:00:02Z',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {
                'notifications': [
                    {
                        'id': '72691367106446e48815f31894274401',
                        'title': 'Test 1',
                        'body': 'Test 1',
                        'is_new': True,
                        'created_at': '2021-01-02T00:00:01+0000',
                        'type': 'warning',
                    },
                ],
            },
        ),
    ],
)
async def test_communications(
        web_context, web_app_client, url, headers, expected_response,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == 200
    assert await response.json() == expected_response


async def test_communications_mark_viewed(web_context, web_app_client):
    response = await web_app_client.post(
        '/communications',
        headers={'X-Yandex-Login': 'liambaev', 'Accept-Language': 'ru-ru'},
        json={'id': '72691367106446e48815f31894274401'},
    )
    assert response.status == 403

    async with web_context.pg.slave_pool.acquire() as conn:
        mass_query_1 = """SELECT * FROM agent.mass_notifications
        WHERE id=\'5c140185d6f24d1a55412dba1f357ef\'"""
        mass_res_1 = await conn.fetchrow(mass_query_1)
        assert mass_res_1['viewed_users'] == 0

    response = await web_app_client.post(
        '/communications',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
        json={'id': '72691367106446e48815f31894274401'},
    )
    assert response.status == 200

    async with web_context.pg.slave_pool.acquire() as conn:
        mass_query_2 = """SELECT * FROM agent.mass_notifications
        WHERE id=\'5c140185d6f24d1a55412dba1f357ef\'"""
        mass_res_2 = await conn.fetchrow(mass_query_2)
        assert mass_res_2['viewed_users'] == 1

    second_response = await web_app_client.post(
        '/communications',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
        json={'id': '72691367106446e48815f31894274401'},
    )
    assert second_response.status == 200

    no_found_response = await web_app_client.post(
        '/communications',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
        json={'id': '72691367106446e48815f31894274499'},
    )

    assert no_found_response.status == 404


@pytest.mark.parametrize('login,count', [('webalex', 5), ('orangevl', 0)])
async def test_communications_count(web_context, web_app_client, login, count):
    response = await web_app_client.get(
        '/communications/count',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'count': count}
