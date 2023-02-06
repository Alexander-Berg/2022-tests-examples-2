import pytest

NAME = 'experiment_false_financial'


@pytest.mark.parametrize('modification', ['close', 'close_and_disable'])
@pytest.mark.pgsql('taxi_exp', files=['experiment_false_financial.sql'])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
async def test_uplift_with_false_financial(taxi_exp_client, modification):
    data = {
        'experiment_name': NAME,
        'last_updated_at': 1,
        'modification': modification,
    }
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=data,
    )
    assert response.status == 200

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': NAME},
    )
    assert response.status == 200
    old_experiment = await response.json()
    assert old_experiment['financial'] is False

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': NAME},
    )
    assert response.status == 200
    new_config = await response.json()
    assert new_config['financial'] is False
