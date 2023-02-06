import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_alias'


@pytest.mark.parametrize(
    'body, aliases, result',
    [
        (
            experiment.generate(
                EXPERIMENT_NAME,
                clauses=[
                    experiment.make_clause('without_alias'),
                    experiment.make_clause('without_alias_v2'),
                ],
            ),
            [None, None],
            200,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                clauses=[
                    experiment.make_clause('without_alias'),
                    experiment.make_clause('with_alias', alias='выавыавы'),
                ],
            ),
            None,
            400,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                clauses=[
                    experiment.make_clause('without_alias'),
                    experiment.make_clause('with_alias', alias='alias_field'),
                ],
            ),
            [None, 'alias_field'],
            200,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                clauses=[
                    experiment.make_clause(
                        'with_alias_first', alias='alias_field',
                    ),
                    experiment.make_clause('with_alias', alias='alias_field'),
                ],
            ),
            None,
            400,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                clauses=[
                    experiment.make_clause(
                        'with_alias_first', alias='another_alias_field',
                    ),
                    experiment.make_clause('with_alias', alias='alias_field'),
                ],
            ),
            ['another_alias_field', 'alias_field'],
            200,
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_alias(taxi_exp_client, body, aliases, result):
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': EXPERIMENT_NAME},
        json=body,
    )
    assert response.status == result
    if result != 200:
        return

    response = await helpers.get_updates(taxi_exp_client, newer_than=0)
    body = response['experiments'][0]
    assert [clause.get('alias') for clause in body['clauses']] == aliases
