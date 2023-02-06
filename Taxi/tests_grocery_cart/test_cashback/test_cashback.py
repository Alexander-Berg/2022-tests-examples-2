# pylint: disable=too-many-lines
import math

from grocery_mocks import grocery_p13n as modifiers  # pylint: disable=E0401
import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_eats_promocodes


@pytest.mark.parametrize(
    'payment_available, availability_type',
    [(True, None), (False, 'buy_plus'), (False, 'charge_disabled')],
)
@pytest.mark.parametrize('balance', [100500, 50])
async def test_charge_cashback_availability(
        overlord_catalog,
        cart,
        payment_available,
        balance,
        grocery_p13n,
        availability_type,
):
    """ if payment_available then available_for_payment should be
    min(balance, total_price - total_items_quantity) """

    products = {
        'item-id-1': {'q': 1, 'p': 165.5},
        'item-id-2': {'q': 2, 'p': 50},
    }
    expected_available_for_payment = 0
    for key, value in products.items():
        price, quantity = value['p'], value['q']
        overlord_catalog.add_product(product_id=key, price=str(price))
        expected_available_for_payment += (
            math.floor(price) * quantity - quantity
        )
    expected_available_for_payment = min(
        balance, expected_available_for_payment,
    )
    grocery_p13n.set_cashback_info_response(
        payment_available,
        balance=balance,
        availability_type=availability_type,
    )

    response = await cart.modify(products=products)
    response_cashback = response['cashback']
    assert response_cashback['available_for_payment'] == str(
        expected_available_for_payment,
    )
    assert 'availability' not in response_cashback
    if payment_available:
        assert 'charge_availability' not in response_cashback
    elif payment_available is False:
        assert (
            response_cashback['charge_availability']['type']
            == availability_type
        )
    else:
        assert False


# item_price: 50, quantity: 3
@pytest.mark.parametrize(
    'balance,promocode,available_for_payment',
    [
        (
            100500,
            100,
            150  # total
            - 100  # promocode
            - 3,  # quantity * min_item_price(=1 rub)
        ),
        (
            30,
            100,
            30,  # 150 - 100 - 3 > balance(=30),
            # so available_for_payment = balance
        ),
        (30, 1000, 0),  # 100% promocode case
    ],
)
async def test_available_for_payment_with_promocode(
        overlord_catalog,
        cart,
        balance,
        mockserver,
        promocode,
        available_for_payment,
        grocery_coupons,
        grocery_p13n,
):
    """ if promocode is enabled then available_for_payment should be
    min(balance, total_price - promo_code_discount - total_items_quantity) """

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        return mock_eats_promocodes.discount_payload(discount=promocode)

    item_id = 'item-id'
    price = 50
    quantity = 3
    payment_available = True

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify(products={item_id: {'q': quantity, 'p': price}})

    response = await cart.apply_promocode('LAVKA100')
    assert mock_validate.times_called == 1

    cashback = response['cashback']
    assert cashback['available_for_payment'] == str(available_for_payment)


@pytest.mark.parametrize(
    'flow, available_for_checkout',
    [('gain', False), ('charge', False), ('disabled', True)],
)
async def test_zero_cart_total_price(
        overlord_catalog,
        cart,
        mockserver,
        flow,
        available_for_checkout,
        grocery_coupons,
        grocery_p13n,
):
    promocode_discount = 10000

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        return mock_eats_promocodes.discount_payload(
            discount=promocode_discount,
        )

    item_id = 'item-id'
    price = 50
    quantity = 3
    payment_available = True
    balance = '100'

    # 100% promocode
    assert price * quantity < promocode_discount

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    await cart.modify(products={item_id: {'q': quantity, 'p': price}})

    await cart.set_cashback_flow(flow)
    response = await cart.apply_promocode('LAVKA100')
    assert mock_validate.times_called == 1

    cashback = response['cashback']
    assert cashback['availability'] == {
        'disabled_reason': 'Кэшбэк не работает при 100% промокоде',
        'type': 'cart_zero_total_price',
    }

    assert response['available_for_checkout'] == available_for_checkout
    if not available_for_checkout:
        assert (
            response['checkout_unavailable_reason']
            == 'cashback-flow-not-allowed'
        )


