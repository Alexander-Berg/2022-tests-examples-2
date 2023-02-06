import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'closed_experiment'


@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'closed_experiment.sql'))
async def test_update_closed_experiemnt(taxi_exp_client):
    last_modified_at = await helpers.get_last_modified_at(
        taxi_exp_client, EXPERIMENT_NAME,
    )

    experiment_body = experiment.generate(EXPERIMENT_NAME)
    response = await taxi_exp_client.put(
        '/v1/closed-experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': last_modified_at},
        json=experiment_body,
    )
    assert response.status == 200
