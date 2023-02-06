import datetime
import json

import dateutil.parser
import pytest

from . import consts
from . import experiments
from . import headers
from . import helpers
from . import models

TIPS_DUE_DELAY = datetime.timedelta(minutes=1)

EDIT_ORDER_TIPS_ITEM = {
    'item_id': 'tips',
    'price': consts.TIPS_AMOUNT_STR,
    'quantity': '1',
    'total_price': consts.TIPS_AMOUNT_STR,
}

EDIT_ORDER_ITEMS = [
    EDIT_ORDER_TIPS_ITEM,
    {
        'item_id': 'item-id',
        'price': '10.15',
        'quantity': '3',
        'total_price': '30.45',
    },
]

PAYMENT_METHOD = {'type': 'card', 'id': 'test_payment_method_id'}


@experiments.TIPS_EXPERIMENT
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_grocery_payments_cycle(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        country,
):
    order = _setup_order(pgsql, grocery_cart)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country.country_iso3,
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await _pay_tips(taxi_grocery_orders, order.order_id)

    order.update()
    assert order.state.tips_status == 'pending'
    assert order.tips[0] == consts.TIPS_AMOUNT

    assert response.status_code == 200

    processing_event = _get_last_processing_events(processing, order, 1)[0]
    assert processing_event.payload == {
        'order_id': order.order_id,
        'reason': 'created',
    }
    assert (
        dateutil.parser.isoparse(processing_event.due)
        == consts.NOW_DT + TIPS_DUE_DELAY
    )

    grocery_payments.check_create(
        order_id=order.order_id,
        country_iso3=country.country_iso3,
        operation_id=str(order.order_revision),
        items_by_payment_types=[
            {
                'items': [
                    {
                        'item_id': 'tips',
                        'item_type': 'tips',
                        'price': consts.TIPS_AMOUNT_STR,
                        'quantity': '1',
                    },
                ],
                'payment_method': PAYMENT_METHOD,
            },
        ],
    )

    pay_response = await taxi_grocery_orders.post(
        '/processing/v1/tips/pay',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert pay_response.status_code == 200

    assert grocery_payments.times_create_called() == 1
    order.update()
    assert order.state.tips_status == 'hold_pending'

    hold_response = await taxi_grocery_orders.post(
        '/processing/v1/tips/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {},
        },
    )
    assert hold_response.status_code == 200
    order.update()
    assert order.state.tips_status == 'close_pending'

    closed_response = await taxi_grocery_orders.post(
        '/processing/v1/tips/set-state',
        json={
            'order_id': order.order_id,
            'state': 'close_money',
            'payload': {},
        },
    )
    assert closed_response.status_code == 200
    order.update()
    assert order.state.tips_status == 'paid'


@pytest.mark.parametrize(
    'tips_amount, tips_amount_type, cart_total, tips_total',
    [('149', 'absolute', '0', 149.00), ('10', 'percent', '355.5', 35.00)],
)
async def test_tips_v2_order_state(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        tips_amount,
        tips_amount_type,
        cart_total,
        tips_total,
):
    order = _setup_order(pgsql, grocery_cart, total=cart_total)

    response = await _pay_tips_v2(
        taxi_grocery_orders,
        order.order_id,
        amount=tips_amount,
        amount_type=tips_amount_type,
    )
    assert response.status_code == 200

    order.update()
    assert order.state.tips_status == 'pending'
    assert order.tips[0] == tips_total


@pytest.mark.now(consts.NOW)
async def test_tips_v2_processing(
        taxi_grocery_orders, pgsql, grocery_cart, processing,
):
    order = _setup_order(pgsql, grocery_cart)
    response = await _pay_tips_v2(taxi_grocery_orders, order.order_id)
    assert response.status_code == 200

    processing_event = _get_last_processing_events(processing, order, 1)[0]
    assert processing_event.payload == {
        'order_id': order.order_id,
        'reason': 'created',
    }
    assert (
        dateutil.parser.isoparse(processing_event.due)
        == consts.NOW_DT + TIPS_DUE_DELAY
    )