@pytest.mark.parametrize('balance', [100500, 50])
async def test_available_for_payment_delivery(
        overlord_catalog,
        cart,
        balance,
        grocery_p13n,
        offers,
        experiments3,
        grocery_surge,
):
    """ available_for_payment should not be affected by paid delivery """
    delivery_cost = '100'
    delivery = {
        'cost': delivery_cost,
        'next_cost': delivery_cost,
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
        delivery=delivery,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price}},
    )

    total_price = price * quantity
    available_for_payment = min(balance, total_price - quantity)

    assert 'charge_availability' not in response['cashback']
    assert 'availability' not in response['cashback']
    assert response['cashback']['available_for_payment'] == str(
        available_for_payment,
    )


async def test_cashback_localizations(grocery_p13n, cart):
    payment_available = True
    balance = 100500
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify(products={})
    assert 'charge_full_cart_price_with_cashback' in response['l10n']
    assert (
        response['l10n']['charge_full_cart_price_with_cashback']
        == 'Вы платите за каждый товар по 1 $SIGN$$CURRENCY$'
    )


@pytest.mark.now(keys.TS_NOW)
async def test_cashback_localizations_paid_delivery(
        cart, grocery_p13n, experiments3, offers, grocery_surge,
):
    delivery_cost = '100'
    delivery = {
        'cost': delivery_cost,
        'next_cost': delivery_cost,
        'next_threshold': '9999999',
    }

    payment_available = True
    balance = 100500
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=delivery,
    )

    response = await cart.modify(products={})
    assert 'charge_full_cart_price_with_cashback' in response['l10n']
    assert (
        response['l10n']['charge_full_cart_price_with_cashback']
        == 'Вы платите за каждый товар по 1 $SIGN$$CURRENCY$ и '
        + delivery_cost
        + ' $SIGN$$CURRENCY$ за доставку'
    )


async def test_no_cashback_payment_for_corp(
        overlord_catalog, cart, grocery_p13n, experiments3,
):
    """ for corp payment method payment_available should be false
    and payment_available should be False, also
    incompatible_payment_method error should be present in availability """
    item_id = 'item-id'
    price = 165
    quantity = 1
    balance = 100500
    payment_available = True

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price}},
    )
    assert 'cashback' in response

    response = await cart.set_payment('corp')

    total_price = price * quantity
    available_for_payment = min(balance, total_price - quantity)
    assert response['cashback']['available_for_payment'] == str(
        available_for_payment,
    )
    assert response['cashback']['availability'] == {
        'type': 'incompatible_payment_method',
        'disabled_reason': 'Несовместимый метод оплаты',
    }


async def test_no_cashback_payment_for_incomplement_type(
        overlord_catalog, cart, grocery_p13n,
):
    """ for incomplement payment method payment_available should be false,
    incompatible_charge_payment_method error should be
    present in availability """
    item_id = 'item-id'
    price = 165
    quantity = 1
    balance = 100500
    payment_available = True

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price}},
    )
    assert 'cashback' in response

    response = await cart.set_payment('unknown')

    total_price = price * quantity
    available_for_payment = min(balance, total_price - quantity)
    assert response['cashback']['available_for_payment'] == str(
        available_for_payment,
    )
    assert response['cashback']['availability'] == {
        'type': 'incompatible_payment_method',
        'disabled_reason': 'Несовместимый метод оплаты',
    }


