import pytest

from . import helpers
from . import models


@pytest.fixture
def _prepare(pgsql, grocery_cart, grocery_depots):
    def _do(**kwargs):
        order = models.Order(pgsql=pgsql, **kwargs)

        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )

        return order

    return _do


@pytest.mark.parametrize(
    'operation_type, times_called', [('create', 1), ('update', 0)],
)
@pytest.mark.parametrize('success', [True, False])
async def test_hold(
        taxi_grocery_orders,
        _prepare,
        payments_tracking,
        success,
        operation_type,
        times_called,
):
    order = _prepare()

    status = 'success' if success else 'fail'

    payments_tracking.check_update_status(
        order_id=order.order_id, status=status,
    )

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': helpers.make_set_state_payload(
                success=success, operation_type=operation_type,
            ),
        },
    )

    assert payments_tracking.times_update_status_called() == times_called


async def test_processing_cancel(
        taxi_grocery_orders, payments_tracking, _prepare,
):
    order = _prepare()

    payments_tracking.check_update_status(
        order_id=order.order_id, status='cancel',
    )

    cancel_reason_message = 'smth failed'
    cancel_reason_type = 'timeout'
    cancel_reason_meta = {'any': 'json'}

    await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'cancel_reason_meta': cancel_reason_meta,
            'payload': {},
        },
    )

    assert payments_tracking.times_update_status_called() == 1
