import pytest

from tests_grocery_cart import common


SOME_PAYMENT_ID = '123123123'
SOME_CART_ID = '8da556be-0971-4f3b-a454-d980130662cc'


@pytest.fixture
def _check_cart_pg_payment(cart, fetch_cart):
    def _check(payment_type, payment_id):
        cart_from_pg = fetch_cart(cart.cart_id)
        assert cart_from_pg.payment_method_type == payment_type
        assert cart_from_pg.payment_method_id == payment_id

    return _check


async def test_basic(taxi_grocery_cart, cart, _check_cart_pg_payment):
    await cart.init(['test_item'])

    payment_method_type = 'card'
    await cart.set_payment(payment_method_type)

    _check_cart_pg_payment(payment_method_type, payment_id=None)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/save-payment-method-id',
        json={
            'cart_id': cart.cart_id,
            'payment_type': payment_method_type,
            'payment_id': SOME_PAYMENT_ID,
        },
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 200

    _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)


async def test_another_payment_type(
        taxi_grocery_cart, cart, _check_cart_pg_payment,
):
    await cart.init(['test_item'])

    payment_method_type = 'card'
    another_payment_type = 'applepay'

    await cart.set_payment(payment_method_type)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/save-payment-method-id',
        json={
            'cart_id': cart.cart_id,
            'payment_type': another_payment_type,
            'payment_id': SOME_PAYMENT_ID,
        },
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 409

    _check_cart_pg_payment(payment_method_type, None)


async def test_already_set_payment_id(
        taxi_grocery_cart, cart, _check_cart_pg_payment,
):
    await cart.init(['test_item'])

    payment_method_type = 'card'

    await cart.set_payment(payment_method_type, SOME_PAYMENT_ID)

    _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/save-payment-method-id',
        json={
            'cart_id': cart.cart_id,
            'payment_type': payment_method_type,
            'payment_id': SOME_PAYMENT_ID,
        },
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 200

    _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)


async def test_already_set_another_payment_id(
        taxi_grocery_cart, cart, _check_cart_pg_payment,
):
    await cart.init(['test_item'])

    payment_method_type = 'card'

    await cart.set_payment(payment_method_type, SOME_PAYMENT_ID)

    _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/save-payment-method-id',
        json={
            'cart_id': cart.cart_id,
            'payment_type': payment_method_type,
            'payment_id': SOME_PAYMENT_ID + 'xxx',
        },
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 409

    _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)


async def test_idempotency(taxi_grocery_cart, cart, _check_cart_pg_payment):
    await cart.init(['test_item'])

    payment_method_type = 'card'

    await cart.set_payment(payment_method_type)

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/save-payment-method-id',
            json={
                'cart_id': cart.cart_id,
                'payment_type': payment_method_type,
                'payment_id': SOME_PAYMENT_ID,
            },
            headers=common.TAXI_HEADERS,
        )
        assert response.status_code == 200

        _check_cart_pg_payment(payment_method_type, SOME_PAYMENT_ID)


async def test_not_found(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/save-payment-method-id',
        json={
            'cart_id': SOME_CART_ID,
            'payment_type': 'card',
            'payment_id': SOME_PAYMENT_ID,
        },
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 404
