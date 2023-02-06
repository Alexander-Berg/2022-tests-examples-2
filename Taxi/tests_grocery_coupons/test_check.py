# pylint: disable=too-many-lines

import copy

import pytest

from tests_grocery_coupons import consts
from tests_grocery_coupons import models


def _check_error_log(pgsql, coupon, error_code, coupon_type='support'):
    log = models.ErrorLog(
        pgsql, coupon=coupon, error_code=error_code, coupon_type=coupon_type,
    )
    log.compare_with_db()


SAVING_COUPONS_DISABLED = consts.grocery_coupons_save_coupons()
REQUIRED_ERROR_TEXT = 'Brand X required'


@pytest.mark.parametrize(
    'response_body',
    [
        consts.VALID_PROMOCODE,
        consts.PROMO_CAN_BE_VALID,
        consts.PROMO_ERROR_INVALID_CODE,
        consts.PROMO_ERROR_INVALID_CODE_2,
        consts.PROMO_ERROR_INVALID_CODE_3,
        consts.PROMO_ERROR_INVALID_CODE_4,
    ],
)
@pytest.mark.parametrize(
    'depot_region_id, expected_zone_name',
    [(213, consts.MOSCOW_ZONE_NAME), (2, consts.SPB_ZONE_NAME)],
)
@consts.COUPONS_ERROR_CODES
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_basic(
        pgsql,
        taxi_grocery_coupons,
        grocery_depots,
        coupons,
        response_body,
        depot_region_id,
        expected_zone_name,
):
    promocode = 'test_promocode_01'
    country = 'RUS'
    time_zone = '+3'
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3=country,
        region_id=depot_region_id,
        timezone=time_zone,
    )

    coupons.check_check_request(
        yandex_uid=consts.YANDEX_UID,
        code=promocode,
        application={
            'name': consts.APP_NAME,
            'platform_version': [0, 0, 0],
            'version': [0, 0, 0],
        },
        country=country.lower(),
        current_yandex_uid=consts.YANDEX_UID,
        format_currency=True,
        locale='ru',
        payment_info={'method_id': '1', 'type': 'card'},
        payment_options=['coupon'],
        phone_id=consts.PHONE_ID,
        region_id=depot_region_id,
        service='grocery',
        time_zone=time_zone,
        user_ip='',
        zone_classes=[],
        zone_name=expected_zone_name,
    )

    coupons.set_coupons_check_response(body=response_body)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert coupons.check_times_called() == 1
    assert response.status_code == 200
    body = response.json()

    assert body['valid'] == response_body['valid']
    assert (
        body['promocode_info']['currency_code']
        == response_body['currency_code']
    )

    if 'percent' in response_body:
        assert body['promocode_info']['type'] == 'percent'
        assert body['promocode_info']['value'] == str(response_body['percent'])
    else:
        assert body['promocode_info']['type'] == 'fixed'
        assert body['promocode_info']['value'] == str(response_body['value'])

    if 'limit' in response_body:
        assert body['promocode_info']['limit'] == str(response_body['limit'])
    else:
        assert 'limit' not in body['promocode_info']

    assert (
        body['promocode_info']['series_purpose']
        == response_body['series_purpose']
    )

    if 'error_code' in response_body:
        assert body['error_code'] == response_body['error_code']
        _check_error_log(
            pgsql,
            promocode,
            body['error_code'],
            coupon_type=response_body['series_purpose'],
        )
    else:
        assert 'error_code' not in body


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 2,
        },
    },
)
@pytest.mark.parametrize(
    'first_limit, orders_count, payment_orders_count, valid',
    [(2, 1, 2, True), (2, 2, 4, False), (2, 3, 2, False)],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_first_limit(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        first_limit,
        orders_count,
        payment_orders_count,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    payment_id = 'payment_id-1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=orders_count,
        user_id=consts.YANDEX_UID,
    )

    grocery_marketing.add_payment_id_tag(
        tag_name='total_paid_orders_count',
        usage_count=payment_orders_count,
        payment_id=payment_id,
    )

    series_meta = {'first_limit': first_limit}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert body[
            'error_message'
        ] == consts.ORDERS_FIRST_LIMIT_REACHED_ERROR.format(first_limit)
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_ORDERS_FIRST_LIMIT_REACHED,
        )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


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
@pytest.mark.now(consts.NOW_TIME)
@pytest.mark.parametrize(
    'cart_cost, min_cart_cost, ok_usage_count, '
    'valid, error_message, error_code',
    [
        ('500.1', '500.1', True, True, None, None),
        ('600', '500.1', True, True, None, None),
        (
            '500',
            '500.1',
            True,
            False,
            consts.NO_MIN_CART_COST_ERROR.format('500.1 RUB'),
            consts.ERROR_CODE_NO_MIN_CART_COST,
        ),
        (
            '400',
            '500.1',
            True,
            False,
            consts.NO_MIN_CART_COST_ERROR.format('500.1 RUB'),
            consts.ERROR_CODE_NO_MIN_CART_COST,
        ),
        (
            '400',
            '500.1',
            False,
            False,
            consts.TAG_FIRST_LIMIT_REACHED_ERROR.format(1),
            consts.ERROR_CODE_TAG_FIRST_LIMIT_REACHED,
        ),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_check_min_cart_cost(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
        cart_cost,
        min_cart_cost,
        ok_usage_count,
        valid,
        error_message,
        error_code,
):
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    depot_id = '1337'
    matched_products = ['id_1']
    first_limit = 1
    usage_count = 0 if ok_usage_count else 1
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {
        'tag': tag,
        'matching_error_message': (
            'coupons.error_message.coffee_matching_error'
        ),
        'first_limit': first_limit,
    }

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(
        min_cart_cost=min_cart_cost,
        products=matched_products,
        usage_count=usage_count,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': cart_cost,
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    body = response.json()

    assert body['valid'] == valid
    if not valid:
        _check_error_log(pgsql, promocode, error_code)

    if min_cart_cost is not None:
        assert body['min_cart_cost'] == min_cart_cost
    else:
        assert 'min_cart_cost' not in body

    assert body['product_ids'] == matched_products

    if error_message is not None:
        assert body['error_message'] == error_message
    else:
        assert 'error_message' not in body


@pytest.mark.now(consts.NOW_TIME)
@pytest.mark.parametrize(
    'cart_cost, min_cart_cost_meta, min_cart_cost_marketing, valid',
    [
        ('100', '50', '50', True),
        ('100', '100', '50', True),
        ('100', '120', '100', False),
        ('100', '50', '100', True),
        ('100', '50', '120', True),
        ('100', None, '120', False),
        ('100', None, '50', True),
        ('100', '120', None, False),
        ('100', '50', None, True),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_min_cart_cost_from_series_meta(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
        cart_cost,
        min_cart_cost_meta,
        min_cart_cost_marketing,
        valid,
):
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    depot_id = '1337'
    matched_products = ['id_1']
    first_limit = 1
    usage_count = 0

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {
        'tag': tag,
        'matching_error_message': (
            'coupons.error_message.coffee_matching_error'
        ),
        'first_limit': first_limit,
    }

    if min_cart_cost_meta is not None:
        series_meta['min_cart_cost'] = min_cart_cost_meta

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(
        min_cart_cost=min_cart_cost_marketing,
        products=matched_products,
        usage_count=usage_count,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': cart_cost,
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    body = response.json()

    assert body['valid'] == valid
    if not valid:
        _check_error_log(pgsql, promocode, consts.ERROR_CODE_NO_MIN_CART_COST)

    if min_cart_cost_meta is not None:
        assert body['min_cart_cost'] == min_cart_cost_meta
    elif min_cart_cost_marketing is not None:
        assert body['min_cart_cost'] == min_cart_cost_marketing
    else:
        assert 'min_cart_cost' not in body

    assert body['product_ids'] == matched_products


@pytest.mark.parametrize(
    'required_items, valid',
    [
        (
            [
                {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                {'id': 'item-id-2', 'title': 'title-2', 'quantity': '1'},
            ],
            True,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777',
                    'title': 'title-1',
                    'quantity': '1',
                },
                {
                    'id': '77776666555544443333222211110000',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            True,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777item-id-1',
                    'title': 'title-1',
                    'quantity': '1',
                },
                {
                    'id': '77776666555544443333222211110000item-id-2',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            True,
        ),
        (
            [
                {'id': 'item-id-1', 'title': 'title-1', 'quantity': '2'},
                {'id': 'item-id-2', 'title': 'title-2', 'quantity': '1'},
            ],
            False,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777',
                    'title': 'title-1',
                    'quantity': '2',
                },
                {
                    'id': '77776666555544443333222211110000',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            False,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777item-id-1',
                    'title': 'title-1',
                    'quantity': '2',
                },
                {
                    'id': '77776666555544443333222211110000item-id-2',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            False,
        ),
        ([{'id': 'item-id-3', 'title': 'title-3', 'quantity': '1'}], False),
        (
            [
                {
                    'id': '01234567890123456789012345678901',
                    'title': 'title-3',
                    'quantity': '1',
                },
            ],
            False,
        ),
        (
            [
                {
                    'id': '01234567890123456789012345678901item-id-3',
                    'title': 'title-3',
                    'quantity': '1',
                },
            ],
            False,
        ),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_required_items(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        required_items,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    usage_count = 0
    items = [
        {
            'id': '00001111222233334444555566667777item-id-1',
            'quantity': '1',
            'category_ids': ['category-id-1'],
        },
        {
            'id': '77776666555544443333222211110000item-id-2',
            'quantity': '2',
            'category_ids': ['category-id-2'],
        },
    ]

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=usage_count,
        user_id=consts.YANDEX_UID,
    )

    series_meta = {'required_items': required_items}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
            'cart_items': items,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert body['error_message'] == consts.NO_REQUIRED_ITEM_ERROR.format(
            required_items[0]['title'],
        )
        _check_error_log(pgsql, promocode, consts.ERROR_CODE_NO_REQUIRED_ITEM)
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


@pytest.mark.parametrize(
    'required_items_groups, required_error_key, required_error_text,'
    'valid, failed_or_rule, failed_item',
    [
        (
            {
                'rule': 'or',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-3', 'title': 'title-3', 'quantity': '2'},
                ],
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'and',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-2', 'title': 'title-2', 'quantity': '1'},
                ],
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'or',
                'groups': [
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'item-id-1',
                                'title': 'title-1',
                                'quantity': '1',
                            },
                            {
                                'id': 'item-id-3',
                                'title': 'title-3',
                                'quantity': '1',
                            },
                        ],
                    },
                    {
                        'rule': 'or',
                        'items': [
                            {
                                'id': 'item-id-1',
                                'title': 'title-1',
                                'quantity': '1',
                            },
                            {
                                'id': 'item-id-4',
                                'title': 'title-4',
                                'quantity': '1',
                            },
                        ],
                    },
                ],
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'and',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-3', 'title': 'title-3', 'quantity': '1'},
                ],
            },
            'custom_no_required',
            None,
            False,
            False,
            'title-3',
        ),
        (
            {
                'rule': 'and',
                'groups': [
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'item-id-1',
                                'title': 'title-1',
                                'quantity': '1',
                            },
                            {
                                'id': 'item-id-2',
                                'title': 'title-2',
                                'quantity': '1',
                            },
                        ],
                    },
                    {
                        'rule': 'or',
                        'items': [
                            {
                                'id': 'item-id-1',
                                'title': 'title-1',
                                'quantity': '1',
                            },
                            {
                                'id': 'item-id-4',
                                'title': 'title-4',
                                'quantity': '1',
                            },
                        ],
                    },
                ],
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-3', 'title': 'title-3', 'quantity': '1'},
                ],
            },
            None,
            None,
            False,
            False,
            'title-3',
        ),
        (
            {
                'rule': 'or',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '10'},
                    {'id': 'item-id-3', 'title': 'title-3', 'quantity': '1'},
                ],
            },
            None,
            REQUIRED_ERROR_TEXT,
            False,
            True,
            None,
        ),
        (
            {
                'rule': 'or',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-2', 'title': 'title-3', 'quantity': '1'},
                ],
                'total_quantity': 3,
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'or',
                'items': [
                    {'id': 'item-id-1', 'title': 'title-1', 'quantity': '1'},
                    {'id': 'item-id-2', 'title': 'title-2', 'quantity': '1'},
                    {'id': 'item-id-3', 'title': 'title-3', 'quantity': '1'},
                ],
                'total_quantity': 5,
            },
            None,
            None,
            False,
            True,
            None,
        ),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_required_items_groups(
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        required_items_groups,
        required_error_key,
        required_error_text,
        valid,
        failed_or_rule,
        failed_item,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    usage_count = 0
    items = [
        {
            'id': 'item-id-1',
            'quantity': '1',
            'category_ids': ['category-id-1'],
        },
        {
            'id': 'item-id-2',
            'quantity': '2',
            'category_ids': ['category-id-2'],
        },
    ]

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=usage_count,
        user_id=consts.YANDEX_UID,
    )

    series_meta = {'required_items_groups': required_items_groups}
    if required_error_key:
        series_meta['required_error_key'] = required_error_key
    if required_error_text:
        series_meta['required_error_text'] = required_error_text

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
            'cart_items': items,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        if required_error_key:
            assert body['error_message'] == consts.CUSTOM_NO_REQUIRED_ERROR
        elif required_error_text:
            assert body['error_message'] == REQUIRED_ERROR_TEXT
        elif not failed_or_rule:
            assert body[
                'error_message'
            ] == consts.NO_REQUIRED_ITEM_ERROR.format(failed_item)
        else:
            assert (
                body['error_message'] == consts.NO_ANY_OF_REQUIRED_ITEMS_ERROR
            )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


