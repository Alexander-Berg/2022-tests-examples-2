import pytest

from tests_grocery_coupons import consts


@pytest.mark.config(GROCERY_COUPONS_ALWAYS_DO_EXTERNAL_VALIDATION=False)
async def test_product_category(taxi_grocery_coupons):
    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/validate',
        headers=consts.HEADERS,
        json={
            'coupon_id': 'LAVKA_SELF_ISOLATION_100',
            'external_ref': 'lavka:cart:44455',
            'series_meta': {
                'product_ids': ['beer'],
                'category_ids': ['snacks'],
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {
        'valid': True,
        'valid_any': True,
        'descriptions': [],
        'details': [],
    }


@pytest.mark.config(GROCERY_COUPONS_ALWAYS_DO_EXTERNAL_VALIDATION=False)
@pytest.mark.parametrize(
    'first_limit,orders_count,expected_valid',
    [(4, 2, True), (1, 0, True), (3, 3, False), (1, 2, False)],
)
async def test_first_limit(
        taxi_grocery_coupons,
        grocery_order_log,
        first_limit,
        orders_count,
        expected_valid,
):
    grocery_order_log.set_not_canceled_orders_count(orders_count)

    grocery_order_log.check_request(yandex_uid='555')

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/validate',
        headers=consts.HEADERS,
        json={
            'coupon_id': 'LAVKA_SELF_ISOLATION_100',
            'external_ref': 'sdh732nedksaf',
            'series_meta': {'first_limit': first_limit},
        },
    )
    assert response.status_code == 200
    response = response.json()

    assert response['valid'] == expected_valid
    assert response['valid_any'] == expected_valid
    if not expected_valid:
        assert 'error_description' in response
        assert response['error_code'] == 'first_limit_exceeded'


@pytest.mark.config(GROCERY_COUPONS_ALWAYS_DO_EXTERNAL_VALIDATION=False)
async def test_first_limit_payload_yandex_uid(
        taxi_grocery_coupons, grocery_order_log,
):
    yandex_uid = '1234'

    grocery_order_log.set_not_canceled_orders_count(2)
    grocery_order_log.check_request(yandex_uid=yandex_uid)

    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/validate',
        headers={'X-Request-Language': 'ru'},
        json={
            'coupon_id': 'LAVKA_SELF_ISOLATION_100',
            'external_ref': 'sdh732nedksaf',
            'series_meta': {'first_limit': 3},
            'payload': {'yandex_uid': yandex_uid},
        },
    )
    assert response.status_code == 200
    response = response.json()

    assert response['valid']
    assert response['valid_any']


@pytest.mark.config(GROCERY_COUPONS_ALWAYS_DO_EXTERNAL_VALIDATION=True)
async def test_always_validate(taxi_grocery_coupons):
    response = await taxi_grocery_coupons.post(
        '/internal/v1/coupons/validate',
        headers={'X-Request-Language': 'ru'},
        json={
            'coupon_id': 'LAVKA_SELF_ISOLATION_100',
            'external_ref': 'sdh732nedksaf',
            'series_meta': {'first_limit': 3},
            'payload': {'yandex_uid': '111'},
        },
    )
    assert response.status_code == 200
    response = response.json()

    assert response['valid']
    assert response['valid_any']
