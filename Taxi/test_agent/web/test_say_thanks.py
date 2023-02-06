import pytest


USER1_HEADERS = {'X-Yandex-Login': 'user1', 'Accept-Language': 'ru-RU'}
USER2_HEADERS = {'X-Yandex-Login': 'user2', 'Accept-Language': 'en-EN'}
USER3_HEADERS = {'X-Yandex-Login': 'user3', 'Accept-Language': 'en-EN'}
REQUEST_DATA_TOO_MANY_TO_THANK = {
    'say_thanks': [
        {
            'login': 'user1',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
        {
            'login': 'user2',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
        {
            'login': 'user3',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
        {
            'login': 'user4',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
    ],
}
REQUEST_DATA_TWO_TIMES_TO_ONE_PERSON = {
    'say_thanks': [
        {
            'login': 'user1',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
        {
            'login': 'user1',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
    ],
}
REQUEST_DATA_OK1 = {
    'say_thanks': [
        {'login': 'user3', 'thank_themes': ['sociable_id']},
        {
            'login': 'user2',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
    ],
}
REQUEST_DATA_OK2 = {
    'say_thanks': [
        {'login': 'user1', 'thank_themes': ['sociable_id']},
        {
            'login': 'user2',
            'thank_themes': ['sociable_id', 'fast_response_id'],
        },
    ],
}


@pytest.mark.now('2022-06-03T22:01:00+0000')
@pytest.mark.config(
    AGENT_THANK_THEMES={
        'sociable_id': {'tanker_key': 'sociable_tanker_key'},
        'fast_response_id': {'tanker_key': 'fast_response_tanker_key'},
    },
    AGENT_PROJECT_SETTINGS={'thank': {'main_permission': 'user_thank'}},
)
@pytest.mark.parametrize(
    'headers,status_code, body',
    [
        (USER1_HEADERS, 200, REQUEST_DATA_OK1),
        (USER2_HEADERS, 400, REQUEST_DATA_TOO_MANY_TO_THANK),
        (USER2_HEADERS, 400, REQUEST_DATA_TWO_TIMES_TO_ONE_PERSON),
        (USER3_HEADERS, 400, REQUEST_DATA_OK2),
    ],
)
async def test_say_thanks(web_app_client, headers, status_code, body):
    response = await web_app_client.post(
        '/say_thanks/', headers=headers, json=body,
    )
    assert response.status == status_code
