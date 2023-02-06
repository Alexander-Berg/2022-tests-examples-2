import pytest

from tests_scooters_misc import utils


@pytest.mark.parametrize(
    ['tackle_to_insert', 'request_body', 'expected_code', 'response_body'],
    [
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'grocery:tuchkovo',
                'version': 2,
            },
            {},
            200,
            {
                'tackle': {
                    'id': 'tackle_id',
                    'kind': 'recharging_wire',
                    'version': 3,
                },
            },
            id='Case 1: Changing depot',
        ),
        pytest.param(
            {'id': 'tackle_id', 'kind': 'recharging_wire', 'version': 2},
            {},
            200,
            {
                'tackle': {
                    'id': 'tackle_id',
                    'kind': 'recharging_wire',
                    'version': 3,
                },
            },
            id='Case 2: Setting depot',
        ),
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'grocery:krasnodar',
                'performer_id': 'tackle_performer',
                'version': 2,
            },
            {},
            400,
            {
                'code': '400',
                'message': (
                    'NotAvailableTackle. '
                    'performer_id must not be set to change depot_id'
                ),
            },
            id='Case 3: ActiveTackle error - performer_id',
        ),
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'grocery:krasnodar',
                'recharge_task_id': 'tackle_recharge_task',
                'version': 2,
            },
            {},
            400,
            {
                'code': '400',
                'message': (
                    'NotAvailableTackle. '
                    'recharge_task_id must not be set to change depot_id'
                ),
            },
            id='Case 4: ActiveTackle error - recharge_task_id',
        ),
        pytest.param(
            {'id': 'tackle_id', 'kind': 'recharging_wire', 'version': 4},
            {},
            409,
            {
                'code': '409',
                'message': 'TackleVersion. ' + 'Invalid Tackle Version',
            },
            id='Case 5: TackleVersion error',
        ),
        pytest.param(
            {
                'id': 'tackle_404',
                'kind': 'recharging_wire',
                'performer_id': 'tackle_performer',
                'version': 3,
            },
            {},
            404,
            {'code': '404', 'message': 'No tackle with specified id'},
            id='Case 6: Error404',
        ),
    ],
)
async def test_tackles_depot_drop(
        taxi_scooters_misc,
        pgsql,
        tackle_to_insert,
        request_body,
        expected_code,
        response_body,
):
    utils.add_tackle(pgsql, tackle_to_insert)

    res = await taxi_scooters_misc.post(
        f'/v1/tackles/depot/drop?id=tackle_id&version=2', json=request_body,
    )
    assert res.status_code == expected_code
    assert res.json() == response_body
