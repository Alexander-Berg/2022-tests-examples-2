import copy

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/processing/claim-updates/arrived'
SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'cargo_claim_id': 'claim_1',
    'performer_id': 'performer_1',
    'status': 'performing',
    'revision': 1,
    'points': [
        {
            'point_id': 'point_1',
            'eta': '2022-04-01T07:00:00+00:00',
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_1', 'number': 'Scooter 1'},
            },
            'status': 'visited',
            'cargo_point_id': '123',
            'jobs': [
                {
                    'job_id': 'job_1',
                    'type': 'battery_exchange',
                    'status': 'completed',
                    'typed_extra': {},
                },
            ],
        },
        {
            'point_id': 'point_2',
            'eta': '2022-04-01T08:00:00+00:00',
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_2', 'number': 'Scooter 2'},
            },
            'status': 'planned',
            'cargo_point_id': '456',
            'jobs': [
                {
                    'type': 'battery_exchange',
                    'status': 'planned',
                    'typed_extra': {},
                },
            ],
        },
    ],
}


@pytest.mark.parametrize(
    ['cargo_point_id', 'point_id', 'expected_completion', 'expected_history'],
    [
        pytest.param(
            123, 'point_1', False, [], id='Depot point already completed',
        ),
        pytest.param(
            456,
            'point_2',
            True,
            [
                {
                    'type': 'point_arrived',
                    'extra': {
                        'point_type': 'scooter',
                        'eta': '2022-04-01T08:00:00+00:00',
                        'point_location': [37.0, 55.0],
                        'performer_location': [37.1, 55.1],
                        'point_extra': {
                            'scooter': {
                                'id': 'scooter_2',
                                'number': 'Scooter 2',
                            },
                        },
                    },
                },
                {
                    'type': 'job_started',
                    'extra': {'job_extra': {}, 'job_type': 'battery_exchange'},
                },
            ],
            id='Set scooter point arrived',
        ),
    ],
)
async def test_ok(
        taxi_scooters_ops,
        pgsql,
        driver_trackstory,
        cargo_point_id,
        point_id,
        expected_completion,
        expected_history,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': cargo_point_id},
    )

    assert response.status == 200

    point = db_utils.get_points(
        pgsql,
        ids=[point_id],
        fields=['point_id', 'status', 'revision'],
        job_params={'field': ['status']},
    )[0]

    if expected_completion:
        assert point['revision'] == 2
        assert point['status'] == 'arrived'
        assert point['jobs'][0]['status'] == 'performing'
    else:
        assert point['revision'] == 1

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    assert history == expected_history


async def test_idempotency(taxi_scooters_ops, pgsql, driver_trackstory):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': 456},
    )
    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': 456},
    )

    assert response1.status == 200
    assert response2.status == 200

    points = db_utils.get_points(
        pgsql, fields=['point_id', 'status', 'revision'],
    )
    assert points == [
        {'point_id': 'point_1', 'status': 'visited', 'revision': 1},
        {'point_id': 'point_2', 'status': 'arrived', 'revision': 2},
    ]


async def test_no_actions_if_new_flow_mission(taxi_scooters_ops, pgsql):
    mission_before = {
        'mission_id': 'mission_id',
        'cargo_claim_id': 'claim_1',
        'performer_id': 'performer_1',
        'status': 'performing',
        'revision': 1,
        'points': [
            {
                'cargo_point_id': '123',
                'eta': '2022-04-01T07:00:00+00:00',
                'type': 'depot',
                'typed_extra': {},
                'status': 'prepared',
                'revision': 1,
                'jobs': [
                    {
                        'job_id': 'job_1',
                        'revision': 1,
                        'type': 'dropoff_vehicles',
                        'status': 'prepared',
                        'typed_extra': {'quantity': 1, 'vehicles': []},
                    },
                ],
            },
        ],
    }
    db_utils.add_mission(pgsql, mission_before)
    db_utils.add_tags(
        pgsql,
        {
            'tag': ['new_pro'],
            'entity_id': 'mission_id',
            'entity_type': 'mission',
        },
    )

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': '123'},
    )

    assert response.status == 200

    mission_after = db_utils.get_missions(
        pgsql, ids=['mission_id'], point_params={'job_params': {}},
    )[0]
    utils.assert_partial_diff(
        mission_after,
        {
            'revision': 1,
            'points': [
                {
                    'status': 'prepared',
                    'revision': 1,
                    'jobs': [{'status': 'prepared', 'revision': 1}],
                },
            ],
        },
    )


async def test_not_found(taxi_scooters_ops):
    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'absent_claim_id', 'cargo_point_id': 456},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not-found',
        'message': 'Cannot find mission with cargo claim id: absent_claim_id',
    }
