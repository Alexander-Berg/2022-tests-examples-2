import copy

import pytest

from tests_grocery_cart import common

HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-Uid': '555',
    'X-YaTaxi-PhoneId': 'phone_id',
}

PROMOCODE_WITH_EXCLUDED_CATEGORY = {
    'valid': True,
    'promocode_info': {
        'currency_code': 'RUB',
        'format_currency': True,
        'value': '400',
        'type': 'fixed',
        'series_purpose': 'support',
        'excluded_discounts': [
            {'discount_category': 'test_discount_category'},
        ],
    },
}

COUPON_LIST_PROMOCODE = [
    {
        'valid': True,
        'promocode': 'lavka300',
        'excluded_discounts': [
            {'discount_category': 'test_discount_category'},
        ],
    },
]

ITEM_PRICE = 2000
PROMOCODE_VALUE = 400
DISCOUNT_VALUE = 200

PRICE_WITH_PROMOCODE = ITEM_PRICE - PROMOCODE_VALUE
PRICE_WITH_DISCOUNT = ITEM_PRICE - DISCOUNT_VALUE
PRICE_WITH_PROMOCODE_AND_DISCOUNT = (
    ITEM_PRICE - PROMOCODE_VALUE - DISCOUNT_VALUE
)


def format_sign_currency(price: int):
    return f'{price} $SIGN$$CURRENCY$'


def enable_excluded_discounts(enabled):
    def decorator(func):
        return pytest.mark.experiments3(
            name='grocery_enable_discount_exclusion',
            consumers=['grocery-cart'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'always',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
            default_value={'enabled': False},
            is_config=True,
        )(func)

    return decorator


def check_products_times_called(overlord_catalog, grocery_p13n):
    # one for update one for apply_promocode
    assert grocery_p13n.discount_modifiers_times_called == 2
    assert overlord_catalog.times_called() == 2


def add_discount(grocery_p13n):
    meta = {
        'discount_id': 'discount_id',
        'discount_category': 'test_discount_category',
    }

    grocery_p13n.add_cart_modifier(
        steps=[('0', str(DISCOUNT_VALUE))],
        payment_rule='discount_value',
        meta=meta,
    )


def composed(*decorators):
    def deco(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func

    return deco


EXCLUDED_DISCOUNTS_SETUP = composed(
    common.GROCERY_ORDER_FLOW_VERSION_CONFIG,
    common.GROCERY_ORDER_CYCLE_ENABLED,
    enable_excluded_discounts(enabled=True),
)


@enable_excluded_discounts(enabled=False)
@EXCLUDED_DISCOUNTS_SETUP
async def test_excluded_discounts_config_disabled(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'test_promocode_01'
    item_id = 'item_id_2'

    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))
    add_discount(grocery_p13n)

    grocery_coupons.set_check_response(
        response_body=PROMOCODE_WITH_EXCLUDED_CATEGORY,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )
    cart = await cart.apply_promocode(promocode, headers=HEADERS)

    assert cart['total_price_template'] == format_sign_currency(
        PRICE_WITH_PROMOCODE_AND_DISCOUNT,
    )
    assert grocery_coupons.check_times_called() == 1
    check_products_times_called(overlord_catalog, grocery_p13n)


@EXCLUDED_DISCOUNTS_SETUP
async def test_excluded_discounts(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'test_promocode_01'
    item_id = 'item_id_2'

    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))
    add_discount(grocery_p13n)

    grocery_coupons.set_check_response(
        response_body=PROMOCODE_WITH_EXCLUDED_CATEGORY,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )
    cart = await cart.apply_promocode(promocode, headers=HEADERS)

    assert cart['total_price_template'] == format_sign_currency(
        PRICE_WITH_PROMOCODE,
    )
    assert grocery_coupons.check_times_called() == 2

    check_products_times_called(overlord_catalog, grocery_p13n)


@EXCLUDED_DISCOUNTS_SETUP
async def test_excluded_discounts_invalid_promocode(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'test_promocode_01'
    item_id = 'item_id_2'
    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))

    add_discount(grocery_p13n)

    invalid_promocode = copy.deepcopy(PROMOCODE_WITH_EXCLUDED_CATEGORY)
    invalid_promocode['valid'] = False

    grocery_coupons.set_check_response(response_body=invalid_promocode)
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )
    cart = await cart.apply_promocode(promocode, headers=HEADERS)

    assert cart['total_price_template'] == format_sign_currency(
        PRICE_WITH_DISCOUNT,
    )
    assert grocery_coupons.check_times_called() == 1
    check_products_times_called(overlord_catalog, grocery_p13n)


