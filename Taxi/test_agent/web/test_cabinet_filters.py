import pytest


@pytest.mark.parametrize(
    'headers, expected_answer',
    [
        (
            {'X-Yandex-Login': 'chief', 'Accept-Language': 'ru-ru'},
            {
                'logins': ['calltaxi_support', 'chief'],
                'countries': [
                    {'id': 'by', 'name': 'Беларусь'},
                    {'id': 'ru', 'name': 'Россия'},
                ],
                'departments': [{'id': 'yandex', 'name': 'Яндекс'}],
                'teams': [{'id': 'a_team', 'name': 'A-команда'}],
                'lines': [
                    {
                        'id': 'null_tanker_key_line',
                        'name': 'null_tanker_key_line',
                    },
                    {'id': 'line_1', 'name': 'Линия 1'},
                    {'id': 'line_2', 'name': 'Линия 2'},
                    {'id': 'line_4', 'name': 'Линия 4'},
                ],
                'languages': [
                    {'id': 'en', 'name': 'Английский'},
                    {'id': 'ru', 'name': 'Русский'},
                ],
                'projects': [{'id': 'calltaxi', 'name': 'Коллтакси'}],
            },
        ),
        (
            {'X-Yandex-Login': 'chief', 'Accept-Language': 'en-en'},
            {
                'logins': ['calltaxi_support', 'chief'],
                'countries': [
                    {'id': 'by', 'name': 'Belarus'},
                    {'id': 'ru', 'name': 'Russia'},
                ],
                'departments': [{'id': 'yandex', 'name': 'Яндекс'}],
                'teams': [{'id': 'a_team', 'name': 'A team'}],
                'lines': [
                    {'id': 'line_1', 'name': 'Line 1'},
                    {'id': 'line_2', 'name': 'Line 2'},
                    {'id': 'line_4', 'name': 'Line 4'},
                    {
                        'id': 'null_tanker_key_line',
                        'name': 'null_tanker_key_line',
                    },
                ],
                'languages': [
                    {'id': 'en', 'name': 'English'},
                    {'id': 'ru', 'name': 'Russian'},
                ],
                'projects': [{'id': 'calltaxi', 'name': 'Calltaxi'}],
            },
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'line_1_name': {'ru': 'Линия 1', 'en': 'Line 1'},
        'line_2_name': {'ru': 'Линия 2', 'en': 'Line 2'},
        'line_4_name': {'ru': 'Линия 4', 'en': 'Line 4'},
    },
    agent={
        'country_ru': {'ru': 'Россия', 'en': 'Russia'},
        'country_by': {'ru': 'Беларусь', 'en': 'Belarus'},
        'language_ru': {'ru': 'Русский', 'en': 'Russian'},
        'language_en': {'ru': 'Английский', 'en': 'English'},
        'name_project_calltaxi': {'ru': 'Коллтакси', 'en': 'Calltaxi'},
    },
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {},
        'calltaxi': {'main_permission': 'user_calltaxi'},
    },
)
async def test_cabinet_filters(web_app_client, headers, expected_answer):
    response = await web_app_client.get(
        '/cabinet/filter_info', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_answer
