import base64
import json

import pytest

URL = '/internal/pro-platform/income/events/search/v1'
PBE_EVENTS_URL = (
    '/pro-business-events/internal/events/bulk-retrieve/by-external-ids/v1'
)
NOW = '2020-01-02T00:00:00'
CATEGORY_TIPS = 'tips'
LIMIT = 3


@pytest.mark.now(NOW)
async def test_income_events_post(
        taxi_fleet_transactions_api,
        load_json,
        billing_reports,
        mockserver,
        fleet_parks,
):
    @mockserver.json_handler(PBE_EVENTS_URL)
    def _mock_pbe(request):
        return load_json('expected_pbe_events_response.json')

    @mockserver.json_handler('/territories/v1/countries/list')
    def _mock_countries_list(request):
        return load_json('countries_response.json')

    billing_reports.entries = load_json('journal_select_entries.json')

    response = await taxi_fleet_transactions_api.post(
        URL,
        json={
            'park_id': 'park0',
            'contractor_profile_id': 'driver0',
            'event_at': {
                'from': '2020-01-01T00:00:00Z',
                'to': '2020-01-02T00:00:00Z',
            },
            'mode': {
                'type': 'by_category',
                'finance_group_id': 'market',
                'category_id': CATEGORY_TIPS,
            },
            'limit': LIMIT,
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected_response_post.json')


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'billing_cursor,expected_response,previous_last_item',
    [
        (
            '0',
            'expected_response_get_from_event2.json',
            {
                'event_at': '2020-01-01T06:03:00+00:00',
                'platform_consumer': 'market',
                'event_id': 'event3',
            },
        ),
        (
            '1',
            'expected_response_get_from_event1.json',
            {
                'event_at': '2020-01-01T06:03:00+00:00',
                'platform_consumer': 'market',
                'event_id': 'event2',
            },
        ),
    ],
)
async def test_income_events_get(
        taxi_fleet_transactions_api,
        load_json,
        billing_reports,
        mockserver,
        billing_cursor,
        expected_response,
        previous_last_item,
):
    billing_reports.entries = load_json('journal_select_entries.json')

    @mockserver.json_handler(PBE_EVENTS_URL)
    def _mock_pbe(request):
        return load_json('expected_pbe_events_response.json')

    cursor = {
        'park_id': 'park0',
        'contractor_id': 'driver0',
        'event_at_from': '2020-01-01T00:00:00Z',
        'event_at_to': '2020-01-02T00:00:00Z',
        'limit': 10,
        'billing_cursor': billing_cursor,
        'previous_last_item': previous_last_item,
        'currency': 'RUB',
        'mode': {
            'type': 'by_category',
            'finance_group_id': 'market',
            'category_id': CATEGORY_TIPS,
        },
    }

    as_str = json.dumps(cursor, ensure_ascii=False)
    as_bytes = bytes(as_str, 'utf8')
    encoded_cursor = base64.b64encode(as_bytes).decode()

    response = await taxi_fleet_transactions_api.get(
        URL, params={'cursor': encoded_cursor},
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now(NOW)
async def test_billing_request(
        taxi_fleet_transactions_api,
        load_json,
        billing_reports,
        mockserver,
        fleet_parks,
):
    @mockserver.json_handler(PBE_EVENTS_URL)
    def _mock_pbe(request):
        return load_json('expected_pbe_events_response.json')

    billing_reports.entries = load_json('journal_select_entries.json')

    response = await taxi_fleet_transactions_api.post(
        URL,
        json={
            'park_id': 'park0',
            'contractor_profile_id': 'driver0',
            'event_at': {
                'from': '2020-01-01T00:00:00Z',
                'to': '2020-01-02T00:00:00Z',
            },
            'mode': {'type': 'total_by_group', 'finance_group_id': 'market'},
            'limit': LIMIT,
        },
    )

    assert response.status_code == 200
    assert billing_reports.get_request_subaccounts() == ['total']
