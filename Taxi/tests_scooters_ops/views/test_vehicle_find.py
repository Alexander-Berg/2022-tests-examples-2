import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/driver/v1/scooters/v1/vehicle/find'
HORN_AND_BLINK = 'HORN_AND_BLINK'


def create_missions(pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'type': 'depot',
                    'status': 'arrived',
                    'point_id': 'point_id_depot_1',
                    'typed_extra': {'depot': {'id': 'depot_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'job_id_depot_1',
                            'type': 'battery_exchange',
                            'status': 'performing',
                            'typed_extra': {'vehicle_id': 'scooter_id_1'},
                        },
                        {
                            'job_id': 'job_id_depot_2',
                            'type': 'do_nothing',
                            'status': 'cancelled',
                            'typed_extra': {},
                        },
                    ],
                },
                {
                    'type': 'scooter',
                    'status': 'skipped',
                    'point_id': 'point_id_scooter_1',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                },
            ],
        },
    )
    db_utils.add_mission(
        pgsql, {'mission_id': 'mission_id_2', 'status': 'preparing'},
    )


@common.TRANSLATIONS
async def test_handler(taxi_scooters_ops, mockserver, pgsql):
    create_missions(pgsql)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'scooter_id_1'
        assert request.json['action'] == HORN_AND_BLINK
        return {}

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_depot_1',
            'job_id': 'job_id_depot_1',
            'scooter_id': 'scooter_id_1',
        },
    )

    assert response.status == 200
    assert car_control.times_called == 1


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'point_id': 'point_id',
                'job_id': 'job_id_1',
                'scooter_id': 'scooter_id_1',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id',
                'job_id': 'job_id_1',
                'scooter_id': 'scooter_id_1',
            },
            id='Invalid point_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_1',
                'scooter_id': 'scooter_id_1',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_depot_1',
                'job_id': 'job_id_1',
                'scooter_id': 'scooter_id_1',
            },
            id='Invalid job_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_depot_1',
                'job_id': 'job_id_depot_2',
                'scooter_id': 'scooter_id_1',
            },
            id='Incorrect job status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_depot_1',
                'job_id': 'job_id_depot_1',
                'scooter_id': 'scooter_id_2',
            },
            id='No scooter in job',
        ),
    ],
)
async def test_validation_request(taxi_scooters_ops, pgsql, params):
    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=params,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Некорректный запрос',
        'message': 'Что-то пошло не так...',
    }


@common.TRANSLATIONS
@pytest.mark.parametrize(
    [
        'car_control_response',
        'expected_response_message',
        'expected_telematic_errors_times_called',
    ],
    [
        pytest.param(
            {'error_details': {}},
            {'code': '500', 'message': 'Internal Server Error'},
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
            {
                'code': 'Ошибка телематики',
                'message': 'Не удалось передать команду самокату',
            },
            1,
            id='Car control telematic error',
        ),
    ],
)
async def test_car_control_errors(
        taxi_scooters_ops,
        mockserver,
        testpoint,
        pgsql,
        car_control_response,
        expected_response_message,
        expected_telematic_errors_times_called,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'scooter_id_1'
        assert request.json['action'] == HORN_AND_BLINK
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
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_depot_1',
            'job_id': 'job_id_depot_1',
            'scooter_id': 'scooter_id_1',
        },
    )

    assert car_control.times_called == 1
    assert (
        telematic_error.times_called == expected_telematic_errors_times_called
    )

    assert response.status == 500
    assert response.json() == expected_response_message
