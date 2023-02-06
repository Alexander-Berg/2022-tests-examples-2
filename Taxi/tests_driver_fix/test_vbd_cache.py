# pylint: disable=import-error
import datetime
import json

from driver_fix.fbs import VirtualPaymentsData as fbs_vpd
import pytest

from tests_driver_fix import common
from tests_driver_fix import utils

VBD_RESPONSE = {
    'subventions': [
        {
            'type': 'driver_fix',
            'subvention_rule_id': 'subvention_rule_id',
            'payoff': {'amount': '0', 'currency': 'RUB'},
            'period': {
                'start_time': '2019-01-01T00:00:01+03:00',
                'end_time': '2019-01-02T00:00:00+03:00',
            },
            'commission_info': {
                'payoff_commission': {'amount': '10', 'currency': 'RUB'},
            },
            'details': {
                'accounted_time_seconds': 600,
                'cash_income': {'amount': '0', 'currency': 'RUB'},
                'guarantee': {'amount': '1000', 'currency': 'RUB'},
                'cash_commission': {'amount': '0', 'currency': 'RUB'},
            },
        },
    ],
}

FOUND_SUMMARY_RESPONSE = {
    'cash_income': 0.0,
    'payoff': 0.0,
    'total_income': 0.0,
    'commission': 10.0,
    'guaranteed_money': 1000.0,
    'no_shifts': False,
    'time': 600,
}

NOT_FOUND_SUMMARY_RESPONSE = {
    'cash_income': 0.0,
    'payoff': 0.0,
    'total_income': 0.0,
    'commission': 0.0,
    'guaranteed_money': 0.0,
    'no_shifts': True,
    'time': 0,
}

FOUND_STATUS_RESPONSE = {
    'keep_in_busy': False,
    'panel_body': {'items': []},
    'panel_header': {
        'icon': 'time',
        'subtitle': '10;1000 ₽',
        'title': 'Driver-fix',
    },
    'reminiscent_overlay': {'text': '10'},
    'status': 'subscribed',
}

NOT_FOUND_STATUS_RESPONSE = {
    'keep_in_busy': False,
    'panel_body': {'items': []},
    'panel_header': {
        'icon': 'time',
        'subtitle': '0;0 ₽',
        'title': 'Driver-fix',
    },
    'reminiscent_overlay': {'text': '0'},
    'status': 'subscribed',
}


def _get_shift_start_end(summary_call: bool):
    if summary_call:
        return (
            utils.parse_time('1970-01-01T00:00:00+00:00'),
            utils.parse_time('1970-01-01T00:00:00+00:00'),
        )
    return (
        utils.parse_time('2019-01-01T00:00:00+03:00'),
        utils.parse_time('2019-01-02T00:00:00+03:00'),
    )


def _get_not_found_cache_data(
        cache_time: datetime.datetime, summary_call: bool, version: str,
) -> dict:
    shift_start, shift_end = _get_shift_start_end(summary_call)

    if version == 'v1':
        return {
            'created_at': cache_time,
            'shift_start': shift_start,
            'shift_end': shift_end,
            'seconds': 0,
            'money': 0.0,
            'payoff_commission': 0.0,
            'cash': 0.0,
            'cash_commission': 0.0,
            'payoff': 0.0,
            'total_income': 0.0,
            'no_shifts': True,
        }

    return {
        'created_at': cache_time,
        'shift_start': shift_start,
        'shift_end': shift_end,
        'seconds': 0,
        'money': [],
        'payoff_commission': [],
        'cash': [],
        'cash_commission': [],
        'payoff': [],
        'total_income': [],
        'no_shifts': True,
    }


