import decimal

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments


@pytest.mark.parametrize(
    'cashback_flow, cashback_to_pay', [('charge', '60'), ('gain', None)],
)
async def test_checkout_cashback_payment(
        taxi_grocery_cart, cart, cashback_flow, cashback_to_pay, grocery_p13n,
):

    await cart.init(['test_item'])

    await taxi_grocery_cart.invalidate_caches()

    grocery_p13n.set_cashback_info_response(
        payment_available=True, balance=12345,
    )

    await cart.set_cashback_flow(flow=cashback_flow)
    response = await cart.checkout(cashback_to_pay=cashback_to_pay)
    assert response['checkout_unavailable_reason'] == 'no-payment-method'

    await cart.set_payment('corp')
    response = await cart.checkout(cashback_to_pay=cashback_to_pay)
    assert (
        response['checkout_unavailable_reason'] == 'cashback-flow-not-allowed'
    )

    await cart.set_payment('card')
    response = await cart.checkout(cashback_to_pay=cashback_to_pay)
    assert 'checkout_unavailable_reason' not in response

    assert response['cashback_flow'] == cashback_flow


def _cashback_to_pay(cashback_flow):
    if cashback_flow == 'charge':
        return '60'
    return None


@pytest.mark.parametrize(
    'payment_type, cashback_flows, available_for_checkout',
    [
        ('card', ['gain', 'charge'], True),
        ('corp', ['gain', 'charge'], False),
        ('unknown', ['gain'], True),
        ('unknown', ['charge'], False),
    ],
)
async def test_bad_payment_method_types(
        cart,
        payment_type,
        cashback_flows,
        available_for_checkout,
        grocery_p13n,
):
    payment_available = True
    balance = 12345
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    for cashback_flow in cashback_flows:
        cart.unsubscribe()

        await cart.init(['test_item'])

        await cart.set_payment(payment_type)
        await cart.set_cashback_flow(flow=cashback_flow)

        response = await cart.checkout(
            cashback_to_pay=_cashback_to_pay(cashback_flow),
        )

        if available_for_checkout:
            assert 'checkout_unavailable_reason' not in response
        else:
            reason = response['checkout_unavailable_reason']
            assert reason == 'cashback-flow-not-allowed'


@pytest.mark.parametrize(
    'balance, available_for_checkout', [('100', True), ('50', False)],
)
async def test_cashback_low_balance(
        taxi_grocery_cart, cart, balance, available_for_checkout, grocery_p13n,
):
    payment_available = True
    await cart.init(['test_item'])

    await taxi_grocery_cart.invalidate_caches()

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(flow='charge')
    await cart.set_payment('card')

    response = await cart.checkout(cashback_to_pay='60')

    if available_for_checkout:
        assert 'checkout_unavailable_reason' not in response
    else:
        assert (
            response['checkout_unavailable_reason'] == 'cashback-low-balance'
        )


@pytest.mark.parametrize('flow', ['charge', 'gain'])
async def test_cashback_exp_disabled_during_checkout(
        taxi_grocery_cart, cart, flow, grocery_p13n,
):
    payment_available = True
    balance = 200
    await cart.init(['test_item'])

    await taxi_grocery_cart.invalidate_caches()

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(flow)
    await cart.set_payment('card')

    grocery_p13n.remove_cashback_info()

    cashback_to_pay = None
    if flow == 'charge':
        cashback_to_pay = '60'
    response = await cart.checkout(cashback_to_pay=cashback_to_pay)

    assert (
        response['checkout_unavailable_reason'] == 'cashback-flow-not-allowed'
    )

    await cart.set_cashback_flow(flow='disabled')
    response = await cart.checkout()
    assert 'checkout_unavailable_reason' not in response


async def test_payment_disabled_during_checkout(
        taxi_grocery_cart, cart, grocery_p13n,
):
    payment_available = False
    balance = 12345
    await cart.init(['test_item'])
    await taxi_grocery_cart.invalidate_caches()

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(flow='charge')
    await cart.set_payment('card')

    grocery_p13n.remove_cashback_info()
    response = await cart.checkout(cashback_to_pay='60')

    assert (
        response['checkout_unavailable_reason'] == 'cashback-flow-not-allowed'
    )

    await cart.set_cashback_flow(flow='disabled')
    response = await cart.checkout()
    assert 'checkout_unavailable_reason' not in response