@pytest.mark.parametrize(
    'required_categories, valid',
    [
        (
            [
                {'id': 'category-id-1', 'title': 'title-1', 'quantity': '2'},
                {'id': 'category-id-2', 'title': 'title-2', 'quantity': '1'},
            ],
            True,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777',
                    'title': 'title-1',
                    'quantity': '2',
                },
                {
                    'id': '77776666555544443333222211110000',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            True,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777category-id-1',
                    'title': 'title-1',
                    'quantity': '2',
                },
                {
                    'id': '77776666555544443333222211110000category-id-2',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            True,
        ),
        (
            [
                {'id': 'category-id-1', 'title': 'title-1', 'quantity': '3'},
                {'id': 'category-id-2', 'title': 'title-2', 'quantity': '1'},
            ],
            False,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777',
                    'title': 'title-1',
                    'quantity': '3',
                },
                {
                    'id': '77776666555544443333222211110000',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            False,
        ),
        (
            [
                {
                    'id': '00001111222233334444555566667777category-id-1',
                    'title': 'title-1',
                    'quantity': '3',
                },
                {
                    'id': '77776666555544443333222211110000category-id-2',
                    'title': 'title-2',
                    'quantity': '1',
                },
            ],
            False,
        ),
        (
            [{'id': 'category-id-3', 'title': 'title-3', 'quantity': '1'}],
            False,
        ),
        (
            [
                {
                    'id': '12345678901234567890123456789012',
                    'title': 'title-3',
                    'quantity': '1',
                },
            ],
            False,
        ),
        (
            [
                {
                    'id': '12345678901234567890123456789012category-id-3',
                    'title': 'title-3',
                    'quantity': '1',
                },
            ],
            False,
        ),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_required_categories(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        required_categories,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    usage_count = 0
    items = [
        {
            'id': 'item-id-1',
            'quantity': '1',
            'category_ids': ['00001111222233334444555566667777category-id-1'],
        },
        {
            'id': 'item-id-2',
            'quantity': '2',
            'category_ids': ['77776666555544443333222211110000category-id-2'],
        },
        {
            'id': 'item-id-3',
            'quantity': '1',
            'category_ids': ['00001111222233334444555566667777category-id-1'],
        },
    ]

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=usage_count,
        user_id=consts.YANDEX_UID,
    )

    series_meta = {'required_categories': required_categories}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
            'cart_items': items,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert (
            body['error_message']
            == consts.NO_REQUIRED_CATEGORY_ERROR.format(
                required_categories[0]['title'],
            )
        )
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_NO_REQUIRED_CATEGORY,
        )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


@pytest.mark.parametrize(
    'required_category_groups, required_error_key, required_error_text,'
    'valid, failed_or_rule, failed_item',
    [
        (
            {
                'rule': 'or',
                'items': [
                    {
                        'id': 'category-id-1',
                        'title': 'title-1',
                        'quantity': '2',
                    },
                    {
                        'id': 'category-id-2',
                        'title': 'title-2',
                        'quantity': '3',
                    },
                ],
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'and',
                'items': [
                    {
                        'id': 'category-id-1',
                        'title': 'title-1',
                        'quantity': '2',
                    },
                    {
                        'id': 'category-id-2',
                        'title': 'title-2',
                        'quantity': '3',
                    },
                ],
            },
            None,
            None,
            False,
            False,
            'title-2',
        ),
        (
            {
                'rule': 'or',
                'groups': [
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'category-id-3',
                                'title': 'title-1',
                                'quantity': '2',
                            },
                            {
                                'id': 'category-id-4',
                                'title': 'title-4',
                                'quantity': '3',
                            },
                        ],
                    },
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'category-id-1',
                                'title': 'title-1',
                                'quantity': '2',
                            },
                            {
                                'id': 'category-id-2',
                                'title': 'title-2',
                                'quantity': '3',
                            },
                        ],
                    },
                ],
                'items': [
                    {
                        'id': 'category-id-1',
                        'title': 'title-1',
                        'quantity': '2',
                    },
                    {
                        'id': 'category-id-2',
                        'title': 'title-2',
                        'quantity': '3',
                    },
                ],
            },
            None,
            None,
            True,
            False,
            None,
        ),
        (
            {
                'rule': 'and',
                'groups': [
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'category-id-3',
                                'title': 'title-3',
                                'quantity': '2',
                            },
                            {
                                'id': 'category-id-4',
                                'title': 'title-4',
                                'quantity': '3',
                            },
                        ],
                    },
                    {
                        'rule': 'and',
                        'items': [
                            {
                                'id': 'category-id-1',
                                'title': 'title-1',
                                'quantity': '2',
                            },
                            {
                                'id': 'category-id-2',
                                'title': 'title-2',
                                'quantity': '3',
                            },
                        ],
                    },
                ],
            },
            'custom_no_required',
            None,
            False,
            False,
            'title-2',
        ),
        (
            {
                'rule': 'or',
                'items': [
                    {
                        'id': 'category-id-4',
                        'title': 'title-4',
                        'quantity': '2',
                    },
                    {
                        'id': 'category-id-5',
                        'title': 'title-5',
                        'quantity': '3',
                    },
                ],
            },
            None,
            REQUIRED_ERROR_TEXT,
            False,
            True,
            None,
        ),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_required_category_groups(
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        required_category_groups,
        required_error_key,
        required_error_text,
        valid,
        failed_or_rule,
        failed_item,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    usage_count = 0
    items = [
        {
            'id': 'item-id-1',
            'quantity': '1',
            'category_ids': ['category-id-1'],
        },
        {
            'id': 'item-id-2',
            'quantity': '2',
            'category_ids': ['category-id-2'],
        },
        {
            'id': 'item-id-3',
            'quantity': '1',
            'category_ids': ['category-id-1'],
        },
    ]

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=usage_count,
        user_id=consts.YANDEX_UID,
    )

    series_meta = {'required_category_groups': required_category_groups}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    if required_error_key:
        series_meta['required_error_key'] = required_error_key
    if required_error_text:
        series_meta['required_error_text'] = required_error_text

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
            'cart_items': items,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        if required_error_key:
            assert body['error_message'] == consts.CUSTOM_NO_REQUIRED_ERROR
        elif required_error_text:
            assert body['error_message'] == REQUIRED_ERROR_TEXT
        elif not failed_or_rule:
            assert body[
                'error_message'
            ] == consts.NO_REQUIRED_CATEGORY_ERROR.format(failed_item)
        else:
            assert (
                body['error_message']
                == consts.NO_ANY_OF_REQUIRED_CATEGORY_ERROR
            )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


