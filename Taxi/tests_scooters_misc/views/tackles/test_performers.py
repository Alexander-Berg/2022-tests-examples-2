import pytest

from tests_scooters_misc import utils


@pytest.mark.parametrize(
    ['tackle', 'expected'],
    [
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'any',
                'performer_id': 'performer1',
                'recharge_task_id': 'any',
                'version': '5',
            },
            {'status': 200},
            id='Assign same as already assigned',
        ),
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'any',
                'recharge_task_id': 'any',
                'version': '5',
            },
            {'status': 200},
            id='Assign',
        ),
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'any',
                'performer_id': 'performer5',
                'recharge_task_id': 'any',
                'version': '5',
            },
            {
                'status': 400,
                'log': (
                    'Cannot assign: performer1, already assigned: performer5'
                ),
                'response': 'Performer already assigned',
            },
            id='Cannot assign, another performer assigned',
        ),
        pytest.param(
            {
                'id': 'invalid_id',
                'kind': 'recharging_wire',
                'depot_id': 'any',
                'performer_id': 'performer_1',
                'recharge_task_id': 'any',
                'version': '5',
            },
            {'status': 404},
            id='Cannot assign, invalid id',
        ),
    ],
)
async def test_assign(taxi_scooters_misc, pgsql, testpoint, tackle, expected):

    utils.add_tackle(pgsql, tackle)

    @testpoint('v1_tackles_assign/exception')
    def trace_error(request):
        assert request == {'exception': expected['log']}

    res = await taxi_scooters_misc.post(
        f'/v1/tackles/assign?id=tackle_id&performer_id=performer1', {},
    )
    assert res.status_code == expected['status']
    if 'response' in expected:
        assert res.json()['message'] == expected['response']
    if 'log' in expected:
        assert trace_error.times_called == 1


async def test_assign_idempotency(pgsql, taxi_scooters_misc):

    utils.add_tackle(
        pgsql,
        {
            'id': '10',
            'kind': 'recharging_wire',
            'depot_id': 'any',
            'recharge_task_id': 'any',
            'version': '5',
        },
    )

    res = await taxi_scooters_misc.post(
        f'/v1/tackles/assign?id=10&performer_id=performer1', {},
    )
    assert res.status_code == 200
    res = await taxi_scooters_misc.post(
        f'/v1/tackles/assign?id=10&performer_id=performer1', {},
    )
    assert res.status_code == 200
