import pytest


TRANSLATE = {
    'access_denied': {'ru': 'Ошибка доступа', 'en': 'Access denied'},
    'shop_permissions_conflict': {'ru': 'конфликт', 'en': 'conflict'},
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'url,headers,status,response_content',
    [
        (
            '/shop/goods/list',
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'X-Yandex-Login is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            '/shop/goods/list',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            403,
            {'code': 'shop_permissions_conflict', 'message': 'конфликт'},
        ),
        (
            '/shop/goods/list',
            {'X-Yandex-Login': 'testlogin', 'Accept-Language': 'en-en'},
            403,
            {'code': 'access_denied', 'message': 'Access denied'},
        ),
        (
            '/shop/goods/list',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            [
                {
                    'id': 1,
                    'name': 'test_name',
                    'type': 'test_type',
                    'permission': 'read_shop_test_taxi',
                    'description': 'test_description',
                    'image_mds_id': 'test_image',
                    'amount': 7,
                    'assortment': [
                        {
                            'id': 1,
                            'goods_id': 1,
                            'price': 222.33,
                            'attribute': 'test_attr',
                            'amount': 2,
                        },
                        {
                            'id': 3,
                            'goods_id': 1,
                            'price': 4444.55,
                            'attribute': 'test_attr3',
                            'amount': 5,
                        },
                    ],
                },
            ],
        ),
        (
            '/shop/goods/list',
            {'X-Yandex-Login': 'test3', 'Accept-Language': 'ru-ru'},
            200,
            [
                {
                    'id': 2,
                    'name': '2test_name',
                    'type': '2test_type',
                    'permission': 'read_shop_test_eda',
                    'description': '2test_description',
                    'image_mds_id': '2test_image',
                    'amount': 12,
                    'assortment': [
                        {
                            'id': 4,
                            'goods_id': 2,
                            'price': 111.33,
                            'attribute': '2test_attr',
                            'amount': 7,
                        },
                        {
                            'id': 5,
                            'goods_id': 2,
                            'price': 311.22,
                            'attribute': '2test_attr2',
                            'amount': 4,
                        },
                        {
                            'id': 6,
                            'goods_id': 2,
                            'price': 4111.55,
                            'attribute': '2test_attr3',
                            'amount': 1,
                        },
                    ],
                },
                {
                    'id': 6,
                    'name': '6test_name',
                    'type': '6test_type',
                    'permission': 'read_shop_test_eda',
                    'description': '6test_description',
                    'image_mds_id': '6test_image',
                    'amount': 8,
                    'assortment': [
                        {
                            'id': 13,
                            'goods_id': 6,
                            'price': 555.33,
                            'attribute': '4test_attr',
                            'amount': 7,
                        },
                        {
                            'id': 15,
                            'goods_id': 6,
                            'price': 422.55,
                            'attribute': '4test_attr3',
                            'amount': 1,
                        },
                    ],
                },
            ],
        ),
        (
            '/shop/goods',
            {'X-Yandex-Login': 'test3', 'Accept-Language': 'ru-ru'},
            200,
            {
                'categories': [
                    {'id': 'category_1', 'image': 'image', 'name': 'Test'},
                ],
                'goods': [
                    {
                        'id': 2,
                        'name': '2test_name',
                        'type': '2test_type',
                        'permission': 'read_shop_test_eda',
                        'description': '2test_description',
                        'image_mds_id': '2test_image',
                        'amount': 12,
                        'assortment': [
                            {
                                'id': 4,
                                'goods_id': 2,
                                'price': 111.33,
                                'attribute': '2test_attr',
                                'amount': 7,
                            },
                            {
                                'id': 5,
                                'goods_id': 2,
                                'price': 311.22,
                                'attribute': '2test_attr2',
                                'amount': 4,
                            },
                            {
                                'id': 6,
                                'goods_id': 2,
                                'price': 4111.55,
                                'attribute': '2test_attr3',
                                'amount': 1,
                            },
                        ],
                    },
                    {
                        'id': 6,
                        'name': '6test_name',
                        'type': '6test_type',
                        'permission': 'read_shop_test_eda',
                        'description': '6test_description',
                        'image_mds_id': '6test_image',
                        'amount': 8,
                        'assortment': [
                            {
                                'id': 13,
                                'goods_id': 6,
                                'price': 555.33,
                                'attribute': '4test_attr',
                                'amount': 7,
                            },
                            {
                                'id': 15,
                                'goods_id': 6,
                                'price': 422.55,
                                'attribute': '4test_attr3',
                                'amount': 1,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            '/shop/goods?category=noexist',
            {'X-Yandex-Login': 'test3', 'Accept-Language': 'ru-ru'},
            200,
            {
                'categories': [
                    {'id': 'category_1', 'image': 'image', 'name': 'Test'},
                ],
                'goods': [],
            },
        ),
        (
            '/shop/goods/list?category=category_1',
            {'X-Yandex-Login': 'test3', 'Accept-Language': 'ru-ru'},
            200,
            [
                {
                    'id': 2,
                    'name': '2test_name',
                    'type': '2test_type',
                    'permission': 'read_shop_test_eda',
                    'description': '2test_description',
                    'image_mds_id': '2test_image',
                    'amount': 12,
                    'assortment': [
                        {
                            'id': 4,
                            'goods_id': 2,
                            'price': 111.33,
                            'attribute': '2test_attr',
                            'amount': 7,
                        },
                        {
                            'id': 5,
                            'goods_id': 2,
                            'price': 311.22,
                            'attribute': '2test_attr2',
                            'amount': 4,
                        },
                        {
                            'id': 6,
                            'goods_id': 2,
                            'price': 4111.55,
                            'attribute': '2test_attr3',
                            'amount': 1,
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_get_list_goods(
        web_app_client, url, headers, status, response_content,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == status
    content = await response.json()
    assert content == response_content