async def test_update_with_cashback_basic(
        overlord_catalog, cart, grocery_p13n,
):
    item_id = 'item_id_1'
    price = 100500
    cashback = 123
    payment_available = True
    balance = 100500

    overlord_catalog.add_product(
        product_id=item_id, price=str(price), in_stock='10',
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify(
        {item_id: {'q': 1, 'p': price, 'c': cashback}},
    )
    item = response['items'][0]
    assert item['price'] == str(price)
    assert item['cashback'] == str(cashback)

    items = cart.fetch_items()
    assert len(items) == 1
    assert items[0].cashback == cashback


async def test_accepted_differ_from_overlord_cashback(
        overlord_catalog, cart, grocery_p13n,
):
    item_id = 'item_id_1'
    price = 100500
    accepted_cashback = 123
    overlord_cashback = 456
    payment_available = True
    balance = 100500

    overlord_catalog.add_product(
        product_id=item_id, price=str(price), in_stock='10',
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(overlord_cashback),
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )

    response = await cart.modify(
        {item_id: {'q': 1, 'p': price, 'c': accepted_cashback}},
    )
    _check_diff(response, accepted_cashback, overlord_cashback, item_id)

    items = cart.fetch_items()
    assert len(items) == 1
    assert items[0].cashback == accepted_cashback
    assert response['checkout_unavailable_reason'] == 'cashback-mismatch'


async def test_no_cashback_for_corp(
        overlord_catalog,
        cart,
        grocery_p13n,
        offers,
        experiments3,
        grocery_surge,
):
    """ corp payment method disables cashback """
    item_id = 'item_id_1'
    price = 165
    quantity = 1
    cashback = 100
    payment_available = True
    balance = 100500

    overlord_catalog.add_product(product_id=item_id, price=str(price))

    common.create_offer(
        offers, experiments3, grocery_surge, offer_id='some_offer_id',
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(cashback),
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': cashback}},
    )
    assert 'cashback' in response
    assert response['cashback']['amount_to_gain'] == str(cashback)

    response = await cart.set_payment('corp')
    assert response['cashback']['amount_to_gain'] == '0'
    _check_diff(response, cashback, 0, item_id)

    response = await cart.modify(
        products={item_id: {'q': 0, 'p': price, 'c': cashback}},
    )
    assert response['cashback']['amount_to_gain'] == '0'

    # With cashback in request
    response = await cart.modify(
        products={item_id: {'q': 1, 'p': price, 'c': cashback}},
    )
    assert response['cashback']['amount_to_gain'] == '0'
    _check_diff(response, cashback, 0, item_id)

    # Without cashback in request
    response = await cart.modify(products={item_id: {'q': 1, 'p': price}})
    assert response['cashback']['amount_to_gain'] == '0'
    assert not response['diff_data']
    assert (
        response.get('checkout_unavailable_reason', '') == ''
    ), 'Test for LAVKABACKEND-3468'


async def test_cashback_experiment_disabled(
        overlord_catalog, cart, grocery_p13n,
):
    item_id = 'item_id_1'
    price = 165
    quantity = 1
    cashback = 100
    payment_available = True
    balance = 100500

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(cashback),
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': cashback}},
    )
    assert 'cashback' in response
    assert response['cashback']['amount_to_gain'] == str(cashback)

    overlord_catalog.remove_product(item_id)
    overlord_catalog.add_product(product_id=item_id, price=str(price))

    grocery_p13n.remove_cashback_info()

    grocery_p13n.clear_modifiers()
    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': cashback}},
    )
    response = await cart.set_payment('corp')

    assert 'cashback' not in response
    assert response['checkout_unavailable_reason'] == 'cashback-mismatch'
    _check_diff(response, cashback, 0, item_id)


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 1},
        'ILS': {'__default__': 0.1},
    },
)
@pytest.mark.parametrize(
    'cashback, quantity, currency, expected_cashback',
    [
        ([10], [5], 'RUB', '50'),
        ([10], [5], 'ILS', '50'),
        ([12.3, 4.56], [2, 3], 'RUB', '41'),
        ([12.3, 4.56], [2, 3], 'ILS', '38.4'),
    ],
)
async def test_cashback_amount_to_gain(
        overlord_catalog,
        grocery_p13n,
        cart,
        grocery_depots,
        cashback,
        quantity,
        currency,
        expected_cashback,
):
    """ amount_to_gain should be sum cashback[i] * quantity[i] """

    assert len(cashback) == len(quantity)

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ, currency=currency,
    )

    payment_available = True
    balance = 100500
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    items_price = 165
    products = {}
    for i, item_cashback in enumerate(cashback):
        item_id = 'item-' + str(i)
        products[item_id] = {
            'q': quantity[i],
            'p': items_price,
            'c': cashback[i],
        }
        overlord_catalog.add_product(
            product_id=item_id, price=str(items_price),
        )
        grocery_p13n.add_modifier(
            product_id=item_id,
            value=str(item_cashback),
            payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
        )

    response = await cart.modify(products=products)

    assert 'cashback' in response
    assert response['cashback']['amount_to_gain'] == expected_cashback


