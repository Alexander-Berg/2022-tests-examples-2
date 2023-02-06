import base64
import json

import pytest

ENDPOINT_URL = '/internal/pro-platform/balance/transactions/search/v1'
BILLING_REPORTS_MOCK_URL = '/billing-reports/v2/journal/select'
PARK_ID = '7ad35b'
CONTRACTOR_PROFILE_ID = '9c5e35'
EXTERNAL_ID = f'taximeter_driver_id/{PARK_ID}/{CONTRACTOR_PROFILE_ID}'
NOW = '2022-06-01T12:00:00+00:00'
BEGIN_TIME = '2022-01-01T12:00:00+00:00'
END_TIME = '2022-04-01T12:00:00+00:00'
TARGET_SIZE = 12
BILLING_LIMIT = 10
BILLING_CURSOR = 'billing_cursor'
CURSOR = {
    'billing_cursor': BILLING_CURSOR,
    'limit': TARGET_SIZE,
    'park_id': PARK_ID,
    'contractor_profile_id': CONTRACTOR_PROFILE_ID,
    'from': BEGIN_TIME,
    'to': END_TIME,
}


@pytest.fixture(name='fleet_parks')
def _driver_profiles(mockserver, load_json):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock(request):
        return {
            'parks': [
                {
                    'city_id': 'Москва',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'id': 'id',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'login',
                    'name': 'name',
                },
            ],
        }


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_MAX_LIMIT_FOR_JOURNAL_SELECT=BILLING_LIMIT,
)
@pytest.mark.now(NOW)
async def test_post_ok(
        taxi_fleet_transactions_api, load_json, mockserver, fleet_parks,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_billing_reports(request):
        assert request.json['accounts'][0]['entity_external_id'] == EXTERNAL_ID
        assert request.json['begin_time'] == BEGIN_TIME
        assert request.json['end_time'] == END_TIME
        assert request.json['exclude'] == {'zero_entries': True}
        if request.json['cursor'] == '':
            assert request.json['limit'] == min(BILLING_LIMIT, TARGET_SIZE)
            assert (
                billing_response1['entries'][0]['account'][
                    'entity_external_id'
                ]
                == EXTERNAL_ID
            )
            return billing_response1

        assert request.json['limit'] == len(billing_response2['entries'])
        assert (
            billing_response2['entries'][0]['account']['entity_external_id']
            == EXTERNAL_ID
        )
        return billing_response2

    billing_response1 = load_json('billing_response1.json')
    billing_response2 = load_json('billing_response2.json')

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        json={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
            'limit': TARGET_SIZE,
            'event_at': {'from': BEGIN_TIME, 'to': END_TIME},
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('expected_post_response.json')
    assert (
        json.loads(base64.b64decode(response.json()['cursor'] + '=='))
        == CURSOR
    )


@pytest.mark.now(NOW)
async def test_get_ok(
        taxi_fleet_transactions_api, load_json, mockserver, fleet_parks,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_billing_reports(request):
        assert request.json['accounts'][0]['entity_external_id'] == EXTERNAL_ID
        assert request.json['begin_time'] == BEGIN_TIME
        assert request.json['end_time'] == END_TIME
        assert request.json['limit'] == TARGET_SIZE
        assert request.json['exclude'] == {'zero_entries': True}
        assert request.json['cursor'] == BILLING_CURSOR
        assert (
            billing_response3['entries'][0]['account']['entity_external_id']
            == EXTERNAL_ID
        )
        return billing_response3

    billing_response3 = load_json('billing_response3.json')

    response = await taxi_fleet_transactions_api.get(
        ENDPOINT_URL,
        params={
            'cursor': base64.b64encode(json.dumps(CURSOR).encode()).decode(),
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('expected_get_response.json')
