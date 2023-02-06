import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/driver/v1/scooters/v1/vehicle/dropoff'
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
                                    },
                                    {
                                        'id': 'vehicle_id_11',
                                        'number': '947',
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
                            'typed_extra': {'quantity': 5, 'vehicles': []},
                        },
                        {
                            'job_id': 'dropoff_job_2',
                            'type': 'dropoff_vehicles',
                            'status': 'planned',
                            'typed_extra': {'quantity': 1, 'vehicles': []},
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
async def test_handler(taxi_scooters_ops, mockserver, pgsql):
    create_missions(pgsql)

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_2',
            'job_id': 'dropoff_job_1',
            'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
        },
    )

    assert response1.status == 200
    assert (
        db_utils.get_jobs(
            pgsql, ids=['dropoff_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles']
        == [{'id': 'vehicle_id_1', 'number': '1337', 'status': 'processed'}]
    )

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_2',
            'job_id': 'dropoff_job_1',
            'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=947',
        },
    )

    assert response2.status == 200
    assert (
        db_utils.get_jobs(
            pgsql, ids=['dropoff_job_1'], fields=['typed_extra'], flatten=True,
        )[0]['vehicles']
        == [
            {'id': 'vehicle_id_1', 'number': '1337', 'status': 'processed'},
            {'id': 'vehicle_id_11', 'number': '947', 'status': 'processed'},
        ]
    )


@common.TRANSLATIONS
async def test_scan_twice(taxi_scooters_ops, mockserver, pgsql):
    create_missions(pgsql)

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_2',
            'job_id': 'dropoff_job_1',
            'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
        },
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_2',
            'job_id': 'dropoff_job_1',
            'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
        },
    )
    assert response2.status == 400
    assert response2.json() == {
        'code': 'Ошибка',
        'message': 'Самокат уже отсканирован',
    }


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['scooter_link'],
    [
        pytest.param(
            'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=42',
            id='incorrect scooter number',
        ),
        pytest.param('HTTPS://starcev.misha/42', id='wrongs link'),
    ],
)
@common.TRANSLATIONS
async def test_wrong_scooter(
        taxi_scooters_ops, mockserver, pgsql, scooter_link,
):
    create_missions(pgsql)
    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_1',
            'point_id': 'parking_place_1',
            'job_id': 'dropoff_job_1',
            'scooter_id': 'vehicle_id_1',
            'scooter_link': scooter_link,
        },
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Отсканирован не тот самокат',
    }

    typed_extra = db_utils.get_jobs(
        pgsql, ids=['dropoff_job_1'], fields=['typed_extra'], flatten=True,
    )[0]
    assert typed_extra['vehicles'] == []


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'mission_id': 'wrong_mission_id',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect mission',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'point_id': 'point_id_scooter_1',
                'job_id': 'job_id_scooter_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect mission status',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'wrong_point_id',
                'job_id': 'job_id_scooter_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Invalid point_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_1',
                'point_id': 'depot_point_2',
                'job_id': 'dropoff_job_11',
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
                'job_id': 'dropoff_job_2',
                'scooter_id': 'vehicle_id_1',
                'scooter_link': 'HTTPS://GO.YANDEX/SCOOTERS?NUMBER=1337',
            },
            id='Incorrect job status',
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
