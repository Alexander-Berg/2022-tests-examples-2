import copy

import pytest

from tests_grocery_coupons import consts
from tests_grocery_coupons import models

CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_VERSION = 1


def _check_error_log(pgsql, coupons_errors, cart_id, coupon_type='support'):
    for coupon_error in coupons_errors:
        print(coupon_error)
        log = models.ErrorLog(
            pgsql,
            coupon=coupon_error['coupon'],
            error_code=coupon_error['error'],
            cart_id=cart_id,
            coupon_type=coupon_type,
        )
        log.compare_with_db()


def _check_no_error_log(pgsql, coupons, cart_id):
    for coupon in coupons:
        log = models.ErrorLog(pgsql, coupon=coupon, cart_id=cart_id)
        log.check_no_log()


@consts.GROCERY_MARKETING_TAG_CHECK
@pytest.mark.parametrize(
    'cart_id, skip_cart_check', [(None, True), (CART_ID, False)],
)
@pytest.mark.parametrize(
    'depot_region_id, expected_zone_name',
    [(213, consts.MOSCOW_ZONE_NAME), (2, consts.SPB_ZONE_NAME)],
)
@consts.GROCERY_COUPONS_SERIES_WITH_TAGS
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_basic(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_tags,
        grocery_depots,
        cart_id,
        skip_cart_check,
        depot_region_id,
        expected_zone_name,
):
    depot_id = '1337'
    personal_phone_id = consts.PERSONAL_PHONE_ID
    user_tag = 'team1'
    grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag=user_tag)
    excluded_discounts = [{'discount_category': 'excluded_category'}]

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        region_id=depot_region_id,
        timezone='+3',
    )

    coupons.check_list_request(
        payload={'yandex_uid': consts.YANDEX_UID},
        zone_name=expected_zone_name,
    )

    coupons.set_coupons_list_response(
        body={
            'coupons': [
                {
                    'code': 'promocode_with_tag',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'title_tanker_key_tag',
                        'subtitle': 'subtitle_tanker_key_tag',
                        'tag': 'some_tag',
                        'excluded_discounts': excluded_discounts,
                    },
                    'value': 100.0,
                    'series_id': 'promocode',
                    'expire_at': '2020-05-25T17:43:45+00:00',
                    'currency_code': 'RUB',
                    'reason_type': 'referral_reward',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'fixed_promocode',
                    'status': 'valid',
                    'value': 200.0,
                    'series_id': 'promocode',
                    'expire_at': '2020-05-25T17:43:45+00:00',
                    'currency_code': 'RUB',
                    'reason_type': 'marketing',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'fixed_promocode_without_currency',
                    'status': 'valid',
                    'value': 300.0,
                    'series_id': 'promocode',
                    'expire_at': '2020-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_with_first_limit',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'title_tanker_key_first_limit',
                        'first_limit': 1,
                    },
                    'percent': 10,
                    'limit': 1000.0,
                    'currency_code': 'RUB',
                    'series_id': 'promocode_first',
                    'expire_at': '2021-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_unknown',
                    'status': 'valid',
                    'series_meta': {'title': 'title_tanker_key_unknown'},
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_invalid',
                    'status': 'invalid',
                    'error': {
                        'code': 'NOT_EXISTS',
                        'description': 'no such promocode',
                    },
                    'series_meta': {'title': 'title_tanker_key_invalid'},
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_with_min_cart_cost',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'min_cart_cost',
                        'first_limit': 1,
                        'min_cart_cost': '500',
                    },
                    'percent': 10,
                    'currency_code': 'RUB',
                    'series_id': 'promocode_first',
                    'expire_at': '2021-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
            ],
        },
    )

    grocery_marketing.set_response_data(products=['id_1'])
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=0,
        user_id=consts.YANDEX_UID,
    )

    series_meta = {'personal_phone_id_tag': user_tag}
    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': cart_id,
            'skip_cart_check': skip_cart_check,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.couponlist_times_called() == 1
    if skip_cart_check:
        assert grocery_marketing.times_tag_check() == 0
    else:
        assert grocery_marketing.times_tag_check() == 1
    assert grocery_marketing.retrieve_v2_times_called == 2

    body = response.json()

    min_cart_promo = {
        'title': 'min_cart_cost',
        'valid': skip_cart_check,
        'promocode': 'promocode_with_min_cart_cost',
        'type': 'percent',
        'value': '10',
        'currency_code': 'RUB',
        'series_id': 'promocode_first',
        'expire_at': '2021-05-25T17:43:45+00:00',
        'min_cart_cost': '500',
    }
    if not skip_cart_check:
        min_cart_promo[
            'error_message'
        ] = 'Стоимость корзины меньше, чем 500 RUB'

    assert body == {
        'coupons': [
            {
                'title': 'Скидка 100 рублей на заказы с кофе',
                'subtitle': '10% скидка',
                'valid': True,
                'promocode': 'promocode_with_tag',
                'type': 'fixed',
                'value': '100',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'currency_code': 'RUB',
                'reason_type': 'referral_reward',
                'excluded_discounts': excluded_discounts,
            },
            {
                'title': 'Скидка 200 ₽',
                'valid': True,
                'promocode': 'fixed_promocode',
                'type': 'fixed',
                'value': '200',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'currency_code': 'RUB',
                'reason_type': 'marketing',
            },
            {
                'valid': True,
                'promocode': 'fixed_promocode_without_currency',
                'type': 'fixed',
                'value': '300',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
            },
            {
                'title': 'Скидка 100 рублей на первый заказ',
                'valid': True,
                'promocode': 'promocode_with_first_limit',
                'type': 'percent',
                'value': '10',
                'limit': '1000',
                'currency_code': 'RUB',
                'series_id': 'promocode_first',
                'expire_at': '2021-05-25T17:43:45+00:00',
            },
            {
                'title': 'Скидка 10%',
                'valid': True,
                'promocode': 'promocode_unknown',
            },
            {
                'title': 'title_tanker_key_invalid',
                'valid': False,
                'promocode': 'promocode_invalid',
                'error_message': 'Не удалось применить данный промокод',
            },
            min_cart_promo,
            {
                'valid': True,
                'promocode': 'promotag1',
                'type': 'percent',
                'value': '30',
                'limit': '100',
                'currency_code': 'RUB',
            },
        ],
    }

    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count',
        usage_count=1,
        user_id=consts.YANDEX_UID,
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': cart_id,
            'skip_cart_check': skip_cart_check,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body == {
        'coupons': [
            {
                'title': 'Скидка 100 рублей на заказы с кофе',
                'subtitle': '10% скидка',
                'valid': True,
                'promocode': 'promocode_with_tag',
                'type': 'fixed',
                'value': '100',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'currency_code': 'RUB',
                'reason_type': 'referral_reward',
                'excluded_discounts': excluded_discounts,
            },
            {
                'title': 'Скидка 200 ₽',
                'valid': True,
                'promocode': 'fixed_promocode',
                'type': 'fixed',
                'value': '200',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'currency_code': 'RUB',
                'reason_type': 'marketing',
            },
            {
                'valid': True,
                'promocode': 'fixed_promocode_without_currency',
                'type': 'fixed',
                'value': '300',
                'series_id': 'promocode',
                'expire_at': '2020-05-25T17:43:45+00:00',
            },
            {
                'title': 'Скидка 100 рублей на первый заказ',
                'valid': False,
                'promocode': 'promocode_with_first_limit',
                'type': 'percent',
                'value': '10',
                'limit': '1000',
                'currency_code': 'RUB',
                'series_id': 'promocode_first',
                'expire_at': '2021-05-25T17:43:45+00:00',
                'error_message': (
                    'Промокод действует только на первые 1 заказа'
                ),
            },
            {
                'title': 'Скидка 10%',
                'valid': True,
                'promocode': 'promocode_unknown',
            },
            {
                'title': 'title_tanker_key_invalid',
                'valid': False,
                'promocode': 'promocode_invalid',
                'error_message': 'Не удалось применить данный промокод',
            },
            {
                'title': 'min_cart_cost',
                'valid': False,
                'promocode': 'promocode_with_min_cart_cost',
                'type': 'percent',
                'value': '10',
                'currency_code': 'RUB',
                'series_id': 'promocode_first',
                'expire_at': '2021-05-25T17:43:45+00:00',
                'min_cart_cost': '500',
                'error_message': (
                    'Промокод действует только на первые 1 заказа'
                ),
            },
            {
                'valid': True,
                'promocode': 'promotag1',
                'type': 'percent',
                'value': '30',
                'limit': '100',
                'currency_code': 'RUB',
            },
        ],
    }

    coupons_errors = [
        {'coupon': 'promocode_invalid', 'error': 'NOT_EXISTS'},
        {
            'coupon': 'promocode_with_first_limit',
            'error': consts.ERROR_CODE_ORDERS_FIRST_LIMIT_REACHED,
        },
    ]

    if not skip_cart_check:
        coupons_errors.append(
            {
                'coupon': 'promocode_with_min_cart_cost',
                'error': consts.ERROR_CODE_NO_MIN_CART_COST,
            },
        )

    if cart_id:
        _check_error_log(pgsql, coupons_errors, cart_id, coupon_type=None)


