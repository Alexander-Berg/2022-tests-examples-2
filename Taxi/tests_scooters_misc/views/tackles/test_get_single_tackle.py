import pytest

from tests_scooters_misc import utils


@pytest.mark.parametrize(
    ['tackle_to_insert', 'expected_code', 'response_body'],
    [
        pytest.param(
            {
                'id': 'tackle_id',
                'kind': 'recharging_wire',
                'depot_id': 'grocery:kukuevo',
                'version': 2,
            },
            200,
            {
                'tackle': {
                    'id': 'tackle_id',
                    'kind': 'recharging_wire',
                    'depot_id': 'grocery:kukuevo',
                    'version': 2,
                },
            },
            id='Case 1: 200',
        ),
        pytest.param(
            {'id': 'tackle_di', 'kind': 'recharging_wire', 'version': 2},
            404,
            {'code': '404', 'message': 'No tackle with specified id'},
            id='Case 2: 404',
        ),
    ],
)
async def test_get_single_tackle(
        taxi_scooters_misc,
        pgsql,
        tackle_to_insert,
        expected_code,
        response_body,
):
    utils.add_tackle(pgsql, tackle_to_insert)

    res = await taxi_scooters_misc.get(f'/v1/tackles/tackle?id=tackle_id')
    assert res.status_code == expected_code
    assert res.json() == response_body
