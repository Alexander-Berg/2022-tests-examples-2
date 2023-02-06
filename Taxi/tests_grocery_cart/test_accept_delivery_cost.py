import decimal

from tests_grocery_cart import common


BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}


async def test_basic(taxi_grocery_cart, cart):
    delivery_cost = '123.456'

    await cart.modify({'test_item': {'p': 345, 'q': 1}})

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/accept-delivery-cost',
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
            'delivery_cost': delivery_cost,
        },
        headers={
            'X-Idempotency-Token': common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cart_id'] == cart.cart_id
    assert response_json['cart_version'] == cart.cart_version + 1

    cart_doc = cart.fetch_db()
    assert cart_doc.delivery_cost == decimal.Decimal(delivery_cost)
