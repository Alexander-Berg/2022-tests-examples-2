# pylint: disable=invalid-name
import pytest

from taxi_exp.util import pg_helpers


EXP_NAME = 'valid_experiment_name'


@pytest.mark.pgsql('taxi_exp', files=('many_many_files.sql',))
async def test_get_hardlinked_files_by_experiment(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    pool = taxi_exp_app['pool']
    query = taxi_exp_app.postgres_queries[
        'files/get_hardlinked_files_by_experiment.sql'
    ]

    response = await pg_helpers.fetch(pool, query, EXP_NAME, None)

    assert len(response) == 3

    response = await pg_helpers.fetch(pool, query, EXP_NAME, 'market')

    assert not response


@pytest.mark.pgsql('taxi_exp', files=('many_many_files.sql',))
async def test_get_softlinked_files_by_experiment(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    pool = taxi_exp_app['pool']
    query = taxi_exp_app.postgres_queries['files/get_softlinked_files.sql']

    response = await pg_helpers.fetch(pool, query, EXP_NAME, None)

    assert len(response) == 2
    assert response[0]['version'] == 3
    assert response[0]['name'] == 'f11_in_exp'
    assert response[1]['version'] == 1

    response = await pg_helpers.fetch(pool, query, EXP_NAME, 'market')

    assert not response
