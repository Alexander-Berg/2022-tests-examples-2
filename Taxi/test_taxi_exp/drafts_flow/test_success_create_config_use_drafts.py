import pytest

from test_taxi_exp.helpers import experiment

CONFIG_NAME = 'config'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'prestable_flow': True}},
        'settings': {
            'common': {
                'departments': {'market': {'map_to_namespace': 'market'}},
            },
        },
    },
)
@pytest.mark.parametrize('test_implicit_financial', [True, False])
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_experiment(taxi_exp_client, test_implicit_financial):
    experiment_body = experiment.generate_config(department='market')
    params = {'name': CONFIG_NAME}

    if test_implicit_financial:
        experiment_body.pop('financial')

    response = await taxi_exp_client.post(
        '/v1/configs/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200
    body = await response.json()
    assert body['change_doc_id'] == f'config_{CONFIG_NAME}'
    assert body['data']['status_wait_prestable'] == 'no_warning'
    assert body['tplatform_namespace'] == 'market'
    assert body['data']['config']['financial'] is True

    response = await taxi_exp_client.post(
        '/v1/configs/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200
