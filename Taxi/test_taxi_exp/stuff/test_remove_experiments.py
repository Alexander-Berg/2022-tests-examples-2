import datetime

import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db

MARK_AS_REMOVED_QUERY = (
    'UPDATE clients_schema.experiments '
    'SET removed = TRUE, removed_stamp = $2::timestamp '
    'WHERE name = $1;'
)
GET_EXPERIMENTS_QUERY = 'SELECT id FROM clients_schema.experiments;'
REMOVING_DELAY = 10000


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'experiments_removing_delay': REMOVING_DELAY}},
    },
)
@pytest.mark.config(EXP_BLOCK_SAVING_ENABLED_EXPERIMENT={})
async def test_remove_experiments(taxi_exp_client):
    predicate = {'type': 'true'}
    data = {
        'description': 'test_description',
        'match': {
            'enabled': True,
            'schema': """
                type:
                    integer
            """,
            'predicate': predicate,
            'action_time': {
                'from': '2018-10-05T03:00:00+0300',
                'to': '2018-10-05T04:00:00+0300',
            },
            'consumers': [{'name': 'test_consumer'}],
            'applications': [
                {
                    'name': 'android',
                    'version_range': {'from': '3.14.0', 'to': '3.20.0'},
                },
            ],
        },
        'default_value': None,
        'financial': True,
        'clauses': [{'title': 'test', 'value': 1, 'predicate': predicate}],
        'department': 'common',
    }

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 200, await response.text()

    # adding second experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name_2'},
        json=data,
    )
    assert response.status == 200, await response.text()

    # make sure there are 2 experiments
    response = await taxi_exp_client.get(
        '/v1/experiments/updates/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'newer_than': 0},
    )
    assert response.status == 200, await response.text()
    result = await response.json()
    assert len(result['experiments']) == 2

    # deleting experiment via query
    pool = taxi_exp_client.app['pool']
    async with pool.acquire() as connection:
        await connection.execute(
            MARK_AS_REMOVED_QUERY,
            'test_name',
            datetime.datetime.utcnow()
            - datetime.timedelta(seconds=2 * REMOVING_DELAY),
        )
        await connection.execute(
            MARK_AS_REMOVED_QUERY, 'test_name_2', datetime.datetime.utcnow(),
        )

    # running cron
    await cron_run.main(['taxi_exp.stuff.remove_experiments', '-t', '0'])

    # make sure there is only one experiment in DB
    async with pool.acquire() as connection:
        experiments = await connection.fetch(GET_EXPERIMENTS_QUERY)
    assert len(experiments) == 1
