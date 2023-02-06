import pytest

from tests_scooters_misc import utils

ENDPOINT = '/scooters-misc/v1/service/vehicle-control'


@pytest.mark.parametrize(
    ['request_action', 'expected_car_control_action'],
    [
        pytest.param('unlock_cable_lock', 'SCENARIO_UNLOCK_DOORS_AND_HOOD'),
        pytest.param('unlock_battery_cover', 'YADRIVE_UNLOCK_HOOD'),
        pytest.param('horn_and_blink', 'HORN_AND_BLINK'),
        pytest.param('unlock_wheel', 'OPEN_DOORS'),
        pytest.param('lock_wheel', 'CLOSE_DOORS'),
    ],
)
async def test_handler(
        taxi_scooters_misc,
        pgsql,
        load_json,
        mockserver,
        request_action,
        expected_car_control_action,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    def mock_car_control(request):
        assert request.json['car_id'] == 'vehicle_id_1'
        assert request.json['action'] == expected_car_control_action
        return {'telematic_status': 'success'}

    res = await taxi_scooters_misc.post(
        ENDPOINT,
        {
            'vehicle_id': 'vehicle_id_1',
            'action': request_action,
            'user_id': 'user_id_1',
        },
    )
    assert res.status_code == 200

    assert mock_car_details.times_called == 2
    assert mock_car_control.times_called == 1

    assert (
        utils.get_vehicle_control_log(pgsql, vehicle_ids=['vehicle_id_1'])
        == [
            {
                'id': 1,
                'timestamp': utils.AnyValue(),
                'user_id': 'user_id_1',
                'vehicle_id': 'vehicle_id_1',
                'action': request_action,
                'source': 'unknown',
            },
        ]
    )


async def test_unknown_vehicle(
        taxi_scooters_misc, pgsql, load_json, mockserver,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details_empty.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    def mock_car_control(request):
        return {}

    res = await taxi_scooters_misc.post(
        ENDPOINT,
        {
            'vehicle_id': 'unknown_vehicle_id_1',
            'action': 'lock_wheel',
            'user_id': 'user_id_1',
        },
    )
    assert res.status_code == 404

    assert mock_car_details.times_called == 2
    assert mock_car_control.times_called == 0

    assert (
        utils.get_vehicle_control_log(
            pgsql, vehicle_ids=['unknown_vehicle_id_1'],
        )
        == []
    )


@pytest.mark.parametrize(
    ['car_control_response'],
    [
        pytest.param({'error_details': {}}, id='Car control 500'),
        pytest.param(
            {
                'error_details': {},
                'telematic_message_code': 'code',
                'telematic_status': 'telematic_status',
                'telematics_message': 'telematics_message',
            },
            id='Car control telematic error',
        ),
    ],
)
async def test_car_control_errors(
        taxi_scooters_misc, mockserver, car_control_response, load_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        return load_json('car_details.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    def _mock_car_control(request):
        return mockserver.make_response(status=500, json=car_control_response)

    res = await taxi_scooters_misc.post(
        ENDPOINT,
        {
            'vehicle_id': 'unknown_vehicle_id_1',
            'action': 'lock_wheel',
            'user_id': 'user_id_1',
        },
    )
    assert res.status_code == 500
