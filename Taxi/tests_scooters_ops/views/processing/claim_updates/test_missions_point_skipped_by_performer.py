import copy

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = (
    '/scooters-ops/v1/processing/claim-updates/point_skipped_by_performer'
)
SIMPLE_MISSION = {
    'mission_id': 'missionid',
    'cargo_claim_id': 'claim_1',
    'performer_id': 'performer_1',
    'status': 'performing',
    'revision': 1,
    'points': [
        {
            'point_id': 'point1',
            'status': 'visited',
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_1', 'number': 'Scooter 1'},
            },
            'cargo_point_id': '123',
            'jobs': [
                {
                    'job_id': 'job1',
                    'type': 'battery_exchange',
                    'status': 'completed',
                    'typed_extra': {},
                },
            ],
        },
        {
            'point_id': 'point2',
            'status': 'arrived',
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_2', 'number': 'Scooter 2'},
            },
            'cargo_point_id': '456',
            'jobs': [
                {
                    'job_id': 'job2',
                    'type': 'battery_exchange',
                    'status': 'performing',
                    'typed_extra': {},
                },
            ],
        },
    ],
}


@pytest.mark.parametrize(
    ['request_body', 'expected'],
    [
        pytest.param(
            {'comment': 'Не смог', 'reasons': ['reason_1', 'reason_2']},
            {'comment': 'Не смог', 'reasons': ['reason_1', 'reason_2']},
            id='comment and reasons in body',
        ),
        pytest.param({}, {'comment': '', 'reasons': []}, id='empty body'),
    ],
)
async def test_handler(taxi_scooters_ops, pgsql, request_body, expected):
    mission = db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'stub_draft_id',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
            'mission_id': mission['mission_id'],
            'point_id': mission['points'][1]['point_id'],
            'job_id': mission['points'][1]['jobs'][0]['job_id'],
        },
    )

    response = await taxi_scooters_ops.post(
        HANDLER,
        request_body,
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': '456'},
    )
    assert response.status == 200

    point = db_utils.get_points(pgsql, ids=['point2'], job_params={})[0]

    utils.assert_partial_diff(
        point,
        {
            'status': 'skipped',
            'comment': expected['comment'],
            'fail_reasons': expected['reasons'],
            'jobs': [
                {
                    'status': 'failed',
                    'comment': expected['comment'],
                    'fail_reasons': expected['reasons'],
                },
            ],
        },
    )

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['missionid'],
    )
    assert notifications == [
        {
            'idempotency_token': 'missionid_point2_job2_job_skipped',
            'mission_id': 'missionid',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
            'created_at': utils.AnyValue(),
            'updated_at': utils.AnyValue(),
        },
    ]

    history = db_utils.get_history(
        pgsql, mission_ids=['missionid'], fields=['type', 'extra'],
    )
    assert history == [
        {
            'extra': {
                'comment': expected['comment'],
                'reasons': expected['reasons'],
            },
            'type': 'job_failed',
        },
        {
            'extra': {
                'comment': expected['comment'],
                'reasons': expected['reasons'],
            },
            'type': 'point_skipped',
        },
    ]

    draft_released = db_utils.get_drafts(
        pgsql, ids=['stub_draft_id'], fields=['mission_id'], flatten=True,
    ) == [None]

    assert draft_released is True


async def test_idempotency(taxi_scooters_ops, pgsql):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': '456'},
    )
    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': '456'},
    )

    assert response1.status == 200
    assert response2.status == 200

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['missionid'],
    )
    assert len(notifications) == 1


async def test_point_already_skipped(taxi_scooters_ops, pgsql):
    mission = copy.deepcopy(SIMPLE_MISSION)
    mission['points'][1]['status'] = 'skipped'
    mission['points'][1]['jobs'][0]['status'] = 'failed'

    db_utils.add_mission(pgsql, mission)

    assert db_utils.get_points(
        pgsql, ids=['point2'], fields=['revision'], flatten=True,
    ) == [1]

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'cargo_claim_id': 'claim_1', 'cargo_point_id': '456'},
    )

    assert response.status == 200
    assert db_utils.get_points(
        pgsql, ids=['point2'], fields=['revision'], flatten=True,
    ) == [1]
