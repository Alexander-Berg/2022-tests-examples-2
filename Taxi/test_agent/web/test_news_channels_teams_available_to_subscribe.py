import pytest

JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
ADMIN_HEADERS = {'X-Yandex-Login': 'admin', 'Accept-Language': 'ru-RU'}
ROMFORD_HEADERS = {'X-Yandex-Login': 'romford', 'Accept-Language': 'en-EN'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}

CONFIG = {
    'project_1': {
        'main_permission': 'user_project_1_perm',
        'ru_name': 'Проект 1',
        'en_name': 'Project 1',
    },
    'project_2': {
        'main_permission': 'user_project_2_perm',
        'ru_name': 'Проект 2',
        'en_name': 'Project 2',
    },
}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'headers,status_code,expected_data',
    [
        (
            JUSTMARK0_HEADERS,
            200,
            [
                {
                    'team_id': 'team_1',
                    'name': 'team_1',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Проект 1',
                    },
                },
                {
                    'team_id': 'team_2',
                    'name': 'team_2',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Проект 1',
                    },
                },
            ],
        ),
        (
            ROMFORD_HEADERS,
            200,
            [
                {
                    'team_id': 'team_1',
                    'name': 'team_1_en',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Project 1',
                    },
                },
                {
                    'team_id': 'team_2',
                    'name': 'team_2_en',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Project 1',
                    },
                },
                {
                    'team_id': 'team_3',
                    'name': 'team_3_en',
                    'project_info': {
                        'project_id': 'project_2',
                        'name': 'Project 2',
                    },
                },
                {
                    'team_id': 'team_4',
                    'name': 'team_4_en',
                    'project_info': {
                        'project_id': 'project_2',
                        'name': 'Project 2',
                    },
                },
            ],
        ),
        (WEBALEX_HEADERS, 200, []),
        (
            ADMIN_HEADERS,
            200,
            [
                {
                    'team_id': 'team_1',
                    'name': 'team_1',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Проект 1',
                    },
                },
                {
                    'team_id': 'team_2',
                    'name': 'team_2',
                    'project_info': {
                        'project_id': 'project_1',
                        'name': 'Проект 1',
                    },
                },
                {
                    'team_id': 'team_3',
                    'name': 'team_3',
                    'project_info': {
                        'project_id': 'project_2',
                        'name': 'Проект 2',
                    },
                },
                {
                    'team_id': 'team_4',
                    'name': 'team_4',
                    'project_info': {
                        'project_id': 'project_2',
                        'name': 'Проект 2',
                    },
                },
            ],
        ),
    ],
)
async def test_news_teams_available_to_subscribe(
        web_app_client, headers, status_code, expected_data,
):
    response = await web_app_client.get(
        '/channel/available_teams_to_subscribe', headers=headers,
    )
    assert response.status == status_code
    content = await response.json()
    assert content == expected_data
