import datetime
from typing import Any
from typing import Dict

import pytest

import const
import maas_types

MAAS_TARIFFS_CONFIG = {'maas_tariff_id': const.MAAS_TARIFF_SETTINGS}


def patch_tariff_config(**kwargs) -> dict:
    tariff_settings: Dict[str, Any] = const.MAAS_TARIFF_SETTINGS.copy()
    tariff_settings.update(**kwargs)
    return {'maas_tariff_id': tariff_settings}


def get_status_history(subscription, expected_size=1, reason='vtb_request'):
    status_history = [
        maas_types.StatusHistory(updated_status.updated_at, 'reserved', reason)
        for updated_status in subscription.status_history
    ]
    assert len(status_history) == expected_size
    return status_history


@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS_CONFIG)
@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.parametrize(
    'check_task_call_enabled',
    (
        False,
        pytest.param(
            True,
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS={
                    'first_check_delay_ms': 2000,
                    'second_check_delay_ms': 500,
                    'task_call_enabled': True,
                },
            ),
        ),
    ),
)
async def test_main(
        mockserver,
        get_subscription_by_id,
        taxi_maas,
        load_json,
        check_task_call_enabled,
):
    @mockserver.json_handler('/coupons/internal/generate')
    def _coupons_generate(request):
        assert 'expire_at' in request.json
        request.json.pop('expire_at')
        assert request.json == {
            'phone_id': 'phone_id',
            'token': 'maas_sub_id',
            'series_id': 'coupon_series_id',
        }
        return mockserver.make_response(
            json={
                'promocode': 'coupon_id',
                'promocode_params': {
                    'value': 30,
                    'expire_at': '2021-05-20T00:00:00+00:00',
                    'currency_code': 'RUB',
                },
            },
        )

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def mock_stq(request, queue_name):
        pass

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    vtb_reserve = '/vtb/v1/sub/reserve'
    response = await taxi_maas.post(
        vtb_reserve,
        headers=headers,
        json=load_json('vtb_sub_reserve_request.json'),
    )

    assert response.status == 200
    response_body = response.json()
    response_body.pop('reserve_time')
    assert response_body == load_json('vtb_sub_reserve_response.json')

    expected_tariff_info = maas_types.TariffInfo(
        tariff_id='maas_tariff_id',
        trips_count='10',
        duration_days='30',
        taxi_price='100.5',
        subscription_price='200.5',
    )

    subscription = get_subscription_by_id('maas_sub_id')
    expected_status_history = get_status_history(subscription, expected_size=1)
    expected_subscription = maas_types.Subscription(
        sub_id='maas_sub_id',
        status='reserved',
        maas_user_id='maas_user_id',
        phone_id='phone_id',
        coupon_id='coupon_id',
        coupon_series_id='coupon_series_id',
        tariff_info=expected_tariff_info,
        status_history=expected_status_history,
    )

    assert subscription == expected_subscription

    if check_task_call_enabled:
        assert mock_stq.times_called == 1
    else:
        assert mock_stq.times_called == 0


@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS_CONFIG)
@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.parametrize('bought_through_go', [True, False])
async def test_bought_through_go(
        mockserver,
        get_subscription_by_id,
        taxi_maas,
        load_json,
        bought_through_go,
):
    @mockserver.json_handler('/coupons/internal/generate')
    def _coupons_generate(request):
        assert 'expire_at' in request.json
        request.json.pop('expire_at')
        assert request.json == {
            'phone_id': 'phone_id',
            'token': 'maas_sub_id',
            'series_id': 'coupon_series_id',
        }
        return mockserver.make_response(
            json={
                'promocode': 'coupon_id',
                'promocode_params': {
                    'value': 30,
                    'expire_at': '2021-05-20T00:00:00+00:00',
                    'currency_code': 'RUB',
                },
            },
        )

    request_body = load_json('vtb_sub_reserve_request.json')
    if bought_through_go:
        request_body['additional_data'].append(
            {'key': 'bought_through_go', 'value': 'true'},
        )

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post(
        '/vtb/v1/sub/reserve', headers=headers, json=request_body,
    )

    assert response.status == 200
    response_body = response.json()
    response_body.pop('reserve_time')
    assert response_body == load_json('vtb_sub_reserve_response.json')

    subscription = get_subscription_by_id('maas_sub_id')
    assert subscription.bought_through_go == bought_through_go


