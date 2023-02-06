# pylint: disable=too-many-lines
import copy
import datetime
import decimal
import math
import uuid

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_p13n as modifiers
from metrics_aggregations import helpers as metrics_helpers
import pytest
import pytz

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_grocery_coupons

DATETIME_VALUE = datetime.datetime(
    2020,
    3,
    14,
    0,
    0,
    tzinfo=datetime.timezone(datetime.timedelta(minutes=180)),
)

TS_NOW = keys.TS_NOW
DEFAULT_VAT = keys.DEFAULT_VAT
DEFAULT_IDEMPOTENCY_TOKEN = 'checkout-token'

BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}

DEFAULT_HEADERS = {
    'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN,
    **BASIC_HEADERS,
}


@pytest.mark.now(TS_NOW)
async def test_basic(taxi_grocery_cart, cart, overlord_catalog, pgsql):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    client_price = '690'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock='2', logistic_tags=['cold'],
    )
    delivery_type = 'eats_dispatch'

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        cart={'id': cart.cart_id},
        delivery_type=delivery_type,
        delivery_cost='0',
        logistic_tags=['cold'],
    )
    assert overlord_catalog.times_called() == 2  # update + checkout

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    _check_items_extra_data(extra, item_id, price)
    assert cart_db == [{'cart_version': 1, 'status': 'checked_out'}]
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'depot_id': '0',
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': '(0.0000,,)',
            'promocode': None,
            'unavailable_checkout_reason': 'no_reason',
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': False,
        },
    ]

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_type=delivery_type,
        delivery_cost='0',
        logistic_tags=['cold'],
    )  # cached data
    assert overlord_catalog.times_called() == 2  # no more request to overlord


@pytest.mark.now(TS_NOW)
async def test_cart_not_found(taxi_grocery_cart):
    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': str(uuid.uuid4()),
        'cart_version': 1,
        'offer_id': 'test_offer_id',
    }
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )
    assert response.status_code == 404


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize('price, has_surge', [('300', True), ('400', False)])
async def test_order_conditions(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        price,
        has_surge,
        offers,
        experiments3,
        grocery_surge,
        umlaas_eta,
):
    item_id = 'item_id_1'
    quantity = 1
    delivery_type = 'eats_dispatch'

    next_delivery_threshold = '350'
    delivery_cost = '100'
    next_delivery_cost = '50'

    min_eta = 1
    max_eta = 2
    total_time = 3
    cooking_time = 2
    delivery_time = 1

    if int(price) < int(next_delivery_threshold):
        cur_delivery_cost = delivery_cost
    else:
        cur_delivery_cost = next_delivery_cost

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }
    common.create_offer(
        offers, experiments3, grocery_surge, offer_id='offer_id',
    )
    common.add_delivery_conditions(
        experiments3, delivery=actual_delivery, surge=has_surge,
    )

    umlaas_eta.add_prediction(
        min_eta,
        max_eta,
        total_time=total_time,
        cooking_time=cooking_time,
        delivery_time=delivery_time,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    requirements = {
        'sum_to_min_order': '0',
        'sum_to_min_order_template': _currency('0'),
    }
    if cur_delivery_cost != next_delivery_cost:
        sum_to_next_delivery = str(int(next_delivery_threshold) - int(price))
        requirements = {
            'next_delivery_cost': next_delivery_cost,
            'next_delivery_cost_template': _currency(next_delivery_cost),
            'next_delivery_threshold': next_delivery_threshold,
            'next_delivery_threshold_template': _currency(
                next_delivery_threshold,
            ),
            'sum_to_next_delivery': sum_to_next_delivery,
            'sum_to_next_delivery_template': _currency(sum_to_next_delivery),
            'sum_to_min_order': '0',
            'sum_to_min_order_template': _currency('0'),
        }

    client_price = str(int(price) * quantity + int(cur_delivery_cost))

    cart_response = {'id': cart.cart_id, 'requirements': requirements}
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_cost=cur_delivery_cost,
        cart=cart_response,
        delivery_type=delivery_type,
        max_eta=max_eta,
        min_eta=min_eta,
        total_time=total_time,
        cooking_time=cooking_time,
        delivery_time=delivery_time,
    )
    assert overlord_catalog.times_called() == 2  # update + checkout

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    _check_items_extra_data(extra, item_id, price)
    assert cart_db == [{'cart_version': 1, 'status': 'checked_out'}]
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'depot_id': '0',
            'order_conditions_with_eta': f'({cur_delivery_cost}.0000,2,1)',
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'promocode': None,
            'unavailable_checkout_reason': 'no_reason',
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': has_surge,
        },
    ]

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    # cached data
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_cost=cur_delivery_cost,
        delivery_type=delivery_type,
        min_eta=min_eta,
        max_eta=max_eta,
        total_time=total_time,
        cooking_time=cooking_time,
        delivery_time=delivery_time,
    )
    assert overlord_catalog.times_called() == 2  # no more request to overlord


@pytest.mark.now(TS_NOW)
async def test_markdown_products_delivery_unavailable(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id_1:st-md'
    quantity = 1
    price = '400'

    next_delivery_threshold = '350'
    delivery_cost = '100'
    next_delivery_cost = '50'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id',
        delivery=actual_delivery,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    try:
        await cart.modify({item_id: {'q': quantity, 'p': price}})
    except common.CartHttpError as exc:
        assert exc.status_code == 400
    else:
        assert False

    try:
        await cart.modify(
            {item_id: {'q': quantity, 'p': price}},
            delivery_type='eats_dispatch',
        )
    except common.CartHttpError as exc:
        assert exc.status_code == 400
    else:
        assert False

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 400


@pytest.mark.now(TS_NOW)
@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_markdown_products_delivery(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id_1:st-md'
    quantity = 1
    price = '400'
    delivery_type = 'pickup'

    next_delivery_threshold = '350'
    delivery_cost = '100'
    next_delivery_cost = '50'
    cur_delivery_cost = '0'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id',
        delivery=actual_delivery,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify(
        {item_id: {'q': quantity, 'p': price}},
        delivery_type='pickup',
        headers={'X-Yandex-Uid': '8484'},
    )

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={'X-Yandex-Uid': '8484', **DEFAULT_HEADERS},
        json=json,
    )
    assert response.status_code == 200

    # Delivery cost shouldn't change and stay 0
    cart_response = {'id': cart.cart_id, 'diff': {}}

    client_price = str(int(price) * quantity + int(cur_delivery_cost))

    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_cost=cur_delivery_cost,
        cart=cart_response,
        delivery_type=delivery_type,
    )
    assert overlord_catalog.times_called() == 2  # update + checkout

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    _check_items_extra_data(extra, item_id, price)
    assert cart_db == [{'cart_version': 1, 'status': 'checked_out'}]
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'depot_id': '0',
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': f'({cur_delivery_cost}.0000,,)',
            'promocode': None,
            'unavailable_checkout_reason': 'no_reason',
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': False,
        },
    ]

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={'X-Yandex-Uid': '8484', **DEFAULT_HEADERS},
        json=json,
    )

    assert response.status_code == 200
    # cached data
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_cost=cur_delivery_cost,
        delivery_type=delivery_type,
    )
    assert overlord_catalog.times_called() == 2  # no more request to overlord


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'valid,include_promocode', [(True, True), (False, False), (False, True)],
)
async def test_promocode_eats(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        mockserver,
        valid,
        include_promocode,
        grocery_coupons,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'
    client_price = '345'
    if valid:
        client_price = '245'
    delivery_type = 'eats_dispatch'

    promo_code = 'LAVKA1235'
    promocode_limit = '500'
    promocode_discount_type = 'fixed'
    promocode_discount = '100'
    promocode_discount_value = '200'

    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        assert request.json == {
            'code': promo_code,
            'user': {'id': '1234', 'idProvider': 'yandex'},
            'place': {'id': '0'},
            'paymentMethod': 'taxi',
            'applyForAmount': '345',
        }
        validation_response = {
            'payload': {'validationResult': {'valid': valid, 'message': '1'}},
        }
        if include_promocode:
            validation_response['payload']['validationResult']['promocode'] = {
                'discount': promocode_discount_value,
                'discountType': promocode_discount_type,
                'discountLimit': promocode_limit,
                'discountResult': promocode_discount,
            }
        return validation_response

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    assert overlord_catalog.times_called() == 1

    await cart.apply_promocode(
        promo_code, headers={'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN},
    )

    assert overlord_catalog.times_called() == 2
    assert mock_validate.times_called == 1

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert overlord_catalog.times_called() == 3
    assert mock_validate.times_called == 2

    assert response.status_code == 200
    promo = {'code': promo_code, 'valid': valid}
    cart_response = {'id': cart.cart_id, 'version': 2}

    discount = '0'
    if valid:
        discount = promocode_discount

    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        discount=discount,
        promo=promo,
        cart=cart_response,
        delivery_type=delivery_type,
        delivery_cost='0',
    )

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    _check_items_extra_data(extra, item_id, price)
    assert cart_db == [{'cart_version': 2, 'status': 'checked_out'}]

    promocode_properties = {'source': 'eats'}
    if include_promocode:
        promocode_properties['limit'] = promocode_limit
        promocode_properties['discount_value'] = promocode_discount_value

    expected_data = {
        'cart_id': cart.cart_id,
        'cart_version': 2,
        'depot_id': '0',
        'depot_status': 'available',
        'depot_switch_time': DATETIME_VALUE,
        'order_conditions_with_eta': '(0.0000,,)',
        'promocode': f'({_get_pg_flag(valid)},{promo_code})',
        'unavailable_checkout_reason': 'no_reason',
        'promocode_properties': promocode_properties,
        'promocode_discount': (
            decimal.Decimal(promocode_discount)
            if include_promocode
            else decimal.Decimal(0)
        ),
        'has_surge': False,
    }
    if include_promocode:
        expected_data['promocode_properties'][
            'discount_type'
        ] = promocode_discount_type
    assert data == [expected_data]

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    # cached data
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        discount=discount,
        promo=promo,
        delivery_type=delivery_type,
        delivery_cost='0',
    )
    assert overlord_catalog.times_called() == 3  # no more requests to overlord
    assert mock_validate.times_called == 2  # no more requests to promocode


