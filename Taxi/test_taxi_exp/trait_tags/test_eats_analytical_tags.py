import typing

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

FILL = (
    """
    INSERT INTO clients_schema.experiments
    (
        name, date_from, date_to,
        rev, clauses, predicate, description, enabled, schema, closed
    ) VALUES (
                '%s',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE
    );"""
    % experiment.DEFAULT_EXPERIMENT_NAME
)

FILL_READY = (
    """
    INSERT INTO clients_schema.experiments
    (
        name, date_from, date_to,
        rev, clauses, predicate, description, enabled, schema, closed,
        trait_tags
    ) VALUES (
                '%s',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                '{"eat-experiment-ready"}'::text[]
    );"""
    % experiment.DEFAULT_EXPERIMENT_NAME
)


class Case(typing.NamedTuple):
    tag: str
    is_update: bool
    status: int
    result: typing.Dict
    body: typing.Dict = experiment.generate(owners=['serg-novikov'])


@pytest.mark.parametrize(
    helpers.get_args(Case),
    (
        pytest.param(
            *Case(
                tag='prepare-eat-experiment',
                is_update=False,
                status=200,
                result={},
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY]),
            id='allow_prepare_for_create',
        ),
        pytest.param(
            *Case(
                tag='prepare-eat-experiment',
                is_update=True,
                status=400,
                result={
                    'message': (
                        'Do not set `prepare-eat-experiment` tag for update'
                    ),
                    'code': 'EATS_TRAIT_TAGS_RESTRICTIONS',
                },
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY, FILL]),
            id='disallow_prepare_for_update',
        ),
        pytest.param(
            *Case(
                tag='eat-experiment-ready',
                is_update=True,
                status=400,
                result={
                    'message': (
                        'Do not set auto installed `eat-experiment-ready` tag'
                    ),
                    'code': 'EATS_TRAIT_TAGS_RESTRICTIONS',
                },
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY, FILL]),
            id='disallow_ready_for_update_if_ready_not_found',
        ),
        pytest.param(
            *Case(
                tag='eat-experiment-ready',
                is_update=True,
                status=200,
                result={},
            ),
            marks=pytest.mark.pgsql(
                'taxi_exp', queries=[db.INIT_QUERY, FILL_READY],
            ),
            id='allow_ready_for_update_if_ready_found',
        ),
        pytest.param(
            *Case(
                tag='eat-experiment-ready',
                is_update=False,
                status=400,
                result={
                    'message': (
                        'Do not set `eat-experiment-ready` tag for create'
                    ),
                    'code': 'EATS_TRAIT_TAGS_RESTRICTIONS',
                },
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY]),
            id='disallow_ready_for_create',
        ),
        pytest.param(
            *Case(
                tag='prepare-eat-experiment',
                is_update=False,
                status=400,
                result={
                    'message': (
                        'You should specify at least one clause when using '
                        'prepare-eat-experiment tag'
                    ),
                    'code': 'EATS_TRAIT_TAGS_RESTRICTIONS',
                },
                body=experiment.generate(clauses=[], owners=['serg-novikov']),
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY]),
            id='disallow_ready_for_create',
        ),
        pytest.param(
            *Case(
                tag='prepare-eat-experiment',
                is_update=False,
                status=400,
                result={
                    'message': (
                        'You should specify at least one owner when using '
                        'prepare-eat-experiment tag'
                    ),
                    'code': 'EATS_TRAIT_TAGS_RESTRICTIONS',
                },
                body=experiment.generate(owners=[]),
            ),
            marks=pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY]),
            id='disallow_ready_for_create_if_empty_owners',
        ),
    ),
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {
                'trait_tags_v2': {
                    'prepare-eat-experiment': {'availability': ['__any__']},
                    'eat-experiment-ready': {'availability': ['__any__']},
                },
                'blocked_trait_tags': {
                    'add': ['eat-experiment-ready'],
                    'update': ['prepare-eat-experiment'],
                },
            },
        },
    },
)
async def test_eats_analytical_tags(
        taxi_exp_client, tag, is_update, status, result, body,
):
    body['trait_tags'] = [tag]

    params = {'name': experiment.DEFAULT_EXPERIMENT_NAME}
    handler = taxi_exp_client.post
    if is_update:
        response = await taxi_exp_client.get(
            'v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params=params,
        )
        params['last_modified_at'] = (await response.json())[
            'last_modified_at'
        ]
        handler = taxi_exp_client.put
    response = await handler(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body,
    )

    assert response.status == status, await response.text()
    assert await response.json() == result
