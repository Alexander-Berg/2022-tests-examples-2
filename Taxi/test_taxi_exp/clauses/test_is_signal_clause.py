import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_signal_clauses'
SCHEMA = """
type: object
additionalProperties: false
required:
  - enabled
properties:
    enabled:
        type: boolean"""


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_signal_clause(taxi_exp_client):
    experiment_body = experiment.generate(
        EXPERIMENT_NAME,
        schema=SCHEMA,
        clauses=[
            experiment.make_clause('without_signal', value={'enabled': True}),
            experiment.make_clause('with_signal', is_signal=True),
        ],
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == 200, await response.text()

    response = await helpers.get_updates(taxi_exp_client, newer_than=0)
    body = response['experiments'][0]
    assert 'is_signal' not in body['clauses'][0]
    assert body['clauses'][1]['is_signal']