@consts.GROCERY_COUPONS_SERIES_WITH_TAGS
@consts.GROCERY_COUPONS_ZONE_NAME
@pytest.mark.parametrize(
    'cart_id, skip_cart_check', [(None, True), (CART_ID, False)],
)
@pytest.mark.parametrize('is_valid', [True, False])
async def test_personal_promocodes(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_tags,
        grocery_depots,
        cart_id,
        skip_cart_check,
        is_valid,
):
    depot_id = '1337'
    personal_phone_id = consts.PERSONAL_PHONE_ID
    grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag='team1')

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    series_meta = {'personal_phone_id_tag': 'team1' if is_valid else 'team2'}
    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': cart_id,
            'skip_cart_check': skip_cart_check,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1

    body = response.json()
    if is_valid:
        assert body == {
            'coupons': [
                {
                    'valid': True,
                    'promocode': 'promotag1',
                    'type': 'percent',
                    'value': '30',
                    'limit': '100',
                    'currency_code': 'RUB',
                },
            ],
        }
    else:
        assert body == {'coupons': []}
    _check_error_log(pgsql, [], cart_id, coupon_type=None)


@pytest.mark.parametrize('country', ['rus', 'isr'])
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_country_passed_to_coupons(
        taxi_grocery_coupons, grocery_depots, mockserver, country,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3=country,
        region_id=213,
        timezone='+3',
    )

    country_json = {'country': country}
    depot_id_json = {'depot_id': depot_id}

    expected_request = {
        **country_json,
        'payload': {'yandex_uid': consts.YANDEX_UID},
        'payment': {'type': ''},
        'service': 'grocery',
        'services': ['grocery'],
        'zone_name': 'moscow',
    }

    @mockserver.json_handler('/coupons/internal/couponlist')
    def mock_check_request_contents(request):
        assert request.json == expected_request
        return {'coupons': []}

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={'skip_cart_check': True, **depot_id_json},
    )

    assert response.status == 200
    assert mock_check_request_contents.times_called == 1
    assert response.json()['coupons'] == []


