import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'

TEST_SCHEMA = """
description: 'schema to test things'
additionalProperties: False
required:
  - something
properties:
    something:
        type: string
    else:
        type: string
"""

TEST_DEFAULT_VALUE = {'something': 'something'}


@pytest.mark.parametrize(
    'gen_func,init_func,update_func,get_func,is_config',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            helpers.get_experiment,
            False,
            id='experiment_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            helpers.get_config,
            True,
            id='config_direct',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_upload_schema_before_uploading_exp(
        taxi_exp_client, gen_func, init_func, update_func, get_func, is_config,
):
    # add schema draft with test schema
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=TEST_SCHEMA,
        is_config=is_config,
        skip_validating_values=True,
    )
    assert response.status == 200

    # init exp/config with test default value
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        default_value=TEST_DEFAULT_VALUE,
        clauses=[],
        schema='',
    )

    await init_func(taxi_exp_client, experiment_body, allow_empty_schema=True)

    # publish schema for exp
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200
    # try setting empty default to confirm that validation still happens
    experiment_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    experiment_body['default_value'] = {}
    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True,
    )
    assert response.status == 400
    response_body = await response.json()
    assert response_body == {
        'code': 'VALUE_VALIDATION_ERROR',
        'message': (
            'clause default is not valid: \'something\' is a required property'
        ),
    }
