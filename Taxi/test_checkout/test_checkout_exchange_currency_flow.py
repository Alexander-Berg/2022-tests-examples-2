import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_payments_currency_rates


DEPOT_ID = '100'
COUNTRY_ISO3 = 'ISR'
CURRENCY = 'ILS'

EXCHANGE_CURRENCY = 'RUB'
PAYMENT_TYPE = 'card'
CARD_ISSUER = 'RUS'
CART_PAYMENT_META = {'card': {'issuer_country': CARD_ISSUER}}

# CURRENCY_EXCHANGE_RATE == 1.1111
CURRENCY_EXCHANGE_RATE = mock_payments_currency_rates.STOCK_PRICE_1

ITEM_ID = 'item_id_1'
PRICE = '10'
QUANTITY = '2'

EXPECTED_EXCHANGE_PRICE = '11.111'


DEFAULT_PRECISION = '0.0001'

DELIVERY_COST = '5'
EXPECTED_DELIVERY_EXCHANGED = '5.5555'


@pytest.fixture(name='init_depots')
def _init_depots(overlord_catalog, grocery_depots):
    async def _inner():
        overlord_catalog.add_product(product_id=ITEM_ID, price=PRICE)

        grocery_depots.add_depot(
            int(DEPOT_ID),
            legacy_depot_id=DEPOT_ID,
            country_iso3=COUNTRY_ISO3,
            currency=CURRENCY,
            location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        )

    return _inner


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
async def test_db(cart, experiments3, init_depots, fetch_cart):
    experiments.set_exchanger_currency_settings(experiments3)
    await init_depots()

    await cart.init(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )
    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)
    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
    )

    cart_from_pg = fetch_cart(cart.cart_id)
    assert cart_from_pg.payment_method_meta == CART_PAYMENT_META

    items_pricing = cart_from_pg.items_pricing
    assert (
        items_pricing['items'][0]['sub_items'][0]['price_exchanged']
        == EXPECTED_EXCHANGE_PRICE
    )

    assert items_pricing['exchange_currency_info'] == {
        'from_currency': EXCHANGE_CURRENCY,
        'to_currency': CURRENCY,
        'exchange_rate': CURRENCY_EXCHANGE_RATE,
    }


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
@pytest.mark.parametrize(
    'to_currency_precision, expected',
    [('1', '12'), ('0.1', '11.2'), ('0.01', '11.12'), ('0.001', '11.111')],
)
async def test_retrive_raw(
        cart,
        experiments3,
        init_depots,
        grocery_payments,
        to_currency_precision,
        expected,
):
    experiments.set_exchanger_currency_settings(
        experiments3, to_currency_precision=to_currency_precision,
    )
    await init_depots()

    await cart.init(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )
    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)
    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
    )

    response = await cart.internal_retrieve_raw()

    assert (
        response['items_v2'][0]['sub_items'][0]['price_exchanged'] == expected
    )


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
async def test_delivery_exchanged(
        cart, offers, experiments3, grocery_surge, init_depots,
):
    experiments.set_exchanger_currency_settings(experiments3)
    await init_depots()

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        depot_id=DEPOT_ID,
        delivery={
            'cost': DELIVERY_COST,
            'next_threshold': '100',
            'next_cost': DELIVERY_COST,
        },
    )

    await cart.modify(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )

    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)
    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
    )

    response = await cart.internal_retrieve_raw()

    assert response['delivery']['pricing'] == {
        'item_id': 'delivery',
        'price': DELIVERY_COST,
        'full_price': DELIVERY_COST,
        'quantity': '1',
        'price_exchanged': EXPECTED_DELIVERY_EXCHANGED,
    }


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
async def test_currency_info(cart, experiments3, init_depots):
    experiments.set_exchanger_currency_settings(experiments3)
    await init_depots()

    await cart.modify(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )

    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)
    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
    )

    response = await cart.internal_retrieve_raw()

    assert response['currency_settings'] == {
        'from_currency': 'RUB',
        'to_currency': 'ILS',
    }


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
async def test_wrong_settings(cart, experiments3, init_depots):
    experiments.set_exchanger_currency_settings(experiments3, empty_exp=True)
    await init_depots()

    await cart.modify(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )

    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)
    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
        required_status_code=500,
    )

    response = await cart.internal_retrieve_raw()

    assert 'currency_settings' not in response


@experiments.EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ITEMS_PRICING_ENABLED
@pytest.mark.parametrize(
    'tested_exp',
    ['grocery_order_flow_version', 'grocery_exchange_currency_settings'],
)
async def test_kwargs(experiments3, cart, init_depots, tested_exp):
    experiments.set_exchanger_currency_settings(experiments3)
    await init_depots()

    await cart.init(
        {ITEM_ID: {'price': PRICE, 'quantity': QUANTITY}}, currency=CURRENCY,
    )
    exp3_recorder = experiments3.record_match_tries(tested_exp)

    await cart.set_payment(PAYMENT_TYPE, payment_meta=CART_PAYMENT_META)

    await cart.checkout(
        payment_method={'type': PAYMENT_TYPE, 'id': 'qwe'},
        order_flow_version='exchange_currency',
    )

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert tries[0].kwargs['country_iso3'] == 'ISR'
    assert tries[0].kwargs['card_issuer_country'] == 'RUS'
    assert tries[0].kwargs['payment_method_type'] == 'card'