@pytest.mark.now(TS_NOW)
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'expected_type, expected_purpose',
    [
        ('fixed', 'support'),
        ('percent', 'marketing'),
        ('percent', 'referral'),
        ('percent', 'referral_reward'),
    ],
)
async def test_promocode_properties_taxi(
        taxi_grocery_cart,
        cart,
        eats_promocodes,
        overlord_catalog,
        grocery_coupons,
        pgsql,
        mockserver,
        expected_type,
        expected_purpose,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'

    expected_value = '100'
    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response_custom(
        expected_value, expected_type, expected_purpose,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    assert overlord_catalog.times_called() == 1

    await cart.apply_promocode(
        'test_promocode',
        headers={'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN},
    )

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
    }

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={**DEFAULT_HEADERS, 'User-Agent': keys.DEFAULT_USER_AGENT},
        json=json,
    )
    assert response.status_code == 200

    assert grocery_coupons.check_times_called() == 2

    data = _fetch_data(pgsql, cart.cart_id)
    assert len(data) == 1

    assert data[0]['promocode_properties'] == {
        'discount_type': expected_type,
        'discount_value': expected_value,
        'series_purpose': expected_purpose,
        'source': 'taxi',
    }


# check that checkout_data timestamp is properly updated on checkouts
async def test_checkout_timestamp(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        taxi_grocery_cart_monitor,
        pgsql,
        now,
):
    item_id = 'item_id_1'
    bad_item_id = 'item_id_2'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')
    overlord_catalog.add_product(
        product_id=bad_item_id, price=price, in_stock='1',
    )

    await cart.modify(
        {
            item_id: {'q': quantity, 'p': price},
            bad_item_id: {'q': quantity, 'p': price},
        },
    )

    overlord_catalog.remove_product(product_id=bad_item_id)

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_cart_monitor,
            sensor='grocery_cart_unavailable_for_check_out_carts',
            labels={'country': 'Russia'},
    ) as collector:
        response = await taxi_grocery_cart.post(
            '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
        )

    assert response.status_code == 200
    _check_unavailable_for_check_out_carts(
        collector.get_single_collected_metric(),
        country_name='Russia',
        city_name='Moscow',
        depot_id='0',
        reason='quantity_over_limit',
    )
    assert (
        response.json()['checkout_unavailable_reason'] == 'quantity-over-limit'
    )

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    assert cart_db == [{'cart_version': 1, 'status': 'editing'}]

    checkout_ts1 = _fetch_checkout_data_updated(pgsql, cart.cart_id)
    assert _to_utc(checkout_ts1) >= now

    await cart.modify(
        {
            item_id: {'q': quantity, 'p': price},
            bad_item_id: {'q': 0, 'p': price},
        },
    )

    json['cart_version'] = cart.cart_version

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    assert response.json().get('checkout_unavailable_reason', 'none') == 'none'

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    assert cart_db == [{'cart_version': 2, 'status': 'checked_out'}]

    checkout_ts2 = _fetch_checkout_data_updated(pgsql, cart.cart_id)
    assert checkout_ts2 > checkout_ts1


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.now(TS_NOW)
async def test_promocode_not_valid(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'
    promocode = 'some_promocode'

    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    await cart.apply_promocode(promocode)

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'grocery_flow_version': 'grocery_flow_v1',
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.json()['code'] == 'PROMOCODE_NOT_APPLIED'
    assert grocery_coupons.check_times_called() > 0


@pytest.mark.now(TS_NOW)
async def test_reason(taxi_grocery_cart, cart, overlord_catalog, pgsql):
    item_id = 'item_id_1'
    bad_item_id = 'item_id_2'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')
    overlord_catalog.add_product(
        product_id=bad_item_id, price=price, in_stock='1',
    )

    await cart.modify(
        {
            item_id: {'q': quantity, 'p': price},
            bad_item_id: {'q': quantity, 'p': price},
        },
    )

    assert overlord_catalog.times_called() == 1

    overlord_catalog.remove_product(product_id=bad_item_id)

    response = await cart.checkout()
    assert overlord_catalog.times_called() == 2

    diff = {
        'products': [
            {
                'has_substitutions': False,
                'product_id': 'item_id_2',
                'quantity': {'actual_limit': '0', 'wanted': '1'},
            },
        ],
        'cart_total': {
            'actual_template': '345 $SIGN$$CURRENCY$',
            'diff_template': '345 $SIGN$$CURRENCY$',
            'previous_template': '690 $SIGN$$CURRENCY$',
            'trend': 'decrease',
        },
    }

    answer_response = {
        'cart': {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'diff_data': diff,
            'requirements': {},
        },
        'checkout_unavailable_reason': 'quantity-over-limit',
        'depot_id': '0',
        'delivery_type': 'eats_dispatch',
        'order_conditions': {'delivery_cost': '0'},
    }
    assert response == answer_response
    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    assert extra == [
        {
            'full_price': None,
            'title': None,
            'vat': None,
            'is_expiring': None,
            'supplier_tin': None,
        },
        {
            'full_price': None,
            'title': None,
            'vat': None,
            'is_expiring': None,
            'supplier_tin': None,
        },
    ]
    assert cart_db == [{'cart_version': 1, 'status': 'editing'}]
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'depot_id': '0',
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': '(0.0000,,)',
            'promocode': None,
            'unavailable_checkout_reason': 'quantity_over_limit',
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': False,
        },
    ]

    response = await cart.checkout()
    # cached data
    answer_response.pop('cart')
    assert response == answer_response
    assert overlord_catalog.times_called() == 2  # no more requests to overlord


