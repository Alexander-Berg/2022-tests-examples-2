from typing import Dict

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'
NOT_FOUND_NAME = 'something'

VALID_TEST_CLAUSES = [
    {
        'title': 'test_clause',
        'predicate': {'type': 'true'},
        'value': {'something': 'or_other'},
    },
]
INVALID_TEST_CLAUSES = [
    {'title': 'test_clause', 'predicate': {'type': 'true'}, 'value': {}},
]

VALID_DEFAULT_VALUE = {'something': 'or_other'}
INVALID_DEFAULT_VALUE: Dict[str, str] = {}

TEST_SCHEMA = """
description: 'default schema'
additionalProperties: False
required:
  - something
properties:
    something:
        type: string
"""


@pytest.mark.parametrize(
    'gen_func,init_func,is_config,not_found_error',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            False,
            {
                'message': (
                    f'experiment {NOT_FOUND_NAME} in tariff-editor namespace '
                    f'is not found'
                ),
                'code': 'EXPERIMENT_NOT_FOUND',
            },
            id='experiment',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            True,
            {
                'message': (
                    f'config {NOT_FOUND_NAME} in tariff-editor namespace '
                    f'is not found'
                ),
                'code': 'CONFIG_NOT_FOUND',
            },
            id='config',
        ),
    ],
)
@pytest.mark.parametrize(
    'exp_name,schema_body,add_twice,skip_validating_values,expected_status,'
    'expected_error,default_value,clauses',
    [
        pytest.param(
            NOT_FOUND_NAME,
            '',
            False,
            False,
            404,
            {},
            VALID_DEFAULT_VALUE,
            VALID_TEST_CLAUSES,
            id='config/exp_does_not_exist',
        ),
        pytest.param(
            'experiment',
            'something',
            False,
            False,
            400,
            {
                'code': 'INVALID_SCHEMA_ERROR',
                'message': (
                    'check schema has incorrect format: '
                    '\'something\' is not of type \'object\''
                ),
            },
            VALID_DEFAULT_VALUE,
            VALID_TEST_CLAUSES,
            id='schema_has_invalid_format',
        ),
        pytest.param(
            'experiment',
            TEST_SCHEMA,
            False,
            False,
            400,
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause test_clause is not valid: '
                    '\'something\' is a required property'
                ),
            },
            VALID_DEFAULT_VALUE,
            INVALID_TEST_CLAUSES,
            id='clauses_fail_to_validate_by_schema',
        ),
        pytest.param(
            'experiment',
            TEST_SCHEMA,
            False,
            False,
            400,
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: '
                    '\'something\' is a required property'
                ),
            },
            INVALID_DEFAULT_VALUE,
            VALID_TEST_CLAUSES,
            id='default_fails_to_validate_by_schema',
        ),
        pytest.param(
            'experiment',
            TEST_SCHEMA,
            False,
            True,
            200,
            {},
            VALID_DEFAULT_VALUE,
            INVALID_TEST_CLAUSES,
            id='ignore_invalid_clauses_and_do_not_validate_by_schema',
        ),
        pytest.param(
            'experiment',
            TEST_SCHEMA,
            False,
            True,
            200,
            {},
            INVALID_DEFAULT_VALUE,
            VALID_TEST_CLAUSES,
            id='ignore_invalid_default_and_do_not_validate_by_schema',
        ),
        pytest.param(
            'experiment',
            experiment.DEFAULT_SCHEMA,
            True,
            None,
            409,
            {'code': 'SCHEMA_DRAFT_EXISTS'},
            VALID_DEFAULT_VALUE,
            VALID_TEST_CLAUSES,
            id='schema_draft_exists',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_add_schema_draft(
        taxi_exp_client,
        gen_func,
        init_func,
        is_config,
        not_found_error,
        exp_name,
        schema_body,
        add_twice,
        skip_validating_values,
        expected_status,
        expected_error,
        default_value,
        clauses,
):
    # init exp/config
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, default_value=default_value, clauses=clauses,
    )

    await init_func(taxi_exp_client, experiment_body)
    # add schema draft
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=exp_name,
        schema_body=schema_body,
        is_config=is_config,
        skip_validating_values=skip_validating_values,
    )
    # check errors
    if not add_twice:
        response_body = await response.json()
        assert response.status == expected_status
        if expected_status == 404:
            assert response_body == not_found_error
        elif expected_status != 200:
            assert response_body == expected_error
        return
    assert response.status == 200
    assert (await response.json()) == {'draft_id': 1, 'name': EXPERIMENT_NAME}
    # if successful, check with get
    response = await helpers.get_schema_draft(
        taxi_exp_client, name=EXPERIMENT_NAME, is_config=is_config,
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body == {
        'schema_body': experiment.DEFAULT_SCHEMA,
        'draft_id': 1,
    }
    # add a second draft to test 409
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=exp_name,
        schema_body=schema_body,
        is_config=is_config,
    )
    assert response.status == expected_status
    response_body = await response.json()
    assert response_body['code'] == expected_error['code']
    assert response_body['details'] == 'Existing draft id: 1'