async def test_tips_payment_already_started(
        taxi_grocery_orders, pgsql, grocery_cart,
):
    order = _setup_order(pgsql, grocery_cart)
    order_version = None

    for _ in range(2):
        response = await _pay_tips(taxi_grocery_orders, order.order_id)
        assert response.status_code == 200

        order.update()
        if order_version is None:
            order_version = order.order_version

        assert order_version == order.order_version


async def test_race(taxi_grocery_orders, pgsql, grocery_cart, testpoint):
    order = _setup_order(pgsql, grocery_cart)

    @testpoint('after_order_loaded')
    def _state_race_testpoint(data):
        # эмулирую гонку при вызове ручки
        order.upsert(state=models.OrderState(tips_status='paid'))

    response = await _pay_tips(taxi_grocery_orders, order.order_id)
    assert _state_race_testpoint.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'state, tips_status',
    [('hold_money', 'hold_pending'), ('close_money', 'close_pending')],
)
async def test_grocery_payments_failed(
        taxi_grocery_orders, pgsql, grocery_cart, state, tips_status,
):
    order = _setup_order(pgsql, grocery_cart)
    order.upsert(state=models.OrderState(tips_status=tips_status))

    error = {'error_reason_code': 'some error'}
    response = await taxi_grocery_orders.post(
        '/processing/v1/tips/set-state',
        json={
            'order_id': order.order_id,
            'state': state,
            'payload': {'errors': [error]},
        },
    )
    assert response.status_code == 200
    order.update()
    assert order.state.tips_status == 'failed'


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'country', [models.Country.Israel, models.Country.Russia],
)
async def test_tips_info(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, country,
):
    order = _setup_order(pgsql, grocery_cart)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country.country_iso3,
    )

    tips_info = await _get_tips_info(taxi_grocery_orders, order.order_id)
    expected_tips_proposals = []
    expected_tips_templates = []
    if country == models.Country.Russia:
        expected_tips_proposals = consts.RUS_TIPS_PROPOSALS
        expected_tips_templates = consts.RUS_TIPS_PROPOSAL_TEMPLATES
    if country == models.Country.Israel:
        expected_tips_proposals = consts.ISR_TIPS_PROPOSALS
        expected_tips_templates = consts.ISR_TIPS_PROPOSAL_TEMPLATES
    assert tips_info == {
        'ask_for_tips': True,
        'tips_proposals': expected_tips_proposals,
        'tips_currency': 'RUB',
        'tips_currency_sign': '₽',
        'tips_proposal_templates': expected_tips_templates,
    }

    pay_response = await _pay_tips(taxi_grocery_orders, order.order_id)
    assert pay_response.status_code == 200

    tips_info = await _get_tips_info(taxi_grocery_orders, order.order_id)
    assert tips_info == {
        'ask_for_tips': False,
        'tips_paid': consts.TIPS_AMOUNT_STR,
    }


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize('delivery_type', ['pickup', 'rover'])
async def test_no_tips_for_pickup_or_rover(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        delivery_type,
):
    dispatch_status_info = models.DispatchStatusInfo()
    if delivery_type == 'rover':
        dispatch_status_info.dispatch_transport_type = 'rover'
        dispatch_status_info.dispatch_status = 'created'
        dispatch_status_info.dispatch_id = 'dispatch_id_12345'
        dispatch_status_info.dispatch_cargo_status = 'new'

    order = _setup_order(
        pgsql,
        grocery_cart,
        delivery_type=delivery_type,
        dispatch_status_info=dispatch_status_info,
    )
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        country_iso3=models.Country.Israel.country_iso3,
    )

    tips_info = await _get_tips_info(taxi_grocery_orders, order.order_id)

    assert tips_info == {'ask_for_tips': False}


