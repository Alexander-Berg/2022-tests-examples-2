import pytest

from tests_coupons import util


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
async def test_coupons_disabled(taxi_coupons):
    response = await taxi_coupons.post(
        'internal/activate_bulk', json={'codes': []},
    )
    assert response.status_code == 429


@pytest.mark.config(COUPONS_INTERNAL_ACTIVATE_ENABLED=False)
async def test_internal_disabled(taxi_coupons):
    response = await taxi_coupons.post(
        'internal/activate_bulk', json={'codes': []},
    )
    assert response.status_code == 429


async def test_4xx(taxi_coupons):
    response = await taxi_coupons.post('internal/activate_bulk')
    assert response.status_code == 400

    response = await taxi_coupons.post('internal/activate_bulk', {})
    assert response.status_code == 400


@pytest.mark.config(MAX_COUPONS_PER_USER=3)
@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'coupons_bulk,expected',
    [
        (
            [
                ('7001', ['first'], 'iphone'),
                ('7001', ['first', 'first', 'second'], 'android'),
                ('7002', ['second', 'third', 'second'], 'iphone'),
                ('7003', ['third'], 'yango_android'),
                ('7004', ['1', '2', '3', '4'], 'uber_iphone'),
            ],
            {
                '7001': [
                    ('yataxi', ['first', 'second']),
                    ('yango', []),
                    ('yauber', []),
                ],
                '7002': [
                    ('yataxi', ['second', 'third']),
                    ('yango', []),
                    ('yauber', []),
                ],
                '7003': [('yataxi', []), ('yango', ['third']), ('yauber', [])],
                '7004': [
                    ('yataxi', []),
                    ('yango', []),
                    ('yauber', ['1', '2', '3']),
                ],
            },
        ),
    ],
)
async def test_activated_promo(
        taxi_coupons, coupons_bulk, expected, mongodb, collections_tag,
):
    request = {'codes': []}
    for coupon_tuple in coupons_bulk:
        (yandex_uid, promocodes, application_name) = coupon_tuple
        for code in promocodes:
            request['codes'].append(
                {
                    'uid': yandex_uid,
                    'code': code,
                    'application_name': application_name,
                },
            )

    response = await taxi_coupons.post('internal/activate_bulk', json=request)
    assert response.status_code == 200

    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)

    for (yandex_uid, brand_data) in expected.items():
        for (brand_name, expected_codes) in brand_data:

            for collection in collections:
                user_coupons = collection.find_one(
                    {'yandex_uid': yandex_uid, 'brand_name': brand_name},
                )
                if user_coupons:
                    codes = [
                        promo['code'] for promo in user_coupons['promocodes']
                    ]
                else:
                    codes = []
                assert codes == expected_codes
