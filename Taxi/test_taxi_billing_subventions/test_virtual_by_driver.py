import datetime as dt
import types

import pytest

from taxi import discovery
from taxi.billing.util import dates

from taxi_billing_subventions import config
from taxi_billing_subventions.api import virtual_by_driver as vbd
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models


def _patch_available_since(monkeypatch, time=None):
    available_since = time or dt.datetime(2018, 1, 1, tzinfo=dt.timezone.utc)
    monkeypatch.setattr(
        models.DailyGuaranteeRule,
        'available_since',
        lambda x: available_since,
    )
    monkeypatch.setattr(
        models.GeoBookingRule, 'available_since', lambda x: available_since,
    )


def _patch_config(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT', True,
    )


def _increment_at_round_time_config_mark(**overrides):
    defaults = dict(
        BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME=True,
        BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES=['driver_fix'],
        TIME_EVENTS_MIGRATION_BY_ZONE={
            'driver_fix': {
                'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
            },
        },
    )
    return pytest.mark.config(**{**defaults, **overrides})


def _now_mark():
    return pytest.mark.now('2019-09-17T13:48:50.000000+03:00')


@pytest.mark.parametrize(
    'test_data_path',
    [
        pytest.param('no_shift_ended_docs.json', marks=_now_mark()),
        pytest.param('daily_guarantee_with_payoff.json', marks=_now_mark()),
        pytest.param(
            'daily_guarantee_commission_via_modificator.json',
            marks=_now_mark(),
        ),
        pytest.param('request_by_type.json', marks=_now_mark()),
        pytest.param('driver_fix.json', marks=_now_mark()),
        pytest.param('driver_fix_with_commission.json', marks=_now_mark()),
        pytest.param('few_driver_fix.json', marks=_now_mark()),
        pytest.param(
            'driver_fix_with_cash_commission.json', marks=_now_mark(),
        ),
        pytest.param('driver_fix_with_increment.json', marks=_now_mark()),
        pytest.param(
            'driver_fix_gurantee_for_time_on_order_is_added_to_increment.json',
            marks=[_increment_at_round_time_config_mark(), _now_mark()],
        ),
        pytest.param(
            'driver_fix_with_increment_at_round_time.json',
            marks=[
                _increment_at_round_time_config_mark(),
                pytest.mark.now('2019-09-17T13:48:50.000000+03:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_start_earlier_than_shift_start.json',
            marks=[
                _increment_at_round_time_config_mark(),
                pytest.mark.now('2019-09-16T21:10:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_start_later_than_shift_end.json',
            marks=[
                _increment_at_round_time_config_mark(),
                pytest.mark.now('2019-09-17T23:00:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_only.json',
            marks=[
                _increment_at_round_time_config_mark(),
                pytest.mark.now('2019-09-17T13:48:50.000000+03:00'),
            ],
        ),
        pytest.param(
            'driver_fix_honor_migration_time_for_increment.json',
            marks=[
                _increment_at_round_time_config_mark(
                    TIME_EVENTS_MIGRATION_BY_ZONE={
                        'driver_fix': {
                            'enabled': {
                                '__default__': [
                                    {'since': '2019-09-17T10:00:00'},
                                ],
                            },
                        },
                    },
                ),
                pytest.mark.now('2019-09-17T13:48:50.000000+03:00'),
            ],
        ),
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_test_virtual_by_driver',
    subvention_rules='for_test_virtual_by_driver',
    commission_contracts='for_test_virtual_by_driver',
)
async def test_virtual_subventions_by_driver(
        test_data_path,
        db,
        loop,
        load_py_json_dir,
        billing_subventions_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        request_headers,
):
    _patch_available_since(monkeypatch)
    _patch_config(monkeypatch)
    test_data = load_py_json_dir('test_virtual_by_driver', test_data_path)
    query = test_data['query']
    accounts = test_data['accounts']
    expected_result = test_data['expected_result']
    expected_request = test_data['expected_balances_request']
    expected_docs_requests = test_data['expected_docs_requests']
    expected_docs = test_data['expected_docs']
    balances_increment = test_data.get('balances_increment') or []

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _patch_accounts_request(request):
        def key(acc):
            return acc['agreement_id']

        assert set(request.json['accrued_at']) == set(
            expected_request['accrued_at'],
        )
        assert sorted(request.json['accounts'], key=key) == sorted(
            expected_request['accounts'], key=key,
        )
        return mockserver.make_response(json=accounts)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_request(method, url, json, **kwargs):
        assert 'v3/docs/by_tag' in url
        assert json == expected_docs_requests
        return response_mock(json=expected_docs)

    @patch_aiohttp_session(
        discovery.find_service('billing_time_events').url, 'POST',
    )
    def _patch_bte_request(method, url, json, **kwargs):
        assert 'v1/balances' in url
        return response_mock(json={'balances': balances_increment})

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_driver_id_handler(*args, **kwargs):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'quas_wex',
                    'data': {'unique_driver_id': '0123456789abcdef00000001'},
                },
            ],
        }

    response = await _request(
        billing_subventions_client, query, request_headers,
    )
    assert response.status == 200
    actual_result = await response.json()

    def key(entry):
        return (
            entry['type'],
            entry['subvention_rule_id'],
            entry['payoff']['amount'],
        )

    assert sorted(actual_result['subventions'], key=key) == sorted(
        expected_result['subventions'], key=key,
    )


async def test_virtual_subventions_not_found(
        db,
        loop,
        billing_subventions_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        request_headers,
        mockserver,
):
    _patch_available_since(monkeypatch)
    query = {'driver': {'db_id': 'quas', 'uuid': 'wex'}}
    expected_text = 'Could not find unique_driver_id for db_id=quas uuid=wex'

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def unique_driver_id_handler(*args, **kwargs):
        # pylint: disable=unused-variable
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'quas_wex',
                    # No data if driver not found
                },
            ],
        }

    response = await _request(
        billing_subventions_client, query, request_headers,
    )
    assert response.status == 404
    actual_text = await response.text()
    assert expected_text == actual_text


async def _request(client, payload, request_headers):
    return await client.post(
        '/v1/virtual_by_driver', headers=request_headers, json=payload,
    )


@pytest.mark.now('2019-09-18T13:48:50.000000+00:00')
@pytest.mark.parametrize(
    'cfg, rule, park_id, expected_start',
    [
        (
            {'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True},
            {'has_increment': False},
            None,
            None,
        ),
        (
            {
                'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True,
                'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES': [],
            },
            {
                'subvention_type': models.rule.SubventionType.DRIVER_FIX,
                'has_increment': True,
            },
            None,
            None,
        ),
        (
            {
                'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True,
                'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES': ['driver_fix'],
                'BILLING_TIME_EVENTS_TEST_RULE_TYPES': ['driver_fix'],
            },
            {
                'subvention_type': models.rule.SubventionType.DRIVER_FIX,
                'has_increment': True,
            },
            None,
            None,
        ),
        (
            {
                'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True,
                'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES': ['driver_fix'],
                'BILLING_TIME_EVENTS_TEST_RULE_TYPES': [],
                'TIME_EVENTS_MIGRATION_BY_ZONE': {
                    'driver_fix': {
                        'enabled': {
                            'kursk': [{'since': '1999-01-01T00:00:00'}],
                        },
                    },
                },
            },
            {
                'subvention_type': models.rule.SubventionType.DRIVER_FIX,
                'geoarea': 'kursk',
                'has_increment': True,
            },
            None,
            dt.datetime(2019, 9, 18, 12, 30, tzinfo=dt.timezone.utc),
        ),
        (
            {
                'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True,
                'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES': ['geo_booking'],
                'BILLING_TIME_EVENTS_TEST_RULE_TYPES': [],
                'TIME_EVENTS_MIGRATION_BY_ZONE': {},
                'TIME_EVENTS_MIGRATION_BY_PARK': {
                    'geo_booking': {
                        'enabled': {'123': [{'since': '1999-01-01T00:00:00'}]},
                    },
                },
            },
            {
                'subvention_type': (
                    models.rule.SubventionType.BOOKING_GEO_ON_TOP
                ),
                'geoarea': 'kursk',
                'has_increment': True,
            },
            '123',
            dt.datetime(2019, 9, 18, 12, 30, tzinfo=dt.timezone.utc),
        ),
        (
            {
                'BILLING_SUBVENTIONS_VBD_GUESS_INCREMENT_TIME': True,
                'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES': ['geo_booking'],
                'BILLING_TIME_EVENTS_TEST_RULE_TYPES': [],
                'TIME_EVENTS_MIGRATION_BY_ZONE': {},
                'TIME_EVENTS_MIGRATION_BY_PARK': {
                    'geo_booking': {
                        'enabled': {'123': [{'since': '2019-09-18T13:00:00'}]},
                    },
                },
            },
            {
                'subvention_type': (
                    models.rule.SubventionType.BOOKING_GEO_ON_TOP
                ),
                'geoarea': 'kursk',
                'has_increment': True,
            },
            '123',
            dt.datetime(2019, 9, 18, 13, 00, tzinfo=dt.timezone.utc),
        ),
    ],
)
def test_get_time_events_increment_start_configs(
        cfg, rule, park_id, expected_start,
):
    shift = intervals.closed_open(
        dt.datetime(2019, 9, 18, tzinfo=dt.timezone.utc),
        dt.datetime(2019, 9, 19, tzinfo=dt.timezone.utc),
    )
    # pylint: disable=protected-access
    actual_start = vbd._maybe_get_increment_start_for_time_events(
        _mimic_obj(cfg), shift, _mimic_obj(rule), park_id, {},
    )
    assert expected_start == actual_start


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            '2020-09-18T05:00:00+00:00',
            marks=pytest.mark.now('2020-09-18T06:28:00+00:00'),
        ),
        pytest.param(
            '2020-09-18T05:30:00+00:00',
            marks=pytest.mark.now('2020-09-18T06:30:00+00:00'),
        ),
        pytest.param(
            '2020-09-18T05:00:00+00:00',
            marks=pytest.mark.now('2020-09-18T06:00:01+00:00'),
        ),
    ],
)
def test_guess_when_balance_is_known(expected):
    # pylint: disable=protected-access
    actual = vbd._guess_when_balance_is_known()
    assert dates.parse_datetime(expected) == actual


def _mimic_obj(dict_: dict):
    return types.SimpleNamespace(**dict_)
