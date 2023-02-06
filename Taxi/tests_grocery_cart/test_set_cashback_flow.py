import copy
import uuid

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

IDEMPOTENCY_TOKEN = 'idempotency-token'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
BASIC_HEADERS['X-Idempotency-Token'] = IDEMPOTENCY_TOKEN
BASIC_HEADERS['User-Agent'] = keys.DEFAULT_USER_AGENT


async def test_unauthorized_access(taxi_grocery_cart, cart):

    basic_headers = BASIC_HEADERS.copy()
    basic_headers['X-YaTaxi-Session'] = ''

    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'gain',
        },
        headers=basic_headers,
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'random_cart_id, checked_out', [(True, False), (False, True)],
)
async def test_not_found(taxi_grocery_cart, cart, random_cart_id, checked_out):
    await cart.init(['test_item'])
    if checked_out:
        await cart.checkout()

    if not random_cart_id:
        cart_id = cart.cart_id
    else:
        cart_id = str(uuid.uuid4())

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'gain',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 404


async def test_conflict(taxi_grocery_cart, cart):
    await cart.init(['test_item_1'])
    await cart.modify(['test_item_2'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'gain',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 409


async def test_retry(taxi_grocery_cart, cart):
    await cart.init(['test_item'])

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/set-cashback-flow',
            json={
                'cart_id': cart.cart_id,
                'cart_version': 1,
                'position': keys.DEFAULT_POSITION,
                'cashback_flow': 'gain',
            },
            headers=BASIC_HEADERS,
        )
        assert response.status_code == 200


@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_db(taxi_grocery_cart, cart, cashback_flow):
    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': cashback_flow,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200

    cart_doc = cart.fetch_db()
    assert cart_doc.cashback_flow == cashback_flow
    assert cart_doc.cart_version == 2
    assert cart_doc.idempotency_token == IDEMPOTENCY_TOKEN


@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_response_cashback_flow(taxi_grocery_cart, cart, cashback_flow):
    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': cashback_flow,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['cashback_flow'] == cashback_flow


@pytest.mark.parametrize('payment_available', [None, False, True])
async def test_checkout_unavailable_reason_by_payment_available(
        taxi_grocery_cart, cart, payment_available, grocery_p13n,
):
    await cart.init(['test_item'])

    await taxi_grocery_cart.invalidate_caches()

    balance = 12345
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'charge',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cashback_flow'] == 'charge'
    if payment_available:
        assert 'checkout_unavailable_reason' not in response_json
    else:
        assert (
            response_json['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )


@pytest.mark.parametrize(
    'payment_method, cashback_flow, available',
    [
        (None, 'charge', True),
        ('card', 'charge', True),
        ('corp', 'charge', False),
        ('unknown', 'charge', False),
        (None, 'gain', True),
        ('card', 'gain', True),
        ('corp', 'gain', False),
        ('unknown', 'gain', True),
    ],
)
async def test_charge_checkout_unavailable_reason_by_payment_method(
        taxi_grocery_cart,
        cart,
        payment_method,
        cashback_flow,
        available,
        grocery_p13n,
):
    await cart.init(['test_item'])
    if payment_method is not None:
        await cart.set_payment(payment_method)

    await taxi_grocery_cart.invalidate_caches()

    payment_available = True
    balance = 12345
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': cashback_flow,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    cart.cart_id = response_json['cart_id']
    cart.cart_version = response_json['cart_version']
    assert response_json['cashback_flow'] == cashback_flow
    if available:
        assert 'checkout_unavailable_reason' not in response_json
    else:
        assert (
            response_json['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'disabled',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cashback_flow'] == 'disabled'
    assert 'checkout_unavailable_reason' not in response_json


@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
@pytest.mark.parametrize('cashback_balance', [5, 500])
async def test_full_price_cashback_flow(
        cart, overlord_catalog, cashback_flow, cashback_balance, grocery_p13n,
):
    item_id = 'item_id_1'
    price = 100
    quantity = 1
    balance = 500
    payment_available = True

    overlord_catalog.add_product(
        product_id=item_id, price=str(price), in_stock='10',
    )

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    total_price_template = price * quantity
    if cashback_flow == 'charge':
        total_price_template -= min(balance, (price - 1) * quantity)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    response = await cart.set_cashback_flow(cashback_flow)

    assert response['cashback_flow'] == cashback_flow
    assert (
        response['total_price_template']
        == str(total_price_template) + ' $SIGN$$CURRENCY$'
    )
    assert ('full_price_template' in response) == (cashback_flow == 'charge')
    if cashback_flow == 'charge':
        assert (
            response['full_price_template']
            == str(price * quantity) + ' $SIGN$$CURRENCY$'
        )


@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
@pytest.mark.parametrize('balance', [5, 500])
@pytest.mark.now(keys.TS_NOW)
async def test_full_price_no_delivery_cashback_flow(
        overlord_catalog,
        cart,
        cashback_flow,
        balance,
        offers,
        experiments3,
        grocery_surge,
        grocery_p13n,
):
    delivery_cost = 100
    delivery = {
        'cost': str(delivery_cost),
        'next_cost': str(delivery_cost),
        'next_threshold': '9999999',
    }

    item_id = 'item-id'
    price = 165
    quantity = 1
    payment_available = True

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        delivery=delivery,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    response = await cart.set_cashback_flow(cashback_flow)

    cashback_available_for_payment = min(balance, (price - 1) * quantity)

    total_price_no_delivery = price * quantity
    total_price_template = total_price_no_delivery + delivery_cost
    if cashback_flow == 'charge':
        total_price_no_delivery -= cashback_available_for_payment
        total_price_template -= cashback_available_for_payment

    assert response['cashback_flow'] == cashback_flow
    assert (
        response['total_price_template']
        == str(total_price_template) + ' $SIGN$$CURRENCY$'
    )
    assert (
        response['total_price_no_delivery_template']
        == str(total_price_no_delivery) + ' $SIGN$$CURRENCY$'
    )
    assert ('full_price_template' in response) == (cashback_flow == 'charge')
    if cashback_flow == 'charge':
        assert (
            response['full_price_template']
            == str(price * quantity + delivery_cost) + ' $SIGN$$CURRENCY$'
        )
        assert (
            response['full_price_no_delivery_template']
            == str(price * quantity) + ' $SIGN$$CURRENCY$'
        )


@pytest.mark.parametrize('balance', [-1, 0, 1])
async def test_charge_cashback_flow_no_balance(
        taxi_grocery_cart, cart, grocery_p13n, balance,
):
    await cart.init(['test_item'])
    await taxi_grocery_cart.invalidate_caches()

    payment_available = True
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    cashback_flow = 'charge'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': cashback_flow,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    cart.cart_id = response_json['cart_id']
    cart.cart_version = response_json['cart_version']
    assert response_json['cashback_flow'] == cashback_flow

    if balance <= 0:
        assert 'checkout_unavailable_reason' in response_json
        assert (
            response_json['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )
    else:
        assert 'checkout_unavailable_reason' not in response_json


@experiments.ENABLED_PARCEL_EXP
@experiments.ENABLED_PICKUP_EXP
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.DELIVERY_TYPES_EXP
@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_tristero_disables_cashback(
        overlord_catalog, tristero_parcels, cart, cashback_flow, grocery_p13n,
):
    product_id = 'item_id_1'
    product_price = 100500
    parcel_product_id = 'parcels_id_1:st-pa'
    payment_available = True
    balance = 100500

    tristero_parcels.add_parcel(parcel_id=parcel_product_id)
    overlord_catalog.add_product(product_id=product_id, price=product_price)
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )
    headers = {**common.TAXI_HEADERS, 'X-Yandex-Uid': '1234'}
    await cart.modify(
        {
            parcel_product_id: {'q': 1, 'p': 0},
            product_id: {'q': 1, 'p': product_price},
        },
        headers=headers,
        delivery_type='pickup',
    )
    await cart.set_payment('card', headers=headers)
    response = await cart.set_cashback_flow(cashback_flow, headers=headers)
    assert response['cashback_flow'] == cashback_flow
    assert response['cashback']['availability'] == {
        'type': 'tristero',
        'disabled_reason': (
            'Баллы Плюса временно недоступны при заказе с посылками'
        ),
    }
    if cashback_flow == 'disabled':
        assert 'checkout_unavailable_reason' not in response
    else:
        assert (
            response['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )


@experiments.ENABLED_PARCEL_EXP
@experiments.ENABLED_PICKUP_EXP
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.DELIVERY_TYPES_EXP
@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_pickup_disables_cashback(
        overlord_catalog, cart, cashback_flow, grocery_p13n,
):
    product_id = 'item_id_1'
    product_price = 100500
    payment_available = True
    balance = 100500

    overlord_catalog.add_product(product_id=product_id, price=product_price)
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify(
        {product_id: {'q': 1, 'p': product_price}}, delivery_type='pickup',
    )
    await cart.set_payment('card')
    response = await cart.set_cashback_flow(cashback_flow)
    assert response['cashback_flow'] == cashback_flow
    assert response['cashback']['availability'] == {
        'type': 'pickup',
        'disabled_reason': 'Баллы Плюса не работают при самовывозе',
    }
    if cashback_flow == 'disabled':
        assert 'checkout_unavailable_reason' not in response
    else:
        assert (
            response['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_grocery_order_with_cashback(
        overlord_catalog, cart, cashback_flow, grocery_p13n,
):
    product_id = 'item_id_1'
    product_price = 100
    balance = 500
    quantity = 2
    payment_available = True
    overlord_catalog.add_product(product_id=product_id, price=product_price)
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify({product_id: {'q': quantity, 'p': product_price}})
    await cart.set_payment('card')
    response = await cart.set_cashback_flow(cashback_flow)

    assert response['cashback_flow'] == cashback_flow
    assert response['available_for_checkout']

    assert response['cashback']['available_for_payment'] == str(
        quantity * (product_price - 1),
    )


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('cashback_flow', ['disabled', 'gain', 'charge'])
async def test_error_temp_unavailable(
        overlord_catalog, cart, grocery_p13n, cashback_flow,
):
    product_id = 'item_id_1'
    product_price = 100
    balance = 500
    quantity = 2
    payment_available = True

    overlord_catalog.add_product(product_id=product_id, price=product_price)
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify({product_id: {'q': quantity, 'p': product_price}})
    await cart.set_payment('card')
    response = await cart.set_cashback_flow(cashback_flow)

    if cashback_flow == 'disabled':
        assert response['available_for_checkout']
        return

    assert not response['available_for_checkout']
    assert 'availability' in response['cashback']

    availability = response['cashback']['availability']
    assert availability['type'] == 'temporary_unavailable'
    assert availability['disabled_reason'] == 'Кэшбек временно не доступен'


async def test_coupons_additional_data(
        taxi_grocery_cart, cart, grocery_coupons, grocery_p13n,
):
    await cart.init(['test_item'])

    assert grocery_p13n.discount_modifiers_times_called == 1
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'charge',
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200

    assert grocery_p13n.discount_modifiers_times_called == 2


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart, cart, user_api, has_personal_phone_id,
):
    await cart.init(['test_item'])

    headers = copy.deepcopy(BASIC_HEADERS)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-cashback-flow',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'cashback_flow': 'charge',
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)
