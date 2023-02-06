import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_passed_experiment_name(taxi_exp_client):
    experiment_name = 'test_name_123::1-s'
    data = experiment.generate(experiment_name)

    # adding experiment with true name
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment_name},
        json=data,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'exp_name',
    [
        'киррилица_с_подчёркиваниями',
        'test,with,commas',
        'test.with.dots',
        r'test\with\slashes',
        'test name',
        'Тестовый эксперимент',
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_failed_experiment_name(exp_name, taxi_exp_client):
    data = experiment.generate(exp_name)

    # adding experiments with bad name
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': exp_name},
        json=data,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'exp_name,last_modified_at',
    [
        ('киррилица_с_подчёркиваниями', 1),
        ('test,with,commas', 2),
        ('test-with-dashes', 3),
        ('test.with.dots', 4),
        (r'test\with\slashes', 5),
        ('test name', 6),
        ('Тестовый эксперимент', 7),
        ('test_name_123', 8),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['experiments.sql', 'default.sql'])
async def test_update_experiment(exp_name, last_modified_at, taxi_exp_client):
    data = experiment.generate(exp_name)

    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': exp_name, 'last_modified_at': last_modified_at},
        json=data,
    )
    assert response.status == 200