def _get_found_cache_data(
        cache_time: datetime.datetime, summary_call: bool, version: str,
) -> dict:
    shift_start, shift_end = _get_shift_start_end(summary_call)

    if version == 'v1':
        return {
            'created_at': cache_time,
            'shift_start': shift_start,
            'shift_end': shift_end,
            'seconds': 600,
            'money': 1000.0,
            'payoff_commission': 10.0,
            'cash': 0.0,
            'cash_commission': 0.0,
            'payoff': 0.0,
            'total_income': 0.0,
            'no_shifts': False,
        }

    return {
        'created_at': cache_time,
        'shift_start': shift_start,
        'shift_end': shift_end,
        'seconds': 600,
        'money': [{'amount': 1000.0, 'currency': 'RUB'}],
        'payoff_commission': [{'amount': 10.0, 'currency': 'RUB'}],
        'cash': [{'amount': 0.0, 'currency': 'RUB'}],
        'cash_commission': [],
        'payoff': [{'amount': 0.0, 'currency': 'RUB'}],
        'total_income': [],
        'no_shifts': False,
        'last_currency': 'RUB',
    }


def _get_key(version):
    return {
        'v1': 'dbid_uuid:virtual_payments',
        'v2': 'dbid_uuid:virtual_payments_v2',
    }[version]


def _get_vbd_cache_data_v1(redis_store):
    def msk_timestamp_to_datetime(time):
        return datetime.datetime.fromtimestamp(time, tz=utils.Timezone.MSK)

    redis_data = redis_store.get(_get_key('v1'))
    if not redis_data:
        return None
    fbs_data = fbs_vpd.VirtualPaymentsData.GetRootAsVirtualPaymentsData(
        bytearray(redis_data), 0,
    )
    data = {}
    data['created_at'] = msk_timestamp_to_datetime(
        fbs_data.CacheEntryCreatedAt(),
    )
    data['shift_start'] = msk_timestamp_to_datetime(fbs_data.ShiftStart())
    data['shift_end'] = msk_timestamp_to_datetime(fbs_data.ShiftEnd())
    data['seconds'] = fbs_data.Seconds()
    data['money'] = fbs_data.Money()
    data['payoff_commission'] = fbs_data.PayoffCommission()
    data['cash'] = fbs_data.Cash()
    data['cash_commission'] = fbs_data.CashCommission()
    data['payoff'] = fbs_data.Payoff()
    data['total_income'] = fbs_data.TotalIncome()
    data['no_shifts'] = fbs_data.NoShifts()

    return data


def _get_vbd_cache_data_v2(redis_store):
    redis_data = redis_store.get(_get_key('v2'))
    if not redis_data:
        return None
    interim = json.loads(redis_data)
    interim['created_at'] = utils.parse_time(interim['created_at'])
    interim['shift_start'] = utils.parse_time(interim['shift_start'])
    interim['shift_end'] = utils.parse_time(interim['shift_end'])
    return interim


