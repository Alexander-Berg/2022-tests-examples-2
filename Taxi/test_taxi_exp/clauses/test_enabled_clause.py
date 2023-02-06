import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'test_enabled_clause'


@pytest.mark.parametrize(
    'body,expected_clauses',
    [
        pytest.param(
            experiment.generate(
                NAME,
                clauses=[
                    experiment.make_clause(
                        'test',
                        predicate=experiment.lt_predicate('abcd'),
                        value={},
                    ),
                ],
            ),
            [
                {
                    'title': 'test',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'abcd',
                        },
                    },
                    'value': {},
                },
            ],
            id='clauses without enabled',
        ),
        pytest.param(
            experiment.generate(
                NAME,
                clauses=[
                    experiment.make_clause(
                        'test',
                        predicate=experiment.lt_predicate('abcd'),
                        value={},
                        enabled=True,
                    ),
                ],
            ),
            [
                {
                    'title': 'test',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'abcd',
                        },
                    },
                    'value': {},
                    'enabled': True,
                },
            ],
            id='clause with True enabled',
        ),
        pytest.param(
            experiment.generate(
                NAME,
                clauses=[
                    experiment.make_clause(
                        'test',
                        predicate=experiment.lt_predicate('abcd'),
                        value={},
                        enabled=False,
                    ),
                ],
            ),
            [
                {
                    'title': 'test',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'abcd',
                        },
                    },
                    'value': {},
                    'enabled': False,
                },
            ],
            id='clause with False enabled',
        ),
        pytest.param(
            experiment.generate(
                NAME,
                clauses=[
                    experiment.make_clause(
                        'group_1',
                        predicate=experiment.lt_predicate('abcd'),
                        value={},
                        enabled=False,
                    ),
                    experiment.make_clause(
                        'group_2',
                        predicate=experiment.lt_predicate('efgty'),
                        value={},
                        enabled=True,
                    ),
                    experiment.make_clause(
                        'group_3',
                        predicate=experiment.lt_predicate('okjer'),
                        value={},
                    ),
                ],
            ),
            [
                {
                    'title': 'group_1',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'abcd',
                        },
                    },
                    'value': {},
                    'enabled': False,
                },
                {
                    'title': 'group_2',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'efgty',
                        },
                    },
                    'value': {},
                    'enabled': True,
                },
                {
                    'title': 'group_3',
                    'predicate': {
                        'type': 'lt',
                        'init': {
                            'arg_name': 'phone_id',
                            'arg_type': 'string',
                            'value': 'okjer',
                        },
                    },
                    'value': {},
                },
            ],
            id='many clauses with and without enabled',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_enable_clause(taxi_exp_client, body, expected_clauses):
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['clauses'] == expected_clauses

    response = await taxi_exp_client.get(
        '/v1/experiments/updates/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['experiments'][0]['clauses'] == expected_clauses
