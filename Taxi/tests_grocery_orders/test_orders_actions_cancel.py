import pytest

from . import consts
from . import headers
from . import models

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'


@pytest.mark.parametrize(
    'cancel_order_reason', ['depot_no_product', 'courier_being_late', None],
)
@pytest.mark.parametrize(
    'order_status,response_status,create_event',
    [
        ('closed', 400, False),
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
        '/lavka/v1/orders/v1/actions/cancel',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id, 'reason': cancel_order_reason},
    )
    assert response.status_code == response_status
    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))
    if create_event:
        assert len(events) == 1

        cancel_reason_message = cancel_order_reason
        if cancel_reason_message is None:
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


@pytest.mark.parametrize(
    'request_cancel_type,order_cancel_type',
    [('user', 'user_request'), ('logical', 'client_side_request')],
)
async def test_cancel_type(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_depots,
        grocery_cart,
        request_cancel_type,
        order_cancel_type,
):
    order = models.Order(pgsql=pgsql, status='reserving')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    reason = 'some reason'

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/cancel',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'cancel_type': request_cancel_type,
            'reason': reason,
        },
    )
    assert response.status_code == 202

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1

    assert events[0].payload['cancel_reason_type'] == order_cancel_type
    assert events[0].payload['cancel_reason_message'] == reason


async def test_too_big_reason(
        taxi_grocery_orders, pgsql, grocery_depots, grocery_cart,
):
    order = models.Order(pgsql=pgsql, status='reserving')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    reason = 'x' * 129

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/cancel',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id, 'reason': reason},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('status', ['canceled', 'pending_cancel'])
async def test_already_canceled(
        taxi_grocery_orders, pgsql, grocery_depots, grocery_cart, status,
):
    order = models.Order(pgsql=pgsql, status=status)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/cancel',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id, 'reason': 'some reason'},
    )
    assert response.status_code == 200
