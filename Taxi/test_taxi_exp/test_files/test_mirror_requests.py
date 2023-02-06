# pylint: disable=invalid-name
import pytest


@pytest.mark.pgsql('taxi_exp', files=('for_get_experiments_by_file.sql',))
async def test_get_experiments_by_file(taxi_exp_client):
    response = await taxi_exp_client.get(
        '/v1/files/ec2f695e09044105bce60bdffd6a36ce/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
    )

    assert response.status == 200

    data = await response.json()
    assert len(data['experiments']) == 3


@pytest.mark.pgsql('taxi_exp', files=('for_get_files_by_experiment.sql',))
async def test_get_files_by_experiment(taxi_exp_client):
    response = await taxi_exp_client.get(
        'v1/files/by_experiment/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'checking_files'},
    )
    assert response.status == 200

    data = await response.json()
    assert len(data['files']) == 2
    assert len(data['linked_files']) == 1
