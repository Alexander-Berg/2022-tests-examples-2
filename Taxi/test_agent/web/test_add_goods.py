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
    'not_permissions_in_db': {
        'ru': 'Пермишены: {permissions_list}, отсутствуют',
        'en': 'Permissions: {permissions_list} are missing',
    },
}

GOOD_HEADERS: dict = {
    'X-Yandex-Login': 'mikh-vasily',
    'Accept-Language': 'ru-ru',
}
NO_ADMIN_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'en-en',
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content,expected_category',
    [
        (
            {
                'ru_name': 'Товар 1',
                'en_name': 'Tovar 1',
                'type': 'test_type',
                'permission': 'read_shop_test_taxi',
                'ru_description': 'Описание',
                'en_description': 'Description',
                'image_mds_id': 'test_img',
                'visible': True,
                'categories': ['test1', 'test2'],
            },
            GOOD_HEADERS,
            201,
            {
                'id': 1,
                'name': 'Товар 1',
                'type': 'test_type',
                'permission': 'read_shop_test_taxi',
                'description': 'Описание',
                'image_mds_id': 'test_img',
                'amount': 0,
                'assortment': [],
            },
            ['test1', 'test2'],
        ),
        (
            {
                'ru_name': 'test',
                'en_name': 'test',
                'type': 'test_type',
                'permission': 'read_shop_test_taxi',
                'ru_description': 'test_desc',
                'en_description': 'test_desc',
                'image_mds_id': 'test_img',
                'visible': True,
                'categories': ['test1', 'test2'],
            },
            NO_ADMIN_HEADERS,
            403,
            {
                'code': 'not_admin_for',
                'message': 'Not admin for: add goods to shop',
            },
            [],
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
        expected_category,
):
    response = await web_app_client.post(
        '/shop/goods/add', headers=headers, json=input_data,
    )
    assert response.status == status
    assert await response.json() == response_content

    if status == 201:
        async with web_context.pg.slave_pool.acquire() as conn:
            products_query = 'SELECT * FROM agent.goods'
            products_result = await conn.fetch(products_query)

            assert len(products_result) == 1

            product = products_result[0]

            assert product['id'] == 1
            assert product['type'] == input_data['type']
            assert product['creator'] == headers['X-Yandex-Login']
            assert product['permission'] == input_data['permission']
            assert product['image_mds_id'] == input_data['image_mds_id']
            assert product['visible'] == input_data['visible']

            assert product['en_name'] == input_data['en_name']
            assert product['ru_name'] == input_data['ru_name']

            assert product['ru_description'] == input_data['ru_description']
            assert product['en_description'] == input_data['en_description']

    async with web_context.pg.slave_pool.acquire() as conn:
        categories_query = (
            'SELECT * FROM agent.shop_categories_goods ORDER BY category_id'
        )
        assert [
            row['category_id'] for row in await conn.fetch(categories_query)
        ] == expected_category
