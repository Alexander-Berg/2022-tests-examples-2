import pytest


EXPERIMENTS = """INSERT INTO clients_schema.experiments
    (
        id,
        name,
        date_from, date_to,
        rev,
        clauses, predicate, default_value,
        description, enabled, schema,
        trait_tags,
        created, last_manual_update
    )
        VALUES
            (
                1,
                'first_experiment',
                '2020-03-25 18:54:05',
                '2022-03-25 18:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                ARRAY['analytical']::text[],
                '2020-03-23 21:54:05',
                '2020-03-24 12:54:05'
            )
            ,(
                2,
                'second_experiment',
                '2020-03-25 18:54:05',
                '2022-03-25 18:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                ARRAY['analytical']::text[],
                '2020-03-23 11:54:05',
                '2020-03-24 22:54:05'
            )
;"""

OWNERS = """INSERT INTO clients_schema.owners
    (experiment_id, owner_login)
    VALUES
        (1, 'first@'::text),
        (2, 'second@'::text)
;"""
WATCHERS = """INSERT INTO clients_schema.watchers
    (experiment_id, watcher_login)
    VALUES
        (1, 'second@'::text),
        (2, 'first@'::text)
;"""


@pytest.mark.parametrize(
    'params,expected_result',
    [
        ({'owner': '@'}, ['first_experiment', 'second_experiment']),
        ({'owner': 'first'}, ['first_experiment']),
        ({'watcher': 'first'}, ['second_experiment']),
        ({'watcher': 'second'}, ['first_experiment']),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[EXPERIMENTS, WATCHERS, OWNERS])
async def test_search_with_order(taxi_exp_client, params, expected_result):
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    names = [item['name'] for item in (await response.json())['experiments']]
    assert names == expected_result
