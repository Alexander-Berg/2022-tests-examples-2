import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'existed_experiment'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY, db.EXISTED_EXPERIMENT])
async def test_update_experiment(taxi_exp_client):
    params = {
        'experiment_name': EXPERIMENT_NAME,
        'last_updated_at': 1,
        'default_value': {},
    }
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/uplift-to-config/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=params,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['change_doc_id'] == f'uplift_experiment_{EXPERIMENT_NAME}'

    apply_request = body['data']
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/uplift-to-config/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=apply_request,
    )
    assert response.status == 200, await response.text()

    # update closed exp
    experiment_body = experiment.generate(
        action_time={
            'from': '2000-01-01T00:00:00+03:00',
            'to': '2100-01-01T00:00:00+03:00',
        },
    )
    params = {'name': EXPERIMENT_NAME, 'last_modified_at': 2}
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['change_doc_id'] == f'update_experiment_{EXPERIMENT_NAME}'
    assert 'diff' in body

    apply_request = body['data']
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=apply_request,
    )
    assert response.status == 200, await response.text()
