import math

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_grocery_coupons

YANDEX_UID = '555'

HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-Uid': YANDEX_UID,
}

EXPECTED_WARNING_MESSAGE = (
    'Промокод дает скидку на все товары кроме алкоголя и медикаментов'
)


def _get_item_v2_description(item_id, price, paid_with_promocode):
    return {
        'info': {
            'item_id': item_id,
            'shelf_type': 'store',
            'title': 'title for ' + item_id,
            'vat': '20',
            'refunded_quantity': '0',
        },
        'sub_items': [
            {
                'item_id': item_id + '_0',
                'price': str(price),
                'paid_with_cashback': '0',
                'paid_with_promocode': str(paid_with_promocode),
                'full_price': str(keys.DEFAULT_PRICE),
                'quantity': '1',
            },
        ],
    }


def _add_products_overlord_catalog(overlord_catalog):
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )
    overlord_catalog.add_product(
        product_id='beer-item',
        price=str(keys.DEFAULT_PRICE),
        legal_restrictions=['RU_18+'],
    )
    overlord_catalog.add_product(
        product_id='medicine_id', price=str(keys.DEFAULT_PRICE),
    )


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'grocery': 0.01}},
    CURRENCY_FORMATTING_RULES={'RUB': {'grocery': 1}},
)
@experiments.DO_NOT_APPLY_PROMO
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'set_fail, response_body',
    [
        (False, {}),
        (True, mock_grocery_coupons.PROMO_CAN_BE_VALID),
        (True, mock_grocery_coupons.PROMO_ERROR_INVALID_CODE),
    ],
)
async def test_taxi_promocode(
        cart,
        overlord_catalog,
        set_fail,
        response_body,
        grocery_coupons,
        eats_promocodes,
):
    promocode = 'test_promocode_01'
    _add_products_overlord_catalog(overlord_catalog)

    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response_custom(value='30')

    response = await cart.modify(
        {
            'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'beer-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'medicine_id': {'q': 1, 'p': keys.DEFAULT_PRICE},
        },
        headers=HEADERS,
    )

    grocery_coupons.check_check_request(
        promocode=promocode,
        depot_id='0',
        cart_id=cart.cart_id,
        cart_version=2,
    )

    assert cart.cart_version == 1
    assert 'promocode' not in response

    response = await cart.apply_promocode(promocode, headers=HEADERS)
    assert cart.cart_version == 2

    assert grocery_coupons.check_times_called() == 1
    assert 'promocode' in response

    # check that promocode doesn't applied
    # to items from DO_NOT_APPLY_PROMO config
    assert response['promocode']['discount'] == '103.5'
    assert (
        response['promocode']['discount_template'] == '103,5 $SIGN$$CURRENCY$'
    )
    assert response['promocode']['warning_message'] == EXPECTED_WARNING_MESSAGE

    assert response['promocode']['discount_percent'] == '30'
    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode

    grocery_coupons.check_check_request()

    response = await cart.modify(
        {'test-item': {'q': 2, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )
    assert 'promocode' in response

    # check that promocode doesn't applied
    # to items from DO_NOT_APPLY_PROMO config
    assert response['promocode']['discount'] == '207'
    assert response['promocode']['discount_template'] == '207 $SIGN$$CURRENCY$'
    assert response['promocode']['warning_message'] == EXPECTED_WARNING_MESSAGE

    assert response['promocode']['discount_percent'] == '30'

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 3
    assert grocery_coupons.check_times_called() == 2

    if set_fail:
        grocery_coupons.set_check_response(response_body=response_body)

    grocery_coupons.check_check_request()
    await cart.modify(
        {'test-item': {'q': 3, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 4

    assert grocery_coupons.check_times_called() == 3


@experiments.DO_NOT_APPLY_PROMO
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
async def test_taxi_promocode_our_order_cycle(
        cart, overlord_catalog, grocery_coupons, eats_promocodes, grocery_p13n,
):
    eats_promocodes.set_valid(False)

    await cart.invalidate_caches()

    cart_item_id = 'test-item'
    _add_products_overlord_catalog(overlord_catalog)

    grocery_p13n.add_modifier(product_id=cart_item_id, value='100')

    promocode = 'fixed_400'
    grocery_coupons.set_check_response_custom(
        value='400', promocode_type='fixed',
    )

    response = await cart.modify(
        {
            cart_item_id: {'q': 1, 'p': keys.DEFAULT_PRICE},
            'beer-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'medicine_id': {'q': 1, 'p': keys.DEFAULT_PRICE},
        },
        headers=HEADERS,
    )
    assert cart.cart_version == 1
    assert grocery_coupons.check_times_called() == 0
    assert 'promocode' not in response
    assert response['order_flow_version'] == 'grocery_flow_v1'

    response = await cart.apply_promocode(promocode, headers=HEADERS)
    assert cart.cart_version == 2
    assert grocery_coupons.check_times_called() == 1
    assert 'promocode' in response
    assert 'discount_percent' not in response['promocode']
    assert response['order_flow_version'] == 'grocery_flow_v1'

    # check that promocode doesn't applied
    # to items from DO_NOT_APPLY_PROMO config
    assert response['promocode']['discount_template'] == '345 $SIGN$$CURRENCY$'
    assert response['promocode']['discount'] == '345'
    assert response['promocode']['warning_message'] == EXPECTED_WARNING_MESSAGE

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode

    response = await cart.modify(
        {cart_item_id: {'q': 2, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )
    assert 'promocode' in response
    assert response['order_flow_version'] == 'grocery_flow_v1'

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 3
    assert grocery_coupons.check_times_called() == 2


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'set_fail, response_code, response_body, promocode_valid,'
    'promocode_message',
    [
        (False, 200, {}, True, 'Не удалось применить данный промокод'),
        (
            True,
            200,
            mock_grocery_coupons.PROMO_CAN_BE_VALID,
            False,
            'Не удалось применить данный промокод',
        ),
        (
            True,
            200,
            mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
            False,
            'Промокод не найден',
        ),
        (
            True,
            200,
            mock_grocery_coupons.PROMO_ERROR_ALREADY_USED,
            False,
            'Промокод уже был использован',
        ),
        (
            True,
            200,
            mock_grocery_coupons.PROMO_ERROR_INVALID_CITY,
            False,
            'Не удалось применить данный промокод',
        ),
        (
            True,
            200,
            mock_grocery_coupons.PROMO_ERROR_NO_PAYMENT_METHOD,
            False,
            'Нужно выбрать способ оплаты',
        ),
    ],
)
async def test_taxi_invalid_promocode(
        cart,
        overlord_catalog,
        set_fail,
        response_code,
        response_body,
        promocode_valid,
        promocode_message,
        grocery_coupons,
        eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )
    assert cart.cart_version == 1

    grocery_coupons.set_check_response(
        status_code=response_code, response_body=response_body,
    )
    await cart.apply_promocode(promocode, headers=HEADERS)

    cart_data = cart.fetch_db()

    assert cart_data.promocode == promocode
    assert cart.cart_version == 2


@experiments.DO_NOT_APPLY_PROMO
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
async def test_cart_has_not_items_to_apply_promocode(
        cart, overlord_catalog, grocery_coupons, eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='beer-item',
        price=str(keys.DEFAULT_PRICE),
        legal_restrictions=['RU_18+'],
    )
    overlord_catalog.add_product(
        product_id='medicine_id', price=str(keys.DEFAULT_PRICE),
    )
    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response_custom(value='400')

    await cart.modify(
        {
            'beer-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'medicine_id': {'q': 1, 'p': keys.DEFAULT_PRICE},
        },
        headers=HEADERS,
    )
    await cart.apply_promocode(promocode, headers=HEADERS)

    cart_data = cart.fetch_db()

    assert cart_data.promocode == promocode
    assert cart.cart_version == 2


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'response_code, response_body',
    [
        (400, mock_grocery_coupons.ERROR_400),
        (429, mock_grocery_coupons.ERROR_429),
        (500, mock_grocery_coupons.ERROR_500),
    ],
)
async def test_taxi_coupons_service_failed(
        cart,
        overlord_catalog,
        response_code,
        response_body,
        grocery_coupons,
        eats_promocodes,
):
    grocery_coupons.set_check_response()
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )
    assert cart.cart_version == 1

    await cart.apply_promocode(promocode, headers=HEADERS)

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 2

    grocery_coupons.set_check_response(
        status_code=response_code, response_body=response_body,
    )
    await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 3


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'response_code, response_body',
    [
        (400, mock_grocery_coupons.ERROR_400),
        (429, mock_grocery_coupons.ERROR_429),
        (500, mock_grocery_coupons.ERROR_500),
    ],
)
async def test_taxi_coupons_service_not_works(
        cart,
        overlord_catalog,
        response_code,
        response_body,
        grocery_coupons,
        eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )
    grocery_coupons.set_check_response()
    eats_promocodes.set_valid(False)

    await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )
    assert cart.cart_version == 1

    grocery_coupons.set_check_response(
        status_code=response_code, response_body=response_body,
    )
    await cart.apply_promocode(promocode, headers=HEADERS)

    cart_data = cart.fetch_db()
    assert cart_data.promocode == promocode
    assert cart.cart_version == 2


@experiments.DO_NOT_APPLY_PROMO
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('use_grocery_flow_version', [True, False])
@pytest.mark.parametrize(
    'promocode_value, promocode_type', [('400', 'fixed'), ('30', 'percent')],
)
async def test_taxi_promocode_checkout_ok(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
        use_grocery_flow_version,
        promocode_value,
        promocode_type,
):
    promocode = 'test_promocode_01'
    _add_products_overlord_catalog(overlord_catalog)
    grocery_coupons.set_check_response_custom(
        value=promocode_value, promocode_type=promocode_type,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {
            'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'beer-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
            'medicine_id': {'q': 1, 'p': keys.DEFAULT_PRICE},
        },
        headers=HEADERS,
    )
    assert cart.cart_version == 1

    await cart.apply_promocode(promocode, headers=HEADERS)
    assert cart.cart_version == 2
    assert grocery_coupons.check_times_called() == 1

    if use_grocery_flow_version:
        await cart.checkout(
            headers=HEADERS, grocery_flow_version='grocery_flow_v1',
        )
    else:
        await cart.checkout(
            headers=HEADERS, order_flow_version='grocery_flow_v1',
        )

    internal_raw_response = await taxi_grocery_cart.post(
        '/internal/v1/cart/retrieve/raw', json={'cart_id': cart.cart_id},
    )
    internal_raw_body = internal_raw_response.json()

    # check that promocode doesn't applied
    # to items from DO_NOT_APPLY_PROMO config
    _expected_internal_raw_body_items = [
        _get_item_v2_description('beer-item', keys.DEFAULT_PRICE, '0'),
        _get_item_v2_description('medicine_id', keys.DEFAULT_PRICE, '0'),
    ]
    if promocode_type == 'fixed':
        _expected_internal_raw_body_items.append(
            _get_item_v2_description('test-item', '0', keys.DEFAULT_PRICE),
        )
    else:
        _expected_internal_raw_body_items.append(
            _get_item_v2_description('test-item', '241.5', '103.5'),
        )
    assert internal_raw_body['items_v2'] == _expected_internal_raw_body_items
    assert internal_raw_body['promocode_properties']['source'] == 'taxi'


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('has_promocode', [True, False])
async def test_promocode_available_checkout(
        cart,
        overlord_catalog,
        has_promocode,
        grocery_coupons,
        eats_promocodes,
):
    promocode = 'test_promocode_01'
    cart_item_id = 'test-item'
    overlord_catalog.add_product(
        product_id=cart_item_id, price=str(keys.DEFAULT_PRICE),
    )
    grocery_coupons.set_check_response_custom(value='400')
    eats_promocodes.set_valid(False)

    await cart.modify(
        {cart_item_id: {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    if has_promocode:
        await cart.apply_promocode(promocode, headers=HEADERS)

    await cart.checkout(headers=HEADERS, order_flow_version='grocery_flow_v1')


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
async def test_grocery_coupons_missing_error_message(
        cart, overlord_catalog, grocery_coupons, eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )

    grocery_coupons.set_check_response(response_body={'valid': False})
    eats_promocodes.set_valid(False)

    response = await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    assert 'promocode' not in response

    await cart.apply_promocode(promocode, headers=HEADERS)

    assert grocery_coupons.check_times_called() == 1


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
async def test_flow_by_promocode_source_eats(
        cart, overlord_catalog, grocery_coupons, eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )
    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    response = await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    assert 'promocode' not in response
    assert response['order_flow_version'] == 'grocery_flow_v3'

    response = await cart.apply_promocode(promocode, headers=HEADERS)

    assert grocery_coupons.check_times_called() == 1
    assert eats_promocodes.times_called() == 1

    assert response['promocode']['valid']


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
async def test_flow_by_promocode_source_taxi(
        cart, overlord_catalog, grocery_coupons, eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )

    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response_custom(value='400')

    response = await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    assert 'promocode' not in response
    assert response['order_flow_version'] == 'grocery_flow_v3'

    response = await cart.apply_promocode(promocode, headers=HEADERS)

    assert grocery_coupons.check_times_called() == 1
    assert eats_promocodes.times_called() == 1

    assert response['promocode']['valid']

    assert response['order_flow_version'] == 'grocery_flow_v1'


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
async def test_flow_by_promocode_source_priority_taxi(
        cart, overlord_catalog, grocery_coupons, eats_promocodes,
):
    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )

    eats_promocodes.set_valid(True)
    grocery_coupons.set_check_response_custom(value='400')

    response = await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    assert 'promocode' not in response
    assert response['order_flow_version'] == 'grocery_flow_v3'

    response = await cart.apply_promocode(promocode, headers=HEADERS)

    assert grocery_coupons.check_times_called() == 1
    assert eats_promocodes.times_called() == 1

    assert response['promocode']['valid']

    assert response['order_flow_version'] == 'grocery_flow_v1'


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('promocode_rounding_value', [5, 1, 0.1, 0.01])
async def test_taxi_promocode_rounding(
        cart,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
        experiments3,
        promocode_rounding_value,
):
    item_price = 153
    experiments.add_lavka_cart_prices_config(
        experiments3,
        currency_min_value='1',
        precision=1,
        minimum_total_cost='1',
        minimum_item_price='1',
        promocode_rounding_value=str(promocode_rounding_value),
    )

    _add_products_overlord_catalog(overlord_catalog)
    eats_promocodes.set_valid(False)

    await cart.modify(
        {'test-item': {'q': 1, 'p': item_price}}, headers=HEADERS,
    )
    assert cart.cart_version == 1

    expected_discount = (
        math.ceil(item_price * 0.1 / promocode_rounding_value)
        * promocode_rounding_value
    )

    grocery_coupons.set_check_response_custom(value='10')
    response = await cart.apply_promocode('percent_10', headers=HEADERS)
    assert response['promocode']['discount'] == str(expected_discount)


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'series_purpose', ['support', 'marketing', 'referral', 'referral_reward'],
)
async def test_promocode_series_purpose(
        cart,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
        series_purpose,
):
    promocode = 'test_promocode_01'
    cart_item_id = 'test-item'
    overlord_catalog.add_product(
        product_id=cart_item_id, price=str(keys.DEFAULT_PRICE),
    )
    grocery_coupons.set_check_response_custom(
        value='400', promocode_type='fixed', purpose=series_purpose,
    )
    eats_promocodes.set_valid(False)

    await cart.modify(
        {cart_item_id: {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    await cart.apply_promocode(promocode, headers=HEADERS)
