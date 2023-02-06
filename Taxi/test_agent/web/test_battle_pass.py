import pytest

from agent import const


async def get_rating(web_context, login):
    async with web_context.pg.slave_pool.acquire() as conn:
        query = (
            """SELECT event,login,current_score,last_score,login,bo,attempts,is_join
            FROM agent.battle_pass_rating WHERE login=\'{}\'""".format(
                login,
            )
        )
        result = await conn.fetch(query)
        return list(map(dict, result))


async def get_logs(web_context, login):
    async with web_context.pg.slave_pool.acquire() as conn:
        query = (
            """SELECT action,login,score
            FROM agent.battle_pass_logs WHERE login=\'{}\'""".format(
                login,
            )
        )
        result = await conn.fetch(query)
        return list(map(dict, result))


@pytest.mark.parametrize(
    """headers,body,status,error_key,
    before_expected_db_data,after_expected_db_data,logs""",
    [
        (
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            {'id': 1},
            201,
            None,
            [
                {
                    'event': 1,
                    'login': 'mikh-vasily',
                    'current_score': 0,
                    'last_score': 0,
                    'bo': 0.0,
                    'attempts': 0,
                    'is_join': False,
                },
            ],
            [
                {
                    'event': 1,
                    'login': 'mikh-vasily',
                    'current_score': 0,
                    'last_score': 0,
                    'bo': 0.0,
                    'attempts': 0,
                    'is_join': True,
                },
            ],
            [{'login': 'mikh-vasily', 'action': 'join', 'score': 0}],
        ),
        (
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            {'id': 2},
            409,
            'battle_pass_event_not_found',
            [
                {
                    'event': 1,
                    'login': 'mikh-vasily',
                    'current_score': 0,
                    'last_score': 0,
                    'bo': 0.0,
                    'attempts': 0,
                    'is_join': False,
                },
            ],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            {'id': 3},
            409,
            'battle_pass_event_not_found',
            [
                {
                    'event': 1,
                    'login': 'mikh-vasily',
                    'current_score': 0,
                    'last_score': 0,
                    'bo': 0.0,
                    'attempts': 0,
                    'is_join': False,
                },
            ],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {'id': 1},
            409,
            'battle_pass_event_not_found',
            [],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {'id': 2},
            201,
            None,
            [],
            [
                {
                    'event': 2,
                    'login': 'webalex',
                    'current_score': 0,
                    'last_score': 0,
                    'bo': 0.0,
                    'attempts': 0,
                    'is_join': True,
                },
            ],
            [{'login': 'webalex', 'action': 'join', 'score': 0}],
        ),
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {'id': 3},
            409,
            'battle_pass_event_not_found',
            [],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'akozhevina', 'Accept-Language': 'ru-ru'},
            {'id': 1},
            409,
            'battle_pass_error_project',
            [],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'akozhevina', 'Accept-Language': 'ru-ru'},
            {'id': 2},
            409,
            'battle_pass_error_project',
            [],
            [],
            [],
        ),
        (
            {'X-Yandex-Login': 'akozhevina', 'Accept-Language': 'ru-ru'},
            {'id': 3},
            409,
            'battle_pass_error_project',
            [],
            [],
            [],
        ),
    ],
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
        'ms': {'enable_chatterbox': False, 'main_permission': 'user_ms'},
    },
)
async def test_join(
        web_context,
        web_app_client,
        headers,
        body,
        status,
        error_key,
        before_expected_db_data,
        after_expected_db_data,
        logs,
):
    assert before_expected_db_data == await get_rating(
        web_context=web_context, login=headers['X-Yandex-Login'],
    )
    response = await web_app_client.post(
        '/battle_pass/join', headers=headers, json=body,
    )
    assert response.status == status
    if response.status == 409:
        content = await response.json()
        assert content['code'] == error_key
    if response.status == 201:

        assert after_expected_db_data == await get_rating(
            web_context=web_context, login=headers['X-Yandex-Login'],
        )

    assert logs == await get_logs(
        web_context=web_context, login=headers['X-Yandex-Login'],
    )

    response = await web_app_client.post(
        '/battle_pass/join', headers=headers, json=body,
    )
    assert response.status == 409


async def test_update_last_score(web_context, web_app_client):
    assert [
        {
            'event': 1,
            'login': 'liambaev',
            'current_score': 100,
            'last_score': 0,
            'bo': 0.0,
            'attempts': 0,
            'is_join': True,
        },
    ] == await get_rating(web_context=web_context, login='liambaev')

    response = await web_app_client.post(
        '/battle_pass/update_last_score',
        headers={'X-Yandex-Login': 'liambaev', 'Accept-Language': 'ru-ru'},
        json={'id': 1},
    )
    assert response.status == 201

    assert [
        {
            'event': 1,
            'login': 'liambaev',
            'current_score': 100,
            'last_score': 100,
            'bo': 0.0,
            'attempts': 0,
            'is_join': True,
        },
    ] == await get_rating(web_context=web_context, login='liambaev')


@pytest.mark.parametrize(
    'headers,expected_data',
    [
        (
            {'X-Yandex-Login': 'liambaev', 'Accept-Language': 'ru-ru'},
            [
                {
                    'id': 1,
                    'is_join': True,
                    'rating': [
                        {
                            'avatar': (
                                const.STAFF_AVATAR_TEMPLATES_URL % 'liambaev'
                            ),
                            'first_name': 'Лиам',
                            'last_name': 'Баев',
                            'login': 'liambaev',
                            'score': 100,
                            'position': 1,
                        },
                    ],
                    'start': '2021-01-01T00:00:00+03:00',
                    'end': '2031-01-01T00:00:00+03:00',
                    'position': 1,
                    'currencies': [
                        {
                            'type': 'snowflake',
                            'current_score': 100,
                            'last_score': 0,
                        },
                        {'current_score': 0, 'last_score': 0, 'type': 'coin'},
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
    },
)
async def test_info(web_context, web_app_client, headers, expected_data):

    response = await web_app_client.get('/battle_pass/info', headers=headers)
    assert response.status == 200
    content = await response.json()
    assert expected_data == content
