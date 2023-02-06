import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'body,expected_answer',
    [
        pytest.param(
            experiment.generate(
                name='test',
                schema={'type': 'number'},
                default_value={'k': True},
                clauses=[experiment.make_clause('first', value=123)],
            ),
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: {\'k\': True} '
                    'is not of type \'number\''
                ),
            },
            id='fail if bad default value',
        ),
        pytest.param(
            experiment.generate(
                name='test',
                schema={'type': 'number'},
                default_value={'k': True},
                clauses=[],
            ),
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: {\'k\': True} is not '
                    'of type \'number\''
                ),
            },
            id='fail if bad default value and clauses empty',
        ),
        pytest.param(
            experiment.generate(
                name='test',
                schema={'type': 'boolean'},
                default_value=True,
                clauses=[],
            ),
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for default_value: '
                        'True does not match any schemes; '
                        'Invalid value for default_value: '
                        'True is not instance of dict'
                    ),
                },
            },
            id='fail if default value is not dict',
        ),
        pytest.param(
            experiment.generate(
                name='test',
                schema='',
                default_value={'k': True},
                clauses=[experiment.make_clause('first', value=123)],
            ),
            {
                'message': 'Provided schema is empty. Schema cannot be empty.',
                'code': 'EMPTY_SCHEMA_ERROR',
            },
            id='fail if schema is empty',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(taxi_exp_client, body, expected_answer):
    response = await helpers.add_exp(taxi_exp_client, body)
    assert response == expected_answer
