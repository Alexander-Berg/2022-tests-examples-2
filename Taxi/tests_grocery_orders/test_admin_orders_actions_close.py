import pytest

from . import headers
from . import helpers
from . import models


NOW = '2020-03-13T07:19:00+00:00'

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'


@pytest.mark.parametrize(
    'dispatch_cargo_status,close_money_status,response_status',
    [
        ('delivery_arrived', 'success', 200),
        ('pickuped', 'success', 405),
        ('delivery_arrived', 'failed', 405),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        grocery_cart,
        pgsql,
        dispatch_cargo_status,
        response_status,
        close_money_status,
        processing,
):
    state = models.OrderState(close_money_status=close_money_status)
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        state=state,
        grocery_flow_version=PROCESSING_FLOW_VERSION,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='id',
            dispatch_status='delivering',
            dispatch_cargo_status=dispatch_cargo_status,
        ),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/close',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )
    order.update()

    assert response.status_code == response_status

    if response_status == 200:
        assert order.desired_status == 'closed'
        order.check_order_history(
            'admin_action',
            {'to_action_type': 'close', 'status': 'success', 'admin_info': {}},
        )
        assert order.desired_status is not None
        processing_event = _get_last_processing_events(processing, order, 1)[0]
        assert processing_event.payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'flow_version': PROCESSING_FLOW_VERSION,
            'is_canceled': False,
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }

    if response_status == 405:
        order.check_order_history(
            'admin_action',
            {'to_action_type': 'close', 'status': 'fail', 'admin_info': {}},
        )
        assert order.desired_status is None


def _get_last_processing_events(processing, order, count=1):
    return helpers.get_last_processing_events(
        processing, order.order_id, queue='processing', count=count,
    )
