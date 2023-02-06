from tests_grocery_coupons import consts
from tests_grocery_coupons import models

DEPOT_ID = '1337'


def _add_depot(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(DEPOT_ID),
        legacy_depot_id=DEPOT_ID,
        country_iso3='RUS',
        region_id=213,
        timezone='+3',
    )


async def _make_check_request(taxi_grocery_coupons, promocode):
    return await taxi_grocery_coupons.post(
        '/internal/v1/coupons/check',
        headers=consts.HEADERS,
        json={
            'promocode': promocode,
            'depot_id': DEPOT_ID,
            'payment_info': {'method_id': '1', 'type': 'card'},
            'cart_id': consts.CART_ID,
            'cart_version': consts.CART_VERSION,
            'cart_cost': '100',
        },
    )


@consts.grocery_coupons_save_coupons()
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_disabled_by_config(
        pgsql, taxi_grocery_coupons, grocery_depots, coupons,
):
    promocode = 'test_promocode_01'

    _add_depot(grocery_depots)

    coupons.set_coupons_check_response(body=consts.VALID_PROMOCODE)

    response = await _make_check_request(taxi_grocery_coupons, promocode)
    assert response.json()['valid']

    saved_coupons = models.get_user_coupons(
        pgsql, consts.HEADERS['X-Yandex-UID'],
    )
    assert not saved_coupons


@consts.grocery_coupons_save_coupons(coupon_types=['support'])
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_valid_coupon_saved(
        pgsql, taxi_grocery_coupons, grocery_depots, coupons,
):
    promocode = 'test_promocode_01'

    _add_depot(grocery_depots)

    coupons.set_coupons_check_response(body=consts.VALID_PROMOCODE)

    response = await _make_check_request(taxi_grocery_coupons, promocode)
    assert response.json()['valid']

    saved_coupons = models.get_user_coupons(
        pgsql, consts.HEADERS['X-Yandex-UID'],
    )

    assert len(saved_coupons) == 1
    assert saved_coupons[0].coupon == promocode
    assert saved_coupons[0].yandex_uid == consts.HEADERS['X-Yandex-UID']
    assert saved_coupons[0].personal_phone_id == consts.PERSONAL_PHONE_ID


@consts.grocery_coupons_save_coupons(coupon_types=['support'])
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_idempotency(
        pgsql, taxi_grocery_coupons, grocery_depots, coupons,
):
    promocode = 'test_promocode_01'

    _add_depot(grocery_depots)

    coupons.set_coupons_check_response(body=consts.VALID_PROMOCODE)

    response = await _make_check_request(taxi_grocery_coupons, promocode)
    assert response.json()['valid']

    response = await _make_check_request(taxi_grocery_coupons, promocode)
    assert response.json()['valid']

    saved_coupons = models.get_user_coupons(
        pgsql, consts.HEADERS['X-Yandex-UID'],
    )

    assert len(saved_coupons) == 1
    assert saved_coupons[0].coupon == promocode
    assert saved_coupons[0].yandex_uid == consts.HEADERS['X-Yandex-UID']
    assert saved_coupons[0].personal_phone_id == consts.PERSONAL_PHONE_ID


@consts.grocery_coupons_save_coupons(coupon_types=['support'])
@consts.GROCERY_COUPONS_ZONE_NAME
async def test_invalid_coupon_not_saved(
        pgsql, taxi_grocery_coupons, grocery_depots, coupons,
):
    promocode = 'test_promocode_01'

    _add_depot(grocery_depots)

    coupons.set_coupons_check_response(body=consts.PROMO_ERROR_INVALID_CODE)

    response = await _make_check_request(taxi_grocery_coupons, promocode)
    assert not response.json()['valid']

    saved_coupons = models.get_user_coupons(
        pgsql, consts.HEADERS['X-Yandex-UID'],
    )
    assert not saved_coupons
