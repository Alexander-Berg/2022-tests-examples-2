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
    'shop_not_products_in_db': {
        'ru': 'Товар отсутствует',
        'en': 'Goods not exist',
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


@pytest.mark.now('2021-01-01T00:00:00+0')
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content,expected_category',
    [
        (
            {
                'id': 1,
                'ru_name': 'test',
                'en_name': 'test',
                'type': 'type_test',
                'permission': 'read_shop_test_eda',
                'ru_description': 'desc_test',
                'en_description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
                'categories': ['test1', 'test2'],
            },
            GOOD_HEADERS,
            200,
            {
                'id': 1,
                'name': 'test',
                'type': 'type_test',
                'created': '2021-01-01T00:00:00Z',
                'updated': '2021-01-01T00:00:00Z',
                'creator': 'mikh-vasily',
                'permission': 'read_shop_test_eda',
                'description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
            },
            ['test1', 'test2'],
        ),
        (
            {
                'id': 1,
                'ru_name': 'test',
                'en_name': 'test',
                'type': 'type_test',
                'permission': 'read_shop_test_eda',
                'ru_description': 'desc_test',
                'en_description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
                'categories': [],
            },
            GOOD_HEADERS,
            200,
            {
                'id': 1,
                'name': 'test',
                'type': 'type_test',
                'created': '2021-01-01T00:00:00Z',
                'updated': '2021-01-01T00:00:00Z',
                'creator': 'mikh-vasily',
                'permission': 'read_shop_test_eda',
                'description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
            },
            [],
        ),
        (
            {
                'id': 1,
                'ru_name': 'test',
                'en_name': 'test',
                'type': 'type_test',
                'permission': 'read_shop_test_eda',
                'ru_description': 'desc_test',
                'en_description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
                'categories': ['test1', 'test2'],
            },
            NO_ADMIN_HEADERS,
            403,
            {
                'code': 'not_admin_for',
                'message': 'Not admin for: update goods in shop',
            },
            [],
        ),
        (
            {
                'id': 3,
                'ru_name': 'test',
                'en_name': 'test',
                'type': 'type_test',
                'permission': 'read_shop_test_eda',
                'ru_description': 'desc_test',
                'en_description': 'desc_test',
                'image_mds_id': 'img_test',
                'visible': False,
                'categories': ['test1', 'test2'],
            },
            GOOD_HEADERS,
            404,
            {
                'code': 'shop_not_products_in_db',
                'message': 'Товар отсутствует',
            },
            [],
        ),
    ],
)
async def test_update_goods(
        web_context,
        web_app_client,
        input_data,
        headers,
        status,
        response_content,
        expected_category,
):
    response = await web_app_client.post(
        '/shop/goods/update', headers=headers, json=input_data,
    )
    assert response.status == status
    assert await response.json() == response_content

    if response.status < 400:
        async with web_context.pg.slave_pool.acquire() as conn:
            products_query = 'SELECT * FROM agent.goods ORDER BY id'
            products_result = await conn.fetchrow(products_query)
            assert input_data['type'] == products_result['type']
            assert input_data['permission'] == products_result['permission']

            assert (
                input_data['image_mds_id'] == products_result['image_mds_id']
            )
            assert input_data['visible'] == products_result['visible']

            assert input_data['ru_name'] == products_result['ru_name']
            assert input_data['en_name'] == products_result['en_name']

            assert (
                input_data['ru_description']
                == products_result['ru_description']
            )
            assert (
                input_data['en_description']
                == products_result['en_description']
            )
        async with web_context.pg.slave_pool.acquire() as conn:
            categories_query = """SELECT * FROM agent.shop_categories_goods
             ORDER BY category_id"""
            assert [
                row['category_id']
                for row in await conn.fetch(categories_query)
            ] == expected_category
