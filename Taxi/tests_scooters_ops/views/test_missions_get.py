import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/missions/get'


@pytest.mark.parametrize(
    'request_params,expected_response',
    [
        pytest.param(
            {'mission_id': 'mission_id_1'},
            {'status': 200, 'json': {'mission': {'id': 'mission_id_1'}}},
            id='search by mission_id',
        ),
        pytest.param(
            {'cargo_claim_id': 'claim_id_1'},
            {'status': 200, 'json': {'mission': {'id': 'mission_id_1'}}},
            id='search by cargo_claim_id',
        ),
        pytest.param(
            {},
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'cargo_claim_id or mission_id required',
                },
            },
            id='no search params',
        ),
        pytest.param(
            {'mission_id': 'bad'},
            {
                'status': 404,
                'json': {
                    'code': 'not-found',
                    'message': (
                        'Mission by filter '
                        '(mission_id:bad or cargo_claim_id:) not found'
                    ),
                },
            },
            id='search absent mission',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops, pgsql, request_params, expected_response,
):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'cargo_claim_id': 'claim_id_1',
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot1'}},
                    'jobs': [
                        {
                            'type': 'pickup_batteries',
                            'typed_extra': {'quantity': 1},
                        },
                    ],
                },
            ],
        },
    )

    response = await taxi_scooters_ops.get(HANDLER, params=request_params)

    assert response.status == expected_response['status']
    utils.assert_partial_diff(response.json(), expected_response['json'])


@pytest.mark.parametrize(
    'depth,expected_parts',
    [
        pytest.param(None, ['points', 'jobs'], id='defailt depth'),
        pytest.param('jobs', ['points', 'jobs'], id='jobs depth'),
        pytest.param('points', ['points'], id='points depth'),
        pytest.param('mission-only', [], id='mission-only depth'),
    ],
)
async def test_depth(taxi_scooters_ops, pgsql, depth, expected_parts):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot1'}},
                    'jobs': [
                        {
                            'type': 'pickup_batteries',
                            'typed_extra': {'quantity': 1},
                        },
                    ],
                },
            ],
        },
    )

    request_params = {'mission_id': 'mission_id_1'}
    if depth:
        request_params['depth'] = depth

    response = await taxi_scooters_ops.get(HANDLER, params=request_params)

    assert response.status == 200

    resp = response.json()
    mission_part = resp['mission']
    points_part = mission_part.get('points')
    jobs_part = points_part[0].get('jobs') if points_part else None

    assert ('points' in expected_parts) == (points_part is not None)
    assert ('jobs' in expected_parts) == (jobs_part is not None)
