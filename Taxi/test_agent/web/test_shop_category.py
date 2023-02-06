import pytest


@pytest.mark.parametrize(
    'headers,body,status,expected',
    [
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            {
                'id': 'id_1',
                'ru_name': 'Первая',
                'en_name': 'First',
                'image_link': 'image_1',
                'position': 1,
            },
            403,
            {},
        ),
        (
            {'X-Yandex-Login': 'admin', 'Accept-Language': 'ru-ru'},
            {
                'id': 'id_2',
                'ru_name': 'Вторая',
                'en_name': 'Second',
                'image_link': 'image_2',
                'position': 2,
            },
            200,
            {'id': 'id_2', 'name': 'Вторая', 'image': 'image_2'},
        ),
        (
            {'X-Yandex-Login': 'admin', 'Accept-Language': 'en-en'},
            {
                'id': 'id_2',
                'ru_name': 'Вторая',
                'en_name': 'Second',
                'image_link': 'image_2',
                'position': 2,
            },
            200,
            {'id': 'id_2', 'name': 'Second', 'image': 'image_2'},
        ),
        (
            {'X-Yandex-Login': 'admin', 'Accept-Language': 'ru-ru'},
            {
                'id': '12345',
                'ru_name': 'tedst',
                'en_name': 'test',
                'image_link': 'test',
                'position': 1,
            },
            200,
            {'id': '12345', 'name': 'Категория', 'image': 'img_link'},
        ),
    ],
)
async def test_create_shop_category(
        web_app_client, headers, body, status, expected,
):
    response = await web_app_client.post(
        '/shop/category', headers=headers, json=body,
    )
    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content == expected
