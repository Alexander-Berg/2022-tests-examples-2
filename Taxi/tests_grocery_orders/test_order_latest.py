import datetime

import pytest

from . import consts
from . import experiments
from . import headers
from . import models


LATEST_ORDERS_COUNT = 4


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'country, expected_tips_proposal, expected_tips_templates',
    [
        (
            models.Country.Israel,
            consts.ISR_TIPS_PROPOSALS,
            consts.ISR_TIPS_PROPOSAL_TEMPLATES,
        ),
        (
            models.Country.Russia,
            consts.RUS_TIPS_PROPOSALS,
            consts.RUS_TIPS_PROPOSAL_TEMPLATES,
        ),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
        country,
        expected_tips_proposal,
        expected_tips_templates,
):
    order = _setup_order(
        pgsql, grocery_cart, grocery_depots, country_iso3=country.country_iso3,
    )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['id'] == order.order_id
    assert body['order']['client_price_template'] == '1000 $SIGN$$CURRENCY$'
    assert body['order']['currency'] == 'RUB'
    assert body['order']['currency_sign'] == '₽'

    assert body['order_tips_info']['ask_for_tips']
    assert body['order_tips_info']['tips_proposals'] == expected_tips_proposal
    assert (
        body['order_tips_info']['tips_proposal_templates']
        == expected_tips_templates
    )
    assert body['order_tips_info']['tips_currency'] == 'RUB'
    assert body['order_tips_info']['tips_currency_sign'] == '₽'
    assert 'tips_paid' not in body['order_tips_info']

    assert body['order']['tips']['ask_for_tips']
    assert body['order']['tips']['tips_proposals'] == expected_tips_proposal
    assert (
        body['order']['tips']['tips_proposal_templates']
        == expected_tips_templates
    )
    assert body['order']['tips']['tips_currency'] == 'RUB'
    assert body['order']['tips']['tips_currency_sign'] == '₽'
    assert 'tips_paid' not in body['order']['tips']


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'tips_in_cart, cart_tips_paid_template',
    [
        ({'amount': '10', 'amount_type': 'absolute'}, '10 $SIGN$$CURRENCY$'),
        ({'amount': '40', 'amount_type': 'percent'}, '12 $SIGN$$CURRENCY$'),
    ],
)
async def test_with_tips_in_cart(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
        tips_in_cart,
        cart_tips_paid_template,
):
    _setup_order(
        pgsql, grocery_cart, grocery_depots, tips_in_cart=tips_in_cart,
    )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert not body['order_tips_info']['ask_for_tips']
    assert (
        body['order']['tips']['cart_tips_paid_template']
        == cart_tips_paid_template
    )


async def test_return_latest_order(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    _setup_order(pgsql, grocery_cart, grocery_depots)

    order_2 = _setup_order(pgsql, grocery_cart, grocery_depots)

    order_2.upsert(
        created=datetime.datetime.now() + datetime.timedelta(minutes=10),
    )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['id'] == order_2.order_id


@pytest.mark.config(GROCERY_ORDERS_LATEST_ORDERS_COUNT=LATEST_ORDERS_COUNT)
async def test_multiple_orders(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    orders = []
    for i in range(LATEST_ORDERS_COUNT + 3):
        orders.append(
            _setup_order(
                pgsql,
                grocery_cart,
                grocery_depots,
                status=(
                    'closed' if i < LATEST_ORDERS_COUNT + 1 else 'delivering'
                ),
            ),
        )
        orders[-1].upsert(
            created=datetime.datetime.now()
            + datetime.timedelta(minutes=i * 10),
        )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['id'] == orders[LATEST_ORDERS_COUNT].order_id
    for i in range(LATEST_ORDERS_COUNT):
        assert (
            body['orders'][i]['order']['id']
            == orders[LATEST_ORDERS_COUNT - i].order_id
        )
    assert body['order']['id'] == body['orders'][0]['order']['id']


async def test_no_orders(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 404


@experiments.TIPS_EXPERIMENT
async def test_basic_tips_paid(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    order = _setup_order(pgsql, grocery_cart, grocery_depots)

    pay_response = await _pay_tips(taxi_grocery_orders, order.order_id)
    assert pay_response.status_code == 200

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['id'] == order.order_id
    assert not body['order_tips_info']['ask_for_tips']
    assert body['order_tips_info']['tips_paid'] == consts.TIPS_AMOUNT_STR
    assert 'tips_proposals' not in body['order_tips_info']

    assert 'tips' in body['order']
    assert not body['order']['tips']['ask_for_tips']
    assert body['order']['tips']['tips_paid'] == consts.TIPS_AMOUNT_STR
    assert 'tips_proposals' not in body['order']['tips']


@experiments.TIPS_EXPERIMENT
async def test_feedback_submitted(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    evaluation = 3
    feedback_status = 'submitted'

    order = _setup_order(pgsql, grocery_cart, grocery_depots)

    order.upsert(feedback_status=feedback_status, evaluation=evaluation)

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['feedback_status'] == feedback_status
    assert body['order']['evaluation'] == evaluation


async def _pay_tips(taxi_grocery_orders, order_id):
    return await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/tips',
        json={'order_id': order_id, 'amount': consts.TIPS_AMOUNT_STR},
        headers=headers.DEFAULT_HEADERS,
    )


def _setup_order(
        pgsql,
        grocery_cart,
        grocery_depots,
        status='closed',
        flow_version='grocery_flow_v1',
        delivery_type='eats_dispatch',
        add_payment_method=True,
        country_iso3='RUS',
        tips_in_cart=None,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status=status,
        grocery_flow_version=flow_version,
        yandex_uid=headers.YANDEX_UID,
    )
    item = models.GroceryCartItem(item_id='item-id')

    grocery_cart.set_items(items=[item])
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_cart.check_request({'source': 'SQL'})
    if add_payment_method:
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
    grocery_cart.set_delivery_type(delivery_type=delivery_type)

    if tips_in_cart is not None:
        grocery_cart.set_tips(tips_in_cart)

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country_iso3,
    )
    return order


async def test_tristero_flow_v2_only(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    _setup_order(
        pgsql, grocery_cart, grocery_depots, flow_version='tristero_flow_v2',
    )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 404


async def test_tristero_flow_v2_ignored(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        transactions_eda,
        transactions_lavka_isr,
):
    order_1 = _setup_order(pgsql, grocery_cart, grocery_depots)

    order_2 = _setup_order(
        pgsql, grocery_cart, grocery_depots, flow_version='tristero_flow_v2',
    )

    order_2.upsert(
        created=datetime.datetime.now() + datetime.timedelta(minutes=10),
    )

    latest_order_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/latest', headers=headers.DEFAULT_HEADERS,
    )
    assert latest_order_response.status_code == 200

    body = latest_order_response.json()
    assert body['order']['id'] == order_1.order_id
