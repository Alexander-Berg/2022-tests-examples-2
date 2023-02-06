import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'

SECOND_TEST_SCHEMA = """
description: 'schema to test things'
additionalProperties: False
required:
  - something
  - else
properties:
    something:
        type: string
    else:
        type: string
"""

FIRST_TEST_SCHEMA = """
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

SECOND_DEFAULT_VALUE = {'something': 'something', 'else': 'else'}
FIRST_DEFAULT_VALUE = {'something': 'something'}


@pytest.mark.parametrize(
    'gen_func,init_func,update_func,get_func,restore_func,is_config',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            helpers.get_experiment,
            helpers.restore_experiment,
            False,
            id='experiment_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            helpers.get_config,
            helpers.restore_config,
            True,
            id='config_direct',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_restore_with_separate_schema(
        taxi_exp_client,
        gen_func,
        init_func,
        update_func,
        get_func,
        restore_func,
        is_config,
):
    # init exp/config with first default value
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        default_value=FIRST_DEFAULT_VALUE,
        clauses=[],
        schema='',
    )

    await init_func(taxi_exp_client, experiment_body, allow_empty_schema=True)
    # add schema draft with first schema and publish it
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=FIRST_TEST_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200

    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200
    # change default value to second, which has more params
    experiment_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    experiment_body['last_modified_at'] = 2
    experiment_body['default_value'] = SECOND_DEFAULT_VALUE

    await update_func(taxi_exp_client, experiment_body)
    # add draft and publish second schema, which has more required params
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=SECOND_TEST_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200

    response = await helpers.publish_schema(taxi_exp_client, draft_id=2)
    assert response.status == 200
    # add an extra draft to confirm it does not interfere with restore
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=SECOND_TEST_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200
    # restore to first default and schema
    response = await restore_func(taxi_exp_client, EXPERIMENT_NAME, 4, 2)
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
