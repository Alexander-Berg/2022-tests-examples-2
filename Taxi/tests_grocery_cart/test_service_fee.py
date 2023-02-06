import decimal

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

APP_NAME = 'android'
YANDEX_UID = '123'
PERSONAL_PHONE_ID = 'personal-phoneid'
HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'token',
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={APP_NAME}',
    'X-Yandex-UID': YANDEX_UID,
    'X-YaTaxi-User': f'personal_phone_id={PERSONAL_PHONE_ID}',
}

SERVICE_FEE_AMOUNT = '20'

PRICE = '123'
QUANTITY = '2'

FULL_PRICE = decimal.Decimal(PRICE) * decimal.Decimal(QUANTITY)


@pytest.mark.parametrize(
    'amount, checked_out', [(SERVICE_FEE_AMOUNT, True), ('9999', False)],
)
async def test_checkout(cart, experiments3, amount, checked_out):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})

    response = await cart.checkout(service_fee=amount)
    if checked_out:
        assert 'checkout_unavailable_reason' not in response
    else:
        assert response['checkout_unavailable_reason'] == 'bad_service_fee'


async def test_checkout_pg(cart, experiments3, fetch_cart):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})
    await cart.checkout(service_fee=SERVICE_FEE_AMOUNT)

    cart_pg = fetch_cart(cart.cart_id)
    assert cart_pg.service_fee == decimal.Decimal(SERVICE_FEE_AMOUNT)


@pytest.mark.parametrize(
    'test_handler',
    ['/internal/v1/cart/retrieve/raw', '/admin/v1/cart/retrieve/raw'],
)
async def test_internal_raw_pg(
        taxi_grocery_cart, cart, experiments3, test_handler,
):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})
    await cart.checkout(service_fee=SERVICE_FEE_AMOUNT)

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    total = decimal.Decimal(SERVICE_FEE_AMOUNT) + FULL_PRICE

    assert response.json()['service_fee'] == SERVICE_FEE_AMOUNT
    assert response.json()['service_fee_template'] == _tmpl(SERVICE_FEE_AMOUNT)
    assert response.json()['full_total_template'] == _tmpl(total)
    assert response.json()['client_price_template'] == _tmpl(total)


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@pytest.mark.parametrize('source, is_found', [('All', True), ('SQL', False)])
@pytest.mark.parametrize(
    'test_handler',
    ['/internal/v1/cart/retrieve/raw', '/admin/v1/cart/retrieve/raw'],
)
async def test_internal_raw_cold_storage(
        taxi_grocery_cart,
        experiments3,
        cart,
        grocery_cold_storage,
        pgsql,
        source,
        is_found,
        test_handler,
):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})
    await cart.checkout(service_fee=SERVICE_FEE_AMOUNT)

    checkout_data = {
        'item_id': cart.cart_id,
        'cart_id': cart.cart_id,
        'depot_id': '123',
        'service_fee': SERVICE_FEE_AMOUNT,
    }
    grocery_cold_storage.set_checkout_data_response(items=[checkout_data])
    grocery_cold_storage.check_carts_request(
        item_ids=[cart.cart_id], fields=None,
    )

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        f'delete from cart.checkout_data WHERE cart_id = %s', [cart.cart_id],
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': source},
    )

    if is_found:
        total = decimal.Decimal(SERVICE_FEE_AMOUNT) + FULL_PRICE

        assert response.json()['service_fee'] == SERVICE_FEE_AMOUNT
        assert response.json()['service_fee_template'] == _tmpl(
            SERVICE_FEE_AMOUNT,
        )
        assert response.json()['full_total_template'] == _tmpl(total)
        assert response.json()['client_price_template'] == _tmpl(total)
    else:
        assert 'service_fee' not in response.json()


@pytest.mark.parametrize(
    'enabled, response_service_fee, total',
    [
        (
            True,
            {
                'amount': SERVICE_FEE_AMOUNT,
                'amount_template': f'{SERVICE_FEE_AMOUNT} $SIGN$$CURRENCY$',
            },
            FULL_PRICE + decimal.Decimal(SERVICE_FEE_AMOUNT),
        ),
        (False, None, FULL_PRICE),
    ],
)
async def test_response(
        cart, experiments3, enabled, response_service_fee, total,
):
    if enabled:
        experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    price = PRICE
    quantity = '2'
    await cart.init({'item_id_1': {'price': price, 'quantity': quantity}})

    response = await cart.retrieve()

    assert response.get('service_fee', None) == response_service_fee
    assert response['total_price_template'] == _tmpl(total)


async def test_service_fee_kwargs(cart, experiments3, user_api):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})

    exp3_recorder = experiments3.record_match_tries('grocery_service_fee')

    payment_type = 'card'
    await cart.set_payment(payment_type, headers=HEADERS)

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs

    assert exp3_kwargs['application'] == APP_NAME
    assert exp3_kwargs['country_iso3'] == 'RUS'
    assert exp3_kwargs['order_flow_version'] == 'eats_core'
    assert exp3_kwargs['personal_phone_id'] == PERSONAL_PHONE_ID
    assert exp3_kwargs['region_id'] == 213
    assert exp3_kwargs['yandex_uid'] == YANDEX_UID
    assert exp3_kwargs['country_iso3'] == 'RUS'
    assert exp3_kwargs['payment_method_type'] == payment_type
    assert exp3_kwargs['depot_id'] == keys.DEFAULT_LEGACY_DEPOT_ID


async def test_lavka_retrieve_raw(
        taxi_grocery_cart, cart, experiments3, offers, grocery_surge,
):
    experiments.set_service_fee(experiments3, amount=SERVICE_FEE_AMOUNT)

    delivery_cost = '123'
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        delivery={
            'cost': delivery_cost,
            'next_threshold': '999999',
            'next_cost': '80',
        },
        minimum_order='100',
    )

    await cart.init({'item_id_1': {'price': PRICE, 'quantity': QUANTITY}})
    await cart.checkout(service_fee=SERVICE_FEE_AMOUNT)

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 200

    resp = response.json()
    assert resp['full_price_no_delivery_template'] == _tmpl(FULL_PRICE)
    assert resp['order_conditions']['service_fee_template'] == _tmpl(
        SERVICE_FEE_AMOUNT,
    )
    assert resp['total_price_no_delivery_template'] == _tmpl(FULL_PRICE)

    total = (
        decimal.Decimal(SERVICE_FEE_AMOUNT)
        + FULL_PRICE
        + decimal.Decimal(delivery_cost)
    )
    assert resp['total_price_template'] == _tmpl(total)


def _tmpl(price):
    return f'{price} $SIGN$$CURRENCY$'
