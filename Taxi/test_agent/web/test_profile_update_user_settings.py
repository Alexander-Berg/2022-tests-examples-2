import pytest

PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'calltaxi': {
        'enable_chatterbox': False,
        'main_permission': 'user_calltaxi',
    },
}


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.parametrize(
    'login, target_login, json, db_users_data, db_user_history_team_data, '
    'db_chatterbox_support_settings_data, status',
    [
        (
            'admin',
            'regular_login',
            {'login': 'regular_login'},
            ['regular_login', 'team_1'],
            [],
            [],
            201,
        ),
        (
            'admin',
            'regular_login',
            {
                'login': 'regular_login',
                'general_settings': {'team': 'team_12'},
                'chatterbox_settings': {
                    'assigned_lines': ['line_1', 'line_2'],
                },
            },
            ['regular_login', 'team_12'],
            ['regular_login', 'team_12'],
            [
                'regular_login',
                ['line_1', 'line_2'],
                True,
                True,
                5,
                [],
                False,
                False,
            ],
            201,
        ),
        (
            'admin',
            'regular_login',
            {
                'login': 'regular_login',
                'general_settings': {'team': 'team_12'},
                'chatterbox_settings': {
                    'assigned_lines': ['line_1', 'line_2'],
                    'can_choose_from_assigned_lines': True,
                    'can_choose_except_assigned_lines': False,
                    'max_chats': 15,
                    'languages': ['ru', 'en'],
                    'work_off_shift': True,
                },
            },
            ['regular_login', 'team_12'],
            ['regular_login', 'team_12'],
            [
                'regular_login',
                ['line_1', 'line_2'],
                True,
                False,
                15,
                ['ru', 'en'],
                True,
                False,
            ],
            201,
        ),
        (
            'admin',
            'regular_login',
            {
                'login': 'regular_login',
                'general_settings': {'team': 'team_30'},
            },
            ['regular_login', 'team_1'],
            [],
            [],
            400,
        ),
        (
            'admin',
            'regular_login',
            {
                'login': 'regular_login',
                'chatterbox_settings': {
                    'assigned_lines': ['line_1', 'line_30', 'line_777'],
                },
            },
            ['regular_login', 'team_1'],
            [],
            ['regular_login', ['line_1'], True, True, 5, [], False, False],
            201,
        ),
        (
            'admin',
            'regular_login',
            {
                'login': 'regular_login',
                'chatterbox_settings': {'languages': ['kz']},
            },
            ['regular_login', 'team_1'],
            [],
            [],
            400,
        ),
    ],
)
@pytest.mark.config(
    AGENT_CHATTERBOX_AVAILABLE_USER_LANGUAGES=['ru', 'en'],
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': True,
            'main_permission': 'user_calltaxi',
        },
    },
)
async def test_update_user_settings(
        web_app_client,
        web_context,
        login,
        target_login,
        json,
        db_users_data,
        db_user_history_team_data,
        db_chatterbox_support_settings_data,
        status,
):
    response = await web_app_client.post(
        '/profile/settings/update',
        headers={'X-Yandex-Login': login},
        json=json,
    )

    assert response.status == status
    async with web_context.pg.slave_pool.acquire() as conn:
        query = (
            f'SELECT login, team FROM agent.users '
            f'WHERE login = \'{target_login}\''
        )
        result = await conn.fetch(query)
        if db_users_data:
            assert list(result[0]) == db_users_data
        else:
            assert result == []

    async with web_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT login, team FROM agent.user_history_team'
        result = await conn.fetch(query)
        if db_user_history_team_data:
            assert list(result[0]) == db_user_history_team_data
        else:
            assert result == []

    async with web_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.chatterbox_support_settings'
        result = await conn.fetch(query)
        if db_chatterbox_support_settings_data:
            assert list(result[0]) == db_chatterbox_support_settings_data
        else:
            assert result == []


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.parametrize(
    'login, target_login, json, expected_code',
    [
        ('regular_login', 'regular_login', {'login': 'regular_login'}, 403),
        ('empty_login', 'regular_login', {'login': 'regular_login'}, 403),
        ('chief', 'regular_login', {'login': 'regular_login'}, 201),
        ('admin', 'regular_login', {'login': 'regular_login'}, 201),
        (
            'market_chief',
            'market_login',
            {
                'login': 'market_login',
                'chatterbox_settings': {'max_chats': 15},
            },
            403,
        ),
    ],
)
async def test_update_user_settings_access(
        web_app_client, web_context, login, target_login, json, expected_code,
):
    response = await web_app_client.post(
        '/profile/settings/update',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json=json,
    )

    assert response.status == expected_code
