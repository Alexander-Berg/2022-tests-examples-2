# pylint: disable=invalid-name
import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=['closed_experiment.sql'])
async def test_no_update_closed_experiment_by_default(taxi_exp_client):
    data = experiment.generate_default()

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'closed_experiment'},
    )
    last_modified_at = (await response.json())['last_modified_at']

    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={
            'name': 'closed_experiment',
            'last_modified_at': last_modified_at,
        },
        json=data,
    )
    assert response.status == 409
