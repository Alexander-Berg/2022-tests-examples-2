import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_signal_clauses'
SCHEMA = """
type: object
additionalProperties: false
required:
  - enabled
properties:
    enabled:
        type: boolean"""


@pytest.mark.parametrize(
    'body, expected_status',
    [
        (
            experiment.generate(
                EXPERIMENT_NAME,
                schema=SCHEMA,
                clauses=[
                    experiment.make_clause(
                        'without_signal', value={'enabled': True},
                    ),
                    experiment.make_clause('with_signal', is_signal=True),
                ],
            ),
            200,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                schema=SCHEMA,
                clauses=[
                    experiment.make_clause(
                        'without_signal', value={'enabled': True},
                    ),
                    experiment.make_clause(
                        'with_signal',
                        is_signal=True,
                        value={'enabled': False},
                    ),
                ],
            ),
            400,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                schema=SCHEMA,
                clauses=[
                    experiment.make_clause(
                        'returned_clause',
                        value={'enabled': True},
                        predicate=experiment.mod_sha1_predicate(),
                    ),
                    experiment.make_clause(
                        'controlled_clause', is_paired_signal=True,
                    ),
                ],
            ),
            200,
        ),
        (
            experiment.generate(
                EXPERIMENT_NAME,
                schema=SCHEMA,
                clauses=[
                    experiment.make_clause(
                        'returned_clause',
                        value={'enabled': True},
                        predicate=experiment.mod_sha1_predicate(),
                    ),
                    experiment.make_clause(
                        'controlled_clause',
                        is_paired_signal=True,
                        value={'enabled': False},
                    ),
                ],
            ),
            400,
        ),
        pytest.param(
            experiment.generate(
                EXPERIMENT_NAME,
                schema=SCHEMA,
                clauses=[
                    experiment.make_clause(
                        'returned_clause',
                        value={'enabled': True},
                        predicate=experiment.mod_sha1_predicate(),
                    ),
                    experiment.make_clause(
                        'controlled_clause',
                        is_paired_signal=True,
                        value={'enabled': False},
                    ),
                ],
            ),
            200,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'backend': {'strictly_empty_signal_value': False},
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'backend': {'strictly_empty_signal_value': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_signal_clause(taxi_exp_client, body, expected_status):
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': EXPERIMENT_NAME},
        json=body,
    )
    assert response.status == expected_status, await response.text()
    if expected_status == 200:
        return

    code = (await response.json())['code']
    assert code == 'VALUE_VALIDATION_ERROR'
