import pytest

JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
USER1_HEADERS = {'X-Yandex-Login': 'user1', 'Accept-Language': 'ru-RU'}
USER2_HEADERS = {'X-Yandex-Login': 'user2', 'Accept-Language': 'en-EN'}


RU_EXPECTED_DATA = {
    'can_thank_up_to': 3,
    'thank_themes': [
        {'id': 'sociable_id', 'name': 'Коммуникабельный'},
        {'id': 'fast_response_id', 'name': 'Быстрый ответ'},
    ],
}


EN_EXPECTED_DATA = {
    'can_thank_up_to': 3,
    'thank_themes': [
        {'id': 'sociable_id', 'name': 'Sociable'},
        {'id': 'fast_response_id', 'name': 'Fast Response'},
    ],
}


@pytest.mark.now('2022-06-03T22:01:00+0000')
@pytest.mark.translations(
    agent={
        'sociable_tanker_key': {'ru': 'Коммуникабельный', 'en': 'Sociable'},
        'fast_response_tanker_key': {
            'ru': 'Быстрый ответ',
            'en': 'Fast Response',
        },
    },
)
@pytest.mark.config(
    AGENT_THANK_THEMES={
        'sociable_id': {'tanker_key': 'sociable_tanker_key'},
        'fast_response_id': {'tanker_key': 'fast_response_tanker_key'},
    },
)
@pytest.mark.parametrize(
    'headers,status_code,response_content',
    [
        (JUSTMARK0_HEADERS, 200, {'can_thank_up_to': 0}),
        (USER1_HEADERS, 200, RU_EXPECTED_DATA),
        (USER2_HEADERS, 200, EN_EXPECTED_DATA),
    ],
)
async def test_is_thank_available(
        web_app_client, headers, status_code, response_content,
):
    response = await web_app_client.get('/thank_available', headers=headers)
    assert response.status == status_code
    content = await response.json()
    assert content == response_content
