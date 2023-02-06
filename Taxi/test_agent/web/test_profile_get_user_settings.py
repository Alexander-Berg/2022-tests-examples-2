import pytest

PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'calltaxi': {
        'enable_chatterbox': False,
        'main_permission': 'user_calltaxi',
    },
}


@pytest.mark.parametrize(
    'login, target_login, expected_answer',
    [
        (
            'chief',
            'regular_login',
            {
                'general_settings': {
                    'available_teams': [
                        {'key': 'team_1', 'name': 'КОМАНДА 1'},
                    ],
                    'team': 'team_1',
                },
                'chatterbox_settings': {
                    'assigned_lines': ['line_1', 'line_2'],
                    'available_languages': [
                        {'id': 'ru', 'name': 'Русский'},
                        {'id': 'en', 'name': 'Английский'},
                    ],
                    'available_lines': [
                        {'id': 'line_1', 'name': 'ЛИНИЯ 1', 'mode': 'online'},
                        {'id': 'line_2', 'name': 'ЛИНИЯ 2', 'mode': 'online'},
                        {
                            'id': 'line_3',
                            'name': 'line_3_tanker_key',
                            'mode': 'offline',
                        },
                    ],
                    'can_choose_except_assigned_lines': True,
                    'can_choose_from_assigned_lines': True,
                    'languages': ['ru', 'en'],
                    'max_chats': 12,
                    'work_off_shift': True,
                },
            },
        ),
        (
            'chief',
            'empty_login',
            {
                'general_settings': {
                    'available_teams': [
                        {'key': 'team_1', 'name': 'КОМАНДА 1'},
                    ],
                    'team': 'team_1',
                },
                'chatterbox_settings': {
                    'assigned_lines': [],
                    'available_languages': [
                        {'id': 'ru', 'name': 'Русский'},
                        {'id': 'en', 'name': 'Английский'},
                    ],
                    'available_lines': [],
                    'can_choose_except_assigned_lines': True,
                    'can_choose_from_assigned_lines': True,
                    'languages': [],
                    'max_chats': 5,
                    'work_off_shift': False,
                },
            },
        ),
        (
            'market_chief',
            'market_login',
            {'general_settings': {'available_teams': [], 'team': 'team_1'}},
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
@pytest.mark.translations(
    agent={
        'language_ru': {'ru': 'Русский', 'en': 'Russian'},
        'language_en': {'ru': 'Английский', 'en': 'English'},
    },
    chatterbox={
        'line_1_tanker_key': {'ru': 'ЛИНИЯ 1', 'en': 'LINE 1'},
        'line_2_tanker_key': {'ru': 'ЛИНИЯ 2', 'en': 'LINE 2'},
    },
)
async def test_get_user_settings(
        web_app_client, web_context, login, target_login, expected_answer,
):
    response = await web_app_client.get(
        '/profile/settings',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        params={'login': target_login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_answer


@pytest.mark.parametrize(
    'login, target_login, expected_code',
    [
        ('regular_login', 'regular_login', 403),
        ('empty_login', 'regular_login', 403),
        ('chief', 'regular_login', 200),
        ('admin', 'regular_login', 200),
    ],
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_get_user_settings_access(
        web_app_client, web_context, login, target_login, expected_code,
):
    response = await web_app_client.get(
        '/profile/settings',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        params={'login': target_login},
    )

    assert response.status == expected_code
