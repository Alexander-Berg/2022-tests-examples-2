# pylint: disable=too-many-statements
# pylint: disable=invalid-name
import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_experiments(taxi_exp_client):
    data = experiment.generate_default()
    data['default_value'] = {}

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 200

    # adding config
    config_data = experiment.generate_config()
    config_data['match']['action_time'] = {'from': '', 'to': ''}
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=config_data,
    )
    assert response.status == 200

    # get last_modified_at by config
    response = await taxi_exp_client.get(
        '/v1/configs/',
        params={'name': 'test_name'},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    last_modified_at = result.pop('last_modified_at')

    # update config
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name', 'last_modified_at': last_modified_at},
        json=config_data,
    )
    assert response.status == 200

    # get last_modified_at by experiment
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params={'name': 'test_name'},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    last_modified_at = result.pop('last_modified_at')

    # update experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name', 'last_modified_at': last_modified_at},
        json=data,
    )
    assert response.status == 200