@pytest.mark.now(TS_NOW)
async def test_bad_version(taxi_grocery_cart, cart, overlord_catalog, pgsql):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'
    delivery_type = 'eats_dispatch'
    client_price = str(int(price) * quantity)
    supplier_tin = 'supplier-tin'

    overlord_catalog.add_product(
        product_id=item_id,
        price=price,
        in_stock='10',
        supplier_tin=supplier_tin,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    assert overlord_catalog.times_called() == 1

    correct_cart_version = 1
    wrong_cart_version = 0
    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': wrong_cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert overlord_catalog.times_called() == 1
    assert response.status_code == 409

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    assert extra == [
        {
            'full_price': None,
            'title': None,
            'vat': None,
            'is_expiring': None,
            'supplier_tin': None,
        },
    ]
    assert cart_db == [{'cart_version': 1, 'status': 'editing'}]
    assert data == {}

    json['cart_version'] = correct_cart_version

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    assert overlord_catalog.times_called() == 2

    cart_response = {'id': cart.cart_id}
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        cart=cart_response,
        delivery_type=delivery_type,
        delivery_cost='0',
        supplier_tin=supplier_tin,
    )

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    assert overlord_catalog.times_called() == 2  # no more requests to overlord

    # cached data
    _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        delivery_type=delivery_type,
        delivery_cost='0',
        supplier_tin=supplier_tin,
    )


# Проверяем правильность шаблона: разделитель и количество знаков
@pytest.mark.parametrize('locale', ['en', 'fr', 'ru'])
@pytest.mark.parametrize(
    'price,expected_result',
    [('5.30', '5.30'), ('5.25', '5.25'), ('1.00', '1.00')],
)
@pytest.mark.parametrize('currency', ['EUR', 'GBP', 'RUB'])
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'grocery': 0.01},
        'GBP': {'grocery': 0.01},
        'RUB': {'grocery': 0.01},
        '__default__': {'__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={
        'EUR': {'__default__': 2, 'iso4217': 2},
        'GBP': {'__default__': 2, 'iso4217': 2},
        'RUB': {'grocery': 2},
    },
)
@pytest.mark.parametrize(
    'test_handler',
    [
        '/internal/v2/cart/checkout',
        '/lavka/v1/cart/v1/retrieve',
        '/lavka/v1/cart/v1/update',
        '/lavka/v1/cart/v1/apply-promocode',
    ],
)
async def test_price_format_and_trailing_zeros(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        taxi_grocery_cart_monitor,
        locale,
        currency,
        price,
        expected_result,
        test_handler,
        grocery_depots,
):
    if currency == 'RUB':
        expected_result = str(float(expected_result))
        if expected_result == '1.0':
            expected_result = '1'
    item_id = 'item_id_1'
    quantity = 1
    legacy_depot_id = keys.DEFAULT_LEGACY_DEPOT_ID
    depot_id = 'depot-id'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        0,
        legacy_depot_id=legacy_depot_id,
        depot_id=depot_id,
        currency=currency,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    await taxi_grocery_cart.invalidate_caches()

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')
    await cart.modify(
        {item_id: {'q': quantity, 'p': price}}, currency=currency,
    )

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': str(quantity),
                'currency': currency,
            },
        ],
    }

    headers = DEFAULT_HEADERS
    headers['X-Request-Language'] = locale
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert response.status_code == 200
    if test_handler == '/internal/v2/cart/checkout':
        actual_price = response.json()['items'][0]['price_template']
    else:
        actual_price = response.json()['total_price_template']
    if locale == 'en':
        assert actual_price == '$SIGN${}$CURRENCY$'.format(expected_result)
    if locale in ('fr', 'ru'):
        expected_result = expected_result.replace('.', ',')
        assert actual_price == '{} $SIGN$$CURRENCY$'.format(expected_result)


@pytest.mark.now(TS_NOW)
async def test_empty_cart(taxi_grocery_cart, cart, overlord_catalog, pgsql):
    item_id = 'item_id_1'
    price = '345'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock='10',
    )

    await cart.modify({item_id: {'q': 1, 'p': price}})

    assert overlord_catalog.times_called() == 1

    cart_modify_data = await cart.modify({item_id: {'q': 0, 'p': price}})
    assert cart_modify_data['available_for_checkout'] is False
    assert cart_modify_data['checkout_unavailable_reason'] == 'cart_empty'

    assert overlord_catalog.times_called() == 2

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert overlord_catalog.times_called() == 3
    assert response.status_code == 200

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    data = _fetch_data(pgsql, cart.cart_id)
    extra = _fetch_items_extra_data(pgsql, cart.cart_id, check_exists=False)

    assert not extra
    assert cart_db == [{'cart_version': 2, 'status': 'editing'}]
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 2,
            'depot_id': '0',
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': '(0.0000,,)',
            'promocode': None,
            'unavailable_checkout_reason': 'cart_empty',
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': False,
        },
    ]

    assert response.json().get('items') is None


