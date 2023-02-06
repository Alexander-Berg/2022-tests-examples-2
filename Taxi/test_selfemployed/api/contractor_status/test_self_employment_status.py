from testsuite.utils import http

HEADERS = {
    'X-Request-Application-Version': '10.12',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'contractorid',
    'X-YaTaxi-Park-Id': 'parkid',
    'User-Agent': (
        'app:pro brand:yandex version:10.12 '
        'platform:ios platform_version:15.0.1'
    ),
}


async def test_has_car(se_client, mock_driver_profiles, mock_fleet_vehicles):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorid'],
            'projection': ['data.car_id'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'car_id': 'carid'},
                },
            ],
        }

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _get_car(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_carid']}
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'parkid_carid',
                    'data': {
                        'brand': 'brand',
                        'model': 'model',
                        'number': 'number',
                        'number_normalized': 'number',
                        'color': 'color',
                        'year': '2020',
                    },
                },
            ],
        }

    # TODO: mock fleet-vehicles and check result

    response = await se_client.get(
        '/driver/self_employment/status', headers=HEADERS,
    )
    assert await response.json() == {
        'car': 'brand model',
        'car_brand': 'brand',
        'car_model': 'model',
        'car_number': 'number',
    }
    assert response.status == 200


async def test_has_no_car(
        se_client, mock_driver_profiles, mock_fleet_vehicles,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorid'],
            'projection': ['data.car_id'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {},
                },
            ],
        }

    response = await se_client.get(
        '/driver/self_employment/status', headers=HEADERS,
    )
    assert await response.json() == {}

    assert response.status == 200
