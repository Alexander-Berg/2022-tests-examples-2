import datetime
import json

import pytest

from . import consts
from . import headers
from . import models
from . import order_v2_submit_consts


RETRY_INTERVAL_MINUTES = 1
ERROR_AFTER_MINUTES = 5
STOP_RETRY_AFTER_MINUTES = 10

ERROR_AFTER_DT = consts.NOW_DT + datetime.timedelta(
    minutes=ERROR_AFTER_MINUTES,
)
STOP_RETRY_AFTER_DT = consts.NOW_DT + datetime.timedelta(
    minutes=STOP_RETRY_AFTER_MINUTES,
)

CLAUSE = {
    'title': 'Config',
    'predicate': {
        'init': {
            'set': ['start-cycle'],
            'arg_name': 'name',
            'set_elem_type': 'string',
        },
        'type': 'in_set',
    },
    'value': {
        'retry_interval': {'minutes': RETRY_INTERVAL_MINUTES},
        'error_after': {'minutes': ERROR_AFTER_MINUTES},
        'stop_retry_after': {'minutes': STOP_RETRY_AFTER_MINUTES},
    },
}

EVENT_POLICY_CONFIG = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=[
        'grocery-orders/processing-policy',
        'grocery-processing/policy',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[CLAUSE],
    is_config=True,
)

CART_ITEMS = [models.GroceryCartItem(item_id='item_id')]


@pytest.fixture
def _prepare(pgsql, grocery_cart, grocery_depots):
    def _do():
        order = models.Order(
            pgsql=pgsql,
            status='checked_out',
            grocery_flow_version='grocery_flow_v3',
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_items(CART_ITEMS)
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )

        return order

    return _do


@pytest.fixture(name='processing_reserve')
async def _processing_reserve(taxi_grocery_orders):
    async def _do(order, status_code=200):
        response = await taxi_grocery_orders.post(
            '/processing/v1/reserve',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'payload': {},
            },
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@EVENT_POLICY_CONFIG
@pytest.mark.now(consts.NOW)
async def test_start_pipeline_event_policy(
        taxi_grocery_orders, grocery_cart, grocery_depots, processing,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_depots.add_depot(legacy_depot_id='2809')

    grocery_cart_items = grocery_cart.get_items()
    grocery_cart.set_items(grocery_cart_items)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=order_v2_submit_consts.SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    create_event = events[0]

    assert create_event.payload['reason'] == 'created'

    retry_interval = RETRY_INTERVAL_MINUTES * 60

    assert create_event.payload['event_policy'] == {
        'error_after': ERROR_AFTER_DT.isoformat(),
        'retry_count': 1,
        'retry_interval': retry_interval,
        'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
    }


@pytest.mark.parametrize('with_paymenth_method', [True, False])
async def test_without_payment_method(
        grocery_cart, _prepare, processing_reserve, with_paymenth_method,
):
    order = _prepare()

    if with_paymenth_method:
        grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    if with_paymenth_method:
        await processing_reserve(order, status_code=200)
    else:
        await processing_reserve(order, status_code=500)


@pytest.mark.now(consts.NOW)
async def test_retry_event_policy(taxi_grocery_orders, _prepare, processing):
    order = _prepare()

    retry_count = 10
    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'event_policy': {
                'error_after': ERROR_AFTER_DT.isoformat(),
                'retry_count': retry_count,
                'retry_interval': RETRY_INTERVAL_MINUTES * 60,
                'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
            },
            'payload': {},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    create_event = events[0]

    assert create_event.payload['reason'] == 'created'

    due = consts.NOW_DT + datetime.timedelta(minutes=RETRY_INTERVAL_MINUTES)
    assert create_event.due == due.isoformat()

    retry_interval = RETRY_INTERVAL_MINUTES * 60

    assert create_event.payload['event_policy'] == {
        'error_after': ERROR_AFTER_DT.isoformat(),
        'retry_count': retry_count + 1,
        'retry_interval': retry_interval,
        'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
    }


ERROR_AFTER_ADD_MINUTE_DT = ERROR_AFTER_DT + datetime.timedelta(minutes=1)
ERROR_AFTER_SUB_MINUTE_DT = ERROR_AFTER_DT - datetime.timedelta(minutes=1)


@pytest.mark.parametrize(
    'time_now, status_code',
    [(ERROR_AFTER_ADD_MINUTE_DT, 500), (ERROR_AFTER_SUB_MINUTE_DT, 200)],
)
async def test_error_after(
        taxi_grocery_orders,
        _prepare,
        processing,
        mocked_time,
        time_now,
        status_code,
):
    mocked_time.set(time_now)

    order = _prepare()

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'event_policy': {
                'error_after': ERROR_AFTER_DT.isoformat(),
                'retry_count': 10,
                'retry_interval': RETRY_INTERVAL_MINUTES * 60,
                'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
            },
            'payload': {},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == status_code

    events = list(processing.events(scope='grocery', queue='processing'))
    if status_code == 500:
        assert not events
    else:
        assert events


STOP_AFTER_ADD_MINUTE_DT = STOP_RETRY_AFTER_DT + datetime.timedelta(minutes=1)
STOP_AFTER_SUB_MINUTE_DT = STOP_RETRY_AFTER_DT - datetime.timedelta(minutes=1)


@pytest.mark.parametrize(
    'time_now, status_code',
    [(STOP_AFTER_ADD_MINUTE_DT, 200), (STOP_AFTER_SUB_MINUTE_DT, 500)],
)
async def test_stop_after(
        taxi_grocery_orders,
        _prepare,
        processing,
        mocked_time,
        time_now,
        status_code,
):
    mocked_time.set(time_now)

    order = _prepare()

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'event_policy': {
                'error_after': ERROR_AFTER_DT.isoformat(),
                'retry_count': 10,
                'retry_interval': RETRY_INTERVAL_MINUTES * 60,
                'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
            },
            'payload': {},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == status_code

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events