@consts.GROCERY_COUPONS_BRAND_NAMES
@consts.GROCERY_COUPONS_ZONE_NAME
@pytest.mark.parametrize(
    'app_name, brand_names',
    [('lavka_app', {'lavka', 'yataxi'}), ('yangodeli_android', {'yangodeli'})],
)
async def test_brand_names_passed_to_coupons(
        taxi_grocery_coupons,
        grocery_depots,
        mockserver,
        app_name,
        brand_names,
):
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id='legacy_depot',
        country_iso3='RUS',
        timezone='+3',
    )

    @mockserver.json_handler('/coupons/internal/couponlist')
    def mock_check_request_contents(request):
        assert set(request.json['brand_names']) == brand_names
        return {'coupons': []}

    headers = copy.deepcopy(consts.HEADERS)
    headers['X-Request-Application'] = f'app_name={app_name}'

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=headers,
        json={'skip_cart_check': True, 'depot_id': 'legacy_depot'},
    )

    assert response.status == 200
    assert mock_check_request_contents.times_called == 1
    assert response.json()['coupons'] == []


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 2,
        },
    },
)
@consts.GROCERY_MARKETING_TAG_CHECK
@consts.GROCERY_COUPONS_ZONE_NAME
@consts.COUPONS_ERROR_CODES
@consts.GROCERY_COUPONS_FATAL_ERRORS
async def test_error_from_coupons(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_marketing,
        grocery_depots,
):
    error_codes = [
        'ERROR_CREDITCARD_REQUIRED',
        'ERROR_NOT_FOUND',
        'ERROR_ORDERS_FIRST_LIMIT_REACHED',
        'ERROR_LESS_THAN_MIN_CART_COST',
    ]
    depot_id = '1337'
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(
        body={
            'coupons': [
                {
                    'code': 'promocode_invalid',
                    'status': 'invalid',
                    'error': {
                        'code': error_codes[0],
                        'description': 'Card payment isn\'t selected',
                    },
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_invalid1',
                    'status': 'invalid',
                    'error': {
                        'code': error_codes[1],
                        'description': 'Promocode was not found',
                    },
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_invalid2',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'title_tanker_key_first_limit',
                        'first_limit': 1,
                    },
                    'percent': 10,
                    'limit': 1000.0,
                    'currency_code': 'RUB',
                    'series_id': 'promocode_first',
                    'expire_at': '2021-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_invalid3',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'title_tanker_key_min_cart_cost',
                        'min_cart_cost': '120',
                    },
                    'percent': 10,
                    'limit': 1000.0,
                    'currency_code': 'RUB',
                    'series_id': 'promocode_min_cart',
                    'expire_at': '2021-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
                {
                    'code': 'promocode_valid',
                    'status': 'valid',
                    'percent': 10,
                    'limit': 1000.0,
                    'currency_code': 'RUB',
                    'series_id': 'promocode_valid',
                    'expire_at': '2021-05-25T17:43:45+00:00',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
            ],
        },
    )

    grocery_marketing.set_response_data(products=['id_1'], min_cart_cost='10')
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=3,
        user_id=consts.YANDEX_UID,
    )

    grocery_marketing.add_payment_id_tag(
        tag_name='total_paid_orders_count', usage_count=3, payment_id='1',
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'skip_cart_check': False,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200

    assert coupons.couponlist_times_called() == 1

    body = response.json()

    assert body == {
        'coupons': [
            {
                'valid': False,
                'promocode': 'promocode_invalid',
                'error_message': 'Нужно выбрать способ оплаты',
            },
            {
                'currency_code': 'RUB',
                'error_message': 'Стоимость корзины меньше, чем 120 RUB',
                'expire_at': '2021-05-25T17:43:45+00:00',
                'limit': '1000',
                'min_cart_cost': '120',
                'promocode': 'promocode_invalid3',
                'series_id': 'promocode_min_cart',
                'title': 'title_tanker_key_min_cart_cost',
                'type': 'percent',
                'valid': False,
                'value': '10',
            },
            {
                'currency_code': 'RUB',
                'expire_at': '2021-05-25T17:43:45+00:00',
                'limit': '1000',
                'promocode': 'promocode_valid',
                'series_id': 'promocode_valid',
                'type': 'percent',
                'valid': True,
                'value': '10',
            },
        ],
    }
    _check_error_log(
        pgsql,
        [
            {'coupon': 'promocode_invalid', 'error': error_codes[0]},
            {'coupon': 'promocode_invalid1', 'error': error_codes[1]},
            {'coupon': 'promocode_invalid2', 'error': error_codes[2]},
            {'coupon': 'promocode_invalid3', 'error': error_codes[3]},
        ],
        CART_ID,
        coupon_type=None,
    )
    _check_no_error_log(pgsql, ['promocode_valid'], CART_ID)
