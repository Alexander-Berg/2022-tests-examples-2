import pytest

from tests_scooters_ops import db_utils

HANDLER = '/scooters-ops/v1/missions/list'
MISSION_1 = {
    'mission_id': 'mission_1',
    'status': 'created',
    'revision': 1,
    'points': [
        {'type': 'depot', 'typed_extra': {'depot': {'id': 'depot1'}}},
        {'type': 'scooter', 'typed_extra': {'scooter': {'id': 'scooter_id'}}},
        {'type': 'depot', 'typed_extra': {'depot': {'id': 'depot1'}}},
    ],
    'created_at': '2000-01-01T12:00:00.00000+00:00',
}
MISSION_2 = {
    'mission_id': 'mission_2',
    'status': 'preparing',
    'revision': 1,
    'points': [],
    'created_at': '2000-01-01T14:00:00.00000+00:00',
}
MISSION_3 = {
    'mission_id': 'mission_3',
    'status': 'performing',
    'revision': 1,
    'points': [],
    'created_at': '2000-01-02T08:00:00.00000+00:00',
}
MISSION_4 = {
    'mission_id': 'mission_4',
    'status': 'completed',
    'revision': 1,
    'points': [],
    'created_at': '2000-01-03T21:00:00.00000+00:00',
}


@pytest.mark.parametrize(
    ['request_body', 'expected_missions_ids'],
    [
        pytest.param(
            {},
            {'mission_1', 'mission_2', 'mission_3', 'mission_4'},
            id='Without filtration',
        ),
        pytest.param(
            {'statuses': ['created', 'completed']},
            {'mission_1', 'mission_4'},
            id='Filter by status',
        ),
        pytest.param(
            {'created': {'after': '2000-01-02T00:00:00.00000+00:00'}},
            {'mission_3', 'mission_4'},
            id='Created after',
        ),
        pytest.param(
            {'created': {'before': '2000-01-02T00:00:00.00000+00:00'}},
            {'mission_1', 'mission_2'},
            id='Created before',
        ),
        pytest.param(
            {
                'created': {
                    'after': '2000-01-01T13:00:00.00000+00:00',
                    'before': '2000-01-02T12:00:00.00000+00:00',
                },
            },
            {'mission_2', 'mission_3'},
            id='Created range',
        ),
        pytest.param(
            {
                'created': {
                    'after': '2000-01-01T13:00:00.00000+00:00',
                    'before': '2000-01-02T12:00:00.00000+00:00',
                },
                'statuses': ['performing'],
            },
            {'mission_3'},
            id='Created range + filter by statuses',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops, pgsql, request_body, expected_missions_ids,
):
    db_utils.add_mission(pgsql, MISSION_1)
    db_utils.add_mission(pgsql, MISSION_2)
    db_utils.add_mission(pgsql, MISSION_3)
    db_utils.add_mission(pgsql, MISSION_4)

    response = await taxi_scooters_ops.post(HANDLER, request_body)

    assert response.status == 200
    assert {
        mission['id'] for mission in response.json()['missions']
    } == expected_missions_ids
