import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/driver/v1/scooters/v1/vehicle/pickup'
OPEN_THE_LOCK = 'SCENARIO_UNLOCK_DOORS_AND_HOOD'


def create_missions(pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_1',
            'status': 'performing',
            'points': [
                {
                    'type': 'parking_place',
                    'status': 'arrived',
                    'point_id': 'parking_place_1',
                    'typed_extra': {'parking_place': {'id': 'parking_1'}},
                    'jobs': [
                        {
                            'job_id': 'pickup_job_1',
                            'type': 'pickup_vehicles',
                            'status': 'performing',
                            'typed_extra': {
                                'vehicles': [
                                    {
                                        'id': 'vehicle_id_1',
                                        'number': '1337',
                                        'status': 'pending',
                                        'problems': [],
                                        'has_lock': True,
                                    },
                                    {
                                        'id': 'vehicle_id_3',
                                        'number': '1338',
                                        'status': 'pending',
                                        'problems': [],
                                        'has_lock': False,
                                    },
                                ],
                            },
                        },
                        {
                            'job_id': 'pickup_job_2',
                            'type': 'pickup_vehicles',
                            'status': 'planned',
                            'typed_extra': {
                                'vehicles': [
                                    {
                                        'id': 'vehicle_id_2',
                                        'number': '0002',
                                        'status': 'pending',
                                        'problems': [],
                                    },
                                ],
                            },
                        },
                        {
                            'job_id': 'pickup_batteries_1',
                            'type': 'pickup_batteries',
                            'status': 'performing',
                            'typed_extra': {},
                        },
                    ],
                },
                {
                    'type': 'depot',
                    'status': 'planned',
                    'point_id': 'depot_point_2',
                    'typed_extra': {'scooter': {'id': 'scooter_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'pickup_job_11',
                            'type': 'battery_exchange',
                            'status': 'planned',
                            'typed_extra': {
                                'vehicles': [
                                    {
                                        'id': 'vehicle_id_11',
                                        'number': '00011',
                                        'status': 'pending',
                                        'problems': [],
                                    },
                                ],
                            },
                        },
                    ],
                },
            ],
        },
    )
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_2',
            'status': 'preparing',
            'points': [
                {
                    'type': 'scooter',
                    'status': 'planned',
                    'point_id': 'm2_point_1',
                    'typed_extra': {'depot': {'id': 'depot_id_1'}},
                },
            ],
        },
    )


@common.TRANSLATIONS
@pytest.mark.parametrize(
    'vehicle_id, scooter_link, times_called',
    [
        pytest.param(
            'vehicle_id_1',
            'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            1,
            id='process with lock',
        ),
        pytest.param(
            'vehicle_id_3',
            'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1338',
            0,
            id='process no lock',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        vehicle_id,
        scooter_link,
        times_called,
        mockserver,
        pgsql,
):
    create_missions(pgsql)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == vehicle_id
        assert request.json['action'] == OPEN_THE_LOCK
        return {}

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': vehicle_id,
            'scooter_link': scooter_link,
        },
    )

    assert response.status == 200
    assert car_control.times_called == times_called

    vehicles = db_utils.get_jobs(
        pgsql, ids=['pickup_job_1'], fields=['typed_extra'], flatten=True,
    )[0]['vehicles']
    assert (
        list(filter(lambda vehicle: vehicle['id'] == vehicle_id, vehicles))[0][
            'status'
        ]
        == 'processed'
    )


@common.TRANSLATIONS
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
        taxi_scooters_ops, mockserver, pgsql, car_control_response,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'vehicle_id_1'
        assert request.json['action'] == OPEN_THE_LOCK
        return mockserver.make_response(status=500, json=car_control_response)

    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
            'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
        },
    )

    assert car_control.times_called == 1

    assert response.status == 500
    assert response.json() == {
        'code': 'Ошибка телематики',
        'message': 'Не удалось открыть замок',
    }
    assert (
        db_utils.get_jobs(
            pgsql, ids=['pickup_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles'][0]['status']
        == 'pending'
    )


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['scooter_link'],
    [
        pytest.param(
            'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=LOL', id='wrongs cooter',
        ),
        pytest.param('HTTPS://starcev.misha/42', id='wrongs link'),
    ],
)
async def test_wrong_scooter(
        taxi_scooters_ops, mockserver, pgsql, scooter_link,
):
    create_missions(pgsql)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/control')
    async def car_control(request):
        assert request.json['car_id'] == 'vehicle_id_1'
        assert request.json['action'] == OPEN_THE_LOCK
        return {}

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
            'scooter_link': scooter_link,
        },
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Отсканирован не тот самокат',
    }
    assert car_control.times_called == 0

    assert (
        db_utils.get_jobs(
            pgsql, ids=['pickup_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles'][0]['status']
        == 'pending'
    )


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'mission_id': 'wrong_mission_id',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect mission',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'wrong_point_id',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Invalid point_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'depot_point_2',
                'job_id': 'pickup_job_11',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect point status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'wrong_job_id',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Invalid job_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'pickup_job_2',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect job status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'pickup_batteries_1',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect job type',
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
        'code': 'Ошибка',
        'message': 'Что-то пошло не так...',
    }
