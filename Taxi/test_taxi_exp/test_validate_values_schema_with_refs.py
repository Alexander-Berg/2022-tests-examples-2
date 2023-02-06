import os

import pytest
import yaml

from taxi_exp import web_context


@pytest.mark.parametrize(
    'schema,clause,answer_code',
    [
        (
            """
                description: "New search screen client options"
                type: object
                properties:
                  default_enabled:
                    type: boolean
                  l10n:
                    $ref: 'l10n.yaml#/l10n'
                required:
                  - l10n
                  - default_enabled
            """,
            {
                'title': 'test',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'default': 'Check car number',
                            'key': 'ask_number_verification',
                            'tanker': {
                                'key': 'ask_number_verification',
                                'keyset': 'client_messages',
                            },
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            200,
        ),
        (
            """
                description: "New search screen client options"
                type: object
                properties:
                  default_enabled:
                    type: boolean
                  l10n:
                    $ref: 'l10n.yaml#/l10n'
                required:
                  - l10n
                  - default_enabled
            """,
            {
                'title': 'test',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'default': 'Check car number',
                            'key': 'ask_number_verification',
                            'tanker': {  # see EXP_L10N_KEYSETS
                                'key': 'ask_number_verification',
                                'keyset': 'non_registered_keyset',
                            },
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            400,
        ),
        (
            """
                description: "New search screen client options"
                type: object
                properties:
                    default_enabled:
                        type: boolean
                    l10n:
                        type: array
                        minItems: 1
                        items:
                            type: object
                            additionalProperties: false
                            required:
                              - default
                              - key
                              - tanker
                            properties:
                                default:
                                    type: string
                                key:
                                    type: string
                                tanker:
                                    type: object
                                    additionalProperties: false
                                    required:
                                      - key
                                      - keyset
                                    properties:
                                        key:
                                            type: string
                                            description: Tanker`s key
                                        keyset:
                                            type: string
                                            description: Tanker`s keyset
                required:
                    - l10n
                    - default_enabled""",
            {
                'title': 'test',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'default': 'Check car number',
                            'key': 'ask_number_verification',
                            'tanker': {
                                'key': 'ask_number_verification',
                                'keyset': 'client_messages',
                            },
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            200,
        ),
        (
            """
                $ref: 'common.yaml#/default_obj'
                description: "New search screen client options"
            """,
            {
                'title': 'clause with obj type',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'default': 'default_value',
                            'key': 'key',
                            'tanker': {
                                'key': 'key',
                                'keyset': 'client_messages',
                            },
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            200,
        ),
        (
            """
                $ref: 'common.yaml#/default_obj'
                description: "New search screen client options"
            """,
            {
                'title': 'clause with invalid type',
                'value': True,
                'predicate': {'type': 'true'},
            },
            400,
        ),
        (
            """
                $ref: '_invalid_path.yaml#/default_obj'
                description: "New search screen client options"
            """,
            {
                'title': 'clause with invalid type',
                'value': True,
                'predicate': {'type': 'true'},
            },
            400,
        ),
        (
            """
                description: "with remove key default"
                type: object
                properties:
                  default_enabled:
                    type: boolean
                  l10n:
                    $ref: 'l10n.yaml#/l10n'
                required:
                  - l10n
                  - default_enabled
            """,
            {
                'title': 'test',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'key': 'ask_number_verification',
                            'tanker': {
                                'key': 'ask_number_verification',
                                'keyset': 'client_messages',
                            },
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            400,
        ),
        (
            """
                description: "New search screen client options"
                type: object
                properties:
                  default_enabled:
                    type: boolean
                  l10n:
                    $ref: 'l10n.yaml#/l10n'
                required:
                  - l10n
                  - default_enabled
            """,
            {
                'title': 'test',
                'value': {
                    'default_enabled': True,
                    'l10n': [
                        {
                            'default': 'Check car number',
                            'key': 'ask_number_verification',
                            'tanker': {'keyset': 'client_messages'},
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
            400,
        ),
        (
            """
                description: "New search screen client options"
                type: object
                properties:
                  default_enabled:
                    type: boolean
                  l10n:
                    $ref: 'l10n.yaml#/l10n'
                required:
                  - l10n
                  - default_enabled
            """,
            {
                'title': 'test',
                'value': {'default_enabled': True, 'l10n': []},
                'predicate': {'type': 'true'},
            },
            200,
        ),
        pytest.param(
            'type: int',
            {'title': 'test', 'value': 123, 'predicate': {'type': 'true'}},
            400,
            id='bad type',
        ),
    ],
)
@pytest.mark.config(
    EXP_BLOCK_SAVING_ENABLED_EXPERIMENT={},
    EXP_L10N_KEYSETS=['client_messages'],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_ref_in_schema(taxi_exp_client, schema, clause, answer_code):
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
    assert response.status == answer_code, await response.text()


def test_shortcuts_schemas():
    def _check_yaml(schemes_basepath, filename):
        filename = os.path.join(schemes_basepath, filename)
        with open(filename, encoding='utf-8') as _f:
            result = yaml.safe_load(_f)
            if not isinstance(result, dict):
                raise TypeError('Schema must be an instance of dict')

    for fname in os.listdir(web_context.SCHEMA_SEARCH_PATH):
        _check_yaml(web_context.SCHEMA_SEARCH_PATH, fname)
