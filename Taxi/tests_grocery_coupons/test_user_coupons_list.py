import copy

import pytest

from tests_grocery_coupons import consts
from tests_grocery_coupons import models

CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_VERSION = 1


def _check_error_log(pgsql, coupons_errors, cart_id, coupon_type='support'):
    for coupon_error in coupons_errors:
        log = models.ErrorLog(
            pgsql,
            coupon=coupon_error['coupon'],
            error_code=coupon_error['error'],
            cart_id=cart_id,
            coupon_type=coupon_type,
        )
        log.compare_with_db()


@consts.grocery_coupons_show_saved(enabled=False)
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_disabled_by_config(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    models.UserCoupon(
        pgsql=pgsql,
        coupon='saved_coupon',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 0
    assert grocery_marketing.retrieve_v2_times_called == 0
    body = response.json()

    assert body == {'coupons': []}

    assert len(models.get_user_coupons(pgsql, consts.YANDEX_UID)) == 1


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_saved_coupons(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
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
            ],
        },
    )

    coupons_response = copy.deepcopy(consts.VALID_FIXED_PROMOCODE)
    coupons_response['series_meta'] = {'first_limit': 1}
    coupons.set_coupons_check_response(body=coupons_response)

    models.UserCoupon(
        pgsql=pgsql,
        coupon='saved_coupon',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    models.UserCoupon(
        pgsql=pgsql,
        coupon='saved_coupon_2',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 2
    assert grocery_marketing.retrieve_v2_times_called == 2
    body = response.json()
    assert body == {
        'coupons': [
            {
                'currency_code': 'RUB',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'promocode': 'fixed_promocode',
                'reason_type': 'marketing',
                'series_id': 'promocode',
                'title': 'Скидка 200 ₽',
                'type': 'fixed',
                'valid': True,
                'value': '200',
            },
            {
                'currency_code': 'RUB',
                'expire_at': '2020-03-01T00:00:00+00:00',
                'limit': '100',
                'promocode': 'saved_coupon',
                'type': 'fixed',
                'title': 'Скидка 100 ₽',
                'valid': True,
                'value': '100',
            },
            {
                'currency_code': 'RUB',
                'expire_at': '2020-03-01T00:00:00+00:00',
                'limit': '100',
                'promocode': 'saved_coupon_2',
                'type': 'fixed',
                'title': 'Скидка 100 ₽',
                'valid': True,
                'value': '100',
            },
        ],
    }

    assert len(models.get_user_coupons(pgsql, consts.YANDEX_UID)) == 2


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_saved_coupons_same_coupon(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
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
            ],
        },
    )

    coupons_response = copy.deepcopy(consts.VALID_FIXED_PROMOCODE)
    coupons_response['series_meta'] = {'first_limit': 1}
    coupons.set_coupons_check_response(body=coupons_response)

    models.UserCoupon(
        pgsql=pgsql,
        coupon='fixed_promocode',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 0
    assert grocery_marketing.retrieve_v2_times_called == 0
    body = response.json()
    assert body == {
        'coupons': [
            {
                'currency_code': 'RUB',
                'expire_at': '2020-05-25T17:43:45+00:00',
                'promocode': 'fixed_promocode',
                'reason_type': 'marketing',
                'series_id': 'promocode',
                'title': 'Скидка 200 ₽',
                'type': 'fixed',
                'valid': True,
                'value': '200',
            },
        ],
    }

    assert len(models.get_user_coupons(pgsql, consts.YANDEX_UID)) == 1


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
@consts.GROCERY_COUPONS_FATAL_ERRORS
@pytest.mark.parametrize(
    'invalid_promocode',
    [consts.PROMO_ERROR_INVALID_CODE, consts.PROMO_ERROR_INVALID_CODE_2],
)
async def test_saved_coupons_not_valid_forever(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
        invalid_promocode,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    coupons_response = copy.deepcopy(invalid_promocode)
    coupons.set_coupons_check_response(body=coupons_response)

    models.UserCoupon(
        pgsql=pgsql,
        coupon='fixed_promocode',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 1
    assert grocery_marketing.retrieve_v2_times_called == 0
    body = response.json()
    assert body == {'coupons': []}

    assert not models.get_user_coupons(pgsql, consts.YANDEX_UID)

    coupons_errors = [
        {
            'coupon': 'fixed_promocode',
            'error': invalid_promocode['error_code'],
        },
    ]

    _check_error_log(pgsql, coupons_errors, CART_ID, coupon_type='support')


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_saved_coupons_can_be_valid(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    coupons_response = copy.deepcopy(consts.PROMO_ERROR_INVALID_CODE_3)
    coupons.set_coupons_check_response(body=coupons_response)

    models.UserCoupon(
        pgsql=pgsql,
        coupon='fixed_promocode',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 1
    assert grocery_marketing.retrieve_v2_times_called == 0
    body = response.json()
    assert body == {
        'coupons': [
            {
                'currency_code': '',
                'error_message': 'Не удалось применить данный промокод',
                'expire_at': '2020-03-01T00:00:00+00:00',
                'promocode': 'fixed_promocode',
                'title': 'Скидка 100 ',
                'type': 'fixed',
                'valid': False,
                'value': '100',
            },
        ],
    }

    assert len(models.get_user_coupons(pgsql, consts.YANDEX_UID)) == 1

    coupons_errors = [
        {
            'coupon': 'fixed_promocode',
            'error': consts.PROMO_ERROR_INVALID_CODE_3['error_code'],
        },
    ]

    _check_error_log(pgsql, coupons_errors, CART_ID, coupon_type='support')


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
@consts.GROCERY_COUPONS_FATAL_ERRORS
async def test_saved_coupons_first_limit(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    coupons_response = copy.deepcopy(consts.VALID_FIXED_PROMOCODE)
    coupons_response['series_meta'] = {'first_limit': 1}
    coupons.set_coupons_check_response(body=coupons_response)

    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=2,
        user_id=consts.YANDEX_UID,
    )

    models.UserCoupon(
        pgsql=pgsql,
        coupon='fixed_promocode',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 1
    assert grocery_marketing.retrieve_v2_times_called == 1
    body = response.json()
    assert body == {'coupons': []}

    assert not models.get_user_coupons(pgsql, consts.YANDEX_UID)

    coupons_errors = [
        {
            'coupon': 'fixed_promocode',
            'error': 'ERROR_ORDERS_FIRST_LIMIT_REACHED',
        },
    ]

    _check_error_log(pgsql, coupons_errors, CART_ID, coupon_type='support')


@consts.grocery_coupons_show_saved()
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_same_coupon_different_uid(
        pgsql,
        taxi_grocery_coupons,
        coupons,
        grocery_depots,
        grocery_marketing,
):
    depot_id = '1337'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        timezone='+3',
    )

    coupons.set_coupons_list_response(body={'coupons': []})

    coupons.set_coupons_check_response(body=consts.VALID_FIXED_PROMOCODE)

    models.UserCoupon(
        pgsql=pgsql,
        coupon='saved_coupon',
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    models.UserCoupon(
        pgsql=pgsql,
        coupon='saved_coupon',
        yandex_uid=consts.YANDEX_UID + '_new',
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    ).save()

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': CART_ID,
            'cart_version': CART_VERSION,
            'cart_cost': '100',
        },
    )

    assert response.status_code == 200
    assert coupons.couponlist_times_called() == 1
    assert coupons.check_times_called() == 1

    body = response.json()
    assert body == {
        'coupons': [
            {
                'currency_code': 'RUB',
                'expire_at': '2020-03-01T00:00:00+00:00',
                'limit': '100',
                'promocode': 'saved_coupon',
                'type': 'fixed',
                'title': 'Скидка 100 ₽',
                'valid': True,
                'value': '100',
            },
        ],
    }

    assert len(models.get_user_coupons(pgsql, consts.YANDEX_UID)) == 1
