import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXP_NAME = 'closed_experiment'


@pytest.mark.pgsql(
    'taxi_exp',
    files=['closed_experiment.sql'],
    queries=[db.ADD_CONSUMER.format('test_consumer')],
)
async def test_experiments(taxi_exp_client):
    data = experiment.generate()

    response = await taxi_exp_client.put(
        '/v1/closed-experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200, await response.text()
