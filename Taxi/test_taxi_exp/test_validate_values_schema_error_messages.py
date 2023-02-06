import pytest


@pytest.mark.parametrize(
    'schema,clause,expected_error',
    [
        pytest.param(
            """
                type: object
                additionalProperties: false
                required:
                  - enabled_option
                properties:
                    enabled_option:
                        type: object
                        additionalProperties: false
                        required:
                          - enabled
                        properties:
                            enabled:
                                type: boolean
                            detail:
                                type: object
                                additionalProperties:
                                    $ref: '#/definitions/Value'
                definitions:
                    Value:
                        type: string
            """,
            {
                'title': 'Clause',
                'value': {'enabled_option': {}},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'clause Clause is not valid: '
                    '\'enabled\' is a required property, '
                    'see `enabled_option`'
                ),
                'code': 'VALUE_VALIDATION_ERROR',
            },
            id='partially_filled_value',
        ),
        pytest.param(
            """
                type: object
                additionalProperties: false
                required:
                  - enabled_option
                properties:
                    enabled_option:
                        type: object
                        additionalProperties: false
                        required:
                          - enabled
                        properties:
                            enabled:
                                type: boolean
                            detail:
                                type: object
                                additionalProperties:
                                    $ref: '#/definitions/Value'
                definitions:
                    Value:
                        type: string
            """,
            {
                'title': 'Clause',
                'value': {'enabled_option': {}},
                'predicate': {'type': 'true'},
                'is_signal': False,
            },
            {
                'message': (
                    'clause Clause is not valid: '
                    '\'enabled\' is a required property, '
                    'see `enabled_option`'
                ),
                'code': 'VALUE_VALIDATION_ERROR',
            },
            id='partially_filled_value_with_is_signal',
        ),
        pytest.param(
            """
                type: object
                additionalProperties: false
                properties:
                    enabled: boolean
            """,
            {
                'title': 'clause with obj type',
                'value': {},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'check schema has incorrect format: '
                    '\'boolean\' is not of type \'object\', '
                    'see `properties->enabled`'
                ),
                'code': 'INVALID_SCHEMA_ERROR',
            },
            id='invalid_type_schema',
        ),
        pytest.param(
            """
                type: object
                additionalProperties_false
                properties:
                    enabled: boolean
            """,
            {
                'title': 'clause with obj type',
                'value': {},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'yaml schema has incorrect format: '
                    'while scanning a simple key\n'
                    '  in "<unicode string>", line 3, column 17:\n'
                    '                    additionalProperties_false\n'
                    '                    ^\n'
                    'could not find expected \':\'\n'
                    '  in "<unicode string>", line 4, column 17:\n'
                    '                    properties:\n'
                    '                    ^'
                ),
                'code': 'INVALID_SCHEMA_ERROR',
            },
            id='invalid_yaml_schema',
        ),
        pytest.param(
            """
                type: object
                additionalProperties: true
                properties:
                    enabled:
                        type: boolean
            """,
            {
                'title': 'clause with obj type',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'additionalProperties set to true '
                    'but x-taxi-additional-properties-true-reason not found'
                ),
                'code': 'BAD_ADDITIONAL_PROPERTIES',
            },
            id='additional_properties_true_no_reason',
        ),
        pytest.param(
            """
                type: object
                additionalProperties: true
                x-taxi-additional-properties-true-reason: {}
                properties:
                    enabled:
                        type: boolean
            """,
            {
                'title': 'clause with obj type',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'Requested key "x-taxi-additional-properties-true-reason" '
                    'value must be instance of type "<class \'str\'>", '
                    'but it has "<class \'dict\'>" type'
                ),
                'code': 'BAD_ADDITIONAL_PROPERTIES',
            },
            id='additional_properties_true_wrong_reason',
        ),
        pytest.param(
            """
                type: object
                properties:
                    enabled:
                        type: boolean
            """,
            {
                'title': 'clause with obj type',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
            {
                'message': (
                    'additionalProperties needs to be specified '
                    'explicitly for object with properties [enabled]'
                ),
                'code': 'BAD_ADDITIONAL_PROPERTIES',
            },
            id='nofilled_additional_properties',
        ),
        pytest.param(
            '',
            {
                'title': 'clause with obj type',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
            {
                'message': 'Provided schema is empty. Schema cannot be empty.',
                'code': 'EMPTY_SCHEMA_ERROR',
            },
            id='fail if schema is empty',
        ),
    ],
)
@pytest.mark.config(
    EXP_BLOCK_SAVING_ENABLED_EXPERIMENT={},
    EXP_L10N_KEYSETS=['client_messages'],
    EXP_VALUES_SCHEMA_SETTINGS={
        'block_additionalproperties_true': {'for_all': True, 'for_some': []},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_ref_in_schema(taxi_exp_client, schema, clause, expected_error):
    # template without applications
    experiment = {
        'description': 'test_description',
        'match': {
            'enabled': True,
            'schema': schema,
            'predicate': {'type': 'true'},
            'action_time': {
                'from': '2018-10-05T03:00:00+0300',
                'to': '2018-10-05T04:00:00+0300',
            },
            'consumers': [{'name': 'test_consumer'}],
        },
        'default_value': None,
        'clauses': [clause],
        'department': 'common',
    }

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name_1'},
        json=experiment,
    )
    body = await response.json()
    assert expected_error == body, response.status
