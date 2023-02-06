import pytest

ROMFORD_HEADERS = {'X-Yandex-Login': 'romford', 'Accept-Language': 'ru'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'en'}

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
                {'project_id': 'project_1', 'name': 'Project 1'},
                {'project_id': 'project_2', 'name': 'Project 2'},
            ],
        ),
        (
            ROMFORD_HEADERS,
            200,
            [{'project_id': 'project_1', 'name': 'Проект 1'}],
        ),
        (WEBALEX_HEADERS, 200, []),
    ],
)
async def test_news_channels_available_to_post(
        web_app_client, headers, status_code, expected_data,
):
    response = await web_app_client.get(
        '/channel/available_projects_to_subscribe', headers=headers,
    )
    assert response.status == status_code
    content = await response.json()
    assert content == expected_data
