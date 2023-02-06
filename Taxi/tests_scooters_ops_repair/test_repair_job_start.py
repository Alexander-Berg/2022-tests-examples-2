import copy

import pytest

from tests_scooters_ops_repair import db_utils


HANDLER = '/scooters-ops-repair/v1/repair-job/start'

REPAIR_1 = {
    'repair_id': 'repair_id_1',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'started',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
}

COMPLETED_REPAIR = {
    'repair_id': 'completed_repair_1',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'completed',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': '2022-04-01T07:05:00+0000',
    'vehicle_info': {'mileage': 370.4},
}

REPAIR_WITH_COMPLETED_JOB = {
    'repair_id': 'repair_id_2',
    'performer_id': 'performer_id_2',
    'depot_id': 'depot_id_2',
    'status': 'started',
    'vehicle_id': 'vehicle_id_2',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
    'jobs': [
        {
            'job_id': 'job_id_1',
            'status': 'completed',
            'type': 'type_1',
            'started_at': '2022-04-01T07:05:00+0000',
            'completed_at': '2022-04-01T07:06:00+0000',
        },
    ],
}


REPAIR_WITH_UNCOMPLETED_JOB = {
    'repair_id': 'repair_id_2',
    'performer_id': 'performer_id_2',
    'depot_id': 'depot_id_2',
    'status': 'started',
    'vehicle_id': 'vehicle_id_2',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 370.4},
    'jobs': [
        {
            'job_id': 'job_id_1',
            'status': 'started',
            'type': 'type_1',
            'started_at': '2022-04-01T07:05:00+0000',
            'completed_at': None,
        },
    ],
}


@pytest.mark.now('2022-04-01T07:05:00+00:00')
@pytest.mark.config(
    SCOOTERS_OPS_REPAIR_TYPES=[{'id': 'type_1', 'name': 'Type 1'}],
)
async def test_handler(taxi_scooters_ops_repair, pgsql):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))
    response = await taxi_scooters_ops_repair.post(
        HANDLER, {'repair_id': 'repair_id_1', 'type': 'type_1'},
    )

    assert response.status == 200
    assert response.json() == {
        'job_id': db_utils.AnyValue(),
        'started_at': '2022-04-01T07:05:00+00:00',
        'status': 'started',
        'type': 'type_1',
    }
    job_id = response.json()['job_id']

    assert db_utils.get_jobs(pgsql, ids=[job_id]) == [
        {
            'job_id': job_id,
            'repair_id': 'repair_id_1',
            'status': 'started',
            'type': 'type_1',
            'started_at': db_utils.parse_timestring_aware(
                '2022-04-01T07:05:00+0000',
            ),
            'completed_at': None,
        },
    ]


@pytest.mark.now('2022-04-01T07:05:00+00:00')
@pytest.mark.config(
    SCOOTERS_OPS_REPAIR_TYPES=[
        {'id': 'type_1', 'name': 'Type 1'},
        {'id': 'type_2', 'name': 'Type 2'},
    ],
)
async def test_handler_with_existing_uncompleted_job_with_different_type(
        taxi_scooters_ops_repair, pgsql,
):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_WITH_UNCOMPLETED_JOB))
    response = await taxi_scooters_ops_repair.post(
        HANDLER, {'repair_id': 'repair_id_2', 'type': 'type_2'},
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'repair has active job with different type',
    }


@pytest.mark.now('2022-04-01T07:05:00+00:00')
@pytest.mark.config(
    SCOOTERS_OPS_REPAIR_TYPES=[{'id': 'type_1', 'name': 'Type 1'}],
)
async def test_handler_with_existing_completed_job(
        taxi_scooters_ops_repair, pgsql,
):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_WITH_COMPLETED_JOB))

    response = await taxi_scooters_ops_repair.post(
        HANDLER, {'repair_id': 'repair_id_2', 'type': 'type_1'},
    )

    assert response.status == 200
    assert db_utils.get_jobs(
        pgsql, repair_ids=['repair_id_2'], fields=['job_id'], flatten=True,
    ) == ['job_id_1', response.json()['job_id']]


@pytest.mark.config(
    SCOOTERS_OPS_REPAIR_TYPES=[{'id': 'type_1', 'name': 'Type 1'}],
)
async def test_retry(taxi_scooters_ops_repair, pgsql, mockserver, load_json):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))

    response1 = await taxi_scooters_ops_repair.post(
        HANDLER, {'repair_id': 'repair_id_1', 'type': 'type_1'},
    )
    response2 = await taxi_scooters_ops_repair.post(
        HANDLER, {'repair_id': 'repair_id_1', 'type': 'type_1'},
    )

    assert response1.status == 200
    assert response2.status == 200
    assert response1.json() == response2.json()

    assert len(db_utils.get_jobs(pgsql, repair_ids=['repair_id_1'])) == 1


@pytest.mark.parametrize(
    ['body', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {
                'repair_id': 'unknown_repair',
                'job_id': 'job_id_1',
                'type': 'type_1',
            },
            404,
            {'code': 'not_found', 'message': 'unknown repair'},
            id='unknown repair',
        ),
        pytest.param(
            {
                'repair_id': 'completed_repair_1',
                'job_id': 'job_id_1',
                'type': 'type_1',
            },
            400,
            {'code': 'bad_request', 'message': 'repair already finished'},
            id='completed repair',
        ),
        pytest.param(
            {
                'repair_id': 'repair_id_1',
                'job_id': 'job_id_1',
                'type': 'unknown_type',
            },
            400,
            {'code': 'bad_request', 'message': 'Unknown job type'},
            id='unknown job type',
        ),
    ],
)
@pytest.mark.config(
    SCOOTERS_OPS_REPAIR_TYPES=[{'id': 'type_1', 'name': 'Type 1'}],
)
async def test_bad_request(
        taxi_scooters_ops_repair,
        pgsql,
        body,
        expected_response,
        expected_code,
):
    db_utils.add_repair(pgsql, copy.deepcopy(REPAIR_1))
    db_utils.add_repair(pgsql, copy.deepcopy(COMPLETED_REPAIR))

    response = await taxi_scooters_ops_repair.post(HANDLER, body)

    assert response.status == expected_code
    assert response.json() == expected_response
