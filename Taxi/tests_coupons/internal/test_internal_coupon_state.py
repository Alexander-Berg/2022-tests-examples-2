import pytest

from tests_coupons.referral import util as referral_util


@pytest.fixture(name='request_internal_state')
def _make_request(taxi_coupons):
    async def _request(
            coupon_code: str,
            phone_id: str,
            yandex_uid: str = None,
            separate_flows_enabled: bool = False,
            service=None,
    ):
        yandex_uid = '4034039654' if yandex_uid is None else yandex_uid
        request_body = {'coupon_code': coupon_code, 'yandex_uid': yandex_uid}
        if separate_flows_enabled and service == 'eats':
            request_body['personal_phone_id'] = phone_id
        else:
            request_body['phone_id'] = phone_id
        return await taxi_coupons.post(
            '/internal/coupon/state', json=request_body,
        )

    return _request


@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
@pytest.mark.parametrize(
    ('coupon_code', 'phone_id', 'expected_orders_left', 'service'),
    (
        pytest.param(
            'seriesone1234',
            '5db2815c7984b5db628dffdb',
            1,
            None,
            id='1 orders_left',
        ),
        pytest.param(
            'seriesone2345',
            '5db2815c7984b5db628dffdc',
            0,
            None,
            id='0 orders_left',
        ),
        pytest.param(
            'series_eats12345',
            '5db2815c7984b5db628dffdb',
            1,
            'eats',
            id='1_eats orders_left',
        ),
        pytest.param(
            'series_eats23456',
            '5db2815c7984b5db628dffdc',
            0,
            'eats',
            id='0_eats orders_left',
        ),
    ),
)
async def test_success(
        request_internal_state,
        coupon_code: str,
        phone_id: str,
        expected_orders_left: int,
        separate_flows_enabled,
        service,
):
    response = await request_internal_state(
        coupon_code,
        phone_id,
        separate_flows_enabled=separate_flows_enabled,
        service=service,
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body == {
        'orders_left': expected_orders_left,
        'total_orders': 2,
        'expire_at': '2022-03-01T00:00:00+00:00',
    }


@pytest.mark.now('2021-06-30T11:30:00+0300')
@pytest.mark.pgsql(referral_util.REFERRALS_DB_NAME, files=['referral.sql'])
@pytest.mark.parametrize(
    ('coupon_code', 'phone_id', 'status', 'error_code'),
    (
        pytest.param(
            'seriesone3456',
            '5db2815c7984b5dbaaaaaaaa',
            400,
            'not_coupon_owner',
            id='Coupon belongs to another user',
        ),
        pytest.param(
            'seriesone0404',
            '5db2815c7984b5dbcccccccc',
            404,
            '',
            id='Coupon not found',
        ),
        pytest.param(
            'multiuser',
            '5db2815c7984b5db628dffdc',
            400,
            'not_implemented',
            id='Not implemented for multiuser coupon',
        ),
        pytest.param(
            'referral0',
            '5db2815c7984b5db628dffdc',
            400,
            'not_implemented',
            id='Not implemented for referal coupon',
        ),
    ),
)
async def test_check_problems(
        request_internal_state,
        coupon_code: str,
        phone_id: str,
        status: int,
        error_code: str,
):
    response = await request_internal_state(coupon_code, phone_id)
    assert response.status_code == status
    if status != 400:
        return
    response_body = response.json()
    assert response_body['code'] == error_code


@pytest.mark.now('2021-06-30T11:30:00+0300')
@pytest.mark.config(
    COUPONS_ANTISPAM_SETTINGS={
        'check_ban_max_attempts': 1,
        'check_ban_period_seconds': 40,
    },
)
async def test_check_antispam(request_internal_state):
    response = await request_internal_state(
        'seriesone4567', '5db2815c7984b5db11111111', '4000000000',
    )
    assert response.status_code == 429
