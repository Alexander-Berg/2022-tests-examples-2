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
    'Accept-Language': 'en-en',
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content',
    [
        ([1, 2, 4, 5], GOOD_HEADERS, 200, [1, 2, 4, 5]),
        ([6], GOOD_HEADERS, 200, [6]),
        (
            [],
            GOOD_HEADERS,
            400,
            {'code': 'body_is_none', 'message': 'Отсутствует тело запроса'},
        ),
        (
            [1, 2],
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'X-Yandex-Login is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            [1, 2],
            NO_ADMIN_HEADERS,
            403,
            {
                'code': 'not_admin_for',
                'message': 'Not admin for: delete subproducts in shop',
            },
        ),
        (
            [7, 8],
            GOOD_HEADERS,
            404,
            {
                'code': 'shop_not_subproducts_in_db',
                'message': 'Подтоваров id: 7, id: 8 нет в базе',
            },
        ),
    ],
)
async def test_delete_subproducts(
        web_context,
        web_app_client,
        input_data,
        headers,
        status,
        response_content,
):
    response = await web_app_client.post(
        '/shop/goods/delete-subproducts', headers=headers, json=input_data,
    )
    assert response.status == status
    assert await response.json() == response_content

    if response.status < 400:
        query_ids_str = ', '.join([str(i) for i in input_data])
        async with web_context.pg.slave_pool.acquire() as conn:
            subproducts_query = (
                'SELECT * FROM agent.goods_detail '
                'WHERE agent.goods_detail.id in ({})'
                'ORDER BY id'.format(query_ids_str)
            )
            subproducts_result = await conn.fetch(subproducts_query)
            assert subproducts_result == []