def _get_vbd_cache_data(redis_store, version):
    if version == 'v1':
        return _get_vbd_cache_data_v1(redis_store)
    return _get_vbd_cache_data_v2(redis_store)


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize(
    'use_vbd_cache,vbd_cache_get_fails,vbd_cache_set_fails',
    (
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, False, True),
        (True, True, True),
    ),
)
@pytest.mark.parametrize('vbd_response', ('found', 'not found', 'failed'))
@pytest.mark.parametrize('version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'summary_call',
    [pytest.param(True, id='summary'), pytest.param(False, id='status')],
)
async def test_status_view_vbd_cache(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        redis_store,
        testpoint,
        mocked_time,
        use_vbd_cache,
        vbd_response,
        vbd_cache_get_fails,
        vbd_cache_set_fails,
        version,
        summary_call,
):
    @testpoint('vbd_get_cache_tp')
    def _vbd_get_cache_tp(data):
        if vbd_cache_get_fails:
            return {'injected_error': True}
        return None

    @testpoint('vbd_set_cache_tp')
    def _vbd_set_cache_tp(data):
        if vbd_cache_set_fails:
            return {'injected_error': True}
        return None

    @testpoint('vbd_wait_set_tp')
    def _vbd_vbd_wait_set_tp(data):
        pass

    update_interval = 60
    cache_config = {
        'enabled': use_vbd_cache,
        'use_cache_as_fallback': False,
        'cache_ttl_in_seconds': 3600,
        'update_interval_in_seconds': update_interval,
        'cache_command_control': {
            'max_retries': 2,
            'timeout_all_ms': 10000,
            'timeout_single_ms': 10000,
        },
        'version': version,
    }
    taxi_config.set_values(
        dict(DRIVER_FIX_VIRTUAL_PAYMENTS_DATA_CACHE=cache_config),
    )
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert request.json == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        if vbd_response == 'failed':
            return None
        if vbd_response == 'not found':
            return mockserver.make_response('not found error', 404)
        return VBD_RESPONSE

    start_utc = datetime.datetime(2019, 1, 1, 9, 0, tzinfo=utils.Timezone.UTC)

    async def _call_and_check(call_number: int, now: datetime.datetime):
        mocked_time.set(now)
        response = None
        if summary_call:
            response = await taxi_driver_fix.get(
                'v1/view/status_summary',
                params={'park_id': 'dbid', 'driver_profile_id': 'uuid'},
                headers={'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET},
            )
        else:
            response = await taxi_driver_fix.get(
                'v1/view/status',
                params=common.get_enriched_params(['native_restrictions']),
                headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
            )

        cache_expiration_time = start_utc + datetime.timedelta(
            seconds=update_interval,
        )

        if (
                use_vbd_cache
                and vbd_response != 'failed'
                and not vbd_cache_get_fails
                and not vbd_cache_set_fails
        ):
            if cache_expiration_time < now:
                assert _get_by_driver.times_called == 2
            else:
                assert _get_by_driver.times_called == 1
        else:
            assert _get_by_driver.times_called == call_number

        if vbd_response == 'failed':
            assert response.status_code == 500
            assert not _get_vbd_cache_data(redis_store, version)
            return

        assert response.status_code == 200

        if not summary_call:
            assert response.headers['X-Polling-Delay'] == '60'

        cache_time = start_utc
        if cache_expiration_time < now or vbd_cache_get_fails:
            cache_time = now

        if vbd_response == 'not found':
            if use_vbd_cache and not vbd_cache_set_fails:
                cache_data = _get_vbd_cache_data(redis_store, version)
                assert cache_data == _get_not_found_cache_data(
                    cache_time, summary_call, version,
                )
            else:
                assert not _get_vbd_cache_data(redis_store, version)

            if summary_call:
                assert response.json() == NOT_FOUND_SUMMARY_RESPONSE
            else:
                assert response.json() == NOT_FOUND_STATUS_RESPONSE
            return

        if summary_call:
            assert response.json() == FOUND_SUMMARY_RESPONSE
        else:
            assert response.json() == FOUND_STATUS_RESPONSE

        if use_vbd_cache and not vbd_cache_set_fails:
            cache_data = _get_vbd_cache_data(redis_store, version)
            assert cache_data == _get_found_cache_data(
                cache_time, summary_call, version,
            )
        else:
            assert not _get_vbd_cache_data(redis_store, version)

    await _call_and_check(1, start_utc)
    await _call_and_check(
        2, start_utc + datetime.timedelta(seconds=(update_interval / 2)),
    )
    await _call_and_check(
        3, start_utc + datetime.timedelta(seconds=(update_interval * 2)),
    )


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize(
    'use_vbd_cache,vbd_cache_get_fails,vbd_cache_set_fails',
    (
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, False, True),
        (True, True, True),
    ),
)
@pytest.mark.parametrize('vbd_response', ('found', 'not found'))
@pytest.mark.parametrize('version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'summary_call',
    [pytest.param(True, id='summary'), pytest.param(False, id='status')],
)
async def test_status_view_vbd_cache_fallback(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        redis_store,
        testpoint,
        mocked_time,
        use_vbd_cache,
        vbd_response,
        vbd_cache_get_fails,
        vbd_cache_set_fails,
        version,
        summary_call,
):
    @testpoint('vbd_get_cache_tp')
    def _vbd_get_cache_tp(data):
        if vbd_cache_get_fails:
            return {'injected_error': True}
        return None

    @testpoint('vbd_set_cache_tp')
    def _vbd_set_cache_tp(data):
        if vbd_cache_set_fails:
            return {'injected_error': True}
        return None

    @testpoint('vbd_wait_set_tp')
    def _vbd_vbd_wait_set_tp(data):
        pass

    update_interval = 60
    cache_ttl = 3600
    cache_config = {
        'enabled': use_vbd_cache,
        'use_cache_as_fallback': True,
        'cache_ttl_in_seconds': cache_ttl,
        'update_interval_in_seconds': update_interval,
        'cache_command_control': {
            'max_retries': 2,
            'timeout_all_ms': 10000,
            'timeout_single_ms': 10000,
        },
        'version': version,
    }
    assert cache_ttl / 2 > update_interval
    taxi_config.set_values(
        dict(DRIVER_FIX_VIRTUAL_PAYMENTS_DATA_CACHE=cache_config),
    )
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    fail_vbd_call = False

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        nonlocal fail_vbd_call
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        if fail_vbd_call:
            return None
        fail_vbd_call = True
        if vbd_response == 'not found':
            return mockserver.make_response('not found error', 404)
        return VBD_RESPONSE

    start_utc = datetime.datetime(2019, 1, 1, 9, 0, tzinfo=utils.Timezone.UTC)

    async def _call_and_check(call_number: int, now: datetime.datetime):
        mocked_time.set(now)
        expired = False
        if start_utc + datetime.timedelta(seconds=cache_ttl) < now:
            # imitate expiration:
            redis_store.delete(_get_key(version))
            expired = True

        response = None
        if summary_call:
            response = await taxi_driver_fix.get(
                'v1/view/status_summary',
                params={'park_id': 'dbid', 'driver_profile_id': 'uuid'},
                headers={'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET},
            )
        else:
            response = await taxi_driver_fix.get(
                'v1/view/status',
                params=common.get_enriched_params(['native_restrictions']),
                headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
            )

        assert _get_by_driver.times_called == call_number

        cache_time = start_utc

        if _get_by_driver.times_called > 1 and (
                not use_vbd_cache
                or (vbd_cache_set_fails or vbd_cache_get_fails or expired)
        ):
            assert response.status_code == 500
            cache_data = _get_vbd_cache_data(redis_store, version)
            if not use_vbd_cache or vbd_cache_set_fails or expired:
                assert not cache_data
            elif vbd_response == 'not found':
                assert cache_data == _get_not_found_cache_data(
                    cache_time, summary_call, version,
                )
            else:
                assert cache_data == _get_found_cache_data(
                    cache_time, summary_call, version,
                )
            return

        assert response.status_code == 200
        if not summary_call:
            assert response.headers['X-Polling-Delay'] == '60'

        if vbd_response == 'not found':
            if use_vbd_cache and not vbd_cache_set_fails:
                cache_data = _get_vbd_cache_data(redis_store, version)
                assert cache_data == _get_not_found_cache_data(
                    cache_time, summary_call, version,
                )
            else:
                assert not _get_vbd_cache_data(redis_store, version)

            if summary_call:
                assert response.json() == NOT_FOUND_SUMMARY_RESPONSE
            else:
                assert response.json() == NOT_FOUND_STATUS_RESPONSE
            return

        if summary_call:
            assert response.json() == FOUND_SUMMARY_RESPONSE
        else:
            assert response.json() == FOUND_STATUS_RESPONSE

        if use_vbd_cache and not vbd_cache_set_fails:
            cache_data = _get_vbd_cache_data(redis_store, version)
            assert cache_data == _get_found_cache_data(
                cache_time, summary_call, version,
            )
        else:
            assert not _get_vbd_cache_data(redis_store, version)

    await _call_and_check(1, start_utc)
    await _call_and_check(
        2, start_utc + datetime.timedelta(seconds=(cache_ttl / 2)),
    )
    await _call_and_check(
        3, start_utc + datetime.timedelta(seconds=(cache_ttl * 2)),
    )
