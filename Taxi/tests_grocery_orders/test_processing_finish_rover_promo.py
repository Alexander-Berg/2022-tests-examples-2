import pytest

from . import consts
from . import models

from datetime import datetime

ROVER_ISR_SITUATION_CODE = 'rovers_isr'
ROVER_PROMO_SITUATION_CODE = 'rover_promo'


def enable_auto_promo(enabled=True, situation_code=ROVER_PROMO_SITUATION_CODE):
    return pytest.mark.experiments3(
        name='grocery_rover_auto_promo_for_order',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': enabled,
                    'country_situation_code': situation_code,
                },
            },
        ],
        is_config=True,
    )


@enable_auto_promo(situation_code=ROVER_ISR_SITUATION_CODE)
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '50', 'is_percent': True, 'is_plus': False},
        },
    ],
    is_config=True,
)
@pytest.mark.now(consts.NOW)
async def test_happy_path(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    order_id = 'some_order_id'
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    order = models.Order(
        pgsql=pgsql,
        status='closed',
        order_id=order_id,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='some_id',
            dispatch_status='closed',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='rover',
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()
    assert order.finished == consts.NOW_DT

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events) == 2

    compensation_payload = events[0].payload

    assert events[0].item_id == order_id
    # consts.Now plus 3 minutes
    assert events[0].due == '2020-03-13T07:22:00+00:00'
    assert compensation_payload['reason'] == 'internal_compensation_create'
    assert compensation_payload['situation_code'] == ROVER_ISR_SITUATION_CODE


@enable_auto_promo(enabled=False)
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '50', 'is_percent': True, 'is_plus': False},
        },
    ],
    is_config=True,
)
@pytest.mark.now(consts.NOW)
async def test_do_not_send(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    order_id = 'some_order_id'
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    order = models.Order(
        pgsql=pgsql,
        status='closed',
        order_id=order_id,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='some_id',
            dispatch_status='closed',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='rover',
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()
    assert order.finished == consts.NOW_DT

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events) == 1


@enable_auto_promo(enabled=True)
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '50', 'is_percent': False, 'is_plus': True},
        },
    ],
    is_config=True,
)
@pytest.mark.now(consts.NOW)
async def test_skip_as_plus_not_supported(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    order_id = 'some_order_id'
    orderstate = models.OrderState()
    orderstate.close_money_status = 'success'
    order = models.Order(
        pgsql=pgsql,
        status='closed',
        order_id=order_id,
        state=orderstate,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='some_id',
            dispatch_status='closed',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='rover',
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()
    assert order.finished == consts.NOW_DT

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events) == 1
