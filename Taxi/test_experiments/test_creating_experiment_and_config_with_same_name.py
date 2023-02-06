# pylint: disable=invalid-name
import pytest

from test_taxi_exp.helpers import experiment as exp_generator

SAME_NAME = 'test'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_creating_experiment_and_config_with_same_name(taxi_exp_client):
    # adding experiment
    experiment = exp_generator.generate_default()
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': SAME_NAME},
        json=experiment,
    )
    assert response.status == 200

    # success adding config
    config = exp_generator.generate_config()
    config['match']['action_time'] = {'from': '', 'to': ''}
    config['default_value'] = {}
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': SAME_NAME},
        json=config,
    )
    assert response.status == 200

    # no create experiment with non-unique name
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': SAME_NAME},
        json=experiment,
    )
    assert response.status == 409

    # no create config with non-unique name
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': SAME_NAME},
        json=config,
    )
    assert response.status == 409
