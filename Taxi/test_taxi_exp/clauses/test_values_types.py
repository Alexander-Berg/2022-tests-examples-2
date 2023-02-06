import typing

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'values_experiment'


class Case(typing.NamedTuple):
    schema: str
    value: typing.Any
    is_config: bool
    is_valid: bool
    answer: typing.Dict


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(
            schema='type: string',
            value='string',
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema='type: number',
            value=123,
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema='type: number',
            value=0.455,
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema="""type: object
additionalProperties: false
properties:
    enabled:
        type: boolean""",
            value={'enabled': True},
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema="""description: Доступные постпроцессоры
default: []
tags:
  - 'notfallback'
maintainers:
  - alex-tsarkov
  - yusupovazat
schema:
    description: Названия постпроцессоров
    type: array
    x-taxi-cpp-type: std::unordered_set
    items:
        description: Название постпроцессора
        type: string""",
            value=[
                'default_logging',
                'yt_logging',
                'sorting',
                'exclude-by-filters',
                'exclude-by-max-score',
            ],
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema="""type: array
items:
    type: string""",
            value=[
                'default_logging',
                'yt_logging',
                'sorting',
                'exclude-by-filters',
                'exclude-by-max-score',
            ],
            is_config=False,
            is_valid=True,
            answer={},
        ),
        *(
            Case(
                schema="""description: "test value"
type: object
required:
  - elastic_host
properties:
  elastic_host:
    type: array
    minItems: 1
    items:
      type: string
  place_index_name:
    type: string
    default: place_production
  place_type_name:
    type: string
    default: place
  menu_item_index_name:
    type: string
    default: menu_item_production
  menu_item_type_name:
    type: string
    default: menu_item
  batch_size:
    type: integer
    min: 10
    max: 1024
    default: 1024
  use_msearch:
    type: boolean
    default: true
additionalProperties: false""",
                value={
                    'batch_size': 120,
                    'use_msearch': True,
                    'elastic_host': [
                        'http://c3po.lxc.eda.tst.yandex.net:9200',
                    ],
                    'place_type_name': 'place',
                    'place_index_name': 'place_production',
                    'menu_item_type_name': 'menu_item',
                    'menu_item_index_name': 'menu_item_production',
                },
                is_config=is_config,
                is_valid=True,
                answer={},
            )
            for is_config in [True, False]
        ),
        Case(
            schema="""
type: array
items:
    type: array
    items:
        type: number
        format: double""",
            value=[[0.1, 1.1], [2.2, 4.5]],
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema="""
type: array
items:
    type: array
    items:
        type: array
        items:
            type: number
            format: double""",
            value=[[[0.1, 1.1], [2.2, 4.5]]],
            is_config=False,
            is_valid=True,
            answer={},
        ),
        Case(
            schema="""description: "test value"
type: object
properties:
  l10n:
    type: array
    items:
      type: string""",
            value={'l10n': ['123']},
            is_config=False,
            is_valid=False,
            answer={
                'message': (
                    """clause title checked by shortcut l10n is not valid: """
                    """'123' is not of type 'object', see `0`"""
                ),
                'code': 'VALUE_VALIDATION_ERROR',
            },
        ),
        Case(
            schema="""description: "test value"
type: object
properties:
    l10n:
        $ref: 'l10n.yaml#/l10n'""",
            value={
                'l10n': [
                    {
                        'default': 'default_123',
                        'key': 'key_123',
                        'tanker': {
                            'key': 'tanker_key_123',
                            'keyset': 'non_registered',
                        },
                    },
                ],
            },
            is_config=False,
            is_valid=False,
            answer={
                'message': (
                    'Clause title is not valid: used "non_registered" keyset '
                    'non-registered in EXP_L10N_KEYSETS'
                ),
                'code': 'VALUE_VALIDATION_ERROR',
            },
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_values_types(
        taxi_exp_client, schema, value, is_config, is_valid, answer,
):
    if is_config:
        body = experiment.generate_config(
            schema=schema,
            clauses=[experiment.make_clause('title', value=value)],
            default_value=value,
        )
    else:
        body = experiment.generate(
            schema=schema,
            clauses=[experiment.make_clause('title', value=value)],
        )
    url = '/v1/configs/' if is_config else '/v1/experiments/'
    response = await taxi_exp_client.post(
        url,
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': EXPERIMENT_NAME},
        json=body,
    )
    if is_valid:
        assert response.status == 200
    else:
        assert response.status == 400
        body = await response.json()
        assert body == answer
        return

    if is_config:
        await helpers.get_configs_updates(taxi_exp_client, newer_than=0)
    else:
        await helpers.get_updates(taxi_exp_client, newer_than=0)