async def test_cart_cashback_gain(overlord_catalog, cart, grocery_p13n):
    price = 165
    item_id = 'item_id'
    overlord_catalog.add_product(product_id=item_id, price=str(price))
    payment_available = True
    balance = 100500
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )
    expected_cashback = 0
    grocery_p13n.add_cart_modifier(
        steps=[('100', '50')], payment_rule='gain_value',
    )
    expected_cashback += 50
    grocery_p13n.add_cart_modifier(
        steps=[('100', '10')], payment_rule='gain_percent',
    )
    expected_cashback += math.ceil(price * 0.1)
    products = {}
    products['item_id'] = {'q': 1, 'p': price, 'c': 0}

    response = await cart.modify(products=products)
    assert response['available_for_checkout']
    assert 'cashback' in response
    assert response['cashback']['amount_to_gain'] == str(expected_cashback)


@pytest.mark.parametrize('cart_cashback_gain', [None, 77])
@pytest.mark.parametrize('cashback_percent', [None, 7, 10])
@pytest.mark.now(keys.TS_NOW)
async def test_cashback_on_cart(
        overlord_catalog,
        cart,
        grocery_p13n,
        cashback_percent,
        cart_cashback_gain,
        experiments3,
        offers,
        grocery_surge,
):
    delivery_cost = 100
    delivery = {
        'cost': str(delivery_cost),
        'next_cost': str(delivery_cost),
        'next_threshold': '9999999',
    }

    item_id = 'item-id'
    price = 165
    item_cashback = 10
    quantity = 2
    total_price = price * quantity + delivery_cost
    payment_available = True
    balance = 100500

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=delivery,
    )

    expected_cashback = item_cashback * quantity
    if cashback_percent is not None:
        experiments.grocery_cashback_percent(
            experiments3, enabled=True, value=str(cashback_percent),
        )
        expected_cashback += math.ceil(total_price * cashback_percent / 100)
    else:
        experiments.grocery_cashback_percent(experiments3, enabled=False)

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(item_cashback),
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )
    if cart_cashback_gain is not None:
        grocery_p13n.add_cart_modifier(
            steps=[('10', str(cart_cashback_gain))], payment_rule='gain_value',
        )
        expected_cashback += cart_cashback_gain

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': item_cashback}},
    )

    assert 'cashback' in response
    assert response['cashback']['amount_to_gain'] == str(expected_cashback)


