import pytest

YANDEX_UID_HEADER = 'X-Yandex-UID'
USER_ID_HEADER = 'X-YaTaxi-UserId'
URL = '/4.0/preorder/v1/availability'
LANGUAGE = 'Accept-Language'
TEST_ITEMS = [
    {'icon_image_tag': 'icon1_tag', 'title': 'text1_key'},
    {'icon_image_tag': 'icon2_tag', 'title': 'text2_key'},
]


@pytest.mark.config(PREORDER_INSTRUCTIONS=TEST_ITEMS)
@pytest.mark.translations(
    client_messages={
        'text1_key': {
            'ru': 'text1 translation ru',
            'en': 'text1 translation en',
        },
        'text2_key': {'ru': 'text2 translation ru'},
    },
)
@pytest.mark.parametrize(
    'language, expected_user_info',
    [
        (
            'ru-RU',
            {
                'items': [
                    {
                        'icon_image_tag': 'icon1_tag',
                        'title': 'text1 translation ru',
                    },
                    {
                        'icon_image_tag': 'icon2_tag',
                        'title': 'text2 translation ru',
                    },
                ],
            },
        ),
        ('en-US', None),
    ],
)
async def test_instructions(
        web_app_client, mockserver, language, expected_user_info,
):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/preorder_available',
    )
    async def _patch_umlaas_dispatch(*args, **kwargs):
        return {'allowed_time_info': []}

    response = await web_app_client.post(
        URL,
        headers={
            YANDEX_UID_HEADER: '123',
            USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
            LANGUAGE: language,
        },
        json={
            'route': [(1, 1), (2, 2)],
            'zone_name': 'moscow',
            'classes': ['econom'],
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json.get('user_info', None) == expected_user_info
