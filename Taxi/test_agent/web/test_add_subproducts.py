import pytest

TRANSLATE = {
    'shop_not_products_in_db': {
        'ru': 'Товаров {products} нет в базе',
        'en': 'Goods {products} not in db',
    },
    'body_is_none': {
        'ru': 'Отсутствует тело запроса',
        'en': 'Missing request body',
    },
    'not_admin_for': {
        'ru': 'Нет админских прав для: {action}',
        'en': 'Not admin for: {action}',
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


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status,response_content',
    [
        (
            {
                'goods_id': 1,
                'price': 11,
                'ru_attribute': 'Название атрибута',
                'en_attribute': 'Name attribute',
                'amount': 5,
                'visible': True,
            },
            GOOD_HEADERS,
            201,
            {
                'id': 1,
                'goods_id': 1,
                'creator': 'mikh-vasily',
                'price': 11,
                'ru_attribute': 'Название атрибута',
                'en_attribute': 'Name attribute',
                'amount': 5,
                'visible': True,
            },
        ),
        (
            {
                'goods_id': 1,
                'price': 11,
                'ru_attribute': 'Название атрибута',
                'en_attribute': 'Name attribute',
                'amount': 5,
                'visible': True,
            },
            NO_ADMIN_HEADERS,
            403,
            {
                'code': 'not_admin_for',
                'message': 'Нет админских прав для: add subproducts to shop',
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
        '/shop/goods/add-subproducts', headers=headers, json=input_data,
    )
    assert response.status == status
    if response.status == 201:
        content = await response.json()
        response_content['created'] = content['created']
        response_content['updated'] = content['updated']

        assert await response.json() == response_content
