import pytest


@pytest.mark.parametrize(
    'headers,expected_data',
    [
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            [
                {'id': 'aaa', 'name': 'Тест', 'image': 'image'},
                {'id': 'bbb', 'name': 'Тест', 'image': 'image'},
                {'id': 'ccc', 'name': 'Тест', 'image': 'image'},
            ],
        ),
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-en'},
            [
                {'id': 'aaa', 'name': 'Test', 'image': 'image'},
                {'id': 'bbb', 'name': 'Test', 'image': 'image'},
                {'id': 'ccc', 'name': 'Test', 'image': 'image'},
            ],
        ),
    ],
)
async def test_categories_list(web_app_client, headers, expected_data):
    response = await web_app_client.get('/shop/category/list', headers=headers)
    assert response.status == 200
    content = await response.json()
    assert content == expected_data