@pytest.mark.parametrize(
    'error_code, error_cause',
    [
        pytest.param('50', 'tariff_not_found', id='tariff_not_found'),
        pytest.param(
            '50',
            'tariff_not_available',
            marks=pytest.mark.config(
                MAAS_TARIFFS=patch_tariff_config(sale_allowed=False),
            ),
            id='tariff_not_available',
        ),
        pytest.param(
            '50',
            'tariff_trips_count_mismatch',
            marks=pytest.mark.config(
                MAAS_TARIFFS=patch_tariff_config(trips_count=1),
            ),
            id='tariff_trips_count_mismatch',
        ),
        pytest.param(
            '50',
            'tariff_duration_days_mismatch',
            marks=pytest.mark.config(
                MAAS_TARIFFS=patch_tariff_config(duration_days=1),
            ),
            id='tariff_duration_days_mismatch',
        ),
        pytest.param(
            '50',
            'tariff_ts_price_mismatch',
            marks=pytest.mark.config(
                MAAS_TARIFFS=patch_tariff_config(taxi_price='1'),
            ),
            id='tariff_ts_price_mismatch',
        ),
        pytest.param(
            '50',
            'tariff_subscription_price_mismatch',
            marks=pytest.mark.config(
                MAAS_TARIFFS=patch_tariff_config(subscription_price='1'),
            ),
            id='tariff_subscription_price_mismatch',
        ),
        pytest.param(
            '34',
            'active_subscription_error',
            marks=[
                pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS_CONFIG),
                pytest.mark.pgsql(
                    'maas', files=['subscriptions.sql', 'users.sql'],
                ),
            ],
            id='active_subscription_error',
        ),
        pytest.param(
            '30',
            'user_not_found',
            marks=[pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS_CONFIG)],
            id='user_not_found',
        ),
    ],
)
async def test_tariff_validation(
        taxi_maas, load_json, error_code: str, error_cause: str,
):
    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post(
        '/vtb/v1/sub/reserve',
        headers=headers,
        json=load_json('vtb_sub_reserve_request.json'),
    )
    assert response.status == 422
    response_body = response.json()
    assert response_body['errorCause'] == error_cause
    assert response_body['errorCode'] == error_code


def _str_to_datetime(
        time_str: str, with_ms: bool = False,
) -> datetime.datetime:
    if with_ms:
        return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S%z')


@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS_CONFIG)
@pytest.mark.pgsql('maas', files=['users.sql', 'subscriptions.sql'])
@pytest.mark.parametrize(
    'user_id, sub_id, expired_at, coupons_called',
    [
        pytest.param(
            'maas_user_id1',
            'fail_reserved1',
            _str_to_datetime(
                '2021-07-30T23:59:00+0300',
            ),  # calc with reserved_at='2021-06-30T21:01:00.00Z'
            True,
            id='coupon_generation_fail_1_00:01',
        ),
        pytest.param(
            'maas_user_id2',
            'fail_reserved2',
            _str_to_datetime(
                '2021-07-30T23:59:00+0300',
            ),  # calc with reserved_at='2021-07-01T20:59:00.00Z'
            True,
            id='coupon_generation_fail_1_23:59',
        ),
        pytest.param(
            'maas_user_id3',
            'fail_reserved3',
            _str_to_datetime(
                '2021-07-31T23:59:00+0300',
            ),  # calc with reserved_at='2021-07-01T21:01:00.00Z'
            True,
            id='coupon_generation_fail_2_00:01',
        ),
        pytest.param(
            'maas_user_id4',
            'fail_reserved4',
            _str_to_datetime('2121-08-02T01:00:00+0000'),  # get from db
            False,
            id='coupon_generation_ok',
        ),
    ],
)
async def test_attempt_after_failed(
        mockserver,
        get_subscription_by_id,
        taxi_maas,
        load_json,
        user_id,
        sub_id,
        expired_at,
        coupons_called,
):
    subscription_before = get_subscription_by_id(
        sub_id=sub_id, with_time_fields=True,
    )
    created_at = subscription_before.created_at
    phone_id = subscription_before.phone_id

    @mockserver.json_handler('/coupons/internal/generate')
    def _coupons_generate(request):
        nonlocal created_at
        req_expired_at = _str_to_datetime(request.json['expire_at'])
        assert req_expired_at == expired_at
        return mockserver.make_response(
            json={
                'promocode': 'coupon_id',
                'promocode_params': {
                    'value': 30,
                    'expire_at': '2021-05-20T00:00:00+00:00',
                    'currency_code': 'RUB',
                },
            },
        )

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    request_body = load_json('vtb_sub_reserve_request.json')
    request_body['maas_sub_id'] = sub_id
    request_body['maas_user_id'] = user_id
    vtb_reserve = '/vtb/v1/sub/reserve'
    response = await taxi_maas.post(
        vtb_reserve, headers=headers, json=request_body,
    )

    assert response.status == 200

    response_body = response.json()
    assert _str_to_datetime(response_body['reserve_time']) == created_at
    response_body.pop('reserve_time')
    expected_response = load_json('vtb_sub_reserve_response.json')
    expected_response['service_sub_id'] = sub_id
    assert response_body == expected_response

    expected_tariff_info = maas_types.TariffInfo(
        tariff_id='maas_tariff_id',
        trips_count='10',
        duration_days='30',
        taxi_price='100.50',
        subscription_price='200.50',
    )

    subscription = get_subscription_by_id(sub_id, with_time_fields=True)

    if coupons_called:
        assert _coupons_generate.times_called == 1
        expected_status_history = get_status_history(
            subscription, expected_size=2,
        )
    else:
        assert _coupons_generate.times_called == 0
        expected_status_history = get_status_history(
            subscription, expected_size=1,
        )

    expected_subscription = maas_types.Subscription(
        sub_id=sub_id,
        status='reserved',
        maas_user_id=user_id,
        phone_id=phone_id,
        coupon_id='coupon_id',
        coupon_series_id='coupon_series_id',
        tariff_info=expected_tariff_info,
        created_at=created_at,
        expired_at=expired_at,
        status_history=expected_status_history,
    )

    assert subscription == expected_subscription
