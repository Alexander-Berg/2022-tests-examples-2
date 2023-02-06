# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
# pylint: enable=import-error
import pytest

from . import headers
from . import models

ABSOLUTE_TIPS = {'amount': '0.01', 'amount_type': 'absolute'}
PERCENT_TIPS = {'amount': '100', 'amount_type': 'percent'}


@pytest.fixture(name='init_order')
def _init_order(pgsql, grocery_cart, grocery_depots):
    def _do(init_status, add_cart=True):
        depot_id = '1234'

        order = models.Order(
            pgsql=pgsql,
            status=init_status,
            dispatch_status_info=models.DispatchStatusInfo(),
            depot_id=depot_id,
        )

        if add_cart is True:
            grocery_cart.add_cart(cart_id=order.cart_id)
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)
        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )

        return order

    return _do


@pytest.mark.parametrize('tips', [ABSOLUTE_TIPS, PERCENT_TIPS, None])
async def test_normal_response(
        taxi_grocery_orders, grocery_cart, init_order, tips,
):
    order = init_order(init_status='checked_out')

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': order.order_id, 'tips': tips},
        headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    body = response.json()

    assert response.status_code == 200
    assert body['order_id'] == order.order_id
    assert grocery_cart.internal_set_tips_called() == 1
    if tips is None:
        assert 'tips' not in body
    else:
        assert body['tips'] == tips


@pytest.mark.parametrize('status', ['closed', 'canceled', 'pending_cancel'])
async def test_wrong_status(
        taxi_grocery_orders, grocery_cart, init_order, status,
):
    order = init_order(init_status=status)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': order.order_id, 'tips': ABSOLUTE_TIPS},
        headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    assert response.status_code == 404
    assert grocery_cart.internal_set_tips_called() == 0


async def test_wrong_order_id(taxi_grocery_orders, grocery_cart, init_order):
    order = init_order(init_status='checked_out')

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': 'another_id', 'tips': ABSOLUTE_TIPS},
        headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    assert response.status_code == 404
    assert grocery_cart.internal_set_tips_called() == 0


async def test_disable_for_tips_with_order(
        taxi_grocery_orders, grocery_cart, init_order,
):
    order = init_order(init_status='checked_out')

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': order.order_id, 'tips': ABSOLUTE_TIPS},
        headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    assert response.status_code == 200
    assert grocery_cart.internal_set_tips_called() == 1


async def test_wrong_cart_id(taxi_grocery_orders, grocery_cart, init_order):
    order = init_order(init_status='checked_out', add_cart=False)
    grocery_cart.check_request(
        fields_to_check={'cart_id': order.cart_id, 'tips': ABSOLUTE_TIPS},
        handler=mock_grocery_cart.Handler.set_tips,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': order.order_id, 'tips': ABSOLUTE_TIPS},
        headers=headers.DEFAULT_HEADERS,
    )
    order.update()

    assert response.status_code == 404
    assert grocery_cart.internal_set_tips_called() == 1


async def test_unauthorized(taxi_grocery_orders, grocery_cart, init_order):
    order = init_order(init_status='checked_out')

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/set-tips',
        json={'order_id': 'another_id', 'tips': ABSOLUTE_TIPS},
    )
    order.update()

    assert response.status_code == 401
    assert grocery_cart.internal_set_tips_called() == 0
