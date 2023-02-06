import copy
import datetime

import pytest

from tests_eats_cart import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}

EATER_ID = 'eater2'


@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'path',
    [
        pytest.param(
            '/api/v1/cart/unavailable-items-by-time',
            id='unavailable-items-by-time',
        ),
        pytest.param('/api/v1/cart/disabled-items', id='disabled-items'),
    ],
)
@pytest.mark.parametrize(
    'enable_discounts',
    [
        pytest.param(True, id='with_discounts'),
        pytest.param(False, id='without_discounts'),
    ],
)
@pytest.mark.parametrize(
    'place_info,shipping_type',
    [
        pytest.param(
            'eats_catalog_internal_place_delivery.json',
            'delivery',
            id='delivery',
        ),
        pytest.param(
            'eats_catalog_internal_place_pickup.json', 'pickup', id='pickup',
        ),
    ],
)
async def test_delete_unavailable_items(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        path,
        place_info,
        shipping_type,
        enable_discounts,
):
    local_services.set_place_slug('place123')
    local_services.core_discounts_response = load_json('get_discount.json')
    local_services.available_discounts = enable_discounts
    local_services.core_items_request = [
        '123',
        '1234',
        '12345',
        '123456',
        '1234567',
        '12345678',
        '123456789',
    ]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(place_info)
    plus_response = load_json('eats_plus_cashback.json')
    local_services.set_plus_response(status=200, json=plus_response)
    local_services.set_params(utils.get_params())

    params = copy.deepcopy(PARAMS)
    params['shippingType'] = shipping_type
    local_services.set_params(params)

    response = await taxi_eats_cart.delete(
        path,
        params=params,
        headers=utils.get_auth_headers(EATER_ID, yandex_uid='uid0'),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1

    eats_cart_cursor.execute(
        'SELECT place_menu_item_id FROM eats_cart.cart_items '
        'WHERE deleted_at IS NULL',
    )

    cart_items = eats_cart_cursor.fetchall()
    expected_items = {'123': 1}
    if shipping_type == 'pickup':
        expected_items['1234'] = 1
    else:
        expected_items['123456'] = 1

    if enable_discounts:
        expected_items['123'] += 1
    else:
        expected_items['12345'] = 1

    assert len(cart_items) == 3

    got_items = dict()
    for item in cart_items:
        got_items[item['place_menu_item_id']] = (
            got_items.get(item['place_menu_item_id'], 0) + 1
        )

    assert got_items == expected_items

    eats_cart_cursor.execute(utils.SELECT_CART)

    carts = eats_cart_cursor.fetchall()
    assert len(carts) == 1
    assert carts[0]['shipping_type'] == shipping_type

    total = float(carts[0]['total'])
    response_cart = response.json()['cart']
    assert response_cart['total'] == int(total)
    assert response_cart['decimal_total'] == '{:.0f}'.format(total)
    assert response_cart['cashbacked_total'] == (
        total - plus_response['cashback_outcome']
        if total > plus_response['cashback_outcome']
        else 0
    )
    assert float(response_cart['decimal_cashbacked_total']) == (
        total - float(plus_response['decimal_cashback_outcome'])
        if total > float(plus_response['decimal_cashback_outcome'])
        else 0
    )

    plus_response = utils.make_cashback_data(plus_response)

    response_cart['yandex_plus'] = {'cashback': plus_response}

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    cart_items = eats_cart_cursor.fetchall()
    assert len(cart_items) == 8 if enable_discounts else 7

    for item in cart_items:
        item_id = item['place_menu_item_id']
        if expected_items.get(item_id, 0) > 0:
            assert item['deleted_at'] is None, f'item {item_id} is deleted'
            expected_items[item_id] -= 1
        else:
            assert (
                item['deleted_at'] is not None
            ), f'item {item_id} is not deleted'


@pytest.mark.parametrize(
    'path',
    [
        pytest.param(
            '/api/v1/cart/unavailable-items-by-time',
            id='unavailable-items-by-time',
        ),
        pytest.param('/api/v1/cart/disabled-items', id='disabled-items'),
    ],
)
@pytest.mark.parametrize('shipping_type', ['pickup', 'delivery'])
@pytest.mark.parametrize('delivery_time', ['2021-04-04T11:00:00+03:00', None])
@pytest.mark.parametrize(
    'point, tz_offset',
    [
        (utils.Point(43.10, 131.87), datetime.timedelta(hours=10)),
        (None, datetime.timedelta(hours=3)),  # Moscow
    ],
)
@pytest.mark.now('2021-06-22T15:58:18+00:00')
async def test_delete_unavailable_items_no_cart(
        taxi_eats_cart,
        load_json,
        local_services,
        path,
        shipping_type,
        delivery_time,
        point,
        tz_offset,
):
    local_services.request_params = utils.get_params(
        shipping_type=shipping_type, delivery_time=delivery_time, point=point,
    )
    response = await taxi_eats_cart.delete(
        path,
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 0
    assert local_services.mock_eats_core_discount.times_called == 0

    empy_cart = utils.get_empty_cart(
        load_json,
        delivery_time,
        '2021-06-22T15:58:18+00:00',
        shipping_type,
        tz_offset,
    )
    assert response.json()['cart'] == empy_cart


@pytest.mark.parametrize(
    'path',
    [
        pytest.param(
            '/api/v1/cart/unavailable-items-by-time',
            id='unavailable-items-by-time',
        ),
        pytest.param('/api/v1/cart/disabled-items', id='disabled-items'),
    ],
)
@pytest.mark.parametrize('shipping_type', ['pickup', 'delivery'])
@pytest.mark.parametrize('delivery_time', ['2021-04-04T11:00:00+03:00', None])
@pytest.mark.parametrize(
    'point, tz_offset',
    [
        (utils.Point(43.10, 131.87), datetime.timedelta(hours=10)),
        (None, datetime.timedelta(hours=3)),  # Moscow
    ],
)
@pytest.mark.now('2021-06-22T15:58:18+00:00')
async def test_delete_unavailable_items_empty_cart(
        taxi_eats_cart,
        load_json,
        local_services,
        path,
        db_insert,
        shipping_type,
        delivery_time,
        point,
        tz_offset,
):

    cart_id = db_insert.cart(EATER_ID)
    db_insert.eater_cart(EATER_ID, cart_id)

    local_services.request_params = utils.get_params(
        shipping_type=shipping_type, delivery_time=delivery_time, point=point,
    )

    response = await taxi_eats_cart.delete(
        path,
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 0
    assert local_services.mock_eats_core_discount.times_called == 0

    empy_cart = utils.get_empty_cart(
        load_json,
        delivery_time,
        '2021-06-22T15:58:18+00:00',
        shipping_type,
        tz_offset,
    )
    assert response.json()['cart'] == empy_cart


@pytest.mark.parametrize(
    'eater_id, is_shop',
    [
        pytest.param('eater2', True, id='shop'),
        pytest.param('eater1', False, id='restaurant'),
    ],
)
@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['not_in_stock.sql'])
async def test_cart_not_in_stock(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        eater_id,
        is_shop,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['1']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['1']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.delete(
        '/api/v1/cart/disabled-items',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    resp_cart = response.json()['cart']
    expected_quantity = 9 if is_shop else 15

    if is_shop:
        assert len(resp_cart['items']) == 1
        assert resp_cart['items'][0]['quantity'] == expected_quantity
    else:
        assert len(resp_cart['items']) == 2
        assert resp_cart['items'][0]['quantity'] == expected_quantity
        assert resp_cart['items'][1]['quantity'] == 15

    eats_cart_cursor.execute(utils.SELECT_CART)

    carts = eats_cart_cursor.fetchall()

    current_user_carts = [
        cart for cart in carts if cart['eater_id'] == eater_id
    ]

    assert len(current_user_carts) == 1

    cart = current_user_carts[0]

    assert cart['promo_subtotal'] == 1500.0 + expected_quantity * 100.0
    assert cart['total'] == cart['promo_subtotal'] + cart['delivery_fee']
    assert resp_cart['total'] == cart['total']

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    cart_items = eats_cart_cursor.fetchall()

    current_user_items = [
        item for item in cart_items if item['cart_id'] == cart['id']
    ]
    if is_shop:
        assert len(current_user_items) == 1
        assert resp_cart['items'][0]['quantity'] == expected_quantity
    else:
        assert len(current_user_items) == 2
        assert current_user_items[0]['quantity'] == expected_quantity
        assert current_user_items[1]['quantity'] == 15
