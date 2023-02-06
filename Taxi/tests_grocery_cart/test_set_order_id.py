import uuid

import pytest


_NO_CART = object()


def _get_cart_id(small_cart_id):
    template = uuid.UUID(int=0).hex
    return small_cart_id + template[len(small_cart_id) :]


def _find_order_id(cart_id, pgsql):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'SELECT order_id FROM cart.carts WHERE cart_id = %s', (cart_id,),
    )
    row = cursor.fetchone()
    return row[0]


@pytest.mark.parametrize(
    'cart_id,response_code, expected_order_id',
    [['bad', 404, _NO_CART], ['fa15e', 400, None], ['720e', 200, '777']],
)
async def test_basic(
        taxi_grocery_cart, cart_id, response_code, expected_order_id, pgsql,
):
    cart_id = _get_cart_id(cart_id)
    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-order-id',
        json={'cart_id': cart_id, 'order_id': '777'},
    )
    assert response.status_code == response_code
    if expected_order_id is not _NO_CART:
        assert _find_order_id(cart_id, pgsql) == expected_order_id


async def test_duplicate_order_id(taxi_grocery_cart, pgsql):
    order_id = '777'
    first_cart_id = _get_cart_id('721e')
    second_cart_id = _get_cart_id('720e')

    response_first = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-order-id',
        json={'cart_id': first_cart_id, 'order_id': order_id},
    )

    response_second = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-order-id',
        json={'cart_id': second_cart_id, 'order_id': order_id},
    )

    assert response_first.status_code == 200
    assert _find_order_id(first_cart_id, pgsql) == order_id

    assert response_second.status_code == 409
    assert _find_order_id(second_cart_id, pgsql) is None


@pytest.mark.parametrize(
    'order_id, response_code', [('777', 200), ('666', 409)],
)
async def test_idempotency(taxi_grocery_cart, order_id, response_code, pgsql):
    cart_id = _get_cart_id('720e')
    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-order-id',
        json={'cart_id': cart_id, 'order_id': '777'},
    )
    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-order-id',
        json={'cart_id': cart_id, 'order_id': order_id},
    )
    assert response.status_code == response_code
    assert _find_order_id(cart_id, pgsql) == '777'
