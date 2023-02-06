import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/driver/v1/scooters/v1/vehicle/problems'


def create_missions(pgsql, status=None, problems=None):
    status = status if status else 'pending'
    problems = problems if problems else []
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
                                    },
                                ],
                            },
                        },
                        {
                            'job_id': 'pickup_job_2',
                            'type': 'dropoff_vehicles',
                            'status': 'planned',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
                {
                    'type': 'parking_place',
                    'status': 'arrived',
                    'point_id': 'parking_place_2',
                    'typed_extra': {'parking_place': {'id': 'parking_1'}},
                    'jobs': [
                        {
                            'job_id': 'dropoff_job_1',
                            'type': 'dropoff_vehicles',
                            'status': 'performing',
                            'typed_extra': {'quantity': 5},
                        },
                        {
                            'job_id': 'dropoff_job_2',
                            'type': 'dropoff_vehicles',
                            'status': 'planned',
                            'typed_extra': {'quantity': 1},
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
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.parametrize(
    'status, problems, expected_status, expected_problems',
    [
        pytest.param(
            'pending',
            [],
            'problems',
            ['discharged', 'not_found', 'didnt_open'],
            id='set_pending_to_problems',
        ),
        pytest.param(
            'problems',
            ['discharged', 'not_found', 'didnt_open'],
            'pending',
            [],
            id='unset_problems',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        mockserver,
        pgsql,
        status,
        problems,
        expected_status,
        expected_problems,
):
    create_missions(pgsql, status, problems)

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {'problems': expected_problems},
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
        },
    )

    assert response1.status == 200
    assert (
        db_utils.get_jobs(
            pgsql, ids=['pickup_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles']
        == [
            {
                'id': 'vehicle_id_1',
                'number': '1337',
                'status': expected_status,
                'problems': expected_problems,
            },
        ]
    )


@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
async def test_incorrect_problems(taxi_scooters_ops, pgsql):
    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'problems': ['wrong_problem']},
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
        },
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Что-то пошло не так...',
    }


@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
async def test_request_twice(taxi_scooters_ops, mockserver, pgsql):
    create_missions(pgsql)

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {'problems': ['discharged']},
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
        },
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {'problems': ['not_found']},
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'pickup_job_1',
            'scooter_id': 'vehicle_id_1',
        },
    )
    assert response2.status == 200
    assert (
        db_utils.get_jobs(
            pgsql, ids=['pickup_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles']
        == [
            {
                'id': 'vehicle_id_1',
                'number': '1337',
                'status': 'problems',
                'problems': ['not_found'],
            },
        ]
    )


@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'mission_id': 'wrong_mission_id',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
            },
            id='Incorrect mission',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'wrong_point_id',
                'job_id': 'job_id_scooter_1',
                'scooter_id': 'vehicle_id_1',
            },
            id='Invalid point_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'depot_point_2',
                'job_id': 'pickup_job_11',
                'scooter_id': 'vehicle_id_1',
            },
            id='Incorrect point status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'wrong_job_id',
                'scooter_id': 'vehicle_id_1',
            },
            id='Invalid job_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'pickup_job_2',
                'scooter_id': 'vehicle_id_1',
            },
            id='Incorrect job status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'parking_place_1',
                'job_id': 'pickup_batteries_1',
                'scooter_id': 'vehicle_id_1',
            },
            id='Incorrect job type',
        ),
    ],
)
async def test_validation_request(taxi_scooters_ops, pgsql, params):
    create_missions(pgsql)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'problems': ['discharged']},
        headers=common.DAP_HEADERS,
        params=params,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Что-то пошло не так...',
    }
