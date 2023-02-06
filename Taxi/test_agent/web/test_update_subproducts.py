import pytest

TRANSLATE = {
    'body_is_none': {
        'ru': 'Отсутствует тело запроса',
        'en': 'Missing request body',
    },
    'not_admin_for': {
        'ru': 'Нет админских прав для: {action}',
        'en': 'Not admin for: {action}',
    },
    'shop_not_products_in_db': {
        'ru': 'Товаров {products} нет в базе',
        'en': 'Goods {products} not in db',
    },
    'shop_not_subproducts_in_db': {
        'ru': 'Подтоваров {subproducts} нет в базе',
        'en': 'Subproducts {subproducts} not in db',
    },
}


GOOD_HEADERS: dict = {
    'X-Yandex-Login': 'mikh-vasily',
    'Accept-Language': 'ru-ru',
}
NO_ADMIN_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'ru-ru',
}


@pytest.mark.now('2021-01-01T00:00:00+0')
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content',
    [
        (
            {
                'id': 1,
                'goods_id': 1,
                'price': 11.22,
                'ru_attribute': 'test_attr',
                'en_attribute': 'test_attr',
                'amount': 5,
                'visible': True,
            },
            GOOD_HEADERS,
            200,
            {
                'id': 1,
                'goods_id': 1,
                'created': '2021-01-01T00:00:00Z',
                'updated': '2021-01-01T00:00:00Z',
                'creator': 'mikh-vasily',
                'price': 11.22,
                'attribute': 'test_attr',
                'amount': 5,
                'visible': True,
            },
        ),
        (
            {
                'id': 1,
                'goods_id': 1,
                'price': 11.22,
                'ru_attribute': 'test_attr',
                'en_attribute': 'test_attr',
                'amount': 5,
                'visible': True,
            },
            NO_ADMIN_HEADERS,
            403,
            {
                'code': 'not_admin_for',
                'message': (
                    'Нет админских прав для: update subproducts in shop'
                ),
            },
        ),
    ],
)
async def test_goods_add(
        web_context,
        web_app_client,
        input_data,
        headers,
        status,
        response_content,
):
    response = await web_app_client.post(
        '/shop/goods/update-subproducts', headers=headers, json=input_data,
    )
    assert response.status == status
    assert await response.json() == response_content
