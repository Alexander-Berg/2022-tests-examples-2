import copy

import pytest

from tests_scooters_ops import db_utils


HANDLER = '/scooters-ops/v1/processing/missions/set-status'
SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'status': 'created',
    'revision': 1,
    'points': [
        {'type': 'depot', 'typed_extra': {'depot_id': 'depot1'}},
        {
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_id', 'number': 'scooter_number'},
            },
        },
        {'type': 'depot', 'typed_extra': {'depot_id': 'depot1'}},
    ],
}


@pytest.mark.parametrize(
    ['status', 'expected_history_type'],
    [
        ('preparing', 'mission_status_updated'),
        ('assigning', 'mission_status_updated'),
        ('performing', 'mission_started'),
        ('completed', 'mission_completed'),
        ('cancelling', 'mission_cancelling'),
        ('failed', 'mission_status_updated'),
    ],
)
async def test_handler(
        taxi_scooters_ops, pgsql, status, expected_history_type,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'status': status},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )

    assert response.status == 200
    assert response.json()['mission']['status'] == status

    assert db_utils.get_missions(
        pgsql, ids=['mission_id'], fields=['status', 'revision'],
    ) == [{'status': status, 'revision': 2}]

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    assert history == [
        {
            'type': expected_history_type,
            'extra': {
                'mission_status': status,
                'performer_id': '',
                'tags': [],
            },
        },
    ]


async def test_idempotency(taxi_scooters_ops, pgsql):
    db_utils.add_mission(pgsql, SIMPLE_MISSION)

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {'status': 'preparing'},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {'status': 'preparing'},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )
    assert response2.status == 200

    assert db_utils.get_missions(
        pgsql, ids=['mission_id'], fields=['status', 'revision'],
    ) == [{'status': 'preparing', 'revision': 2}]

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    assert len(history) == 1


async def test_not_found(taxi_scooters_ops):
    response = await taxi_scooters_ops.post(
        HANDLER,
        {'status': 'preparing'},
        params={'mission_id': 'absent_mission_id', 'mission_revision': 1},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not-found',
        'message': 'Cannot find mission: absent_mission_id',
    }


async def test_conflict_revision(taxi_scooters_ops, pgsql):
    current_revision = SIMPLE_MISSION['revision']

    db_utils.add_mission(pgsql, SIMPLE_MISSION)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'status': 'preparing'},
        params={
            'mission_id': 'mission_id',
            'mission_revision': current_revision + 10,
        },
    )

    assert response.status == 409
    assert response.json() == {
        'code': 'conflict',
        'message': 'Conflict on update mission: mission_id. Revision mismatch',
    }