@pytest.mark.parametrize('is_expiring', [True, False, None])
@pytest.mark.now(TS_NOW)
async def test_fetch_extra_data_before_checkout(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        grocery_p13n,
        is_expiring,
):
    item_id = 'item_id_1'
    full_price = '500'
    price = '345'
    supplier_tin = 'supplier_tin'

    overlord_catalog.add_product(
        product_id=item_id,
        price=full_price,
        in_stock='10',
        supplier_tin=supplier_tin,
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(int(full_price) - int(price)),
        meta={'is_expiring': is_expiring},
    )

    await cart.modify({item_id: {'q': 1, 'p': price}})

    assert overlord_catalog.times_called() == 1
    assert grocery_p13n.discount_modifiers_times_called == 1

    items_extra_data = _fetch_items_extra_data(pgsql, cart.cart_id)
    assert items_extra_data == [
        {
            'full_price': None,
            'title': None,
            'vat': None,
            'is_expiring': None,
            'supplier_tin': None,
        },
    ]

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={**DEFAULT_HEADERS, 'User-Agent': keys.DEFAULT_USER_AGENT},
        json=json,
    )

    assert overlord_catalog.times_called() == 2
    assert response.status_code == 200
    assert grocery_p13n.discount_modifiers_times_called == 2

    extra = _fetch_items_extra_data(pgsql, cart.cart_id)
    _check_items_extra_data(
        extra,
        item_id,
        full_price,
        is_expiring=is_expiring,
        supplier_tin=supplier_tin,
    )


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'stored_unavailable_checkout_reason,'
    'cart_version_pg,'
    'request_cart_version,'
    'checkout_data_cart_version,'
    'use_overlord,'
    'reason_at_the_end',
    [
        # # Somebody successfully checked out cart just before us.
        ('no_reason', 1, 1, 1, False, 'no_reason'),
        # Somebody tried to check out old cart and stored old version, we
        # should ignore this data and override it.
        ('minimum_price', 3, 3, 1, True, 'no_reason'),
        # Somebody tried to check out old cart and stored old version, we
        # should ignore this data and override it.
        ('minimum_price', 3, 3, 1, True, 'price_missmatch'),
        # Somebody unsuccessfully checked out cart just before us, we should
        # return the same answer for the same version.
        ('minimum_price', 1, 1, 1, False, 'minimum_price'),
    ],
)
async def test_concurrent_checkout(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        testpoint,
        stored_unavailable_checkout_reason,
        cart_version_pg,
        request_cart_version,
        checkout_data_cart_version,
        use_overlord,
        reason_at_the_end,
        grocery_p13n,
):
    item_id = 'item_id_1'
    quantity = 1
    discount_price = '100'
    overlord_full_price = '500'
    overlord_vat = '20.00'
    overlord_supplier_tin = 'overlord-supplier-tin'
    pg_full_price = '345'
    pg_vat = '10.00'
    pg_is_expiring = True
    pg_supplier_tin = 'pg-supplier-tin'
    depot_id = '0'
    discount_value = int(overlord_full_price) - int(discount_price)
    meta = {'is_expiring': pg_is_expiring}

    overlord_catalog.add_product(
        product_id=item_id,
        price=overlord_full_price,
        in_stock='10',
        vat=overlord_vat,
        supplier_tin=overlord_supplier_tin,
    )
    if reason_at_the_end != 'price_missmatch':
        grocery_p13n.add_modifier(
            product_id=item_id, value=str(discount_value), meta=meta,
        )

    await cart.modify({item_id: {'q': quantity, 'p': discount_price}})

    was_checked_out = stored_unavailable_checkout_reason == 'no_reason'
    status = 'checked_out' if was_checked_out else 'editing'
    has_surge = False if was_checked_out else None

    # Emulate concurrent request which changed actual cart state just
    # before us.
    @testpoint('start_checkout')
    def start_checkout(data):
        cart.update_db(status=status)
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(
            """
           INSERT INTO cart.checkout_data
           (cart_id, cart_version, depot_id, depot_status,
           depot_switch_time, unavailable_checkout_reason,
            promocode, order_conditions, has_surge)
           VALUES(%s, %s, %s, %s, %s, %s, NULL, NULL, %s)
            """,
            [
                cart.cart_id,
                checkout_data_cart_version,
                depot_id,
                'available',
                DATETIME_VALUE,
                stored_unavailable_checkout_reason,
                has_surge,
            ],
        )
        if was_checked_out:
            cursor.execute(
                f"""
               UPDATE cart.cart_items SET
               full_price = %s, title = %s, vat = %s, is_expiring = %s, 
               supplier_tin = %s
                """,
                [
                    decimal.Decimal(pg_full_price),
                    f'title for {item_id}',
                    pg_vat,
                    pg_is_expiring,
                    pg_supplier_tin,
                ],
            )
        return {}

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': request_cart_version,
        'offer_id': cart.offer_id,
    }

    if reason_at_the_end == 'price_missmatch':
        overlord_catalog.add_product(
            product_id=item_id, price=overlord_full_price, in_stock='10',
        )
        grocery_p13n.add_modifier(
            product_id=item_id, value=str(discount_value - 1), meta=meta,
        )

    cart.update_db(cart_version=cart_version_pg)

    overlord_catalog.flush()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )
    assert response.status_code == 200
    assert overlord_catalog.times_called() == 1

    is_checked_out = reason_at_the_end == 'no_reason'

    def _check_item_full_price(resp_json, full_price):
        if not is_checked_out:
            assert 'items' not in resp_json
        else:
            assert len(response.json()['items']) == 1
            item = response.json()['items'][0]
            assert item['price'] == discount_price
            assert item['full_price'] == full_price

    def _check_extra(extra, full_price, vat, is_expiring, supplier_tin):
        if not is_checked_out:
            assert extra == [
                {
                    'title': None,
                    'full_price': None,
                    'vat': None,
                    'is_expiring': None,
                    'supplier_tin': None,
                },
            ]
        else:
            _check_items_extra_data(
                extra, item_id, full_price, vat, is_expiring, supplier_tin,
            )

    extra = _fetch_items_extra_data(pgsql, cart.cart_id)

    resp_json = response.json()
    if use_overlord:
        # Checks that full_price in response got from overlord data
        _check_item_full_price(resp_json, overlord_full_price)
        _check_checkout_unavailable_reason(response, is_checked_out)
        _check_extra(
            extra,
            overlord_full_price,
            overlord_vat,
            pg_is_expiring,
            overlord_supplier_tin,
        )
    else:
        # Not |overlord_full_price|, because when we did checkout, somebody
        # inserted checkout data in pg, and overlord data is not more actual.
        _check_item_full_price(resp_json, pg_full_price)
        # No data from overlord
        assert 'cart' not in response.json()
        _check_extra(
            extra, pg_full_price, pg_vat, pg_is_expiring, pg_supplier_tin,
        )

    cart_db = _fetch_cart(pgsql, cart.cart_id)
    status = 'checked_out' if is_checked_out else 'editing'
    assert cart_db == [
        {'cart_version': request_cart_version, 'status': status},
    ]
    data = _fetch_data(pgsql, cart.cart_id)

    has_surge = False if was_checked_out or use_overlord else None
    assert data == [
        {
            'cart_id': cart.cart_id,
            'cart_version': request_cart_version,
            'depot_id': depot_id,
            'depot_status': 'available',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': (
                '(0.0000,,)' if use_overlord else None
            ),
            'promocode': None,
            'unavailable_checkout_reason': reason_at_the_end,
            'promocode_properties': None,
            'promocode_discount': None,
            'has_surge': has_surge,
        },
    ]

    assert start_checkout.times_called == 1


