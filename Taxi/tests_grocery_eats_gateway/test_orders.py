import copy

import pytest

from tests_grocery_eats_gateway import headers

GROCERY_ORDER_CYCLE_ENABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-eats-gateway/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_basic(
        taxi_grocery_eats_gateway, grocery_order_log, load_json,
):
    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/orders',
        json={'limit': 1},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_test_basic_response.json')


@GROCERY_ORDER_CYCLE_ENABLED
async def test_with_eats_eaters(
        taxi_grocery_eats_gateway, grocery_order_log, load_json, eats_eaters,
):
    eats_user_id = 'eats-user-id'
    headers_data_missing = copy.deepcopy(headers.DEFAULT_HEADERS)
    del headers_data_missing['X-Yandex-UID']
    headers_data_missing['X-YaTaxi-User'] = 'eats_user_id=' + eats_user_id
    eats_eaters.check_request(eats_id=eats_user_id)
    grocery_order_log.set_yandex_uid('yandex_uid')
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/orders',
        json={'limit': 1},
        headers=headers_data_missing,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_test_basic_response.json')


async def test_no_order_cycle(
        taxi_grocery_eats_gateway, grocery_order_log, load_json,
):
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/orders',
        json={'limit': 1},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 0
    assert response.json() == []


async def test_no_eaters_call(
        taxi_grocery_eats_gateway, grocery_order_log, eats_eaters,
):
    headers_data_missing = copy.deepcopy(headers.DEFAULT_HEADERS)
    del headers_data_missing['X-Yandex-UID']
    del headers_data_missing['X-YaTaxi-User']
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/orders',
        json={'limit': 1},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert eats_eaters.times_find_by_id_called() == 0
    assert grocery_order_log.times_retrieve_raw_called() == 0
    assert response.json() == []


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_with_images(
        taxi_grocery_eats_gateway, overlord_catalog, load_json, mockserver,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_orders(request):
        return {'orders': load_json('grocery_order_log.json')}

    overlord_catalog.add_product_data(
        product_id='product_1',
        title='Product 1',
        image_url_template='url/image_1.jpg',
    )

    overlord_catalog.add_product_data(
        product_id='product_2',
        title='Product 2',
        image_url_template='url/image_2.jpg',
    )

    overlord_catalog.add_product_data(
        product_id='product_3',
        title='Product 3',
        image_url_template='url/image_3.jpg',
    )

    overlord_catalog.add_product_data(
        product_id='product_4', title='Product 4',
    )

    overlord_catalog.add_product_data(
        product_id='product_5',
        title='Product 5',
        image_url_template='url/image_5.jpg',
    )

    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/orders',
        json={'limit': 3},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert mock_grocery_orders.times_called == 1
    assert response.json() == load_json(
        'expected_test_with_images_response.json',
    )


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_basic_v2(
        taxi_grocery_eats_gateway, grocery_order_log, load_json,
):
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_id'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_test_basic_response_v2.json')


@GROCERY_ORDER_CYCLE_ENABLED
async def test_with_eats_eaters_v2(
        taxi_grocery_eats_gateway, grocery_order_log, load_json, eats_eaters,
):
    eats_user_id = 'eats-user-id'
    headers_data_missing = copy.deepcopy(headers.DEFAULT_HEADERS)
    del headers_data_missing['X-Yandex-UID']
    headers_data_missing['X-YaTaxi-User'] = 'eats_user_id=' + eats_user_id
    eats_eaters.check_request(eats_id=eats_user_id)
    grocery_order_log.set_yandex_uid('yandex_uid')
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_id'},
        headers=headers_data_missing,
    )
    assert response.status == 200, response
    assert grocery_order_log.times_retrieve_raw_called() == 1
    assert response.json() == load_json('expected_test_basic_response_v2.json')


async def test_no_order_cycle_v2(
        taxi_grocery_eats_gateway, grocery_order_log, load_json,
):
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_id'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 404, response
    assert grocery_order_log.times_retrieve_raw_called() == 0


async def test_no_eaters_call_v2(
        taxi_grocery_eats_gateway, grocery_order_log, eats_eaters, load_json,
):
    headers_data_missing = copy.deepcopy(headers.DEFAULT_HEADERS)
    del headers_data_missing['X-Yandex-UID']
    del headers_data_missing['X-YaTaxi-User']
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_id'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 404, response
    assert eats_eaters.times_find_by_id_called() == 0
    assert grocery_order_log.times_retrieve_raw_called() == 0


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_with_images_v2(
        taxi_grocery_eats_gateway, load_json, mockserver,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_orders(request):
        return {'orders': load_json('grocery_order_log_v2.json')}

    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_1'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert mock_grocery_orders.times_called == 1
    assert response.json() == load_json(
        'expected_test_with_images_response_v2.json',
    )


@GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.config(GROCERY_EATS_GATEWAY_SHOW_PRODUCT_WEIGHT=True)
async def test_orders_with_images_and_weight_v2(
        taxi_grocery_eats_gateway, load_json, mockserver,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_orders(request):
        orders = load_json('grocery_order_log_v2.json')
        for order in orders:
            items = order['calculation']['items']
            items[0]['gross_weight'] = '10'
            items[1]['gross_weight'] = '0'
        return {'orders': orders}

    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/order',
        json={'order_nr': 'order_1'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert mock_grocery_orders.times_called == 1
    assert response.json() == load_json(
        'expected_test_with_images_response_v2_with_weight.json',
    )
