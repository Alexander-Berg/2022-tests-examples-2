import pytest

from tests_fleet_offers import utils

ENDPOINT = '/internal/v1/fleet-offers/v1/not-signed/count'

MOCK_RESPONSE = {
    'profiles': [
        {
            'data': {'uuid': 'driver1'},
            'park_driver_profile_id': 'park1_driver1',
        },
    ],
}


def build_params(park_id, driver_id, section_id=None):
    params = {'park_id': park_id, 'driver_id': driver_id}
    if section_id is not None:
        params['section_id'] = section_id
    return params


OK_PARAMS = [
    ('driver1', None, 3),
    ('driver2', None, 5),
    ('driver1', 'section1', 1),
]


@pytest.mark.parametrize('driver_id, section_id, expected_count', OK_PARAMS)
async def test_ok(
        taxi_fleet_offers, mockserver, driver_id, section_id, expected_count,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return MOCK_RESPONSE

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.SERVICE_HEADERS,
        params=build_params(
            park_id='park1', driver_id=driver_id, section_id=section_id,
        ),
    )

    assert _mock_driver_profiles.times_called == 1

    assert response.status_code == 200, response.text
    assert response.json() == {'count': expected_count}


async def test_not_found(taxi_fleet_offers, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {'profiles': []}

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.SERVICE_HEADERS,
        params=build_params(park_id='park1', driver_id='bad_driver_id'),
    )

    assert _mock_driver_profiles.times_called == 1

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'driver_not_found',
        'message': 'Driver not found',
    }
