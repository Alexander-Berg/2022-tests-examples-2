import pytest

from agent import const


TRANSLATE = {
    const.PURCHASE_SUCCESSFULL_STATUS_KEY: {'ru': 'Успех', 'en': 'Success'},
    const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY: {
        'ru': 'Недостаточно товара',
        'en': 'Not enough product',
    },
    const.PURCHASE_BILLING_ERROR_KEY: {
        'ru': 'Ошибка биллинга',
        'en': 'Billing error',
    },
    const.PURCHASE_NOT_ENOUGH_COINS_KEY: {
        'ru': 'Нет денег',
        'en': 'Not money',
    },
    'test_attr': {'ru': 'Тест', 'en': 'Test'},
    'test_name': {'ru': 'Тест имя', 'en': 'Test name'},
    'test_attr1': {'ru': 'Тест1', 'en': 'Test1'},
    'test_promo': {'ru': 'Тест промо', 'en': 'Test promo'},
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'url, headers, status, response_content',
    [
        (
            '/shop/purchase-history?page=1&limit=10',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'results': [
                    {
                        'purchase_id': '2222',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:04Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'price': 222.33,
                        'name': 'test_name',
                        'image_mds_id': 'test_image',
                        'delivery_address': {
                            'postcode': '222333',
                            'country': 'ru',
                            'city': 'Москва',
                            'street': 'Кривая',
                            'house': '1',
                            'building': 'test_build',
                            'flat': 'test_flat',
                        },
                    },
                    {
                        'purchase_id': '5555',
                        'status_key': const.PURCHASE_BILLING_ERROR_KEY,
                        'status_locale': 'Ошибка биллинга',
                        'created': '2021-01-01T03:00:01Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'image_mds_id': 'test_image',
                        'price': 222.33,
                        'name': 'test_name',
                    },
                    {
                        'purchase_id': '7777',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:01Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'image_mds_id': 'test_image',
                        'price': 222.33,
                        'name': 'test_name',
                    },
                ],
                'pagination': {'total': 3, 'page': 1, 'limit': 10},
            },
        ),
        (
            '/shop/purchase-history?page=2&limit=2',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'results': [
                    {
                        'purchase_id': '7777',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:01Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'image_mds_id': 'test_image',
                        'price': 222.33,
                        'name': 'test_name',
                    },
                ],
                'pagination': {'total': 1, 'page': 2, 'limit': 2},
            },
        ),
        (
            '/shop/purchase-history?page=2&limit=10',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'results': [],
                'pagination': {'total': 0, 'page': 2, 'limit': 10},
            },
        ),
        (
            '/shop/purchase-history?page=1&limit=10',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-en'},
            200,
            {
                'results': [
                    {
                        'purchase_id': '3333',
                        'status_key': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                        'status_locale': 'Not enough product',
                        'created': '2021-01-01T03:00:03Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'image_mds_id': 'test_image',
                        'price': 222.33,
                        'name': 'test_name',
                    },
                    {
                        'purchase_id': '4444',
                        'status_key': const.PURCHASE_NOT_ENOUGH_COINS_KEY,
                        'status_locale': 'Not money',
                        'created': '2021-01-01T03:00:02Z',
                        'attribute': 'test_attr1',
                        'type': 'promocode',
                        'image_mds_id': 'test_image',
                        'price': 333.33,
                        'name': 'test_promo',
                        'promocode': 'test_hash',
                    },
                ],
                'pagination': {'total': 2, 'page': 1, 'limit': 10},
            },
        ),
        (
            '/shop/purchase-history?page=1&limit=10&purchase_id=3333',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-en'},
            200,
            {
                'results': [
                    {
                        'purchase_id': '3333',
                        'status_key': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                        'status_locale': 'Not enough product',
                        'created': '2021-01-01T03:00:03Z',
                        'attribute': 'test_attr',
                        'type': 'test_type',
                        'image_mds_id': 'test_image',
                        'price': 222.33,
                        'name': 'test_name',
                    },
                ],
                'pagination': {'total': 1, 'page': 1, 'limit': 10},
            },
        ),
        (
            '/shop/purchase-history',
            {'X-Yandex-Login': 'test', 'Accept-Language': 'ru-ru'},
            200,
            {
                'results': [],
                'pagination': {
                    'total': 0,
                    'page': const.PURCHASE_HISTORY_DEFAULT_PAGE,
                    'limit': const.PURCHASE_HISTORY_DEFAULT_LIMIT,
                },
            },
        ),
        (
            '/shop/purchase-history',
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'X-Yandex-Login is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
async def test_purchase_history(
        web_context, web_app_client, url, headers, status, response_content,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == status
    assert await response.json() == response_content