async def test_gain_cashback_with_cashback_to_pay(cart, grocery_p13n):
    payment_available = True
    balance = 200
    await cart.init(['test_item'])

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(flow='gain')
    await cart.set_payment('card')

    response = await cart.checkout(
        cashback_to_pay='60', required_status_code=400,
    )
    assert response['code'] == 'BAD_CASHBACK_USAGE'


async def test_checkout_data(cart, grocery_p13n, pgsql):
    payment_available = True
    balance = 200
    await cart.init(['test_item'])

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(flow='charge')
    await cart.set_payment('card')

    cashback_to_pay = '60'
    await cart.checkout(cashback_to_pay=cashback_to_pay)

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'SELECT cashback_to_pay FROM cart.checkout_data WHERE cart_id = %s',
        [cart.cart_id],
    )
    result = cursor.fetchone()
    assert result

    cashback_to_pay_pg = result[0]
    assert cashback_to_pay_pg == decimal.Decimal(cashback_to_pay)


@pytest.mark.parametrize('cart_cashback_gain', [None, 77])
@pytest.mark.parametrize('cashback_flow', [None, 'gain', 'charge'])
async def test_checkout_cart_cashback_gain(
        cart,
        grocery_p13n,
        overlord_catalog,
        pgsql,
        cashback_flow,
        cart_cashback_gain,
):
    item_id = 'item-id'
    price = 123
    overlord_catalog.add_product(product_id=item_id, price=str(price))

    payment_available = True
    balance = 123
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    if cart_cashback_gain is not None:
        grocery_p13n.add_cart_modifier(
            steps=[('10', str(cart_cashback_gain))], payment_rule='gain_value',
        )

    await cart.modify(products={item_id: {'q': '1', 'p': price}})
    await cart.set_payment('card')
    if cashback_flow is not None:
        await cart.set_cashback_flow(flow=cashback_flow)
    cashback_to_pay = None
    if cashback_flow == 'charge':
        cashback_to_pay = '10'
    await cart.checkout(cashback_to_pay=cashback_to_pay)

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'SELECT cart_cashback_gain FROM cart.checkout_data WHERE cart_id = %s',
        [cart.cart_id],
    )
    result = cursor.fetchone()
    assert result

    cart_cashback_gain_from_pg = result[0]
    if cashback_flow == 'gain' and cart_cashback_gain is not None:
        assert cart_cashback_gain == cart_cashback_gain_from_pg
    else:
        assert cart_cashback_gain_from_pg is None


@pytest.mark.parametrize('cashback_percent', [None, 7, 10])
@pytest.mark.parametrize('cashback_flow', [None, 'gain', 'charge'])
async def test_checkout_cashback_on_cart_percent(
        cart,
        grocery_p13n,
        overlord_catalog,
        pgsql,
        experiments3,
        cashback_percent,
        cashback_flow,
):
    item_id = 'item-id'
    price = 123

    if cashback_percent:
        experiments.grocery_cashback_percent(
            experiments3, enabled=True, value=str(cashback_percent),
        )
    else:
        experiments.grocery_cashback_percent(experiments3, enabled=False)

    overlord_catalog.add_product(product_id=item_id, price=str(price))

    payment_available = True
    balance = 123
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify(products={item_id: {'q': '1', 'p': price}})
    await cart.set_payment('card')
    if cashback_flow is not None:
        await cart.set_cashback_flow(flow=cashback_flow)
    cashback_to_pay = None
    if cashback_flow == 'charge':
        cashback_to_pay = '10'
    await cart.checkout(cashback_to_pay=cashback_to_pay)

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'SELECT cashback_on_cart_percent FROM cart.checkout_data'
        ' WHERE cart_id = %s',
        [cart.cart_id],
    )
    result = cursor.fetchone()
    assert result

    cashback_on_cart_percent = result[0]
    if cashback_flow == 'gain' and cashback_percent is not None:
        assert cashback_on_cart_percent == cashback_percent
    else:
        assert cashback_on_cart_percent is None


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'cashback_flow, cashback_to_pay',
    [('charge', '50'), ('gain', None), ('disabled', None)],
)
async def test_checkout_cashback_grocery_order(
        taxi_grocery_cart, cart, grocery_p13n, cashback_flow, cashback_to_pay,
):
    payment_available = True
    balance = 12345
    await cart.init(['test_item'])
    await taxi_grocery_cart.invalidate_caches()

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.set_cashback_flow(cashback_flow)
    await cart.set_payment('card')

    response = await cart.checkout(
        cashback_to_pay=cashback_to_pay,
        grocery_flow_version='grocery_flow_v1',
    )

    assert 'checkout_unavailable_reason' not in response
    assert response['cashback_flow'] == cashback_flow
