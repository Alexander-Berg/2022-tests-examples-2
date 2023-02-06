import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'params,expected_names',
    [
        ({}, ['first', 'second']),
        ({'show_enabled': 'true'}, ['first']),
        ({'show_disabled': 'true'}, ['second']),
        (
            {'show_enabled': 'true', 'show_disabled': 'true'},
            ['first', 'second'],
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(taxi_exp_client, params, expected_names):
    data = experiment.generate_default()

    # adding experiments
    for name, enabled in (('first', True), ('second', False)):
        data['match']['enabled'] = enabled
        data['name'] = name
        await helpers.add_checked_exp(taxi_exp_client, data)
    assert len(await db.get_all_experiments(taxi_exp_client.app)) == 2

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == expected_names
