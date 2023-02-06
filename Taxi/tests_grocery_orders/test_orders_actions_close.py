import pytest

from . import headers
from . import models

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'


@pytest.mark.parametrize(
    'order_status,delivery_type,response_status,create_event',
    [
        ('closed', 'eats_dispatch', 200, False),
        ('closed', 'pickup', 200, False),
        ('pending_cancel', 'pickup', 200, False),
        ('assembled', 'pickup', 202, True),
        ('assembled', 'eats_dispatch', 409, False),
        ('assembling', 'pickup', 429, False),
        ('assembling', 'eats_dispatch', 429, False),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        mockserver,
        load_json,
        grocery_cart,
        grocery_depots,
        pgsql,
        processing,
        order_status,
        delivery_type,
        response_status,
        create_event,
):
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        grocery_flow_version=PROCESSING_FLOW_VERSION,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_type(delivery_type)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/close',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )
    assert response.status_code == response_status
    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))
    if create_event:
        assert len(events) == 1
        assert events[0].payload == {
            'reason': 'close',
            'order_id': order.order_id,
            'flow_version': PROCESSING_FLOW_VERSION,
            'is_canceled': False,
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }
        assert order.desired_status == 'closed'
    else:
        assert not events
        assert order.desired_status is None
