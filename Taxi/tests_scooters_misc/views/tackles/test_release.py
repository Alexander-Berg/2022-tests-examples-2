import pytest

from tests_scooters_misc import utils


@pytest.mark.parametrize(
    ['tackle_performer_id', 'expected'],
    [
        pytest.param(None, {'status': 200}, id='Release already released'),
        pytest.param('performer1', {'status': 200}, id='Release'),
        pytest.param(
            'performer2',
            {
                'status': 400,
                'log': (
                    'Cannot release with performer_id: performer1'
                    ', actual performer: performer2'
                ),
                'response': 'Invalid performer id',
            },
            id='Cannot assign, another performer assigned',
        ),
    ],
)
async def test_release(
        taxi_scooters_misc, pgsql, testpoint, tackle_performer_id, expected,
):
    utils.add_tackle(
        pgsql,
        {
            'id': 'tackle_id',
            'kind': 'recharging_wire',
            'performer_id': tackle_performer_id,
        },
    )

    @testpoint('v1_tackles_release/exception')
    def trace_error(request):
        assert request == {'exception': expected['log']}

    res = await taxi_scooters_misc.post(
        f'/v1/tackles/release?id=tackle_id&performer_id=performer1', {},
    )
    assert res.status_code == expected['status']
    if 'response' in expected:
        assert res.json()['message'] == expected['response']
    if 'log' in expected:
        assert trace_error.times_called == 1
    if res.status_code == 200:
        tackles = utils.get_tackles(
            pgsql, ids=['tackle_id'], fields=['performer_id'], flatten=True,
        )
        assert tackles == [None]


async def test_release_not_found(taxi_scooters_misc):
    res = await taxi_scooters_misc.post(
        f'/v1/tackles/release?id=invalid_id&performer_id=performer1', {},
    )
    assert res.status_code == 404


async def test_release_idempotency(taxi_scooters_misc, pgsql):
    utils.add_tackle(
        pgsql,
        {
            'id': 'tackle_id',
            'kind': 'recharging_wire',
            'performer_id': 'performer1',
        },
    )
    res = await taxi_scooters_misc.post(
        f'/v1/tackles/release?id=tackle_id&performer_id=performer1', {},
    )
    assert res.status_code == 200
    res = await taxi_scooters_misc.post(
        f'/v1/tackles/release?id=tackle_id&performer_id=performer1', {},
    )
    assert res.status_code == 200