@pytest.mark.now(consts.NOW_TIME)
@pytest.mark.parametrize(
    'matched_products, valid, error_message',
    [
        (['id_1', 'id_2'], True, None),
        ([], False, consts.COFFEE_MATCHING_ERROR),
        (None, False, consts.COFFEE_MATCHING_ERROR),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_check_matching(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
        matched_products,
        valid,
        error_message,
):
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {
        'tag': tag,
        'matching_error_message': (
            'coupons.error_message.coffee_matching_error'
        ),
    }

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(
        products=matched_products, usage_count=1,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    body = response.json()

    assert body['valid'] == valid
    assert 'min_cart_cost' not in body

    if matched_products is not None:
        assert body['product_ids'] == matched_products
    else:
        assert 'product_ids' not in body

    if error_message is not None:
        assert body['error_message'] == error_message
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_CART_WAS_NOT_MATCHED,
        )
    else:
        assert 'error_message' not in body


@pytest.mark.now(consts.NOW_TIME)
@pytest.mark.parametrize(
    'usage_count, first_limit, valid, error_message',
    [
        (0, 1, True, None),
        (1, 4, True, None),
        (1, 1, False, consts.TAG_FIRST_LIMIT_REACHED_ERROR.format(1)),
        (2, 1, False, consts.TAG_FIRST_LIMIT_REACHED_ERROR.format(1)),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_check_first_limit(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
        usage_count,
        first_limit,
        valid,
        error_message,
):
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    depot_id = '1337'
    matched_products = ['id_1']
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {
        'tag': tag,
        'matching_error_message': (
            'coupons.error_message.coffee_matching_error'
        ),
    }

    if first_limit is not None:
        series_meta['first_limit'] = first_limit
    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(
        products=matched_products, usage_count=usage_count,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    body = response.json()

    assert body['valid'] == valid
    assert 'min_cart_cost' not in body
    assert body['product_ids'] == matched_products

    if error_message is not None:
        assert body['error_message'] == error_message
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_TAG_FIRST_LIMIT_REACHED,
        )
    else:
        assert 'error_message' not in body


@pytest.mark.now(consts.NOW_TIME)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_check_no_message(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
):
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {'tag': tag}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(usage_count=0)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    body = response.json()

    assert not body['valid']
    assert 'min_cart_cost' not in body
    assert 'product_ids' not in body
    assert body['error_message'] == consts.CART_WAS_NOT_MATCHED_ERROR
    _check_error_log(pgsql, promocode, consts.ERROR_CODE_CART_WAS_NOT_MATCHED)


@pytest.mark.parametrize(
    'series_meta, valid',
    [
        ({'tag': 'some_tag'}, True),
        ({'first_limit': [1]}, False),
        ({'unknown': 1}, True),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_series_meta(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
        series_meta,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.set_response_data(products=['id_1'])

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    if valid and 'tag' in series_meta:
        assert grocery_marketing.times_tag_check() == 1
    else:
        assert grocery_marketing.times_tag_check() == 0

    body = response.json()

    assert body['valid'] == valid

    if not valid:
        assert body['error_message'] == consts.COMMON_ERROR
        _check_error_log(pgsql, promocode, consts.ERROR_CODE_COMMON_ERROR)
    else:
        assert 'error_message' not in body


@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_check_errors(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = {'tag': 'tag_123'}
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.set_response_data(products=['id_1'])
    grocery_marketing.set_fail_tag_check(code=500)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1

    assert response.status_code == 200
    body = response.json()
    assert not body['valid']
    assert body['error_message'] == consts.COMMON_ERROR
    _check_error_log(pgsql, promocode, consts.ERROR_CODE_COMMON_ERROR)


@pytest.mark.parametrize('status_code', [400, 429])
@consts.COUPONS_ERROR_CODES
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_coupons_error_response(
        pgsql, taxi_grocery_coupons, grocery_depots, coupons, status_code,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=1111,
        timezone='+3',
    )

    coupons.set_coupons_check_response(status_code=status_code)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert coupons.check_times_called() == 1
    assert response.status_code == 200

    body = response.json()
    assert not body['valid']
    assert body['error_message'] == consts.COMMON_ERROR
    _check_error_log(
        pgsql, promocode, consts.ERROR_CODE_COMMON_ERROR, coupon_type=None,
    )
    assert 'promocode_info' not in body


@consts.COUPONS_ERROR_CODES
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize(
    'status_code, response_body',
    [
        (200, consts.PROMO_ERROR_INVALID_CODE),
        (200, consts.PROMO_ERROR_INVALID_CODE_2),
        (200, consts.PROMO_ERROR_INVALID_CODE_3),
        (400, None),
        (429, None),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_coupons_error_message_localization(
        pgsql,
        taxi_grocery_coupons,
        grocery_depots,
        coupons,
        status_code,
        locale,
        response_body,
        load_json,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=1111,
        timezone='+3',
    )

    coupons.set_coupons_check_response(
        status_code=status_code, body=response_body,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers={**consts.HEADERS, 'X-Request-Language': locale},
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert coupons.check_times_called() == 1
    assert response.status_code == 200

    localized = load_json('error_code_expected_translation.json')
    body = response.json()

    if status_code == 200:
        assert (
            body['error_message']
            == localized[response_body['error_code']][locale]
        )
        _check_error_log(pgsql, promocode, response_body['error_code'])
    else:
        assert body['error_message'] == localized[str(status_code)][locale]


@pytest.mark.parametrize(
    'region_id, region_ids, valid',
    [
        (213, None, True),
        (22, None, False),
        (None, [22, 213], True),
        (None, [21, 22], False),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_region_id(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_order_log,
        grocery_depots,
        grocery_marketing,
        region_id,
        region_ids,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_order_log.check_request(yandex_uid=consts.YANDEX_UID)

    series_meta = {'region_id': region_id, 'region_ids': region_ids}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        if region_ids:
            assert body['error_message'] == consts.REGION_ID_ERROR.format(
                region_ids,
            )
        else:
            assert body['error_message'] == consts.REGION_ID_ERROR.format(
                [region_id],
            )
        _check_error_log(pgsql, promocode, consts.ERROR_CODE_REGION_ID)
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 0


@pytest.mark.now(consts.NOW_TIME)
@pytest.mark.parametrize(
    'region_id, region_ids, valid',
    [
        (213, None, True),
        (22, None, False),
        (None, [22, 213], True),
        (None, [21, 22], False),
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_tag_region_id(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_order_log,
        grocery_depots,
        grocery_marketing,
        region_id,
        region_ids,
        valid,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    grocery_order_log.check_request(yandex_uid=consts.YANDEX_UID)
    series_meta = {
        'tag': 'some_tag',
        'region_id': region_id,
        'region_ids': region_ids,
    }
    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)
    grocery_marketing.check_request(
        tag='some_tag',
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=consts.CART_ID,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(products=['id_1'], usage_count=1)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        if region_ids:
            assert body['error_message'] == consts.REGION_ID_ERROR.format(
                region_ids,
            )
        else:
            assert body['error_message'] == consts.REGION_ID_ERROR.format(
                [region_id],
            )
        _check_error_log(pgsql, promocode, consts.ERROR_CODE_REGION_ID)
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_marketing.times_tag_check() == 1


@pytest.mark.parametrize(
    'valid, user_tag', [(True, 'allow_tag'), (False, 'restrict_tag')],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_phone_id_tag_match(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_tags,
        valid,
        user_tag,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    personal_phone_id = consts.PERSONAL_PHONE_ID
    grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag=user_tag)

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {'personal_phone_id_tag': 'allow_tag'}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert body['error_message'] == consts.USER_TAG_WAS_NOT_MATCHED
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_USER_TAG_WAS_NOT_MATCHED,
        )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_tags.bulk_match_times_called() == 1


@pytest.mark.parametrize(
    'valid, user_tag', [(True, 'allow_tag'), (False, 'restrict_tag')],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_yandex_uid_tag_match(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_tags,
        valid,
        user_tag,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'
    yandex_uid = consts.YANDEX_UID
    grocery_tags.add_yandex_uid_tag(yandex_uid=yandex_uid, tag=user_tag)

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    series_meta = {'yandex_uid_tag': 'allow_tag'}

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta

    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert body['error_message'] == consts.USER_TAG_WAS_NOT_MATCHED
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_USER_TAG_WAS_NOT_MATCHED,
        )
    else:
        assert 'error_message' not in body

    assert coupons.check_times_called() == 1
    assert grocery_tags.bulk_match_times_called() == 1


@pytest.mark.now(consts.NOW_TIME)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_excluded_discount_from_series_meta(
        pgsql, taxi_grocery_coupons, coupons, grocery_depots,
):
    promocode = 'test_promocode_01'
    depot_id = '1337'

    excluded_discounts = [{'discount_category': 'excluded_category'}]

    series_meta = {'excluded_discounts': excluded_discounts}

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '1.00',
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1

    body = response.json()

    assert body['promocode_info']['excluded_discounts'] == excluded_discounts


@pytest.mark.parametrize(
    'valid, antifraud_enabled, is_fraud,'
    'antifraud_user_profile_tagged, is_fraud_in_user_profile',
    [
        pytest.param(
            True,
            False,
            True,
            False,
            False,
            marks=consts.ANTIFRAUD_CHECK_DISABLED,
        ),
        pytest.param(
            True,
            True,
            False,
            False,
            True,
            marks=consts.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(
            False,
            True,
            False,
            True,
            True,
            marks=consts.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            False,
            marks=consts.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            False,
            True,
            True,
            True,
            False,
            marks=consts.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
    ],
)
@pytest.mark.now(consts.NOW_TIME)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_antifraud(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        antifraud,
        grocery_marketing,
        grocery_user_profiles,
        testpoint,
        valid,
        antifraud_enabled,
        is_fraud,
        antifraud_user_profile_tagged,
        is_fraud_in_user_profile,
):
    usage_count = 0
    tag = 'some_tag'
    promocode = 'test_promocode_01'
    series_id = 'test_promocode_01_id'
    depot_id = '1337'
    matched_products = ['id_1']
    first_limit = 1
    lon = 30.0
    lat = 40.0
    user_agent = 'user-agent'
    series_meta = {'first_limit': first_limit}
    cart_cost = '1.23'
    currency = 'RUB'
    city = 'city'
    street = 'street'
    house = 'house'
    flat = 'flat'
    comment = 'comment'
    cart_id = consts.CART_ID
    discount_prohibited = (
        antifraud_enabled
        and is_fraud
        or antifraud_user_profile_tagged
        and is_fraud_in_user_profile
    )

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )
    grocery_marketing.check_request(
        tag=tag,
        request_time=consts.NOW_TIME,
        depot_id=depot_id,
        cart_id=cart_id,
        cart_version=consts.CART_VERSION,
    )
    grocery_marketing.set_response_data(
        products=matched_products, usage_count=usage_count,
    )
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=usage_count,
        user_id=consts.YANDEX_UID,
    )
    antifraud.set_is_fraud(is_fraud)
    antifraud.check_discount_antifraud(
        user_id=consts.YANDEX_UID,
        user_id_service='passport',
        user_personal_phone_id=consts.PERSONAL_PHONE_ID,
        user_agent=user_agent,
        application_type='android',
        service_name='grocery',
        order_amount=cart_cost,
        order_currency=currency,
        short_address=f'{city}, {street} {house} {flat}',
        address_comment=comment,
        order_coordinates={'lat': lat, 'lon': lon},
        payment_method_id='1',
        payment_method='card',
        user_device_id=consts.APPMETRICA_DEVICE_ID,
        store_id=depot_id,
        request_source='promocode',
    )
    grocery_user_profiles.set_is_fraud(is_fraud_in_user_profile)
    grocery_user_profiles.check_info_request(
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    )
    grocery_user_profiles.check_save_request(
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
        antifraud_info={'name': 'lavka_newcomer_discount_fraud'},
    )

    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons_response['series'] = series_id
    coupons.set_coupons_check_response(body=coupons_response)

    @testpoint('yt_discount_offer_info')
    def yt_discount_offer_info(discount_offer_info):
        assert discount_offer_info['cart_id'] == cart_id
        assert discount_offer_info['doc'] == {
            'cart_id': cart_id,
            'passport_uid': consts.YANDEX_UID,
            'eats_uid': 'eats-user-id',
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'personal_email_id': '',
            'discount_allowed_by_antifraud': not discount_prohibited,
            'discount_allowed': valid,
            'discount_allowed_by_rt_xaron': not (
                antifraud_enabled and is_fraud
            ),
            'discount_allowed_by_truncated_flat': True,
            'discount_allowed_by_user_profile': not (
                antifraud_user_profile_tagged and is_fraud_in_user_profile
            ),
            'usage_count': usage_count,
            'usage_count_according_to_uid': usage_count,
            'promocode_id': series_id,
            'promocode': promocode,
        }

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': cart_id,
            'cart_version': consts.CART_VERSION,
            'cart_cost': cart_cost,
            'user_agent': user_agent,
            'position': {'location': [lon, lat]},
            'currency': currency,
            'additional_data': {
                'city': city,
                'street': street,
                'house': house,
                'flat': flat,
                'comment': comment,
            },
        },
    )

    assert response.status_code == 200

    assert coupons.check_times_called() == 1
    assert grocery_user_profiles.times_antifraud_info_called() == int(
        antifraud_user_profile_tagged,
    )
    if is_fraud and not is_fraud_in_user_profile:
        assert grocery_user_profiles.times_antifraud_save_called() == int(
            antifraud_user_profile_tagged,
        )
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )
    assert yt_discount_offer_info.times_called == 1

    body = response.json()
    assert body['valid'] == valid
    if not valid:
        assert body['error_message'] == consts.COMMON_ERROR
        _check_error_log(
            pgsql, promocode, consts.ERROR_CODE_UNKNOWN_ORDERS_COUNT,
        )
    else:
        assert 'error_message' not in body
