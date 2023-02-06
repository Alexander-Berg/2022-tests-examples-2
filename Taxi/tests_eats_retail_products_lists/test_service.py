# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_retail_products_lists_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.

BASE_REQUEST_PUBLIC = {
    'brand_slug': 'SLUG',
    'list_name': 'list_name',
    'item_ids': [
        {
            'product_core_id': '119106579',
            'product_public_id': 'dd441306-1d99-4c86-b7e7-fae66eb9eacd',
        },
    ],
}

HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'X-Eats-User': 'user_id=456',
    'X-Idempotency-Token': 'dd441306-1d99-4c86-b7e7-fae66eb9eacd',
}


async def test_menu_products_list_ok(taxi_eats_retail_products_lists):
    resp = await taxi_eats_retail_products_lists.post(
        '/api/v1/products-list/create',
        json=BASE_REQUEST_PUBLIC,
        headers=HEADERS,
    )
    assert resp.status_code == 200


async def test_menu_products_list_error(taxi_eats_retail_products_lists):
    BASE_REQUEST_PUBLIC['brand_slug'] = ' '
    resp = await taxi_eats_retail_products_lists.post(
        '/api/v1/products-list/create',
        json=BASE_REQUEST_PUBLIC,
        headers=HEADERS,
    )
    assert resp.status_code == 400