async def test_eats_flow_version_gain(cart, grocery_p13n):
    item_id = 'item-id-123'
    cashback = '10'
    price = '100'
    discount_price = '90'
    quantity = '2'
    payment_available = True
    balance = 100500

    grocery_p13n.add_modifier(
        product_id=item_id, value=str(int(price) - int(discount_price)),
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value=cashback,
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify({item_id: {'p': price, 'q': quantity}})
    assert response['order_flow_version'] == 'eats_core'

    response = await cart.set_cashback_flow('gain')
    # after set-cashback-flow only eats-payments
    assert response['order_flow_version'] == 'eats_payments'

    response = await cart.modify(
        {item_id: {'p': price, 'q': quantity, 'c': cashback}},
    )
    assert response['order_flow_version'] == 'eats_payments'

    # no changes after set-cashback-flow
    response = await cart.modify({item_id: {'p': price, 'q': quantity}})
    assert response['order_flow_version'] == 'eats_payments'


async def test_eats_flow_version_charge(cart, grocery_p13n):
    item_id = 'item-id-123'
    cashback = '10'
    price = '100'
    discount_price = '90'
    quantity = '2'
    payment_available = True
    balance = 100500

    grocery_p13n.add_modifier(
        product_id=item_id, value=str(int(price) - int(discount_price)),
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value=cashback,
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    response = await cart.modify({item_id: {'p': price, 'q': quantity}})
    assert response['order_flow_version'] == 'eats_core'

    response = await cart.set_cashback_flow('charge')
    assert response['order_flow_version'] == 'eats_payments'

    response = await cart.modify(
        {item_id: {'p': price, 'q': quantity, 'c': cashback}},
    )
    assert response['order_flow_version'] == 'eats_payments'

    response = await cart.modify({item_id: {'p': price, 'q': quantity}})
    assert response['order_flow_version'] == 'eats_payments'


async def test_eats_flow_version_disabled_grocery_cashback_exp(
        cart, grocery_p13n,
):
    item_id = 'item-id-123'
    cashback = '10'
    price = '100'
    discount_price = '90'
    quantity = '2'

    grocery_p13n.add_modifier(
        product_id=item_id, value=str(int(price) - int(discount_price)),
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value=cashback,
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )
    response = await cart.modify({item_id: {'p': price, 'q': quantity}})
    assert response['order_flow_version'] == 'eats_core'

    response = await cart.modify(
        {item_id: {'p': price, 'q': quantity, 'c': cashback}},
    )
    assert response['order_flow_version'] == 'eats_core'


@pytest.mark.parametrize('eats_payments_enabled', [True, False])
async def test_eats_flow_version_by_eats_payments_exp(
        cart, experiments3, eats_payments_enabled, grocery_p13n,
):
    item_id = 'item-id-123'
    price = '100'
    discount_price = '90'
    quantity = '2'

    grocery_p13n.add_modifier(
        product_id=item_id, value=str(int(price) - int(discount_price)),
    )
    experiments.eats_payments_flow(experiments3, enabled=eats_payments_enabled)

    response = await cart.modify({item_id: {'p': price, 'q': quantity}})

    if eats_payments_enabled:
        assert response['order_flow_version'] == 'eats_payments'
    else:
        assert response['order_flow_version'] == 'eats_core'


@pytest.mark.parametrize('cashback_flow', ['gain', 'charge'])
async def test_eats_flow_version_after_disabled(
        cart, grocery_p13n, cashback_flow,
):
    item_id = 'item-id-123'
    cashback = '10'
    price = '100'
    discount_price = '90'
    quantity = '2'
    payment_available = True
    balance = 100500

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id, value=str(int(price) - int(discount_price)),
    )
    await cart.modify({item_id: {'p': price, 'q': quantity}})
    response = await cart.set_cashback_flow(cashback_flow)

    assert response['order_flow_version'] == 'eats_payments'

    response = await cart.modify(
        {item_id: {'p': price, 'q': quantity, 'c': cashback}},
    )
    assert response['order_flow_version'] == 'eats_payments'

    response = await cart.set_cashback_flow('disabled')
    assert response['order_flow_version'] == 'eats_payments'


@pytest.mark.parametrize(
    'catalog_availability_type, cart_availability_type, disabled_reason',
    [
        ('buy_plus', 'buy_plus', 'Подключите Яндекс Плюс'),
        ('some_other', 'charge_disabled', 'Потому что можем'),
    ],
)
async def test_availability_type_forwarding_personal_walled_false(
        overlord_catalog,
        cart,
        catalog_availability_type,
        cart_availability_type,
        disabled_reason,
        grocery_p13n,
):
    item_id = 'item-id'
    price = 100
    quantity = 1
    balance = 123

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    if catalog_availability_type != 'some_other':
        grocery_p13n.set_cashback_info_response(
            payment_available=False,
            balance=balance,
            availability_type=catalog_availability_type,
        )
        response = await cart.modify(
            products={item_id: {'q': quantity, 'p': price}},
        )
        assert response['cashback']['charge_availability'] == {
            'type': cart_availability_type,
            'disabled_reason': disabled_reason,
        }


def _check_diff(response, previous_value, actual_value, item_id):
    if actual_value > previous_value:
        trend = 'increase'
    else:
        trend = 'decrease'
    diff = response['diff_data']['products']
    assert len(diff) == 1
    diff = diff[0]
    cashback_diff = {
        'actual_value': str(actual_value),
        'diff': str(abs(actual_value - previous_value)),
        'previous_value': str(previous_value),
        'trend': trend,
    }
    assert diff == {'cashback': cashback_diff, 'product_id': item_id}
    assert response['diff_data']['cart_total_cashback'] == cashback_diff


@pytest.mark.parametrize(
    'cashback_balance, expected_flag',
    [('1000', True), ('99', True), ('98', False), ('0', False)],
)
async def test_cashback_enough_for_full_payment(
        overlord_catalog, cart, cashback_balance, expected_flag, grocery_p13n,
):
    item_id = 'item-id'
    price = 100
    quantity = 1
    payment_available = False

    overlord_catalog.add_product(product_id=item_id, price=str(price))
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=cashback_balance,
    )

    response = await cart.modify(
        products={item_id: {'q': quantity, 'p': price}},
    )
    assert response['cashback']['full_payment'] == expected_flag


