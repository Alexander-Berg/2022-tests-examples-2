import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_alias'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_update_alias(taxi_exp_client):
    body = experiment.generate(
        EXPERIMENT_NAME,
        clauses=[
            experiment.make_clause('without_alias'),
            experiment.make_clause('with_alias', alias='alias_01'),
        ],
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': EXPERIMENT_NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    body['clauses'][1]['alias'] = 'alias_02'
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=body,
    )
    assert response.status == 200, await response.text()