async def test_order_access(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    order = _setup_order(pgsql, grocery_cart)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    tips_info_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips/info',
        json={'order_id': order.order_id},
        headers=headers.DEFAULT_HEADERS,
    )
    assert tips_info_response.status_code == 200

    order.upsert(
        session=headers.DEFAULT_SESSION + 'we',
        yandex_uid=headers.YANDEX_UID + 'we',
    )
    tips_info_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips/info',
        json={'order_id': order.order_id},
        headers=headers.DEFAULT_HEADERS,
    )
    assert tips_info_response.status_code == 404


async def test_pay_tips_order_not_successful(
        taxi_grocery_orders, pgsql, grocery_cart,
):
    order = _setup_order(pgsql, grocery_cart)
    order.upsert(status='canceled')

    response = await _pay_tips(taxi_grocery_orders, order.order_id)
    assert response.status_code == 409


@pytest.mark.parametrize(
    'tip_size,expected_code',
    [
        pytest.param('0', 400, id='Bad tip size'),
        pytest.param('0.01', 200, id='Good tip size'),
    ],
)
async def test_pay_zero_tips(
        taxi_grocery_orders, pgsql, grocery_cart, tip_size, expected_code,
):
    order = _setup_order(pgsql, grocery_cart)

    response = await _pay_tips(
        taxi_grocery_orders, order.order_id, amount=tip_size,
    )
    assert response.status_code == expected_code


@experiments.TIPS_EXPERIMENT
async def test_pay_tips_with_refunded_items(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    order = _setup_order(pgsql, grocery_cart)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    order.upsert(
        state=models.OrderState(
            close_money_status='success', tips_status='pending',
        ),
        tips=consts.TIPS_AMOUNT_STR,
    )

    refunded_item = models.GroceryCartItem(item_id='item-id')
    refunded_item.refunded_quantity = refunded_item.quantity
    grocery_cart.set_items([refunded_item])

    pay_response = await taxi_grocery_orders.post(
        '/processing/v1/tips/pay',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert pay_response.status_code == 200


async def _get_tips_info(taxi_grocery_orders, order_id):
    tips_info = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips/info',
        json={'order_id': order_id},
        headers=headers.DEFAULT_HEADERS,
    )
    assert tips_info.status_code == 200
    return tips_info.json()


async def _pay_tips(
        taxi_grocery_orders, order_id, amount=consts.TIPS_AMOUNT_STR,
):
    return await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips',
        json={'order_id': order_id, 'amount': amount},
        headers=headers.DEFAULT_HEADERS,
    )


async def _pay_tips_v2(
        taxi_grocery_orders, order_id, amount='149', amount_type='absolute',
):
    tips = {'amount': amount, 'amount_type': amount_type}
    return await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips',
        json={'order_id': order_id, 'amount': '0', 'tips': tips},
        headers=headers.DEFAULT_HEADERS,
    )


def _setup_order(
        pgsql,
        grocery_cart,
        flow_version='grocery_flow_v1',
        delivery_type='eats_dispatch',
        add_payment_method=True,
        dispatch_status_info=models.DispatchStatusInfo(),
        total='0',
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
        grocery_flow_version=flow_version,
        dispatch_status_info=dispatch_status_info,
    )
    item = models.GroceryCartItem(item_id='item-id', price=total, quantity='1')

    grocery_cart.set_items(items=[item])
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    if add_payment_method:
        grocery_cart.set_payment_method(PAYMENT_METHOD)
    grocery_cart.set_delivery_type(delivery_type=delivery_type)

    return order


def _get_last_processing_events(processing, order, count=1):
    return helpers.get_last_processing_events(
        processing, order.order_id, count=count, queue='processing_tips',
    )


@experiments.TIPS_EXPERIMENT
async def test_pay_tips_with_409(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    order = _setup_order(pgsql, grocery_cart, flow_version='tristero_flow_v1')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    order.upsert(
        state=models.OrderState(
            close_money_status='success', tips_status='pending',
        ),
        tips=consts.TIPS_AMOUNT_STR,
    )

    pay_response = await taxi_grocery_orders.post(
        '/processing/v1/tips/pay',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert pay_response.status_code == 409
