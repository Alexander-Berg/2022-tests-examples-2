import json

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'

STARTING_SCHEMA = """
description: 'starting schema'
additionalProperties: False
required:
  - starting_value
properties:
    starting_value:
        type: string
"""

NEW_SCHEMA = """
description: 'schema to test things'
additionalProperties: False
required:
  - next_value
properties:
    next_value:
        type: string
"""

FINAL_SCHEMA = """
description: 'final schema to test things'
additionalProperties: False
required:
  - next_value
properties:
    next_value:
        type: string
    final_value:
        type: string
"""

STARTING_DEFAULT_VALUE = {'starting_value': 'present'}
NEW_DEFAULT_VALUE = {'next_value': 'present'}
ONE_MORE_DEFAULT_VALUE = {'starting_value': 'still present'}
FINAL_DEFAULT_VALUE = {'final_value': 'present', 'next_value': 'still present'}


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
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.update_exp_by_draft,
            helpers.get_experiment,
            False,
            id='experiment_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.update_config_by_draft,
            helpers.get_config,
            True,
            id='config_by_draft',
        ),
    ],
)
@pytest.mark.parametrize(
    'new_schema,new_default_value,skip_validating_values,'
    'draft_response_code,error_body',
    [
        pytest.param(
            NEW_SCHEMA,
            STARTING_DEFAULT_VALUE,
            False,
            400,
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: Additional properties '
                    'are not allowed (\'starting_value\' was unexpected)'
                ),
            },
            id='new_default_fails_validation_no_skip_validation',
        ),
        pytest.param(
            NEW_SCHEMA,
            STARTING_DEFAULT_VALUE,
            True,
            400,
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: Additional properties '
                    'are not allowed (\'starting_value\' was unexpected)'
                ),
            },
            id='new_default_fails_validation_with_skip_validation',
        ),
        pytest.param(
            STARTING_SCHEMA,
            ONE_MORE_DEFAULT_VALUE,
            False,
            200,
            {},
            id='create_draft_even_though_schema_did_not_change',
        ),
        pytest.param(
            NEW_SCHEMA,
            NEW_DEFAULT_VALUE,
            False,
            200,
            {},
            id='correct_behaviour_scenario',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_add_default_from_separate_api(
        taxi_exp_client,
        gen_func,
        init_func,
        update_func,
        get_func,
        is_config,
        new_schema,
        new_default_value,
        skip_validating_values,
        draft_response_code,
        error_body,
):
    # init exp/config with starting schema/default
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        default_value=STARTING_DEFAULT_VALUE,
        clauses=[],
        schema=STARTING_SCHEMA,
    )

    await init_func(taxi_exp_client, experiment_body)

    # add schema draft and check errors
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=new_schema,
        is_config=is_config,
        default_value=new_default_value,
        skip_validating_values=skip_validating_values,
    )
    assert response.status == draft_response_code
    if draft_response_code != 200:
        assert (await response.json()) == error_body
        return

    assert (await response.json()) == {'draft_id': 1, 'name': EXPERIMENT_NAME}
    if new_schema == STARTING_SCHEMA:
        return

    # Only correct behaviour scenario gets past this point
    # ======================================================================
    # Plan:
    # 1. add/publish schema with default, check it worked
    # 2. try to override default by updating exp/config, check it failed
    # 3. add/publish schema with no default, check
    # 4. override default by updating exp/config, check

    # 1. ===================================================================

    # check draft was created
    response = await helpers.get_schema_draft(taxi_exp_client, draft_id=1)
    response_body = await response.json()
    assert response_body['schema_body'] == NEW_SCHEMA
    assert json.loads(response_body['default_value']) == NEW_DEFAULT_VALUE

    # publish
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200

    # check that values have been set
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['schema_id'] == 1
    assert response_body['match']['schema'] == NEW_SCHEMA
    assert response_body['default_value'] == NEW_DEFAULT_VALUE
    assert response_body['separate_default_value']

    # 2. ===================================================================

    # try and rewrite them with different values
    experiment_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    experiment_body['match']['schema'] = STARTING_SCHEMA
    experiment_body['default_value'] = STARTING_DEFAULT_VALUE
    await update_func(taxi_exp_client, experiment_body)

    # check that nothing changed
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['schema_id'] == 1
    assert response_body['match']['schema'] == NEW_SCHEMA
    assert response_body['default_value'] == NEW_DEFAULT_VALUE
    assert response_body['separate_default_value']

    # 3. ===================================================================

    # publish schema one last time, only changing schema now
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=FINAL_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200

    response = await helpers.publish_schema(taxi_exp_client, draft_id=2)
    assert response.status == 200

    # check that schema and flag changed, everything else did not
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['schema_id'] == 2
    assert response_body['match']['schema'] == FINAL_SCHEMA
    assert response_body['default_value'] == NEW_DEFAULT_VALUE
    assert 'separate_default_value' not in response_body

    # 4. ===================================================================

    # update exp again, replacing default value this time
    experiment_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    experiment_body['default_value'] = FINAL_DEFAULT_VALUE
    await update_func(taxi_exp_client, experiment_body)

    # check that update took place
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['schema_id'] == 2
    assert response_body['match']['schema'] == FINAL_SCHEMA
    assert response_body['default_value'] == FINAL_DEFAULT_VALUE
    assert 'separate_default_value' not in response_body
