import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'closed_experiment'


@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'closed_experiment.sql'))
async def test_update_closed_experiment(taxi_exp_client):
    experiment_body = experiment.generate(EXPERIMENT_NAME)

    response = await taxi_exp_client.post(
        '/v1/closed-experiments/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=experiment_body,
    )
    assert response.status == 200
    body = await response.json()
    assert body['change_doc_id'] == f'update_experiment_{EXPERIMENT_NAME}'

    apply_request = (await response.json())['data']
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=apply_request,
    )
    assert response.status == 200
