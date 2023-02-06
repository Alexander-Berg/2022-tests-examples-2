import pytest

from tests_billing_subventions_x import dbhelpers

MOCK_NOW = '2021-04-28T19:31:00+00:00'


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_bulk_create_returns_ruleset_ref(
        taxi_billing_subventions_x, load_json,
):
    query = load_json('bulk_single_ride_request.json')
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response['ruleset_ref'] != ''


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_bulk_create_creates_internal_draft(
        taxi_billing_subventions_x, load_json, pgsql,
):
    query = load_json('bulk_single_ride_request.json')
    response = await _make_request(taxi_billing_subventions_x, query)
    spec = dbhelpers.get_draft_spec(pgsql, response['ruleset_ref'])
    assert spec == {
        'internal_draft_id': response['ruleset_ref'],
        'spec': load_json('bulk_single_ride_spec.json'),
        'creator': 'me',
        'draft_id': None,
        'budget_id': None,
        'tickets': None,
        'approvers': None,
        'approved_at': None,
        'state': 'NEW',
        'error': None,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_bulk_create_fails_for_multiple_currencies(
        taxi_billing_subventions_x, mockserver, load_json,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff_zones(request):
        zones = [
            {
                'name': name,
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': '',
                'currency': {'moscow': 'RUB'}.get(name, 'BYN'),
            }
            for name in request.query['zone_names'].split(',')
        ]
        return {'zones': zones}

    query = load_json('bulk_single_ride_request.json')
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'The currency must be the same for all zones. Got: BYN, RUB'
        ),
    }


async def _make_request(bsx, query, status=200):
    url = '/v2/rules/single_ride/bulk_create'
    headers = {'X-YaTaxi-Draft-Author': 'me'}
    response = await bsx.post(url, query, headers=headers or {})
    assert response.status_code == status, response.json()
    return response.json()