# Тест эмулирует ситуацию, когда корзину изменили в момент чекаута.
# Корзина должна вернуть 409, потому что мы чекаутим уже не актуальную корзину.
async def test_concurrent_checkout_data(
        cart, overlord_catalog, testpoint, fetch_cart,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock='10',
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    request_cart_version = cart.cart_version
    actual_cart_version = 2

    # Emulate concurrent request which changed actual cart state just
    # before us.
    @testpoint('start_checkout')
    async def start_checkout(data):
        await cart.modify({item_id: {'q': quantity + 1, 'p': price}})
        assert cart.cart_version == actual_cart_version

    assert request_cart_version < actual_cart_version
    await cart.checkout(
        cart_version=request_cart_version, required_status_code=409,
    )

    cart_from_pg = fetch_cart(cart.cart_id)

    assert cart_from_pg.cart_version == actual_cart_version
    assert cart_from_pg.status == 'editing'

    assert start_checkout.times_called == 1


@pytest.mark.now(TS_NOW)
async def test_update_during_checkout(
        taxi_grocery_cart, cart, overlord_catalog, pgsql, testpoint,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    cart_version_before_checkout = cart.cart_version
    cart_version_during_checkout = cart.cart_version + 1

    # Emulate concurrent request which update actual cart just before us.
    @testpoint('start_checkout')
    def start_checkout(data):
        cart.update_db(cart_version=cart_version_during_checkout)
        return {}

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart_version_before_checkout,
        'offer_id': cart.offer_id,
    }

    overlord_catalog.flush()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    # During checkout, cart version has changed, it is 409.
    assert response.status_code == 409
    assert overlord_catalog.times_called() == 1

    # Checks that no data changed
    extra = _fetch_items_extra_data(pgsql, cart.cart_id)
    assert extra == [
        {
            'title': None,
            'full_price': None,
            'vat': None,
            'is_expiring': None,
            'supplier_tin': None,
        },
    ]
    data = _fetch_data(pgsql, cart.cart_id)
    assert data == {}
    cart_db = _fetch_cart(pgsql, cart.cart_id)
    assert cart_db == [
        {'cart_version': cart_version_during_checkout, 'status': 'editing'},
    ]

    assert start_checkout.times_called == 1


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'cart_version_pg,'
    'request_cart_version,'
    'checkout_data_cart_version,'
    'is_409,'
    'needs_overlord,'
    'checked_out',
    [
        # Cart version and request version mismatched
        (1, 1, None, False, True, False),
        (1, 0, None, True, False, False),
        # Retry after successful checkout, not 409 and no overlord
        (1, 1, 1, False, False, False),
        # checkout data is too old and request version
        # is lower than cart version
        (5, 4, 3, True, False, False),
        # Request version is too old
        (5, 2, 3, True, False, False),
        # Old request version and cart is already checked out
        (5, 2, 3, True, False, True),
        # User changed cart and try to checkout actual cart
        (5, 5, 3, False, True, False),
        # Request version is greater than version in checkout
        # data but cart is already checked out
        (5, 5, 3, True, False, True),
    ],
)
async def test_409_errors(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        cart_version_pg,
        request_cart_version,
        checkout_data_cart_version,
        is_409,
        needs_overlord,
        checked_out,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '500'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock='10',
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': request_cart_version,
        'offer_id': cart.offer_id,
    }

    if checkout_data_cart_version is not None:
        assert checkout_data_cart_version <= cart_version_pg
        reason = 'minimum_price'
        if checked_out:
            reason = 'no_reason'
        _insert_checkout_data(
            cart.cart_id, checkout_data_cart_version, reason, pgsql,
        )

    cart.update_db(
        cart_version=cart_version_pg,
        status='checked_out' if checked_out else 'editing',
    )
    overlord_catalog.flush()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    if is_409:
        assert response.status_code == 409
    else:
        assert response.status_code == 200

    if needs_overlord:
        assert overlord_catalog.times_called() == 1
    else:
        assert overlord_catalog.times_called() == 0


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize('payment_method_id', ['test_payment_method_id', None])
async def test_payment_method(
        taxi_grocery_cart, overlord_catalog, cart, payment_method_id,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    payment_method_type = 'test_payment_method_type'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    cart.update_db(
        payment_method_type=payment_method_type,
        payment_method_id=payment_method_id,
    )

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    payment_method = response.json()['payment_method']
    assert payment_method['type'] == payment_method_type
    if payment_method_id is not None:
        assert payment_method['id'] == payment_method_id
    else:
        assert 'id' not in payment_method


@pytest.mark.now(TS_NOW)
async def test_payment_method_discount(
        taxi_grocery_cart, cart, overlord_catalog, grocery_p13n,
):
    item_id = 'item_id_1'
    quantity = 1
    price = 100
    discount_price = 90
    discount_value = price - discount_price

    overlord_catalog.add_product(
        product_id=item_id, price=str(price), in_stock=str(quantity),
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(discount_value),
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
    )

    await cart.modify({item_id: {'q': quantity, 'p': discount_price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    for overlord_catalog_times_called in (
            1,  # first checkout try causes overlord-catalog call
            0,  # second checkout try uses 'checkout-data' from PG
    ):
        overlord_catalog.flush()

        response = await taxi_grocery_cart.post(
            '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
        )
        assert overlord_catalog.times_called() == overlord_catalog_times_called

        assert response.status_code == 200
        assert response.json()['payment_method_discount']


@pytest.mark.now(TS_NOW)
async def test_payment_method_discount_calc_log(
        taxi_grocery_cart, cart, overlord_catalog, pgsql, grocery_p13n,
):
    item_id = 'item_id_1'
    quantity = 1
    catalog_price = 112
    mastercard_discount_raw = 11.2

    mastercard_discount = math.ceil(mastercard_discount_raw)
    discount_price = catalog_price - mastercard_discount
    subtotal = discount_price * quantity

    overlord_catalog.add_product(
        product_id=item_id, price=catalog_price, in_stock=str(quantity),
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(mastercard_discount_raw),
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
        meta={
            'picture': 'mastercard',
            'subtitle_tanker_key': 'test_mastercard_discount',
            'draft_id': 'draft_1',
        },
    )

    await cart.modify({item_id: {'q': quantity, 'p': str(discount_price)}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    overlord_catalog.flush()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )
    assert response.status_code == 200

    checkout_data = _fetch_checkout_data_calculation_log(pgsql, cart.cart_id)

    pricing_calculation = {
        'products_calculation': [
            {
                'steps': [
                    {'bag': [{'price': str(catalog_price), 'quantity': '1'}]},
                    {
                        'bag': [
                            {
                                'price': str(
                                    catalog_price - mastercard_discount_raw,
                                ),
                                'quantity': '1',
                            },
                        ],
                        'discount': {
                            'payment_type': 'money_payment',
                            'discount_type': 'payment_method_discount',
                            'draft_id': 'draft_1',
                        },
                        'total_discount': str(mastercard_discount_raw),
                    },
                    {
                        'bag': [
                            {
                                'price': str(
                                    catalog_price - mastercard_discount,
                                ),
                                'quantity': '1',
                            },
                        ],
                        'discount': {'discount_type': 'price_round'},
                        'total_discount': str(
                            round(
                                mastercard_discount - mastercard_discount_raw,
                                1,
                            ),
                        ),
                    },
                ],
                'product_id': str(item_id),
            },
        ],
    }

    assert checkout_data == [
        {
            'cart_id': cart.cart_id,
            'calculation_log': {
                'calculation': pricing_calculation,
                'coupon': {'value': '0'},
                'currency': 'RUB',
                'service_fees': {'delivery_cost': '0'},
                'total': str(subtotal),
            },
        },
    ]


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'req_json',
    [
        ({'cart_id': 'x'}),
        ({'cart_id': '7cf3718c-14784c07-8f473955e8741a99'}),
        ({'cart_id': '7cf3718c14784c078f473955e8741a991'}),
    ],
)
async def test_badrequest(taxi_grocery_cart, req_json):
    base_json = {
        'cart_id': '7cf3718c-1478-4c07-8f47-3955e8741a99',
        'cart_version': 1,
        'offer_id': '3da324af0dc34a6893347500cb5fff0b',
        'position': {
            'location': [37.64256286621094, 55.73575210571289],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'comment': 'please, fast!',
        },
    }
    for k in req_json:
        base_json[k] = req_json[k]

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={'X-Idempotency-Token': 'abc', **BASIC_HEADERS},
        json=base_json,
    )

    assert response.status_code == 400


@pytest.mark.now(TS_NOW)
async def test_idempotency_token_in_retrieve(
        taxi_grocery_cart, cart, overlord_catalog,
):
    price = '345'
    idempotency_token = 'test_idempotency_token'

    overlord_catalog.add_product(product_id='item_id_1', price=price)

    await cart.modify(
        {'item_id_1': {'q': 1, 'p': price}},
        headers={'X-Idempotency-Token': idempotency_token},
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=BASIC_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'offer_id': cart.offer_id,
        },
    )

    assert 'idempotency_token' not in response.json()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={'X-Idempotency-Token': idempotency_token, **BASIC_HEADERS},
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        },
    )

    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={'X-Idempotency-Token': idempotency_token, **BASIC_HEADERS},
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'offer_id': cart.offer_id,
            'allow_checked_out': True,
        },
    )

    assert response.json()['idempotency_token'] == idempotency_token


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'measurements',
    [
        None,
        {
            'width': 1,
            'height': 2,
            'depth': 3,
            'gross_weight': 4,
            'net_weight': 5,
        },
    ],
)
async def test_measurements(
        taxi_grocery_cart, overlord_catalog, cart, measurements,
):
    """ Check cart/checkout returns item measurements, if exists """

    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    overlord_catalog.add_product(
        product_id=item_id, price=price, measurements=measurements,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert response.status_code == 200
    response_json = response.json()
    for item in response_json['items']:
        assert item['id'] == item_id
        if measurements is not None:
            for key in ['width', 'height', 'depth', 'gross_weight']:
                assert item[key] == measurements[key]


@pytest.mark.now(TS_NOW)
@experiments.GROCERY_ORDERS_WEIGHT_EXP
@pytest.mark.parametrize(
    'measurements',
    [
        None,
        {
            'width': 1,
            'height': 2,
            'depth': 3,
            'gross_weight': 0,
            'net_weight': 5,
        },
    ],
)
@pytest.mark.parametrize(
    'personal_phone_id',
    [
        '+79672529051',
        '+79672529052',
        '+79672529053',
        '+79672529054',
        '+79672529055',
    ],
)
async def test_measurements_experiment_retrieve(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        measurements,
        personal_phone_id,
):
    """ Check grocery orders weight experiment in retrieve"""

    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    overlord_catalog.add_product(
        product_id=item_id, price=price, measurements=measurements,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    request_headers = copy.deepcopy(DEFAULT_HEADERS)

    request_headers['X-YaTaxi-User'] = f'personal_phone_id={personal_phone_id}'

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/retrieve/raw', headers=request_headers, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()
    for item in response_json['items']:
        assert item['id'] == item_id
        if personal_phone_id == '+79672529051':
            if measurements is not None:
                assert item['gross_weight'] == measurements['net_weight']
        elif personal_phone_id == '+79672529052':
            if measurements is not None:
                assert item['gross_weight'] == measurements['gross_weight']
        elif personal_phone_id == '+79672529053':
            if measurements is not None:
                assert item['gross_weight'] == max(
                    measurements['gross_weight'], measurements['net_weight'],
                )
        elif personal_phone_id == '+79672529054':
            if measurements is not None:
                assert item['gross_weight'] == 1000
        elif personal_phone_id == '+79672529055':
            if measurements is not None:
                assert item['gross_weight'] == 1000


@pytest.mark.now(TS_NOW)
@experiments.GROCERY_ORDERS_WEIGHT_EXP
@pytest.mark.parametrize(
    'measurements',
    [
        None,
        {
            'width': 1,
            'height': 2,
            'depth': 3,
            'gross_weight': 0,
            'net_weight': 5,
        },
    ],
)
@pytest.mark.parametrize(
    'personal_phone_id',
    [
        '+79672529051',
        '+79672529052',
        '+79672529053',
        '+79672529054',
        '+79672529055',
    ],
)
async def test_measurements_experiment_checkout(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        measurements,
        personal_phone_id,
):
    """ Check grocery orders weight experiment in checkout"""

    item_id = 'item_id_1'
    quantity = 1
    price = '100'

    overlord_catalog.add_product(
        product_id=item_id, price=price, measurements=measurements,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    request_headers = copy.deepcopy(DEFAULT_HEADERS)

    request_headers['X-YaTaxi-User'] = f'personal_phone_id={personal_phone_id}'

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=request_headers, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()
    for item in response_json['items']:
        assert item['id'] == item_id
        if personal_phone_id == '+79672529051':
            if measurements is not None:
                assert item['gross_weight'] == measurements['net_weight']
        elif personal_phone_id == '+79672529052':
            if measurements is not None:
                assert item['gross_weight'] == measurements['gross_weight']
        elif personal_phone_id == '+79672529053':
            if measurements is not None:
                assert item['gross_weight'] == max(
                    measurements['gross_weight'], measurements['net_weight'],
                )
        elif personal_phone_id == '+79672529054':
            if measurements is not None:
                assert item['gross_weight'] == 1000
        elif personal_phone_id == '+79672529055':
            if measurements is not None:
                assert item['gross_weight'] == 1000


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize('depot_status', ['closed', 'coming_soon'])
async def test_depot_is_closed(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        taxi_grocery_cart_monitor,
        depot_status,
        grocery_depots,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        0,
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        status=depot_status,
    )
    await taxi_grocery_cart.invalidate_caches()

    item_id = 'item_id_1'
    quantity = 1
    price = '400'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=str(quantity),
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_cart_monitor,
            sensor='grocery_cart_unavailable_for_check_out_carts',
            labels={'country': 'Russia'},
    ) as collector:
        response = await taxi_grocery_cart.post(
            '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
        )

    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['checkout_unavailable_reason'] == 'depot_is_closed_now'
    )
    _check_unavailable_for_check_out_carts(
        collector.get_single_collected_metric(),
        country_name='Russia',
        city_name='Moscow',
        depot_id='0',
        reason='depot_is_closed_now',
    )

    assert _fetch_data(pgsql, cart.cart_id) == [
        {
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'depot_id': '0',
            'depot_status': 'closed',
            'depot_switch_time': DATETIME_VALUE,
            'order_conditions_with_eta': '(0.0000,,)',
            'promocode': None,
            'promocode_discount': None,
            'promocode_properties': None,
            'has_surge': False,
            'unavailable_checkout_reason': 'depot_is_closed_now',
        },
    ]


@pytest.mark.now(TS_NOW)
async def test_depot_not_found(
        taxi_grocery_cart, cart, overlord_catalog, grocery_depots,
):
    item_id = 'item_id_1'
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({'test_item': {'q': '1', 'p': '123'}})

    grocery_depots.clear_depots()
    await taxi_grocery_cart.invalidate_caches()

    response = await cart.checkout()
    assert response['checkout_unavailable_reason'] == 'cannot_find_depot'


@experiments.ITEMS_PRICING_ENABLED
@pytest.mark.now(TS_NOW)
async def test_depot_not_found_pricing_enabled(
        taxi_grocery_cart, cart, overlord_catalog, grocery_depots,
):
    item_id = 'item_id_1'
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({'test_item': {'q': '1', 'p': '123'}})

    grocery_depots.clear_depots()
    await taxi_grocery_cart.invalidate_caches()

    response = await cart.checkout(grocery_flow_version='tristero_flow_v2')
    assert response['checkout_unavailable_reason'] == 'cannot_find_depot'


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize(
    'delivery_zone_type',
    ['pedestrian', 'yandex_taxi', 'yandex_taxi_remote', 'yandex_taxi_night'],
)
async def test_delivery_zone(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        delivery_zone_type,
        grocery_depots,
):
    item_id = 'item_id_1'
    quantity = '1'
    price = '400'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        0,
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        delivery_type=delivery_zone_type,
    )
    await taxi_grocery_cart.invalidate_caches()

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=quantity,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['delivery_zone_type'] == delivery_zone_type


