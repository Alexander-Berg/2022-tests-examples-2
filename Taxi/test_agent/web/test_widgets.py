import pytest

RU_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
EN_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-us'}

BODY = {'login': 'webalex'}
BODY_UNKOWN_LOGIN = {'login': '_unknown_login_'}


EXPECTED_DATA_RU = [
    {'key': 'widget_csat', 'name': 'КСАТ'},
    {'key': 'widget_quality', 'name': 'Качество'},
    {'key': 'widget_tph', 'name': 'widget_tph'},
]

EXPECTED_DATA_EN = [
    {'key': 'widget_csat', 'name': 'CSAT'},
    {'key': 'widget_quality', 'name': 'Quality'},
    {'key': 'widget_tph', 'name': 'widget_tph'},
]


@pytest.mark.translations(
    agent={
        'widget_quality': {'ru': 'Качество', 'en': 'Quality'},
        'widget_csat': {'ru': 'КСАТ', 'en': 'CSAT'},
    },
)
@pytest.mark.parametrize(
    'body,headers,status_code,expected_data',
    [
        (BODY, RU_HEADERS, 200, {'widgets': EXPECTED_DATA_RU}),
        (BODY, EN_HEADERS, 200, {'widgets': EXPECTED_DATA_EN}),
        (BODY_UNKOWN_LOGIN, RU_HEADERS, 200, {'widgets': []}),
    ],
)
async def test_widgets(
        web_app_client, body, headers, status_code, expected_data,
):
    response = await web_app_client.post(
        '/widgets', headers=headers, json=body,
    )
    assert response.status == status_code
    content = await response.json()
    assert content == expected_data