@pytest.mark.parametrize(
    'cashback_info, cashback_flow',
    [('(f,,1230.0000)', 'gain'), ('(t,10.0000,1230.0000)', 'charge')],
)
async def test_checkout_cashback_info(
        overlord_catalog,
        cart,
        grocery_p13n,
        cashback_info,
        cashback_flow,
        pgsql,
):
    item_id = 'item-id'
    price = 100
    quantity = 1
    payment_available = False
    cashback_balance = 1230

    overlord_catalog.add_product(product_id=item_id, price=str(price))

    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=cashback_balance,
    )

    await cart.modify(products={item_id: {'q': quantity, 'p': price}})

    payment_type = 'card'

    await cart.set_payment(payment_type)
    await cart.set_cashback_flow(flow=cashback_flow)

    cashback_to_pay = None
    headers = None

    if cashback_flow == 'charge':
        cashback_to_pay = '10'
        headers = common.CASHBACK_HEADERS

    await cart.checkout(cashback_to_pay=cashback_to_pay, headers=headers)

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'SELECT cashback FROM cart.checkout_data WHERE cart_id = %s',
        [cart.cart_id],
    )
    result = cursor.fetchone()
    assert result

    cashback = result[0]

    if cashback_info is not None:
        assert cashback == cashback_info
    else:
        assert cashback is None


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 1},
        'ILS': {'__default__': 0.1},
    },
)
@pytest.mark.parametrize(
    'currency, balance, expected_available_for_payment',
    [
        ('RUB', 100500, '421'),
        ('RUB', 420, '420'),
        ('ILS', 100500, '423.7'),
        ('ILS', 423.6, '423.6'),
    ],
)
async def test_rounding_available_for_payment(
        overlord_catalog,
        cart,
        grocery_p13n,
        grocery_depots,
        currency,
        balance,
        expected_available_for_payment,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ, currency=currency,
    )

    grocery_p13n.set_cashback_info_response(
        payment_available=True, balance=balance,
    )

    # items prices will also be rounded according to CURRENCY_ROUNDING_RULES
    products = {'item-1': {'q': 3, 'p': 123.4}, 'item-2': {'q': 5, 'p': 12.3}}
    for item_id, item in products.items():
        overlord_catalog.add_product(product_id=item_id, price=str(item['p']))

    response = await cart.modify(products=products)
    response_cashback = response['cashback']

    # expected_available_for_payment = cart_price - cart_items_count
    assert (
        response_cashback['available_for_payment']
        == expected_available_for_payment
    )
    assert 'availability' not in response_cashback
    assert 'charge_availability' not in response_cashback
