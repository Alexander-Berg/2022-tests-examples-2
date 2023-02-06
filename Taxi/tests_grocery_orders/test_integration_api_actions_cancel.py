import pytest

from . import consts
from . import models

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'


@pytest.mark.parametrize(
    'cancel_order_reason', ['depot_no_product', 'courier_being_late', None],
)
@pytest.mark.parametrize(
    'order_status,response_status,create_event',
    [
        ('closed', 400, False),
        ('canceled', 400, False),
        ('pending_cancel', 400, False),
        ('reserving', 202, True),
        # Forbidden by default, allowed by confing
        ('delivering', 202, True),
    ],
)
@pytest.mark.experiments3(
    name='lavka_order_cancel_allowed_statuses',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'statuses': ['created', 'assembling', 'assembled'],
            },
        },
    ],
    default_value={},
    is_config=True,
)
@pytest.mark.now(consts.NOW)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_depots,
        grocery_cart,
        order_status,
        response_status,
        create_event,
        cancel_order_reason,
):
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        grocery_flow_version=PROCESSING_FLOW_VERSION,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/actions/cancel',
        json={'order_id': order.order_id, 'reason': cancel_order_reason},
    )

    assert response.status_code == response_status
    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))
    if create_event:
        assert len(events) == 1

        cancel_reason_message = 'Got cancel request from user'

        assert events[0].payload == {
            'reason': 'cancel',
            'cancel_reason_type': 'user_request',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_message': cancel_reason_message,
            'order_id': order.order_id,
            'flow_version': PROCESSING_FLOW_VERSION,
            'times_called': 0,
        }
        assert order.desired_status == 'canceled'
    else:
        assert not events
        assert order.desired_status is None
