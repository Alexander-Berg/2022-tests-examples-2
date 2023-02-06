import pytest


ENDPOINT = 'driver/profile-view/v1/vehicles/list'
BINDING = '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id'
VEHICLES_BY_ID = '/fleet-vehicles/v1/vehicles/retrieve'
VEHICLES_BY_PARK = '/fleet-vehicles/v1/vehicles/retrieve_by_park'
CAR_COLORS = '/parks/car-colors'
DRIVE_INTEGRATION_AUTH = (
    '/drive-integration/internal/drive-integration/v1/signed_auth'
)
HEADERS = {
    'X-Driver-Session': 'session1',
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
}


@pytest.mark.config(
    TAXIMETER_MARKETPLACE={
        'cities': [],
        'countries': [],
        'dbs': ['db_id1'],
        'enable': True,
        'home_url': 'http://home_url',
        'driver_url': 'http://driver_url',
    },
)
@pytest.mark.experiments3(filename='experiments3_dvpbs_default.json')
@pytest.mark.experiments3(filename='experiments3_drive_access.json')
@pytest.mark.parametrize(
    'park_id, cars_list, expected_response, request_by_park, drive_state',
    [
        (
            'db_id42',
            'parks_cars_list1.json',
            'response1.json',
            True,
            'not_present',
        ),
        (
            'db_id42',
            'parks_cars_list1.json',
            'response1_1.json',
            True,
            'in_progress',
        ),
        ('db_id1', 'parks_cars_list2.json', 'response2.json', False, 'active'),
    ],
)
@pytest.mark.now('2020-08-08T06:35:00+0500')
async def test_driver_vehicles_list(
        taxi_driver_profile_view,
        taxi_config,
        mockserver,
        driver_authorizer,
        load_json,
        mock_fleet_parks_list,
        unique_drivers_mocks,
        park_id,
        cars_list,
        expected_response,
        request_by_park,
        driver_trackstory_mocks,
        drive_state,
):
    uuid = 'uuid1'
    driver_authorizer.set_session(park_id, 'session1', uuid)
    taxi_config.set_values(
        dict(DRIVER_PROFILE_VIEW_HIDE_NOT_WORKING_VEHICLES=True),
    )

    @mockserver.json_handler(BINDING)
    def _mock_driver_profiles(request):
        response = load_json('vehicle_binding.json')
        return response

    @mockserver.json_handler(VEHICLES_BY_ID)
    def _mock_vehicles_by_id(request):
        return load_json(cars_list)

    @mockserver.json_handler(VEHICLES_BY_PARK)
    def _mock_vehicles_by_park(request):
        return load_json(cars_list)

    @mockserver.json_handler(CAR_COLORS)
    def _mock_parks_car_colors(request):
        response = load_json('parks_car_colors.json')
        return response

    @mockserver.json_handler(DRIVE_INTEGRATION_AUTH)
    def _mock_drive_integration(request):
        if drive_state == 'not_present':
            return {'access_status': drive_state, 'signed_auth': '123'}

        return {'access_status': drive_state}

    unique_drivers_mocks.set_exams(
        park_id,
        uuid,
        [{'course': 'business', 'result': 5, 'updated_by': 'support'}],
    )

    response = await taxi_driver_profile_view.post(
        ENDPOINT, params={'park_id': park_id}, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('responses/' + expected_response)

    if request_by_park:
        assert _mock_vehicles_by_park.times_called == 1
    else:
        assert _mock_vehicles_by_id.times_called == 1

    assert _mock_drive_integration.times_called == 1


@pytest.mark.config(
    TAXIMETER_MARKETPLACE={
        'cities': [],
        'countries': [],
        'dbs': ['db_id88'],
        'enable': True,
        'home_url': 'http://home_url',
        'driver_url': 'http://driver_url',
    },
)
@pytest.mark.experiments3(filename='experiments3_dvpbs_default.json')
async def test_no_vehicles(
        taxi_driver_profile_view,
        taxi_config,
        mockserver,
        driver_authorizer,
        load_json,
        mock_fleet_parks_list,
        driver_trackstory_mocks,
        unique_drivers_mocks,
):
    driver_authorizer.set_session('db_id88', 'session1', 'uuid1')

    @mockserver.json_handler(BINDING)
    def _mock_driver_profiles(request):
        response = load_json('vehicle_binding.json')
        return response

    unique_drivers_mocks.set_exams('db_id88', 'uuid1', [])

    response = await taxi_driver_profile_view.post(
        ENDPOINT, params={'park_id': 'db_id88'}, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('responses/response3.json')
