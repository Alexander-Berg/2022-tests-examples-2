import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'
NOT_FOUND_NAME = 'something'

TEST_SCHEMA = """
description: 'schema to test things'
additionalProperties: False
required:
  - something
properties:
    something:
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
    'schema_in_body,draft_exists,add_twice,'
    'publish_status,update_status,expected_error,exp_updated_before_publish',
    [
        pytest.param(
            '',
            False,
            False,
            404,
            0,
            {'code': 'SCHEMA_DRAFT_NOT_FOUND'},
            False,
            id='draft_not_found',
        ),
        pytest.param(
            '',
            True,
            False,
            400,
            0,
            {
                'message': (
                    'clause default is not valid: \'something\' '
                    'is a required property'
                ),
                'code': 'VALUE_VALIDATION_ERROR',
            },
            True,
            id='fail_to_publish_due_to_validation',
        ),
        pytest.param(
            '',
            True,
            False,
            200,
            400,
            {
                'code': 'VALUE_VALIDATION_ERROR',
                'message': (
                    'clause default is not valid: \'something\' is a '
                    'required property'
                ),
            },
            False,
            id='fail_to_update_because_of_schema',
        ),
        pytest.param('', True, True, 200, 200, {}, False, id='OK'),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_add_schema(
        taxi_exp_client,
        gen_func,
        init_func,
        update_func,
        get_func,
        is_config,
        schema_in_body,
        draft_exists,
        add_twice,
        publish_status,
        update_status,
        expected_error,
        exp_updated_before_publish,
):
    # init exp/config
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        default_value=TEST_DEFAULT_VALUE,
        clauses=[],
        schema=schema_in_body,
    )

    await init_func(taxi_exp_client, experiment_body, allow_empty_schema=True)

    if draft_exists:
        # add schema draft
        response = await helpers.add_schema_draft(
            taxi_exp_client,
            name=EXPERIMENT_NAME,
            schema_body=TEST_SCHEMA,
            is_config=is_config,
        )
        assert response.status == 200

    if exp_updated_before_publish:
        # update exp to test validation on publish
        experiment_body = gen_func(
            name=EXPERIMENT_NAME,
            last_modified_at=1,
            default_value={},
            clauses=[],
            schema=experiment.DEFAULT_SCHEMA,
        )

        await update_func(taxi_exp_client, experiment_body)

    # publish schema draft
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    # check errors
    assert response.status == publish_status
    if publish_status != 200:
        response_body = await response.json()
        assert response_body['code'] == expected_error['code']
        if 'message' in expected_error:
            assert response_body['message'] == expected_error['message']
        return

    assert (await response.json()) == {'name': EXPERIMENT_NAME}
    if add_twice:
        # add schema draft again
        response = await helpers.add_schema_draft(
            taxi_exp_client,
            name=EXPERIMENT_NAME,
            schema_body=experiment.DEFAULT_SCHEMA,
            is_config=is_config,
        )
        assert response.status == 200
        # publish schema draft again
        response = await helpers.publish_schema(taxi_exp_client, draft_id=2)
        assert response.status == 200

    # update exp with new default value
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    response_body['default_value'] = {}

    response = await update_func(
        taxi_exp_client, response_body, raw_answer=True,
    )
    # check errors
    assert response.status == update_status
    response_body = await response.json()
    if update_status != 200:
        assert response_body == expected_error
        return
    # check number of published schemas
    all_schemas = await db.get_all_schemas(taxi_exp_client.app)
    assert len(all_schemas) == 2
