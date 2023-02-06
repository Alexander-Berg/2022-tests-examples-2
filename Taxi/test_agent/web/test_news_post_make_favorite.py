import pytest

ROMFORD_HEADERS = {'X-Yandex-Login': 'romford', 'Accept-Language': 'en-EN'}
JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
NO_ACCESS_USER_HEADERS = {
    'X-Yandex-Login': 'no_access_user',
    'Accept-Language': 'ru-RU',
}


@pytest.mark.parametrize(
    'headers,request_data,status_code,expected_amount_of_favorite_posts',
    [
        (JUSTMARK0_HEADERS, {'post_id': 'post1'}, 200, 1),
        (ROMFORD_HEADERS, {'post_id': 'not_found'}, 404, 0),
        (WEBALEX_HEADERS, {'post_id': 'post2'}, 200, 1),
        (NO_ACCESS_USER_HEADERS, {'post_id': 'private_channel_post'}, 403, 0),
    ],
)
async def test_post_make_favorite(
        web_app_client,
        web_context,
        headers,
        request_data,
        status_code,
        expected_amount_of_favorite_posts,
):
    response = await web_app_client.post(
        '/post/favorite', headers=headers, json=request_data,
    )
    assert response.status == status_code
    async with web_context.pg.slave_pool.acquire() as conn:
        login = headers['X-Yandex-Login']
        query = f'SELECT * FROM agent.post_favorites WHERE login = \'{login}\''
        result = await conn.fetch(query)
        assert len(result) == expected_amount_of_favorite_posts