@EXCLUDED_DISCOUNTS_SETUP
async def test_excluded_discounts_no_conflict(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'test_promocode_01'
    item_id = 'item_id_2'

    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))

    add_discount(grocery_p13n)

    different_category_promocode = copy.deepcopy(
        PROMOCODE_WITH_EXCLUDED_CATEGORY,
    )
    different_category_promocode['promocode_info']['excluded_discounts'] = [
        {'discount_category': 'different_discount_category'},
    ]

    grocery_coupons.set_check_response(
        response_body=different_category_promocode,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )
    cart = await cart.apply_promocode(promocode, headers=HEADERS)

    assert cart['total_price_template'] == format_sign_currency(
        PRICE_WITH_PROMOCODE_AND_DISCOUNT,
    )
    assert grocery_coupons.check_times_called() == 1
    check_products_times_called(overlord_catalog, grocery_p13n)


@EXCLUDED_DISCOUNTS_SETUP
async def test_promocode_list_discount_size_for_applied_promocode(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'LAVKA300'
    item_id = 'item_id_2'

    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))
    add_discount(grocery_p13n)

    grocery_coupons.set_check_response(
        response_body=PROMOCODE_WITH_EXCLUDED_CATEGORY,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )

    grocery_coupons.set_list_response(
        response_body={'coupons': COUPON_LIST_PROMOCODE},
    )
    grocery_coupons.check_list_request(
        cart_id=cart.cart_id,
        cart_version=cart.cart_version,
        cart_cost=str(PRICE_WITH_DISCOUNT),
        depot_id='0',
    )

    response = await cart.promocodes_list(
        headers=HEADERS, required_status=200, include_cart_info=True,
    )

    assert response['promocodes'][0] == {
        'promocode': 'lavka300',
        'valid': True,
    }

    await cart.apply_promocode(promocode, headers=HEADERS)
    grocery_coupons.check_list_request(
        cart_id=cart.cart_id,
        cart_version=cart.cart_version,
        cart_cost=str(PRICE_WITH_DISCOUNT),
        depot_id='0',
    )

    response = await cart.promocodes_list(
        headers=HEADERS, required_status=200, include_cart_info=True,
    )

    assert response['promocodes'][0] == {
        'error_message': (
            'Отменяет скидку ' + str(DISCOUNT_VALUE) + ' $SIGN$$CURRENCY$ на '
            'товары в корзине - вместе они не работают'
        ),
        'promocode': 'lavka300',
        'valid': True,
    }


@enable_excluded_discounts(enabled=False)
@EXCLUDED_DISCOUNTS_SETUP
async def test_promocode_list_disabled_config(
        taxi_grocery_cart,
        grocery_coupons,
        eats_promocodes,
        cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
):
    promocode = 'LAVKA300'
    item_id = 'item_id_2'

    overlord_catalog.add_product(product_id=item_id, price=str(ITEM_PRICE))
    add_discount(grocery_p13n)

    grocery_coupons.set_check_response(
        response_body=PROMOCODE_WITH_EXCLUDED_CATEGORY,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {item_id: {'q': 1, 'p': str(ITEM_PRICE)}}, headers=HEADERS,
    )

    grocery_coupons.set_list_response(
        response_body={'coupons': COUPON_LIST_PROMOCODE},
    )
    grocery_coupons.check_list_request(
        cart_id=cart.cart_id,
        cart_version=cart.cart_version,
        cart_cost=str(PRICE_WITH_DISCOUNT),
        depot_id='0',
    )

    await cart.apply_promocode(promocode, headers=HEADERS)
    grocery_coupons.check_list_request(
        cart_id=cart.cart_id,
        cart_version=cart.cart_version,
        cart_cost=str(PRICE_WITH_DISCOUNT),
        depot_id='0',
    )

    response = await cart.promocodes_list(
        headers=HEADERS, required_status=200, include_cart_info=True,
    )

    assert response['promocodes'][0] == {
        'promocode': 'lavka300',
        'valid': True,
    }
