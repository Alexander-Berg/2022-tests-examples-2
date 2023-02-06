import pytest

ROMFORD_HEADERS = {'X-Yandex-Login': 'romford', 'Accept-Language': 'en-EN'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}

CONFIG = {
    'project_1': {'main_permission': 'user_project_1_perm'},
    'project_2': {'main_permission': 'user_project_2_perm'},
}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'headers,post_ids,expected_views',
    [
        (JUSTMARK0_HEADERS, ['post1', 'post1'], {'post1'}),
        (ROMFORD_HEADERS, ['post-not-exist', 'post2'], {'post2'}),
        (
            WEBALEX_HEADERS,
            ['post1', 'post2', 'post3'],
            {'post1', 'post2', 'post3'},
        ),
    ],
)
async def test_news_channels_available_to_post(
        web_app_client, web_context, headers, post_ids, expected_views,
):
    response = await web_app_client.post(
        '/post/mark_as_viewed', headers=headers, json={'posts': post_ids},
    )
    assert response.status == 200
    login = headers['X-Yandex-Login']
    query = f"""SELECT * FROM agent.post_views WHERE login = \'{login}\' """
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        viewed = set()
        for row in rows:
            row = dict(row)
            viewed.add(row['post_id'])
        assert viewed == expected_views