@pytest.mark.parametrize(
    'order_flow_version', ['tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
async def test_disable_promocode(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        grocery_coupons,
        pgsql,
        mockserver,
        order_flow_version,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'

    promo_code = 'LAVKA1235'
    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        assert request.json == {
            'code': promo_code,
            'user': {'id': '1234', 'idProvider': 'yandex'},
            'place': {'id': '0'},
            'paymentMethod': 'taxi',
            'applyForAmount': '345',
        }
        validation_response = {
            'payload': {'validationResult': {'valid': True, 'message': '1'}},
        }
        return validation_response

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    assert overlord_catalog.times_called() == 1

    await cart.apply_promocode(
        promo_code, headers={'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN},
    )

    assert overlord_catalog.times_called() == 2
    assert mock_validate.times_called == 1

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'order_flow_version': order_flow_version,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )

    assert overlord_catalog.times_called() == 3
    assert mock_validate.times_called == 1

    assert response.status_code == 500


@pytest.mark.now(TS_NOW)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'__default__': 1, 'grocery': 0.01}},
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
)
async def test_price_rounding(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = '1'
    price = '4.63'
    overlord_price = '4.637'
    overlord_catalog.set_location_zone_type(
        location=keys.DEFAULT_DEPOT_LOCATION, zone_type='pedestrian',
    )

    overlord_catalog.add_product(
        product_id=item_id, price=overlord_price, in_stock=quantity,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=DEFAULT_HEADERS, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['items'][0]['price_template'] == '4,63 $SIGN$$CURRENCY$'
    )


@pytest.mark.now(keys.TS_NOW)
async def test_additional_offer_info_log(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        offers,
        experiments3,
        grocery_surge,
        testpoint,
):
    offer_id = cart.offer_id
    user_id = '123456abcd'

    item_id = 'item_id_1'
    price = '345'
    quantity = 1

    delivery_cost = '100'
    next_delivery_cost = '50'
    next_delivery_threshold = '350'
    min_eta = 20
    max_eta = 10
    minimum_order = '300'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }
    legacy_depot_id = keys.DEFAULT_LEGACY_DEPOT_ID

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=offer_id,
        min_eta=str(min_eta),
        max_eta=str(max_eta),
        minimum_order=minimum_order,
        depot_id=legacy_depot_id,
        is_surge=True,
        delivery=actual_delivery,
    )

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    location_str = (
        str(float(keys.DEFAULT_DEPOT_LOCATION[1]))
        + ';'
        + str(float(keys.DEFAULT_DEPOT_LOCATION[0]))
    )

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['offer_id'] == offer_id
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': delivery_cost,
                'delivery_conditions': [
                    {
                        'delivery_cost': delivery_cost,
                        'order_cost': minimum_order,
                    },
                    {
                        'delivery_cost': next_delivery_cost,
                        'order_cost': next_delivery_threshold,
                    },
                ],
                'is_surge': True,
                'is_manual': False,
                'next_delivery_cost': next_delivery_cost,
                'next_delivery_threshold': next_delivery_threshold,
                'max_eta_minutes': str(max_eta),
                'min_eta_minutes': str(min_eta),
                'surge_minimum_order': minimum_order,
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': location_str,
            'depot_id': legacy_depot_id,
        }
        assert offer_additional_info['user_id'] == user_id

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={**DEFAULT_HEADERS, **{'X-YaTaxi-UserId': user_id}},
        json=json,
    )

    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'flow_version, reason',
    [('tristero_flow_v1', 'tips-not-allowed'), ('grocery_flow_v1', None)],
)
async def test_tips_validation_on_checkout(
        cart, overlord_catalog, flow_version, reason,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.set_tips({'amount': '10', 'amount_type': 'absolute'})

    response = await cart.checkout(order_flow_version=flow_version)

    if reason is not None:
        assert response['checkout_unavailable_reason'] == reason
    else:
        assert 'checkout_unavailable_reason' not in response


@experiments.TIPS_EXPERIMENT
async def test_tips_payment_flow_validation(cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.set_tips({'amount': '10', 'amount_type': 'absolute'})

    response = await cart.checkout(tips_payment_flow='with_order')

    assert response['checkout_unavailable_reason'] == 'bad_tips_payment_flow'


@pytest.mark.now(TS_NOW)
@pytest.mark.parametrize('is_heavy_cart_enabled', [False, True])
async def test_heavy_cart(
        taxi_grocery_cart,
        overlord_catalog,
        experiments3,
        cart,
        is_heavy_cart_enabled,
):

    experiments.set_heavy_cart_settings(experiments3, is_heavy_cart_enabled)

    common_measurements = {
        'width': 1,
        'height': 2,
        'depth': 3,
        'net_weight': 5,
    }

    measurements = [
        {**common_measurements, 'gross_weight': 1},
        {**common_measurements, 'gross_weight': 2},
        {**common_measurements, 'gross_weight': 3},
        {**common_measurements, 'gross_weight': 5},
    ]

    item_ids = ['item_id_1', 'item_id_2', 'item_id_3', 'item_id_4']
    price = '10'

    for item_id, measurement in zip(item_ids, measurements):
        overlord_catalog.add_product(
            product_id=item_id, price=price, measurements=measurement,
        )

    await cart.modify(
        {
            item_ids[0]: {'q': 1, 'p': price},
            item_ids[1]: {'q': 1, 'p': price},
            item_ids[2]: {'q': 4, 'p': price},
            item_ids[3]: {'q': 1, 'p': price},
        },
    )

    assert overlord_catalog.times_called() == 1

    diff = {
        'cart_total': {
            'actual_template': '70 $SIGN$$CURRENCY$',
            'diff_template': '1950 $SIGN$$CURRENCY$',
            'previous_template': '-1880 $SIGN$$CURRENCY$',
            'trend': 'increase',
        },
        'products': [
            {
                'product_id': 'item_id_3',
                'quantity': {'actual_limit': '1', 'wanted': '4'},
            },
            {
                'product_id': 'item_id_4',
                'quantity': {'actual_limit': '0', 'wanted': '1'},
            },
        ],
    }

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'items': [],
    }

    headers = DEFAULT_HEADERS
    headers['X-Request-Language'] = 'ru'
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=headers, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()

    if is_heavy_cart_enabled:
        assert response_json['cart']['diff_data'] == diff
        assert response_json['checkout_unavailable_reason'] == 'too_heavy_cart'
    else:
        assert response_json['cart']['diff_data'] == {}
        assert 'checkout_unavailable_reason' not in response_json

    assert overlord_catalog.times_called() == 2


def _check_unavailable_for_check_out_carts(
        metric, country_name, city_name, depot_id, reason,
):
    assert metric.value == 1
    assert metric.labels == {
        'country': country_name,
        'city_name': city_name,
        'reason': reason,
        'sensor': 'grocery_cart_unavailable_for_check_out_carts',
    }


def _add_prices_config(experiments3, precision):
    if precision == 1:
        minimum_total_cost = '1.2'
        minimum_item_price = '0.1'
    elif precision == 2:
        minimum_total_cost = '1.17'
        minimum_item_price = '0.01'
    else:
        raise Exception('unsupported precision')

    experiments3.add_config(
        name='lavka_cart_prices',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'currency_precision': precision,
                    'minimum_total_cost': minimum_total_cost,
                    'minimum_item_price': minimum_item_price,
                },
            },
        ],
        default_value={},
    )


