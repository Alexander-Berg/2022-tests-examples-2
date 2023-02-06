import pytest

from tests_coupons import util

PHONE_ID = '5bbb5faf15870bd76635d5e2'
YANDEX_UID = '4001'
LAVKA_PROMOCODE = 'onlylavka1'


def mock_request(*args, **kwargs):
    kwargs['phone_id'] = kwargs.get('phone_id', PHONE_ID)
    return util.mock_request_activate(*args, **kwargs)


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize(
    'eats_code, eats_response, error_code, error_description_fallback',
    [
        pytest.param(
            200,
            {
                'valid': True,
                'valid_any': True,
                'descriptions': [],
                'details': [],
            },
            None,  # error_code
            None,  # error_description_fallback
            id='external_valid',
        ),
        pytest.param(
            200,
            {
                'valid': False,
                'valid_any': True,
                'descriptions': [],
                'details': [],
                'error_description': 'Промокод действует только на 1й заказ',
            },
            'ERROR_EXTERNAL_VALIDATION_FAILED',
            None,  # error_description_fallback
            id='external_invalid',
        ),
        pytest.param(
            400,
            {'code': 'BAD_REQUEST', 'message': 'Invalid category'},
            'ERROR_EXTERNAL_VALIDATION_FAILED',
            'Промокод недействителен',
            id='external_bad_request',
        ),
        pytest.param(
            500,
            None,  # eats_response
            'ERROR_EXTERNAL_SERVICE_UNAVAILABLE',
            'Активация промокода временно недоступна, повторите позже',
            id='external_error',
        ),
    ],
)
async def test_activate_external(
        taxi_coupons,
        local_services,
        mockserver,
        eats_code,
        eats_response,
        error_code,
        error_description_fallback,
):
    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/validate')
    def _mock_grocery_coupons(request):
        body = request.json
        assert body['coupon_id'] == LAVKA_PROMOCODE
        return mockserver.make_response(status=eats_code, json=eats_response)

    local_services.add_card()
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request_activate(
            [YANDEX_UID], YANDEX_UID, LAVKA_PROMOCODE, PHONE_ID,
        ),
    )
    assert response.status_code == 200
    assert _mock_grocery_coupons.times_called == 1

    coupon = response.json()['coupon']

    if error_code:
        expected_description = error_description_fallback or eats_response.get(
            'error_description',
        )
        assert coupon['error']['code'] == error_code
        assert coupon['error']['description'] == expected_description
    else:
        assert 'error' not in coupon


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize('target_coupon', ['expiredcode', 'supportexpire'])
async def test_expired_promocode(
        load_json, taxi_coupons, local_services, target_coupon,
):
    local_services.add_card()
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request_activate(
            [YANDEX_UID], YANDEX_UID, target_coupon, PHONE_ID,
        ),
    )
    assert response.status_code == 200
    data = response.json()
    coupon = data['coupon']
    assert coupon['status'] == 'invalid'
    assert coupon['error'] == {
        'code': 'ERROR_TOO_LATE',
        'description': 'Срок действия истек',
    }


SERVICES_TITLES_CONFIG = {
    'taxi': {
        'title_for_one': 'coupons.ui.block_title.for_one.taxi',
        'title_for_many': 'coupons.ui.block_title.for_many.taxi',
    },
    'eats': {
        'title_for_one': 'coupons.ui.block_title.for_one.eda',
        'title_for_many': 'coupons.ui.block_title.for_many.eda',
    },
    'grocery': {
        'title_for_one': 'coupons.ui.block_title.for_one.lavka',
        'title_for_many': 'coupons.ui.block_title.for_many.lavka',
    },
}


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.parametrize(
    ('valid', 'eats_result_code', 'error_code', 'promocode_type', 'services'),
    [
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['eats'],
            id='valid_eats_fixed_promocode',
        ),
        pytest.param(
            True, 200, None, 'text', ['eats'], id='valid_eats_text_promocode',
        ),
        pytest.param(
            False, 200, None, 'fixed', ['eats'], id='non_valid_promocode',
        ),
        pytest.param(None, 400, None, None, None, id='eats_error_bad_request'),
        pytest.param(
            None, 401, None, None, None, id='eats_error_unauthorized',
        ),
        pytest.param(None, 404, None, None, None, id='eats_error_not_found'),
        pytest.param(
            None, 500, None, None, None, id='eats_internal_server_error',
        ),
        pytest.param(
            None, 200, None, None, None, id='error_empty_eats_response',
        ),
        pytest.param(
            False, 200, 'not_found', None, None, id='not_found_promocode',
        ),
    ],
)
# pass yandex_uids as a parameter for eats_local_server mock
@pytest.mark.parametrize('yandex_uids', [([YANDEX_UID])])
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_external_promocode(
        load_json,
        taxi_coupons,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        yandex_uids,
        mongodb,
):
    local_services.add_card()

    code = 'Eda12345'
    normalized_code = code.lower()
    response = await util.make_activate_request(
        taxi_coupons, data=mock_request(yandex_uids, yandex_uids[0], code),
    )

    assert response.status_code == 200

    coupon = response.json()['coupon']
    assert coupon['code'] == normalized_code
    if valid:
        assert coupon['status'] == 'valid'
        assert set(coupon['services']) == set(services)

        user_coupons = mongodb.user_coupons.find_one(
            {'yandex_uid': YANDEX_UID, 'brand_name': 'yataxi'},
        )
        codes = [promo['code'] for promo in user_coupons['promocodes']]
        assert normalized_code in codes
    else:
        assert coupon['status'] != 'valid'
        if valid is None:
            assert (
                coupon['error']['code'] == 'ERRROR_EXTERNAL_EATS_SERVICE_FAIL'
            )
        else:
            assert coupon['error']['code'] == 'ERROR_EXTERNAL_INVALID_CODE'
