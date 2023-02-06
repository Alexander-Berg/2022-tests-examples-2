import pytest

from tests_eats_coupons import conftest
from . import experiments
from . import utils


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_4xx(taxi_eats_coupons):
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=None,
    )
    assert response.status_code == 400

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json={},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    ('exp_code', 'exp_resp'),
    [
        (
            200,
            {
                'valid': True,
                'valid_any': True,
                'descriptions': [],
                'details': [],
                'error_code': 'SKIPPED_VALIDATION',
            },
        ),
    ],
)
async def test_validate(taxi_eats_coupons, exp_code, exp_resp):
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json={
            'coupon_id': 'EATS_TEST_PROMO',
            'series_id': 'series_id_1',
            'source_handler': 'check',
        },
        headers=conftest.HEADERS,
    )
    assert response.status_code == exp_code
    response = response.json()
    assert response == exp_resp


@pytest.mark.parametrize(
    ('exp_code', 'exp_resp'),
    [
        (
            200,
            {
                'descriptions': [],
                'details': [],
                'error_code': 'SKIPPED_VALIDATION',
                'valid': True,
                'valid_any': True,
            },
        ),
    ],
)
async def test_validate_non_authorized(taxi_eats_coupons, exp_code, exp_resp):
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json={
            'coupon_id': 'EATS_TEST_PROMO',
            'series_id': 'series_id_1',
            'source_handler': 'check',
        },
    )
    assert response.status_code == exp_code
    response = response.json()
    assert response == exp_resp


