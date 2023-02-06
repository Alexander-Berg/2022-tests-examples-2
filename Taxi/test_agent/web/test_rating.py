import pytest

from agent import const

RU_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
BODY = {'login': 'webalex'}


PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'calltaxi': {
        'enable_chatterbox': False,
        'wfm_effrat_domain': 'mediaservices',
        'piecework_tariff': 'call-taxi-unified',
        'main_permission': 'user_calltaxi',
    },
}

EXPECTED_RESPONSE = {
    'items': [
        {
            'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'webalex',
            'first_name': 'Александр',
            'last_name': 'Иванов',
            'login': 'webalex',
            'place': 1,
            'ratio': 50.0,
            'score': 97.5,
        },
        {
            'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'liambaev',
            'first_name': 'Лиам',
            'last_name': 'Баев',
            'login': 'liambaev',
            'place': 2,
            'ratio': 50.0,
            'score': 90.0,
        },
        {
            'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'piskarev',
            'first_name': 'Александр',
            'last_name': 'Пискарёв',
            'login': 'piskarev',
            'place': 3,
            'ratio': 20.0,
            'score': 81.0,
        },
        {
            'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'akozhevina',
            'first_name': 'Анна',
            'last_name': 'Кожевина',
            'login': 'akozhevina',
            'place': 4,
            'ratio': 20.0,
            'score': 71.0,
        },
        {
            'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'simon',
            'first_name': 'Семён',
            'last_name': 'Семёныч',
            'login': 'simon',
            'place': 5,
            'ratio': 0.0,
            'score': 5.0,
        },
    ],
}


async def test_rating_mock_fail(web_app_client):
    response = await web_app_client.post(
        '/piecework/rating', headers=RU_HEADERS, json=BODY,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'items': []}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_rating_mock_ok(web_app_client, mock_piecework_rating):
    response = await web_app_client.post(
        '/piecework/rating', headers=RU_HEADERS, json=BODY,
    )
    assert response.status == 200
    content = await response.json()

    assert len(content['items']) == 5
    assert sorted(
        EXPECTED_RESPONSE['items'], key=lambda i: i['place'],
    ) == sorted(content['items'], key=lambda i: i['place'])
