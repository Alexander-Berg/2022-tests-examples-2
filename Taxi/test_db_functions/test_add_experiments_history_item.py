import json

import pytest

from taxi.util import dates

from taxi_exp.util import pg_helpers
from test_taxi_exp.helpers import experiment

DELETE_EXPERIMENT_QUERY = """
SELECT pg_temp.delete_experiment(
    name_            := $1::text,
    namespace_       := $2::text,
    last_modified_at := $3::bigint,
    is_config_       := $4::boolean,
    allow_closed     := TRUE,
    change_type_     := 'direct')
;"""
ADD_HISTORY_ITEM = """
    SELECT *
    FROM pg_temp.add_experiments_history_item(obj_rev:=1,
                                              change_type_:='direct');"""
GET_HISTORY_ITEM = (
    'SELECT rev, body, name, is_config '
    'FROM clients_schema.experiments_history LIMIT 1;'
)
EXPERIMENT_NAME = 'add_experiment'


async def _count(pool):
    query = (
        'SELECT COUNT(rev) as count FROM clients_schema.experiments_history;'
    )
    response = await pg_helpers.fetchrow(pool, query)
    return response['count']


@pytest.mark.pgsql('taxi_exp', files=('fill.sql',))
async def test_history_items(taxi_exp_client):
    pool = taxi_exp_client.app['pool']

    assert await _count(pool) == 0
    await pg_helpers.execute_sql_function(pool, ADD_HISTORY_ITEM)
    assert await _count(pool) == 1

    response = await pg_helpers.fetchrow(pool, GET_HISTORY_ITEM)
    assert response['rev'] == 1
    assert response['name'] == 'existed_experiment'
    assert not response['is_config']

    body = json.loads(response['body'])
    body.pop('date_to')
    body.pop('date_from')
    body.pop('created')
    body.pop('last_manual_update')
    body['exp_metadata'].pop('update_time')
    assert body == {
        'id': 1,
        'rev': 1,
        'biz_revision': 1,
        'name': 'existed_experiment',
        'tags': [],
        'files': ['aaaaabbbb'],
        'closed': False,
        'schema': '',
        'clauses': [],
        'enabled': True,
        'removed': False,
        'fallback': None,
        'owners': [],
        'watchers': [],
        'trait_tags': None,
        'st_tickets': None,
        'department': 'commando',
        'service_id': None,
        'namespace': None,
        'consumers': ['test_consumer'],
        'is_config': False,
        'predicate': {'type': 'true'},
        'description': 'DESCRIPTION',
        'applications': [
            {
                'name': 'android',
                'version_to': '10.1.1',
                'version_from': '1.1.1',
            },
            {
                'name': 'iphone',
                'version_to': '10.1.1',
                'version_from': '1.1.1',
            },
        ],
        'default_value': None,
        'self_ok': False,
        'financial': True,
        'is_technical': False,
        'shutdown_mode': 'instant_shutdown',
        'schema_id': None,
        'gradual_shutdown_percentage_step': None,
        'gradual_shutdown_time_step': None,
        'enable_debug': False,
        'removed_stamp': None,
        'merge_values_by': None,
        'rollout_stable_time': None,
        'wait_on_prestable': None,
        'exp_metadata': {
            'change_type': 'direct',
            'exp_schema_version': 10,
            'segmentation_method': None,
        },
    }


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_history_items_after_adding_experiment(taxi_exp_client):
    experiment_body = experiment.generate(EXPERIMENT_NAME)

    pool = taxi_exp_client.app['pool']
    assert await _count(pool) == 0

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == 200
    assert await _count(pool) == 1

    # get experiment id
    query = (
        'SELECT id FROM clients_schema.experiments '
        """WHERE name='{exp_name}' AND """
        'is_config IS FALSE AND removed IS FALSE'.format(
            exp_name=EXPERIMENT_NAME,
        )
    )
    response = await pg_helpers.fetchrow(pool, query)
    exp_id = response['id']

    # trying to modify
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=experiment_body,
    )
    assert response.status == 200
    assert await _count(pool) == 2

    # close experiment using db function
    query = (
        """
    SELECT pg_temp.close_experiment(
    {exp_id}, '{date_from}', '{date_to}', '{apps}'::jsonb, 'direct'
    )""".format(
            exp_id=exp_id,
            date_from=dates.timestring(),
            date_to=dates.timestring(),
            apps=json.dumps(
                [
                    {
                        'name': 'android',
                        'version_range': {'from': '1.1.1', 'to': '2.1.1'},
                    },
                ],
            ),
        )
    )
    await pg_helpers.execute_sql_function(pool, query)
    assert await _count(pool) == 3

    # update closed
    response = await taxi_exp_client.put(
        '/v1/closed-experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 3},
        json=experiment_body,
    )
    assert response.status == 200
    assert await _count(pool) == 4

    # delete experiment using db function
    query = DELETE_EXPERIMENT_QUERY
    await pg_helpers.execute_sql_function(
        pool, query, EXPERIMENT_NAME, None, 4, False,
    )
    assert await _count(pool) == 5
