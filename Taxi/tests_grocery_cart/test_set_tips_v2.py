import copy
import decimal
import uuid

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

# pylint: disable=invalid-name
Decimal = decimal.Decimal


IDEMPOTENCY_TOKEN = 'idempotency-token'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
BASIC_HEADERS['X-Idempotency-Token'] = IDEMPOTENCY_TOKEN


ABSOLUTE_TIPS = {'amount': '15', 'amount_type': 'absolute'}

PERCENT_TIPS = {'amount': '10', 'amount_type': 'percent'}


async def test_unauthorized_access(cart):
    basic_headers = BASIC_HEADERS.copy()
    basic_headers['X-YaTaxi-Session'] = ''

    await cart.init(['test_item'])

    await cart.set_tips_v2(
        tips=ABSOLUTE_TIPS, headers=basic_headers, status_code=401,
    )


async def test_set_tips_after_checkout(cart):
    await cart.init(['test_item'])
    await cart.checkout()

    await cart.set_tips_v2(tips=ABSOLUTE_TIPS, status_code=404)


async def test_not_found(cart):
    await cart.init(['test_item'])
    cart_id = str(uuid.uuid4())

    await cart.set_tips_v2(
        tips=ABSOLUTE_TIPS, cart_id=cart_id, status_code=404,
    )


async def test_retry(cart):
    await cart.init(['test_item'])

    for _ in range(2):
        await cart.set_tips_v2(tips=ABSOLUTE_TIPS)


@pytest.mark.parametrize('tips_data', [ABSOLUTE_TIPS, PERCENT_TIPS])
async def test_db(cart, tips_data):
    await cart.init(['test_item'])

    await cart.set_tips_v2(tips=tips_data, headers=BASIC_HEADERS)

    cart_doc = cart.fetch_db()
    assert cart_doc.tips_amount == decimal.Decimal(tips_data['amount'])
    assert cart_doc.tips_amount_type == tips_data['amount_type']
    assert cart_doc.cart_version == 2
    assert cart_doc.idempotency_token == IDEMPOTENCY_TOKEN

    await cart.set_tips_v2(tips=None, cart_version=2, headers=BASIC_HEADERS)

    cart_doc = cart.fetch_db()
    assert cart_doc.tips_amount is None
    assert cart_doc.tips_amount_type is None
    assert cart_doc.cart_version == 3
    assert cart_doc.idempotency_token == IDEMPOTENCY_TOKEN


async def test_response(cart, experiments3, grocery_coupons, grocery_p13n):
    payment_flow = 'with_order'

    experiments.set_tips_payment_flow(experiments3, payment_flow)

    await cart.init(['test_item'])

    response = await cart.retrieve()
    total = '345'
    _check_price(response['total_price_template'], total)
    assert grocery_p13n.discount_modifiers_times_called == 2

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await cart.set_tips_v2(tips=ABSOLUTE_TIPS)
    tips_amount = Decimal(ABSOLUTE_TIPS['amount'])
    _check_price(
        response['total_price_template'], Decimal(total) + tips_amount,
    )

    assert response['tips'] == {**ABSOLUTE_TIPS, 'payment_flow': payment_flow}
    assert response['cart_version'] == 2
    assert response['cart_id'] == cart.cart_id
    assert grocery_p13n.discount_modifiers_times_called == 3

    response = await cart.set_tips_v2(tips=PERCENT_TIPS, cart_version=2)

    percent = Decimal(PERCENT_TIPS['amount']) / Decimal(100)
    tips_amount = Decimal(int(Decimal(total) * percent))
    _check_price(
        response['total_price_template'], Decimal(total) + tips_amount,
    )

    assert response['tips'] == {**PERCENT_TIPS, 'payment_flow': payment_flow}
    assert response['cart_version'] == 3
    assert response['cart_id'] == cart.cart_id
    assert grocery_p13n.discount_modifiers_times_called == 4


async def test_no_tips_to_total_for_empty_cart(cart, experiments3):
    experiments.set_tips_payment_flow(experiments3, 'with_order')

    item_id = 'test_item'
    await cart.init([item_id])

    response = await cart.retrieve()
    total = '345'
    _check_price(response['total_price_template'], total)

    response = await cart.set_tips_v2(tips=ABSOLUTE_TIPS)
    tips_amount = Decimal(ABSOLUTE_TIPS['amount'])
    response_cart_total = response['total_price_template']
    _check_price(response_cart_total, Decimal(total) + tips_amount)

    response = await cart.modify({item_id: {'p': 345, 'q': 0}})
    _check_price(response['total_price_template'], 0)


async def test_wrong_cart_version(cart):
    await cart.init(['test_item'])

    response = await cart.set_tips_v2(tips=ABSOLUTE_TIPS)

    assert response['tips'] == {**ABSOLUTE_TIPS, 'payment_flow': 'separate'}
    assert response['cart_version'] == 2
    assert response['cart_id'] == cart.cart_id

    await cart.set_tips_v2(tips=PERCENT_TIPS, cart_version=3, status_code=409)


async def test_remove_tips(cart):
    await cart.init(['test_item'])

    response = await cart.set_tips_v2(tips=ABSOLUTE_TIPS)

    assert response['tips'] is not None

    response = await cart.set_tips_v2(tips=None, cart_version=2)

    assert 'tips' not in response


@experiments.ENABLED_PICKUP_EXP
@experiments.TIPS_EXPERIMENT
@experiments.DELIVERY_TYPES_EXP
async def test_tips_validation(cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify(
        {item_id: {'q': quantity, 'p': price}}, delivery_type='pickup',
    )
    response = await cart.set_tips_v2(tips=ABSOLUTE_TIPS)

    assert response['checkout_unavailable_reason'] == 'tips-not-allowed'
    assert response['tips'] == {**ABSOLUTE_TIPS, 'payment_flow': 'separate'}

    response = await cart.set_tips_v2(tips=None, cart_version=2)

    assert 'checkout_unavailable_reason' not in response
    assert 'tips' not in response


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(cart, user_api, has_personal_phone_id):
    await cart.init(['test_item'])

    headers = copy.deepcopy(BASIC_HEADERS)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    await cart.set_tips_v2(tips=ABSOLUTE_TIPS, headers=headers)
    assert user_api.times_called == (1 if has_personal_phone_id else 0)


def _check_price(lhs, rhs):
    lhs = str(lhs).replace('$SIGN$$CURRENCY$', '').strip()
    rhs = str(rhs).replace('$SIGN$$CURRENCY$', '').strip()

    assert Decimal(lhs) == Decimal(rhs)
