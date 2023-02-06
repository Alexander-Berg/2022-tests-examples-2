import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils


def get_handle_action(handle):
    actions = {
        '/driver/v1/scooters/old-flow/v1/vehicle/open_battery_door': (
            'YADRIVE_UNLOCK_HOOD'
        ),
        '/driver/v1/scooters/old-flow/v1/vehicle/find': 'HORN_AND_BLINK',
    }
    return actions[handle]


def create_missions(pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'type': 'depot',
                    'cargo_point_id': 'cargo_point_id_depot_1',
                    'typed_extra': {'depot': {'id': 'depot_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'cargo_point_id': 'cargo_point_id_scooter_1',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_2',
            'status': 'preparing',
            'points': [
                {
                    'type': 'depot',
                    'cargo_point_id': 'cargo_point_id_depot_2',
                    'typed_extra': {'depot': {'id': 'depot_id_2'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'cargo_point_id': 'cargo_point_id_scooter_2',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_2'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )


HANDLERS = [
    '/driver/v1/scooters/old-flow/v1/vehicle/find',
    '/driver/v1/scooters/old-flow/v1/vehicle/open_battery_door',
]


@pytest.mark.parametrize('handle', HANDLERS)
async def test_handler(taxi_scooters_ops, mockserver, pgsql, handle):
    create_missions(pgsql)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'vehicle_id_1'
        assert request.json['action'] == get_handle_action(handle)
        return {}

    response = await taxi_scooters_ops.post(
        handle,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert response.status == 200
    assert response.json() == {}
    assert car_control.times_called == 1


@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'cargo_point_id': 'incorrect_cargo_point_id',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'cargo_point_id': 'incorrect_cargo_point_id',
            },
            id='Invalid point id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'cargo_point_id': 'cargo_point_id_depot_1',
            },
            id='Invalid point type',
        ),
    ],
)
@common.TRANSLATIONS
@pytest.mark.parametrize('handle', HANDLERS)
async def test_validation_request(taxi_scooters_ops, pgsql, params, handle):
    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        handle, headers=common.DAP_HEADERS, params=params,
    )

    assert response.status == 200
    assert response.json()['message'] == {
        'title': 'Некорректный запрос',
        'body': 'Что-то пошло не так...',
    }


@pytest.mark.parametrize(
    [
        'car_control_response',
        'expected_response_code',
        'expected_response_message',
        'expected_telematic_errors_times_called',
    ],
    [
        pytest.param(
            {'error_details': {}},
            500,
            'Internal Server Error',
            0,
            id='Car control 500',
        ),
        pytest.param(
            {
                'error_details': {},
                'telematic_message_code': 'code',
                'telematic_status': 'telematic_status',
                'telematics_message': 'telematics_message',
            },
            200,
            {
                'title': 'Ошибка телематики',
                'body': 'Не удалось передать команду самокату',
            },
            1,
            id='Car control telematic error',
        ),
    ],
)
@common.TRANSLATIONS
@pytest.mark.parametrize('handle', HANDLERS)
async def test_car_control_errors(
        taxi_scooters_ops,
        mockserver,
        testpoint,
        pgsql,
        handle,
        car_control_response,
        expected_response_code,
        expected_response_message,
        expected_telematic_errors_times_called,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'vehicle_id_1'
        assert request.json['action'] == get_handle_action(handle)
        return mockserver.make_response(status=500, json=car_control_response)

    @testpoint('telematic_error')
    def telematic_error(data):
        assert (
            data['message']
            == 'Telematic error, code: code, status: telematic_status, '
            'message: telematics_message'
        )

    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        handle,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert car_control.times_called == 1
    assert (
        telematic_error.times_called == expected_telematic_errors_times_called
    )

    assert response.status == expected_response_code
    assert response.json()['message'] == expected_response_message
