import datetime as dt

import pytest

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


@pytest.mark.parametrize(
    'test_data_path',
    [
        'by_time_one_rule_id.json',
        'by_time_two_rule_id.json',
        'balance_not_found.json',
        'rule_not_found.json',
        'by_range_one_rule_id.json',
        'by_range_one_rule_one_shift.json',
        'one_subacc_absent.json',
        'geo_booking_rule.json',
        'geo_booking_rule_absent_income.json',
        'geo_booking_rule_absent_time.json',
        'geo_booking_rule_by_range.json',
        'net_daily_guarantee.json',
        'not_approved_daily_guarantee.json',
        'goal_rule.json',
        'personal_goal_rule.json',
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_test_by_driver',
    subvention_rules='for_test_by_driver',
    personal_subventions='for_test_by_driver',
    personal_subvention_rules='for_test_by_driver',
)
async def test_subventions_info_by_driver(
        test_data_path,
        db,
        loop,
        load_py_json_dir,
        billing_subventions_client,
        mockserver,
        monkeypatch,
        request_headers,
):
    _patch_available_since(monkeypatch)
    test_data = load_py_json_dir('test_by_driver', test_data_path)
    query = test_data['query']
    accounts = test_data['accounts']
    expected_result = test_data['expected_result']
    expected_request = test_data['expected_balances_request']

    balances_accounts = None
    balances_accrued_at = None

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _patch_billing_accounts_append(request):
        nonlocal balances_accounts
        nonlocal balances_accrued_at
        balances_accounts = request.json['accounts']
        balances_accrued_at = request.json['accrued_at']
        return mockserver.make_response(json=accounts)

    response = await _request(
        billing_subventions_client, query, request_headers,
    )
    assert balances_accounts == expected_request.get('accounts')
    assert balances_accrued_at == expected_request.get('accrued_at')
    assert response.status == 200
    actual_result = await response.json()
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'test_data_path',
    [
        'by_time_one_rule_id.json',
        'by_time_two_rule_id.json',
        'balance_not_found.json',
        'by_range_one_rule_id.json',
        'by_range_one_rule_one_shift.json',
        'one_subacc_absent.json',
        'geo_booking_rule.json',
        'geo_booking_rule_absent_income.json',
        'geo_booking_rule_absent_time.json',
        'geo_booking_rule_by_range.json',
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_test_by_driver',
    subvention_rules='for_test_by_driver',
)
async def test_bad_request_if_too_early(
        test_data_path,
        db,
        loop,
        load_py_json_dir,
        billing_subventions_client,
        patch_aiohttp_session,
        response_mock,
        request_headers,
):
    test_data = load_py_json_dir('test_by_driver', test_data_path)
    query = test_data['query']
    response = await _request(
        billing_subventions_client, query, request_headers,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'test_data_path',
    ['invalid_rule_id.json', 'invalid_time.json', 'driver_fix.json'],
)
@pytest.mark.filldb(
    tariff_settings='for_test_by_driver', subvention_rules='driver_fix',
)
async def test_bad_request(
        test_data_path,
        db,
        loop,
        load_py_json_dir,
        billing_subventions_client,
        patch_aiohttp_session,
        response_mock,
        request_headers,
):
    test_data = load_py_json_dir('test_bad_request', test_data_path)
    query = test_data['query']
    response = await _request(
        billing_subventions_client, query, request_headers,
    )
    assert response.status == 400


async def _request(client, payload, request_headers):
    return await client.post(
        '/v1/by_driver', headers=request_headers, json=payload,
    )
