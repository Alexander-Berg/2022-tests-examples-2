import decimal
import uuid

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments

IDEMPOTENCY_TOKEN = 'idempotency-token'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
BASIC_HEADERS['X-Idempotency-Token'] = IDEMPOTENCY_TOKEN


ABSOLUTE_TIPS = {'amount': '15', 'amount_type': 'absolute'}

PERCENT_TIPS = {'amount': '10', 'amount_type': 'percent'}


async def test_set_tips_before_checkout(taxi_grocery_cart, cart):
    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': ABSOLUTE_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 404


async def test_not_found(taxi_grocery_cart, cart):
    await cart.init(['test_item'])
    cart_id = str(uuid.uuid4())

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart_id, 'tips': ABSOLUTE_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 404


async def test_retry(taxi_grocery_cart, cart):
    await cart.init(['test_item'])
    await cart.checkout()

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/set-tips',
            json={'cart_id': cart.cart_id, 'tips': ABSOLUTE_TIPS},
            headers=BASIC_HEADERS,
        )
        assert response.status_code == 200


@pytest.mark.parametrize('tips_data', [ABSOLUTE_TIPS, PERCENT_TIPS])
async def test_db(taxi_grocery_cart, cart, tips_data):
    await cart.init(['test_item'])
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': tips_data},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200

    cart_doc = cart.fetch_db()
    assert cart_doc.tips_amount == decimal.Decimal(tips_data['amount'])
    assert cart_doc.tips_amount_type == tips_data['amount_type']

    await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )

    cart_doc = cart.fetch_db()
    assert cart_doc.tips_amount is None
    assert cart_doc.tips_amount_type is None


async def test_response(taxi_grocery_cart, cart):
    await cart.init(['test_item'])
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': ABSOLUTE_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['tips'] == ABSOLUTE_TIPS
    assert response.json()['cart_id'] == cart.cart_id

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': PERCENT_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['tips'] == PERCENT_TIPS
    assert response.json()['cart_id'] == cart.cart_id


async def test_remove_tips(taxi_grocery_cart, cart):
    await cart.init(['test_item'])
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': ABSOLUTE_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['tips'] is not None

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    assert 'tips' not in response.json()


async def test_invalid_payment_flow(taxi_grocery_cart, cart, experiments3):
    experiments.set_tips_payment_flow(experiments3, 'with_order')

    await cart.init(['test_item'])
    await cart.set_tips_v2(tips=ABSOLUTE_TIPS)
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/set-tips',
        json={'cart_id': cart.cart_id, 'tips': ABSOLUTE_TIPS},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_tips_payment_flow'
