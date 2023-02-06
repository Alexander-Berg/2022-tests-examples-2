import copy

import pytest

from tests_scooters_ops_repair import db_utils

HANDLER = '/scooters-ops-repair/v1/repair/stop'

REPAIR_1 = {
    'repair_id': 'repair_id_1',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'started',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
    'jobs': [
        {
            'job_id': 'job_id_1',
            'status': 'completed',
            'type': 'type_1',
            'started_at': '2022-04-01T07:05:00+0000',
            'completed_at': '2022-04-01T07:15:00+0000',
        },
    ],
}

REPAIR_WITH_UNCOMPLETED_JOB = {
    'repair_id': 'repair_id_2',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'started',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
    'jobs': [
        {
            'job_id': 'job_id_2',
            'status': 'started',
            'type': 'type_1',
            'started_at': '2022-04-01T07:05:00+0000',
            'completed_at': None,
        },
    ],
}


@pytest.mark.now('2022-04-01T08:05:00+00:00')
async def test_handler(taxi_scooters_ops_repair, pgsql, stq):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))

    response = await taxi_scooters_ops_repair.post(
        HANDLER, params={'repair_id': 'repair_id_1'},
    )

    assert response.status == 200
    assert db_utils.get_repairs(pgsql, ids=['repair_id_1']) == [
        {
            'performer_id': 'performer_id_1',
            'depot_id': 'depot_id_1',
            'repair_id': 'repair_id_1',
            'status': 'completed',
            'vehicle_id': 'vehicle_id_1',
            'started_at': db_utils.parse_timestring_aware(
                '2022-04-01T07:05:00+0000',
            ),
            'completed_at': db_utils.parse_timestring_aware(
                '2022-04-01T08:05:00+0000',
            ),
        },
    ]
    assert stq.scooters_ops_remove_tags.times_called == 1


async def test_retry(taxi_scooters_ops_repair, pgsql):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))

    response1 = await taxi_scooters_ops_repair.post(
        HANDLER, params={'repair_id': 'repair_id_1'},
    )
    assert response1.status == 200
    completed_at_after__response1 = db_utils.get_repairs(
        pgsql, ids=['repair_id_1'],
    )[0]['completed_at']

    response2 = await taxi_scooters_ops_repair.post(
        HANDLER, params={'repair_id': 'repair_id_1'},
    )
    assert response2.status == 200

    completed_at_after__response2 = db_utils.get_repairs(
        pgsql, ids=['repair_id_1'],
    )[0]['completed_at']
    assert completed_at_after__response1 == completed_at_after__response2


@pytest.mark.now('2022-04-01T07:05:00+00:00')
async def test_unknown_repair(taxi_scooters_ops_repair):

    response = await taxi_scooters_ops_repair.post(
        HANDLER, params={'repair_id': 'unknown_repair_id'},
    )

    assert response.status == 404


async def test_uncompleted_jobs(taxi_scooters_ops_repair, pgsql, stq):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_WITH_UNCOMPLETED_JOB))

    response = await taxi_scooters_ops_repair.post(
        HANDLER, params={'repair_id': 'repair_id_2'},
    )

    assert response.status == 400
    assert stq.scooters_ops_remove_tags.times_called == 0
