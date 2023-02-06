import datetime

import pytest

SOME_CART_ID = '00000000-0000-0000-0000-d98013100500'
SOME_ORDER_ID = '111-23456'

COMMON_HEADERS = {
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': 'eats_user_id=111, personal_phone_id=222',
    'X-Idempotency-Token': 'idempotency-token',
    'X-YaTaxi-Session': 'taxi:uuu',
}

URI = (
    'ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.'
    '001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%'
    '20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%9'
    '2%D0%B0%D1%80%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%B'
    'E%D0%B5%20%D1%88%D0%BE%D1%81%D1%81%D0%B5%2C%2014'
    '1%D0%90%D0%BA1%2C%20%D0%BF%D0%BE%D0%B4%D1%8A%D0%B'
    '5%D0%B7%D0%B4%201%20%7B3457696635%7D'
)


def _to_template(price):
    return f'{str(price)} $SIGN$$CURRENCY$'


@pytest.mark.now(datetime.datetime(2020, 3, 25, 10, 0, 0).isoformat())
@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_cart_response_in_case_of_error(taxi_grocery_orders, mockserver):
    depot_id = '71255'

    item_id = 'toilet tissue'
    item_title = 'Toilet tissue'
    item_price = '9000'
    item_quantity = '2'
    new_version = 5
    checkout_unavailable_reason = 'quantity-over-limit'
    diff = {
        'products': [
            {
                'product_id': item_id,
                'quantity': {'actual_limit': '1', 'wanted': item_quantity},
            },
        ],
    }

    @mockserver.json_handler('/grocery-cart/internal/v2/cart/checkout')
    def mock_grocery_cart(request):
        assert request.headers['x-idempotency-token'] == 'idempotency-token'
        assert request.json == {
            'position': {'location': [37.0, 55.0]},
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'order_flow_version': 'eats_core',
            'additional_data': {
                'device_coordinates': {'location': [37.0, 55.0], 'uri': URI},
                'city': 'Moscow',
                'street': 'Varshavskoye Highway',
                'house': '141Ак1',
                'flat': '666',
                'comment': 'please, fast!',
                'doorcode': '42',
                'entrance': '3333',
                'floor': '13',
            },
        }
        return {
            'depot_id': depot_id,
            'items': [
                {
                    'id': item_id,
                    'product_key': {'id': item_id, 'shelf_type': 'store'},
                    'price': item_price,
                    'price_template': _to_template(item_price),
                    'quantity': item_quantity,
                    'title': item_title,
                    'currency': 'RUB',
                    'refunded_quantity': '0',
                },
            ],
            'order_conditions': {'delivery_cost': '199.99'},
            'checkout_unavailable_reason': checkout_unavailable_reason,
            'cart': {
                'cart_id': SOME_CART_ID,
                'cart_version': new_version,
                'requirements': {},
                'diff_data': diff,
            },
            'delivery_type': 'courier',
        }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'entrance': '3333',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'details': {
            'cart': {
                'cart_id': SOME_CART_ID,
                'cart_version': new_version,
                'checkout_unavailable_reason': checkout_unavailable_reason,
                'diff_data': diff,
                'requirements': {},
            },
        },
        'code': 'grocery_unavailable_for_checkout',
        'message': 'Cart unavailable for checkout',
    }

    assert mock_grocery_cart.times_called == 1


@pytest.mark.now(datetime.datetime(2020, 3, 25, 10, 0, 0).isoformat())
@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_409_from_checkout(
        taxi_grocery_orders, mockserver, load_json, yamaps_local,
):
    @mockserver.json_handler('/grocery-cart/internal/v2/cart/checkout')
    def mock_grocery_cart(request):
        assert request.headers['x-idempotency-token'] == 'idempotency-token'
        assert request.json == {
            'position': {'location': [37.0, 55.0]},
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'order_flow_version': 'eats_core',
            'additional_data': {
                'device_coordinates': {'location': [37.0, 55.0], 'uri': URI},
                'city': 'Moscow',
                'street': 'Varshavskoye Highway',
                'house': '141Ак1',
                'flat': '666',
                'comment': 'please, fast!',
                'doorcode': '42',
                'entrance': '3333',
                'floor': '13',
            },
        }
        return mockserver.make_response(
            '{"code": "NO_CODE", "message": ""}', 409,
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'entrance': '3333',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'outdated_cart'

    assert mock_grocery_cart.times_called == 1
