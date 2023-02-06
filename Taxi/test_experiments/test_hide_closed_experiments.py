# pylint: disable=invalid-name
import pytest


@pytest.mark.pgsql('taxi_exp', files=['closed_and_opened_experiments.sql'])
async def test_hide_closed_experiments(taxi_exp_client):

    response = await taxi_exp_client.get(
        '/v1/experiments/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    names = {experiment['name'] for experiment in result['experiments']}
    assert names == {'opened_experiment', 'opened_experiment_2'}

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'show_closed': 'False'},
    )
    assert response.status == 200
    names = {experiment['name'] for experiment in result['experiments']}
    assert names == {'opened_experiment', 'opened_experiment_2'}

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'show_closed': 'True'},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['experiments']) == 3
    names = {experiment['name'] for experiment in result['experiments']}
    assert names == {
        'opened_experiment',
        'opened_experiment_2',
        'closed_experiment',
    }
