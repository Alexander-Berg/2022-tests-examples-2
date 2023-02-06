import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXP_NAME = 'test_name'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_experiment_removing': True,
                'show_removed': True,
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_experiments(taxi_exp_client):
    data = experiment.generate()

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME},
        json=data,
    )
    assert response.status == 200

    # deleting first experiment
    last_modified_at = await helpers.get_last_modified_at(
        taxi_exp_client, EXP_NAME,
    )
    response = await taxi_exp_client.delete(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME, 'last_modified_at': last_modified_at},
        json={},
    )
    assert response.status == 200

    # check removed field
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params={'name': EXP_NAME},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['removed'] is True

    # fail adding experiment with same name
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME},
        json=data,
    )
    assert response.status == 409

    # imitation full remove by crontask
    await db.remove_exp(taxi_exp_client.app, EXP_NAME, last_modified_at + 1)

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    # deleting first experiment
    last_modified_at = await helpers.get_last_modified_at(
        taxi_exp_client, EXP_NAME,
    )
    response = await taxi_exp_client.delete(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXP_NAME, 'last_modified_at': last_modified_at},
        json={},
    )
    assert response.status == 200, await response.text()
