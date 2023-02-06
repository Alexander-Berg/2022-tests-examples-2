import pytest

from test_taxi_exp.helpers import db


@pytest.mark.parametrize(
    'params, link, result_code',
    [
        (
            {'name': 'n1-enabled', 'last_modified_at': 1},
            'experiments/disable',
            200,
        ),
        (
            {'name': 'n1-disabled', 'last_modified_at': 3},
            'experiments/enable',
            200,
        ),
        (
            {'name': 'n1-enabled', 'last_modified_at': 2},
            'configs/disable',
            200,
        ),
        (
            {'name': 'n1-disabled', 'last_modified_at': 4},
            'configs/enable',
            200,
        ),
        (
            {'name': 'n1-disabled', 'last_modified_at': 1},
            'experiments/disable',
            409,
        ),
        (
            {'name': 'n1-disabled', 'last_modified_at': 2},
            'configs/disable',
            409,
        ),
        (
            {'name': 'n1-enabled', 'last_modified_at': 100},
            'configs/disable',
            409,
        ),
        (
            {'name': 'n1-enabled', 'last_modified_at': 100},
            'experiments/disable',
            409,
        ),
        (
            {'name': 'n1-non-existed', 'last_modified_at': 2},
            'configs/disable',
            409,
        ),
        (
            {'name': 'n1-non-existed', 'last_modified_at': 2},
            'experiments/disable',
            409,
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('fill.sql',))
async def test_enable_disable(taxi_exp_client, params, link, result_code):
    response = await taxi_exp_client.post(
        f'/v1/{link}/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == result_code

    if result_code != 200:
        return

    if 'config' in link:
        body = await db.get_config(taxi_exp_client.app, params['name'])
    else:
        body = await db.get_experiment(taxi_exp_client.app, params['name'])

    assert body['exp_enabled'] == ('enable' in link)

    history = await db.get_experiments_history(taxi_exp_client.app)
    assert history
