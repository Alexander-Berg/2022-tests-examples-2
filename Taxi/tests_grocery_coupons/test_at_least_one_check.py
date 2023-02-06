import copy

import pytest

from tests_grocery_coupons import consts


SAVING_COUPONS_DISABLED = consts.grocery_coupons_save_coupons()


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 2,
        },
    },
)
@pytest.mark.parametrize(
    'at_least_one',
    [
        {'first_limit': 2, 'min_cart_cost': '5000.0000'},
        {'first_limit': 1, 'yandex_uid_tag': 'allow_tag'},
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_basic(
        pgsql,
        taxi_grocery_coupons,
        grocery_depots,
        coupons,
        grocery_tags,
        grocery_marketing,
        at_least_one,
):
    promocode = 'test_promocode_01'
    country = 'RUS'
    depot_id = '1337'
    yandex_uid = consts.YANDEX_UID
    user_tag = 'allow_tag'

    grocery_tags.add_yandex_uid_tag(yandex_uid=yandex_uid, tag=user_tag)
    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count', usage_count=1, user_id=yandex_uid,
    )
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3=country,
        region_id=213,
        timezone=consts.MOSCOW_ZONE_NAME,
    )

    series_meta = {'at_least_one': at_least_one}

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

    assert coupons.check_times_called() == 1
    assert response.status_code == 200
    body = response.json()

    assert body['valid'] is True


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 2,
        },
    },
)
@pytest.mark.parametrize(
    'at_least_one',
    [
        {'first_limit': 1, 'min_cart_cost': '5000.0000'},
        {'first_limit': 1, 'yandex_uid_tag': 'restrict_tag'},
    ],
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_no_checks_were_passed(
        pgsql,
        taxi_grocery_coupons,
        grocery_depots,
        coupons,
        grocery_tags,
        grocery_marketing,
        at_least_one,
):
    promocode = 'test_promocode_01'
    country = 'RUS'
    depot_id = '1337'
    yandex_uid = consts.YANDEX_UID
    user_tag = 'allow_tag'

    grocery_tags.add_yandex_uid_tag(yandex_uid=yandex_uid, tag=user_tag)
    grocery_marketing.add_user_tag(
        tag_name='total_paid_orders_count', usage_count=1, user_id=yandex_uid,
    )
    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3=country,
        region_id=213,
        timezone=consts.MOSCOW_ZONE_NAME,
    )

    series_meta = {'at_least_one': at_least_one}

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

    assert coupons.check_times_called() == 1
    assert response.status_code == 200
    body = response.json()

    assert body['valid'] is False


@consts.GROCERY_COUPONS_SERIES_WITH_TAGS
@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 2,
        },
    },
)
@consts.GROCERY_COUPONS_ZONE_NAME
@SAVING_COUPONS_DISABLED
async def test_coupons_list_with_tag(
        pgsql,
        taxi_grocery_coupons,
        grocery_depots,
        coupons,
        grocery_tags,
        grocery_marketing,
):
    user_tag = 'team1'
    depot_id = '1337'
    cart_id = '00000000-0000-0000-0000-d98013100500'
    cart_version = 1
    skip_cart_check = False
    personal_phone_id = consts.PERSONAL_PHONE_ID
    grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag=user_tag)

    series_meta = {'at_least_one': {'personal_phone_id_tag': user_tag}}
    coupons_response = copy.deepcopy(consts.VALID_PROMOCODE)
    coupons_response['series_meta'] = series_meta
    coupons.set_coupons_check_response(body=coupons_response)
    coupons.set_coupons_list_response(body={'coupons': []})

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        legacy_depot_id=depot_id,
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/list',
        headers=consts.HEADERS,
        json={
            'depot_id': depot_id,
            'payment_info': {'payment_method_id': '1', 'type': 'card'},
            'cart_id': cart_id,
            'skip_cart_check': skip_cart_check,
            'cart_version': cart_version,
            'cart_cost': '100',
        },
    )
    assert response.status_code == 200

    body = response.json()
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
