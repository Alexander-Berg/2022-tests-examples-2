import pytest

from tests_fleet_parks import utils


ENDPOINT = 'v1/parks/communications/retrieve'


TEST_GET_PARAMS = [
    (
        {'park_id': 'park_valid_sms_voip_disabled'},
        {'park_id': 'park_valid_sms_voip_disabled'},
    ),
    (
        {'park_id': 'park_valid_sms_voip_missing'},
        {'park_id': 'park_valid_sms_voip_missing'},
    ),
    (
        {'park_id': 'park_valid_sms_voip_filled'},
        {
            'park_id': 'park_valid_sms_voip_filled',
            'sms': {
                'login': 'login',
                'password': 'password',
                'provider': 'provider',
            },
            'voip': {
                'ice_servers': 'ice_servers',
                'provider': 'provider',
                'show_number': False,
            },
        },
    ),
]


@pytest.mark.parametrize('params, expected_response', TEST_GET_PARAMS)
async def test_retrieve_ok(taxi_fleet_parks, params, expected_response):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_park_not_found(taxi_fleet_parks):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    params = {'park_id': 'unknown park id'}

    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park not found',
    }