def _insert_checkout_data(cart_id, cart_version, reason, pgsql):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'INSERT INTO cart.checkout_data '
        '(cart_id, cart_version, depot_id, unavailable_checkout_reason) '
        'VALUES (%s, %s, %s, %s)',
        [cart_id, cart_version, '0', reason],
    )


def _currency(price):
    return f'{price} $SIGN$$CURRENCY$'


def _unpack_tuple(items, fields):
    if isinstance(items, tuple):
        result = {}
        for idx, field in enumerate(items):
            result[fields[idx]] = field
        return result

    result = []
    for item in items:
        result.append(_unpack_tuple(item, fields))
    return result


def _get_pg_flag(flag):
    if flag:
        return 't'
    return 'f'


def _fetch_items_extra_data(pgsql, cart_id, check_exists=True):
    cursor = pgsql['grocery_cart'].cursor()
    fields = ['full_price', 'title', 'vat', 'is_expiring', 'supplier_tin']
    fields_join = ', '.join(fields)
    cursor.execute(
        f'SELECT {fields_join} '
        f'FROM cart.cart_items '
        f'WHERE cart_id = %s and status = \'in_cart\'',
        [cart_id],
    )

    items = cursor.fetchall()
    if check_exists:
        assert items
        return _unpack_tuple(items, fields)

    return items


