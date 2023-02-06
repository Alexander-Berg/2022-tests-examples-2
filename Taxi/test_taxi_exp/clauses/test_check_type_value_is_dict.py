import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'test_tech_groups'


@pytest.mark.parametrize(
    'body,expected_response,is_fail',
    [
        pytest.param(
            experiment.generate(
                name=NAME,
                schema='type: number',
                clauses=[experiment.make_clause('first', value=123)],
            ),
            {},
            False,
            id='feature_disabled',
        ),
        pytest.param(
            experiment.generate(
                name=NAME,
                schema='type: number',
                clauses=[experiment.make_clause('first', value=123)],
            ),
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause first is not valid: value must be object type only'
                ),
            },
            True,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'common': {'check_all_values_are_objects': True},
                    },
                },
            ),
            id='feature_enabled',
        ),
        pytest.param(
            experiment.generate(
                name=NAME,
                schema='type: number',
                clauses=[experiment.make_clause('first', value=123)],
                trait_tags=['deprecated-type-value'],
            ),
            {},
            False,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'common': {'check_all_values_are_objects': True},
                    },
                },
            ),
            id='feature_enabled_but_exp_is_exception',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test(taxi_exp_client, body, expected_response, is_fail):
    if is_fail:
        response = await helpers.check_exp_by_draft(taxi_exp_client, body)
        assert response == expected_response

    response = await helpers.add_exp(taxi_exp_client, body)
    assert response == expected_response
