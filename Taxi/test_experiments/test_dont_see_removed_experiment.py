# pylint: disable=invalid-name
import pytest


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['experiments_list.sql'])
async def test_dont_see_removed_experiment(taxi_exp_client):

    # experiemnts list before delete
    response = await taxi_exp_client.get(
        '/v1/experiments/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    experiments = (await response.json())['experiments']
    assert len(experiments) == 10

    response = await taxi_exp_client.delete(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'experiment_1', 'last_modified_at': 1},
    )
    assert response.status == 200

    # experiments list after delete
    response = await taxi_exp_client.get(
        '/v1/experiments/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    experiments = (await response.json())['experiments']
    assert len(experiments) == 9
