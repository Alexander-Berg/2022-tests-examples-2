import pytest

from agent import const


TRANSLATE = {
    'not_admin_for': {
        'ru': 'Нет админских прав для: {action}',
        'en': 'Not admin for: {action}',
    },
    const.PURCHASE_INIT_STATUS_KEY: {
        'ru': 'Покупка инициализирована',
        'en': 'Purchase initialized',
    },
    const.PURCHASE_SUCCESSFULL_STATUS_KEY: {'ru': 'Успех', 'en': 'Success'},
    const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY: {
        'ru': 'Недостаточно товара',
        'en': 'Not enough product',
    },
}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'url, headers, status, response_content',
    [
        (
            '/shop/admin-purchase-history?page=1&limit=10',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'ok': True,
                'results': [
                    {
                        'purchase_id': '1111',
                        'status_key': const.PURCHASE_INIT_STATUS_KEY,
                        'status_locale': 'Покупка инициализирована',
                        'created': '2021-01-01T03:00:04Z',
                        'updated': '2021-01-01T03:00:04Z',
                        'login': 'mikh-vasily',
                        'image_mds_id': 'test_image',
                        'attribute': 'test_attr',
                        'price': 222.33,
                        'name': 'test_name',
                        'type': 'test_type',
                        'delivery_address': {
                            'id': 1,
                            'type': const.USER_ADDRESS_TYPE,
                            'created': '2021-01-01T03:00:00Z',
                            'updated': '2021-01-01T03:00:00Z',
                            'postcode': '222333',
                            'country': 'ru',
                            'city': 'Москва',
                            'street': 'Кривая',
                            'house': '1',
                            'login': 'mikh-vasily',
                        },
                    },
                    {
                        'purchase_id': '2222',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:03Z',
                        'updated': '2021-01-01T03:00:03Z',
                        'billing_doc_id': 'test_doc',
                        'billing_operations_history_id': '2222',
                        'login': 'mikh-vasily',
                        'image_mds_id': 'test_image',
                        'attribute': 'test_attr',
                        'price': 222.33,
                        'name': 'test_name',
                        'type': 'test_type',
                        'delivery_address': {
                            'id': 2,
                            'type': const.USER_ADDRESS_TYPE,
                            'created': '2021-01-01T03:00:00Z',
                            'updated': '2021-01-01T03:00:00Z',
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
                        'purchase_id': '3333',
                        'status_key': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                        'status_locale': 'Недостаточно товара',
                        'created': '2021-01-01T03:00:02Z',
                        'updated': '2021-01-01T03:00:02Z',
                        'login': 'webalex',
                        'image_mds_id': 'test_image',
                        'attribute': 'test_attr',
                        'price': 222.33,
                        'name': 'test_name',
                        'type': 'test_type',
                    },
                    {
                        'purchase_id': '4444',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:01Z',
                        'updated': '2021-01-01T03:00:01Z',
                        'billing_doc_id': 'test_doc4',
                        'billing_operations_history_id': '4444',
                        'login': 'webalex',
                        'attribute': 'test_attr1',
                        'image_mds_id': 'test_image',
                        'price': 333.33,
                        'name': 'test_promo',
                        'promocode': 'test_hash',
                        'type': 'promocode',
                    },
                ],
                'pagination': {'total': 4, 'page': 1, 'limit': 10},
            },
        ),
        (
            '/shop/admin-purchase-history?page=2&limit=2',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'ok': True,
                'results': [
                    {
                        'purchase_id': '3333',
                        'status_key': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                        'status_locale': 'Недостаточно товара',
                        'created': '2021-01-01T03:00:02Z',
                        'updated': '2021-01-01T03:00:02Z',
                        'image_mds_id': 'test_image',
                        'login': 'webalex',
                        'attribute': 'test_attr',
                        'price': 222.33,
                        'name': 'test_name',
                        'type': 'test_type',
                    },
                    {
                        'purchase_id': '4444',
                        'status_key': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                        'status_locale': 'Успех',
                        'created': '2021-01-01T03:00:01Z',
                        'updated': '2021-01-01T03:00:01Z',
                        'billing_doc_id': 'test_doc4',
                        'image_mds_id': 'test_image',
                        'billing_operations_history_id': '4444',
                        'login': 'webalex',
                        'attribute': 'test_attr1',
                        'price': 333.33,
                        'name': 'test_promo',
                        'promocode': 'test_hash',
                        'type': 'promocode',
                    },
                ],
                'pagination': {'total': 2, 'page': 2, 'limit': 2},
            },
        ),
        (
            '/shop/admin-purchase-history?page=2&limit=10',
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-ru'},
            200,
            {
                'ok': True,
                'results': [],
                'pagination': {'total': 0, 'page': 2, 'limit': 10},
            },
        ),
        (
            '/shop/admin-purchase-history?page=1&limit=10',
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'X-Yandex-Login is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            '/shop/admin-purchase-history',
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            200,
            {
                'ok': False,
                'results': [],
                'pagination': {
                    'total': 0,
                    'page': const.PURCHASE_HISTORY_DEFAULT_PAGE,
                    'limit': const.PURCHASE_HISTORY_DEFAULT_LIMIT,
                },
                'message': 'Нет админских прав для: view admin purchases',
            },
        ),
    ],
)
async def test_admin_purchase_history(
        web_context, web_app_client, url, headers, status, response_content,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == status
    assert await response.json() == response_content