@experiments.eats_coupons_validators(
    [
        'birthday-validator',
        'brand-validator',
        'device-model-validator',
        'minimal-cart-validator',
        'native-validator',
        'partner-validator',
        'place-validator',
        'shipping-type-validator',
        'first-order-in-services-and-apps-validator',
        'exclude-places-validator',
        'exclude-brand-validator',
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    ('exp_code', 'exp_req', 'exp_resp'),
    [
        (
            200,
            {
                'coupon_id': 'ID1',
                'series_id': 'series_id_1',
                'series_meta': {'birthday': True},
                'payload': {'birthday': '2019-03-07'},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'ID2',
                'series_id': 'series_id_1',
                'series_meta': {'brand-ids': [1, 2]},
                'payload': {'brand_id': 1},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID3',
                'series_id': 'series_id_1',
                'series_meta': {'device-models': ['model1', 'model2']},
                'payload': {'device-model': 'model2'},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'ID4',
                'series_id': 'series_id_1',
                'series_meta': {'minimal_cart': 800},
                'payload': {'cart_total': 1000},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID4',
                'series_id': 'series_id_1',
                'series_meta': {'minimal_cart': 800},
                'payload': {'cart_total': 1000.95},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID5',
                'series_id': 'series_id_1',
                'series_meta': {'brand-types': ['brand1', 'brand2']},
                'payload': {'brand-type': 'brand2'},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'ID6',
                'series_id': 'series_id_1',
                'series_meta': {'partners': ['partner1', 'partner2']},
                'payload': {'partner': 'partner2'},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'ID7',
                'series_id': 'series_id_1',
                'series_meta': {'places-ids': [1, 2]},
                'payload': {'place_id': 1},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID8',
                'series_id': 'series_id_1',
                'series_meta': {'shipping-types': ['st1', 'st2']},
                'payload': {'shipping_type': 'st2'},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID10',
                'series_id': 'series_id_1',
                'series_meta': {'first_order_in_apps': True},
                'payload': {'app': 'app1', 'service': 'serv1'},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'ID13',
                'series_id': 'series_id_1',
                'series_meta': {
                    'place_exclude_ids': ['place_id-1', 'place_id-2'],
                },
                'payload': {'place_id': 'place_id-2'},
                'source_handler': 'check',
            },
            utils.create_response(
                False, True, 'EXCLUDE_PLACES_VALIDATION_FAILURE',
            ),
        ),
        (
            200,
            {
                'coupon_id': 'ID13',
                'series_id': 'series_id_1',
                'series_meta': {
                    'place_exclude_ids': ['place_id-1', 'place_id-2'],
                },
                'payload': {'place_id': 'other_place_id'},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'ID14',
                'series_id': 'series_id_1',
                'series_meta': {'exclude-brand-ids': [324, 123]},
                'payload': {'brand_id': 123},
                'source_handler': 'check',
            },
            utils.create_response(
                False,
                True,
                'BRAND_EXCLUDE_VALIDATOR_FAILURE',
                'В этом бренде нельзя применить промокод',
            ),
        ),
        (
            200,
            {
                'coupon_id': 'prom123',
                'series_id': 'series_id_1',
                'series_meta': {'db_validation': True},
                'payload': {'place_id': 1},
                'source_handler': 'check',
            },
            utils.create_response(True, True),
        ),
        (
            200,
            {
                'coupon_id': 'prom123',
                'series_id': 'series_id_1',
                'series_meta': {'db_validation': False},
                'payload': {'place_id': 1},
                'source_handler': 'check',
            },
            utils.create_response(True, True, 'SKIPPED_VALIDATION'),
        ),
        (
            200,
            {
                'coupon_id': 'prom123',
                'series_id': 'series_id_1',
                'series_meta': {'db_validation': True},
                'payload': {'place_id': 3},
                'source_handler': 'check',
            },
            utils.create_response(
                False,
                True,
                'NO_SUITABLE_PLACES',
                'В этом плейсе нельзя применить промокод',
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'use_glue_uids',
    [
        pytest.param(False, id='no_glue_uids'),
        pytest.param(
            True,
            marks=experiments.use_glue_uids(),
            id='invalid_promocode_wo_code_domain',
        ),
    ],
)
async def test_all_validators(
        mock_core_client,
        taxi_config,
        taxi_eats_coupons,
        exp_code,
        exp_req,
        exp_resp,
        mockserver,
        use_glue_uids,
):
    glue = (
        set(exp_req['glue']) if 'glue' in exp_req and use_glue_uids else set()
    )
    glue.add(conftest.YANDEX_UID)
    mock_core_client.yandex_uids = list(glue)
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=exp_req,
        headers=conftest.HEADERS,
    )
    assert response.status_code == exp_code
    response = response.json()
    assert response == exp_resp


@pytest.mark.pgsql('eats_coupons', files=['pg_eats_coupons.sql'])
@experiments.eats_coupons_validators(['users-whitelists-validator'])
@pytest.mark.parametrize(
    'yandex_uid, series_id, is_valid',
    [
        pytest.param('bad_uid', 'series_id_1', False, id='Bad yandex_uid'),
        pytest.param('yandex_uid_1', 'bad_series', False, id='Bad series_id'),
        pytest.param('yandex_uid_2', 'series_id_2', True, id='Success'),
    ],
)
async def test_users_whitelists_vallidator(
        taxi_eats_coupons, yandex_uid, series_id, is_valid,
):
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json={
            'coupon_id': 'coupon_id',
            'series_id': series_id,
            'series_meta': {'check-users-in-whitelist': True},
            'source_handler': 'check',
        },
        headers={
            'X-YaTaxi-Session': 'taxi:1234',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
            'X-Yandex-Uid': yandex_uid,
            'X-YaTaxi-PhoneId': 'PHONE_ID',
            'X-Eats-User': 'user_id=1,personal_phone_id=2',
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response == utils.create_response(
        valid=is_valid,
        valid_any=True,
        error_code='USER_NOT_WHITELISTED' if not is_valid else None,
        error_description='Вы не в whitelist-e' if not is_valid else None,
    )


@experiments.eats_coupons_validators(['place-validator'])
@pytest.mark.parametrize(
    'exclude_checker',
    [
        pytest.param(False, id='no_exclude_checker'),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(filename='exclude_checkers.json'),
            id='exclude_checker',
        ),
    ],
)
@pytest.mark.parametrize(
    'source',
    [
        pytest.param('check', id='not_excluded_source'),
        pytest.param('activate', id='excluded_source'),
    ],
)
@pytest.mark.parametrize(
    ('exp_req', 'exp_resp'),
    [
        (
            {
                'coupon_id': 'prom123',
                'series_meta': {'db_validation': True},
                'series_id': 'series_id_1',
                'payload': {'place_id': 3},
                'source_handler': '',
            },
            utils.create_response(
                False,
                True,
                'NO_SUITABLE_PLACES',
                'В этом плейсе нельзя применить промокод',
            ),
        ),
    ],
)
async def test_exclude_validator(
        taxi_eats_coupons, exclude_checker, exp_req, exp_resp, source,
):
    exp_req['source_handler'] = source
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=exp_req,
        headers=conftest.HEADERS,
    )

    assert response.status_code == 200
    response = response.json()
    if exclude_checker and source == 'activate':
        assert response == utils.create_response(
            True, True, 'SKIPPED_VALIDATION',
        )
    else:
        assert response == exp_resp
