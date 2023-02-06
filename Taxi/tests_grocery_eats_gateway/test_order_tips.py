import pytest

from tests_grocery_eats_gateway import headers


@pytest.mark.parametrize(
    'ask_for_tips, status', [(True, 'allowed'), (False, 'disallowed')],
)
async def test_get_basic_200(
        taxi_grocery_eats_gateway, grocery_orders, ask_for_tips, status,
):
    order_id = '123-grocery'
    grocery_orders.set_tips_info_response(
        status_code=200,
        body={
            'ask_for_tips': ask_for_tips,
            'tips_proposals': ['49', '99', '199'],
            'tips_paid': '99',
            'tips_currency': 'RUB',
            'tips_currency_sign': '₽',
        },
    )
    grocery_orders.add_order(order_id=order_id)

    response = await taxi_grocery_eats_gateway.get(
        f'/orders/v1/tips?order_id={order_id}',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload'] == {
        'currency': {'code': 'RUB', 'sign': '₽'},
        'description': '',
        'options': {
            'defaultSum': [{'sum': '49'}, {'sum': '99'}, {'sum': '199'}],
        },
        'selected': {'sum': '99'},
        'status': status,
    }


async def test_get_order_not_found(taxi_grocery_eats_gateway, grocery_orders):
    order_id = '123-grocery'
    grocery_orders.set_tips_info_response(status_code=404)

    response = await taxi_grocery_eats_gateway.get(
        f'/orders/v1/tips?order_id={order_id}',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['status'] == 'disallowed'


async def test_get_not_authorized(taxi_grocery_eats_gateway, grocery_orders):
    order_id = '123-grocery'
    grocery_orders.set_tips_info_response(status_code=401)

    response = await taxi_grocery_eats_gateway.get(
        f'/orders/v1/tips?order_id={order_id}',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'ask_for_tips, status', [(True, 'allowed'), (False, 'disallowed')],
)
async def test_post_basic_200(
        taxi_grocery_eats_gateway, grocery_orders, ask_for_tips, status,
):
    order_id = '123-grocery'
    grocery_orders.set_tips_response(
        status_code=200,
        body={
            'ask_for_tips': ask_for_tips,
            'tips_proposals': ['49', '99', '199'],
            'tips_paid': '99',
            'tips_currency': 'RUB',
            'tips_currency_sign': '₽',
        },
    )
    grocery_orders.add_order(order_id=order_id)

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/tips?order_id={order_id}',
        json={'sum': '99'},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload'] == {'status': status, 'paymentUrl': None}


@pytest.mark.parametrize('orders_tips_status', [400, 404, 409])
async def test_post_orders_4xx(
        taxi_grocery_eats_gateway, grocery_orders, orders_tips_status,
):
    order_id = '123-grocery'
    grocery_orders.set_tips_response(status_code=orders_tips_status)
    grocery_orders.add_order(order_id=order_id)

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/tips?order_id={order_id}',
        json={'sum': '99'},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 400


async def test_post_not_authorized(taxi_grocery_eats_gateway, grocery_orders):
    order_id = '123-grocery'
    grocery_orders.set_tips_response(status_code=401)

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/tips?order_id={order_id}',
        json={'sum': '99'},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 500
