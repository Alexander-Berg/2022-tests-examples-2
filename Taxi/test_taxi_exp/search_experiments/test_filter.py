import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'first'


@pytest.mark.parametrize(
    'params',
    [
        {'name': NAME, 'owner': ''},
        {'name': NAME},
        {'name': NAME, 'watcher': ''},
        {'name': NAME, 'consumer': ''},
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(taxi_exp_client, params):
    data = experiment.generate_default()
    data['name'] = NAME
    data['owners'] = ['test', 'test2', 'test3']
    data['match']['consumers'] = [
        {'name': 'test_consumer'},
        {'name': 'test_other_consumer'},
    ]
    await helpers.add_checked_exp(taxi_exp_client, data)
    assert await db.get_all_experiments(taxi_exp_client.app)

    # obtaining list
    response = await taxi_exp_client.get(
        f'/v1/experiments/list/?&name={NAME}&owner=',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == [NAME]
