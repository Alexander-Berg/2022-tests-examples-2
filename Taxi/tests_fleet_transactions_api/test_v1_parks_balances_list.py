# encoding=utf-8
import pytest

from tests_fleet_transactions_api import utils


ENDPOINT_URL = 'v1/parks/balances/list'
BILLING_REPORTS_MOCK_URL = '/billing-reports/v1/balances/select'


BAD_PARAMS = [
    (
        ['2020-03-18T14:00:00+03:00', '2020-03-18T14:00:00+03:00'],
        ['partner_other'],
        None,
        'field `query.balance.accrued_ats` '
        'must be sorted in strictly ascending order',
    ),
    (
        ['2020-03-18T15:00:00+03:00', '2020-03-18T14:00:00+03:00'],
        ['partner_other'],
        None,
        'field `query.balance.accrued_ats` '
        'must be sorted in strictly ascending order',
    ),
    (
        ['2020-03-18T14:00:00+03:00'],
        ['partner_other', 'partner_other'],
        None,
        'field `query.balance.group_ids` must contain unique values',
    ),
    (
        ['2020-03-18T14:00:00+03:00'],
        None,
        ['tip', 'tip'],
        'field `query.balance.category_ids` must contain unique values',
    ),
    (
        ['2020-03-18T14:00:00+03:00'],
        ['group_xyz'],
        None,
        'unknown group id `group_xyz`',
    ),
    (
        ['2020-03-18T14:00:00+03:00'],
        None,
        ['category_xyz'],
        'unknown category id `category_xyz`',
    ),
    (
        ['2020-03-18T14:00:00+03:00'],
        None,
        None,
        'at least one of `query.balance.group_ids` or '
        '`query.balance.category_ids` must be present',
    ),
    (
        ['2020-03-18T14:00:00+03:00', '2020-03-18T17:07:00+03:00'],
        ['partner_other'],
        None,
        'field query.balance.accrued_ats must contain dates truncated '
        'to hours for dates older than 168 hours before now',
    ),
]


@pytest.mark.parametrize(
    'accrued_ats, groups, categories, error_message', BAD_PARAMS,
)
async def test_bad_request(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        accrued_ats,
        groups,
        categories,
        error_message,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        json=utils.make_request(None, accrued_ats, groups, categories),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': error_message}


OK_PARAMS = [
    (['2020-03-17T00:00:00+00:00'], ['partner_other'], None),
    (['2020-03-18T00:00:00.123456+00:00'], None, ['manual']),
    (
        ['2020-03-17T00:00:00+00:00', '2020-03-18T00:00:00.123456+00:00'],
        ['partner_other', 'platform_other'],
        ['manual', 'marketing_abc', 'partner_service_manual_1', 'tip'],
    ),
]


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 0,
        'concurrency': 1,
        'truncated_to_hours_offset': 26280,
    },
)
@pytest.mark.parametrize('accrued_ats, groups, categories', OK_PARAMS)
async def test_ok(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        mockserver,
        load_json,
        accrued_ats,
        groups,
        categories,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_billing_reports(request):
        request.get_data()
        return load_json('mock_response.json')

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        json=utils.make_request(None, accrued_ats, groups, categories),
    )

    assert response.status_code == 200, response.text
    assert response.json() == utils.filter_entity_balances(
        load_json('ok_response.json'), accrued_ats, groups, categories,
    )


async def test_status_code_429(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        mockserver,
        load_json,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def mock_billing_reports(request):
        return mockserver.make_response(status=429)

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=utils.make_request(None, *OK_PARAMS[0]),
    )

    assert response.status_code == 429, response.text
    assert mock_billing_reports.has_calls
