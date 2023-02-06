import pytest

from tests_grocery_eats_gateway import headers


ORDER_ID = 'order_id'
SHORT_ORDER_ID = 'short_order_id'
ORDER_ADDRESS = 'some street, 10'


def _get_grocery_order_with_item():
    order_with_item = {
        'order_id': ORDER_ID,
        'short_order_id': SHORT_ORDER_ID,
        'yandex_uid': 'yandex_uid',
        'created_at': '2020-12-31T21:00:00.778583+00:00',
        'status': 'closed',
        'closed_at': '2020-12-31T22:00:00.778583+00:00',
        'calculation': {
            'items': [
                {
                    'name': 'kakao',
                    'cost': '200.00',
                    'product_id': 'product_1',
                    'gross_weight': '10',
                },
            ],
            'final_cost': '123',
            'discount': '0',
            'refund': '0',
            'currency_code': 'RUB',
        },
        'contact': {},
        'legal_entities': [],
        'destinations': [{'point': [0, 0], 'short_text': ORDER_ADDRESS}],
        'receipts': [{'title': 'receipt_title', 'receipt_url': 'receipt_url'}],
        'depot_id': '70134',
    }

    return order_with_item


async def test_orders_basic(
        taxi_grocery_eats_gateway,
        grocery_order_log,
        overlord_catalog,
        load_json,
):
    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.get(
        '/internal/v1/order_info?order_id=order_id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_test_basic_response.json')


async def test_overlord_catalog_not_found_product(
        taxi_grocery_eats_gateway,
        load_json,
        grocery_order_log,
        overlord_catalog,
        mockserver,
):
    grocery_order_log.mock_retrieve(**_get_grocery_order_with_item())

    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.get(
        '/internal/v1/order_info?order_id=order_id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_images_fail_response.json')


async def test_order_with_image(
        taxi_grocery_eats_gateway,
        grocery_order_log,
        load_json,
        overlord_catalog,
):

    overlord_catalog.add_product_data(
        product_id='product_1',
        title='Product 1',
        image_url_template='url/image_1.jpg',
    )

    grocery_order_log.mock_retrieve(**_get_grocery_order_with_item())

    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.get(
        '/internal/v1/order_info?order_id=order_id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_images_response.json')