def _check_items_extra_data(
        extra,
        item_id,
        full_price,
        vat='20.00',
        is_expiring=None,
        supplier_tin=None,
):
    extra_reference = [
        {
            'title': f'title for {item_id}',
            'full_price': decimal.Decimal(full_price),
            'vat': vat,
            'is_expiring': is_expiring,
            'supplier_tin': supplier_tin,
        },
    ]

    assert extra == extra_reference


def _fetch_cart(pgsql, cart_id):
    orders = pgsql['grocery_cart'].cursor()
    fields = ['cart_version', 'status']
    fields_join = ', '.join(fields)
    orders.execute(
        f'SELECT {fields_join} FROM cart.carts WHERE cart_id = %s', [cart_id],
    )

    cart = orders.fetchall()
    assert cart

    return _unpack_tuple(cart, fields)


def _fetch_data(pgsql, cart_id):
    orders = pgsql['grocery_cart'].cursor()
    fields = [
        'cart_id',
        'cart_version',
        'depot_id',
        'depot_status',
        'depot_switch_time',
        'unavailable_checkout_reason',
        'promocode',
        'order_conditions_with_eta',
        'promocode_discount',
        'promocode_properties',
        'has_surge',
    ]
    fields_join = ', '.join(fields)
    orders.execute(
        f'SELECT {fields_join} FROM cart.checkout_data WHERE cart_id = %s',
        [cart_id],
    )
    result = orders.fetchall()
    if not result:
        return {}
    return _unpack_tuple(result, fields)


def _fetch_checkout_data_calculation_log(pgsql, cart_id):
    cursor = pgsql['grocery_cart'].cursor()
    fields = ['cart_id', 'calculation_log']
    fields_join = ', '.join(fields)
    cursor.execute(
        f'SELECT {fields_join} FROM cart.checkout_data WHERE cart_id = %s',
        [cart_id],
    )
    result = cursor.fetchall()
    if not result:
        return {}
    return _unpack_tuple(result, fields)


def _fetch_checkout_data_updated(pgsql, cart_id):
    cursor = pgsql['grocery_cart'].cursor()
    fields = ['cart_id', 'updated']
    fields_join = ', '.join(fields)
    cursor.execute(
        f'SELECT {fields_join} FROM cart.checkout_data WHERE cart_id = %s',
        [cart_id],
    )
    result = cursor.fetchall()
    if not result:
        return {}
    return _unpack_tuple(result, fields)[0]['updated']


def _to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.UTC).replace(tzinfo=None)
    return stamp


def _get_shelf_type(item_id):
    if 'st-pa' in item_id:
        return 'parcel'
    if 'st-md' in item_id:
        return 'markdown'
    return 'store'


def _get_raw_id(item_id):
    return item_id.split(':')[0]


def _to_template(value):
    return f'{round(float(value))} $SIGN$$CURRENCY$'


def _check_response(
        response,
        item_id,
        price,
        quantity,
        client_price,
        discount='0',
        max_eta=None,
        min_eta=None,
        delivery_cost=None,
        promo=None,
        reason_code=None,
        cart=None,
        delivery_type=None,
        delivery_zone_type='pedestrian',
        total_time=None,
        cooking_time=None,
        delivery_time=None,
        logistic_tags=None,
        has_surge=False,
        supplier_tin=None,
):
    order_conditions = {}
    if delivery_cost is not None:
        order_conditions['order_conditions'] = {'delivery_cost': delivery_cost}
    if max_eta is not None:
        order_conditions['order_conditions']['max_eta'] = max_eta
    if min_eta is not None:
        order_conditions['order_conditions']['min_eta'] = min_eta
    if total_time is not None:
        order_conditions['order_conditions']['total_time'] = total_time
    if cooking_time is not None:
        order_conditions['order_conditions']['cooking_time'] = cooking_time
    if delivery_time is not None:
        order_conditions['order_conditions']['delivery_time'] = delivery_time

    promocode = {}
    if promo is not None:
        promocode['promocode'] = promo

    reason = {}
    if reason_code is not None:
        reason['checkout_unavailable_reason'] = reason_code

    log_tags = {}
    if logistic_tags is not None:
        log_tags['logistic_tags'] = logistic_tags

    supp_tin = {}
    if supplier_tin is not None:
        supp_tin['supplier_tin'] = supplier_tin

    cart_response = {}
    if cart is not None:
        requirements = cart.pop('requirements', {})
        diff = cart.pop('diff', {})
        version = cart.pop('version', 1)
        cart_response['cart'] = {
            'cart_id': cart['id'],
            'cart_version': version,
            'diff_data': diff,
            'requirements': requirements,
        }

    delivery_type_response = {}
    if delivery_type is not None:
        delivery_type_response['delivery_type'] = delivery_type

    response_json = response.json()
    assert response_json == {
        'depot_id': '0',
        'items': [
            {
                'id': item_id,
                'product_key': {
                    'id': _get_raw_id(item_id),
                    'shelf_type': _get_shelf_type(item_id),
                },
                'price': price,
                'price_template': _to_template(price),
                'full_price': price,
                'full_price_template': _to_template(price),
                'quantity': str(quantity),
                'title': f'title for {item_id}',
                'currency': 'RUB',
                'refunded_quantity': '0',
                'vat': DEFAULT_VAT,
                **supp_tin,
            },
        ],
        'client_price': client_price,
        'cart_total_discount': discount,
        'delivery_zone_type': delivery_zone_type,
        **cart_response,
        **order_conditions,
        **promocode,
        **reason,
        **delivery_type_response,
        **log_tags,
    }


def _check_checkout_unavailable_reason(response, is_checked_out):
    if is_checked_out:
        assert 'checkout_unavailable_reason' not in response.json()
    else:
        assert response.json()['checkout_unavailable_reason'] != 'no_reason'


# Проверяем, что возвращаем флаг есть ли замены для товара, если
# товара нет в наличии, если товар есть в наличии флаг не возвращается
@pytest.mark.parametrize(
    'product_substitutions,has_substitutions',
    [
        pytest.param(
            ['product-2', 'product-3'], True, id='with_substitutions',
        ),
        pytest.param([], False, id='no_substitutions'),
    ],
)
async def test_substitutions(
        cart,
        overlord_catalog,
        grocery_upsale,
        product_substitutions,
        has_substitutions,
):
    item_1 = 'item_1'
    item_2 = 'item_2'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_1, price=price, in_stock='1')
    overlord_catalog.add_product(product_id=item_2, price=price, in_stock='1')
    grocery_upsale.add_product_substitutions(product_substitutions)

    await cart.modify(
        {
            item_1: {'q': quantity, 'p': price},
            item_2: {'q': quantity, 'p': price},
        },
    )

    overlord_catalog.remove_product(product_id=item_1)
    overlord_catalog.remove_product(product_id=item_2)
    overlord_catalog.add_product(product_id=item_1, price=price, in_stock='0')
    overlord_catalog.add_product(product_id=item_2, price='100', in_stock='1')

    response = await cart.checkout()
    products = response['cart']['diff_data']['products']
    assert products[0]['has_substitutions'] == has_substitutions
    assert 'has_substitutions' not in products[1]


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart,
        user_api,
        grocery_coupons,
        cart,
        has_personal_phone_id,
):
    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-Yandex-UID'] = 'some_uid'
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    await cart.modify({'item_id': {'q': '1', 'p': '10'}})

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=headers, json=request,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)
