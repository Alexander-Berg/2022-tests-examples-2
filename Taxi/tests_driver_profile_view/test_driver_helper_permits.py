import pytest


ENDPOINT = 'driver/profile-view/v1/helper-permits'
BINDING = '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id'
VEHICLE = '/fleet-vehicles/v1/vehicles/retrieve'


@pytest.mark.parametrize(
    'park_id,expected_code,expected_response',
    [
        ('dbid1', 200, '<p>Success: login1, password1</p>'),
        ('dbid2', 500, '<p>No vehicle</p>'),
        ('dbid3', 500, '<p>No vehicle</p>'),
        ('dbid4', 500, '<p>Not found</p>'),
        ('dbid5', 500, '<p>Error</p>'),
    ],
)
@pytest.mark.pgsql('driver_profile_view', files=['helper_permits.sql'])
async def test_driver_helper_permits(
        taxi_driver_profile_view,
        driver_authorizer,
        mockserver,
        load_json,
        park_id,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session(park_id, 'session1', 'uuid1')

    @mockserver.json_handler(BINDING)
    def _mock_driver_profiles(request):
        response = load_json('vehicle_binding.json')
        return response

    @mockserver.json_handler(VEHICLE)
    def _mock_fleet_vehicles(request):
        response = load_json('vehicles_retrieve.json')
        return response

    response = await taxi_driver_profile_view.get(
        ENDPOINT, params={'park_id': park_id, 'session': 'session1'},
    )
    assert response.status_code == expected_code
    assert response.text == expected_response
