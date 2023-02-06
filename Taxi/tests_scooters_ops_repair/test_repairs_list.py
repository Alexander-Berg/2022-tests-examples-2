import copy

from tests_scooters_ops_repair import db_utils

HANDLER = '/scooters-ops-repair/v1/repairs/list'

COMPLETED_REPAIR_1 = {
    'repair_id': 'repair_id_1',
    'performer_id': 'performer_id_1',
    'depot_id': 'depot_id_1',
    'status': 'completed',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-01T07:05:00+0000',
    'completed_at': '2022-04-01T08:05:00+0000',
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

COMPLETED_REPAIR_2 = {
    'repair_id': 'repair_id_2',
    'performer_id': 'performer_id_2',
    'depot_id': 'depot_id_2',
    'status': 'completed',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-02T07:05:00+0000',
    'completed_at': '2022-04-02T08:05:00+0000',
    'vehicle_info': {'mileage': 372.4},
    'jobs': [
        {
            'job_id': 'job_id_2',
            'status': 'completed',
            'type': 'type_1',
            'started_at': '2022-04-02T07:05:00+0000',
            'completed_at': '2022-04-02T07:15:00+0000',
        },
    ],
}

UNCOMPLETED_REPAIR_3 = {
    'repair_id': 'repair_id_3',
    'performer_id': 'performer_id_3',
    'depot_id': 'depot_id_3',
    'status': 'started',
    'vehicle_id': 'vehicle_id_1',
    'started_at': '2022-04-03T07:05:00+0000',
    'completed_at': None,
    'vehicle_info': {'mileage': 372.4},
    'jobs': [
        {
            'job_id': 'job_id_3',
            'status': 'completed',
            'type': 'type_1',
            'started_at': '2022-04-03T07:05:00+0000',
            'completed_at': '2022-04-03T07:15:00+0000',
        },
    ],
}


async def test_handler(taxi_scooters_ops_repair, pgsql):
    db_utils.add_repair(pgsql, copy.deepcopy(COMPLETED_REPAIR_1))
    db_utils.add_repair(pgsql, copy.deepcopy(COMPLETED_REPAIR_2))
    db_utils.add_repair(pgsql, copy.deepcopy(UNCOMPLETED_REPAIR_3))

    response = await taxi_scooters_ops_repair.post(
        HANDLER,
        {'vehicle_id': 'vehicle_id_1', 'statuses': ['completed']},
        params={'limit': 5},
    )

    assert response.status == 200
    assert response.json() == {
        'repairs': [
            {
                'completed_at': '2022-04-01T08:05:00+00:00',
                'jobs': [
                    {
                        'completed_at': '2022-04-01T07:15:00+00:00',
                        'job_id': 'job_id_1',
                        'started_at': '2022-04-01T07:05:00+00:00',
                        'status': 'completed',
                        'type': 'type_1',
                    },
                ],
                'performer_id': 'performer_id_1',
                'repair_id': 'repair_id_1',
                'depot_id': 'depot_id_1',
                'started_at': '2022-04-01T07:05:00+00:00',
                'status': 'completed',
                'vehicle_id': 'vehicle_id_1',
                'vehicle_info': {'mileage': 370.4},
            },
            {
                'completed_at': '2022-04-02T08:05:00+00:00',
                'jobs': [
                    {
                        'completed_at': '2022-04-02T07:15:00+00:00',
                        'job_id': 'job_id_2',
                        'started_at': '2022-04-02T07:05:00+00:00',
                        'status': 'completed',
                        'type': 'type_1',
                    },
                ],
                'performer_id': 'performer_id_2',
                'repair_id': 'repair_id_2',
                'depot_id': 'depot_id_2',
                'started_at': '2022-04-02T07:05:00+00:00',
                'status': 'completed',
                'vehicle_id': 'vehicle_id_1',
                'vehicle_info': {'mileage': 372.4},
            },
        ],
    }
