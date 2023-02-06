ENDPOINT = '/scooters-misc/v1/service/vehicle-info'


async def test_handler(taxi_scooters_misc, load_json, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details.json')

    @mockserver.json_handler(
        '/scooters-ops-repair/scooters-ops-repair/v1/repairs/list',
    )
    def mock_repairs_list(request):
        assert request.json['vehicle_id'] == 'vehicle_id_1'
        assert request.json['statuses'] == ['completed']
        assert request.query['limit'] == '5'

        return load_json('repairs_list.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def mock_telematics_state(request):
        return load_json('telematics_state.json')

    res = await taxi_scooters_misc.get(
        ENDPOINT, params={'vehicle_id': 'vehicle_id_1'},
    )
    assert res.status_code == 200
    assert res.json() == {
        'complains': ['Сломалась ручка газа'],
        'firmware': {
            'ble': 'R00A03V02',
            'ecu': '4401',
            'gps': 'LC29DCNR01A02S_2WDR_HYF_TEMP0412A',
            'iot': 'R06A05V02',
        },
        'sensors': {'mileage': 370.39},
        'repairs': [
            {
                'completed_at': '2022-06-10T10:00:00+00:00',
                'jobs': ['stickers_change'],
                'mileage': 100.5,
            },
            {
                'completed_at': '2022-06-14T11:00:00+00:00',
                'jobs': ['brake_adjustment', 'fender_repair'],
                'mileage': 500.0,
            },
        ],
    }

    assert mock_repairs_list.times_called == 1
    assert mock_car_details.times_called == 2
    assert mock_telematics_state.times_called == 1


async def test_unknown_vehicle(taxi_scooters_misc, load_json, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        return {'timestamp': 1655447659, 'cars': []}

    res = await taxi_scooters_misc.get(
        ENDPOINT, params={'vehicle_id': 'vehicle_id_1'},
    )
    assert res.status_code == 404
    assert res.json() == {
        'code': 'not_found',
        'message': 'unknown vehicle_id:vehicle_id_1',
    }


async def test_empty_responses(taxi_scooters_misc, load_json, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return {
            'cars': [
                {
                    'id': 'vehicle_id_1',
                    'location': {'lat': 56.83585055, 'lon': 60.59104971},
                    'model_id': 'ninebot',
                    'number': '9423',
                    'tags': [],
                    'telematics': {'fuel_level': 96, 'mileage': 370.39},
                },
            ],
            'timestamp': 1655370233,
        }

    @mockserver.json_handler(
        '/scooters-ops-repair/scooters-ops-repair/v1/repairs/list',
    )
    def mock_repairs_list(request):
        return {'repairs': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def mock_telematics_state(request):
        return {'sensors': []}

    res = await taxi_scooters_misc.get(
        ENDPOINT, params={'vehicle_id': 'vehicle_id_1'},
    )
    assert res.status_code == 200
    assert res.json() == {
        'complains': [],
        'firmware': {},
        'sensors': {},
        'repairs': [],
    }

    assert mock_repairs_list.times_called == 1
    assert mock_car_details.times_called == 2
    assert mock_telematics_state.times_called == 1
