import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'name, schema, code, status',
    [
        pytest.param(
            'exp_all',
            """description: 'default schema'
additionalProperties: true""",
            'BAD_ADDITIONAL_PROPERTIES',
            400,
            id='disable_for_all',
            marks=pytest.mark.config(
                EXP_VALUES_SCHEMA_SETTINGS={
                    'block_additionalproperties_true': {
                        'for_all': True,
                        'for_some': [],
                    },
                },
            ),
        ),
        pytest.param(
            'exp_some',
            """description: 'default schema'
additionalProperties: true""",
            'BAD_ADDITIONAL_PROPERTIES',
            400,
            id='disable_for_some',
            marks=pytest.mark.config(
                EXP_VALUES_SCHEMA_SETTINGS={
                    'block_additionalproperties_true': {
                        'for_all': False,
                        'for_some': ['exp_some'],
                    },
                },
            ),
        ),
        pytest.param(
            'exp_other',
            """description: 'default schema'
additionalProperties: true""",
            None,
            200,
            id='disable_for_some_and_other_name',
            marks=pytest.mark.config(
                EXP_VALUES_SCHEMA_SETTINGS={
                    'block_additionalproperties_true': {
                        'for_all': False,
                        'for_some': ['exp_some'],
                    },
                },
            ),
        ),
        pytest.param(
            'exp_other',
            """description: 'default schema'
additionalProperties: false""",
            None,
            200,
            id='disable_for_some_and_other_name_2',
            marks=pytest.mark.config(
                EXP_VALUES_SCHEMA_SETTINGS={
                    'block_additionalproperties_true': {
                        'for_all': True,
                        'for_some': [],
                    },
                },
            ),
        ),
        pytest.param(
            'exp_other',
            """type: object
description: 'default schema'""",
            'BAD_ADDITIONAL_PROPERTIES',
            400,
            id='no_filled_additiona_properties',
            marks=pytest.mark.config(
                EXP_VALUES_SCHEMA_SETTINGS={
                    'block_additionalproperties_true': {
                        'for_all': True,
                        'for_some': [],
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_fail_saving_experiment_with_bad_schema(
        name, schema, code, status, taxi_exp_client,
):
    data = experiment.generate(name, schema=schema)

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name},
        json=data,
    )
    assert response.status == status
    body = await response.json()
    assert body.get('code') == code
