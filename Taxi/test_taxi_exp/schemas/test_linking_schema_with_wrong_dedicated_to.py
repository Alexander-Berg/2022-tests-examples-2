import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'
ANOTHER_EXPERIMENT_NAME = 'totally_different_experiment'

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
    'gen_func,init_func,get_func,update_func,is_config',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.get_experiment,
            helpers.update_exp,
            False,
            id='experiment',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.get_config,
            helpers.update_config,
            True,
            id='config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_delete_exp_with_schema(
        taxi_exp_client, gen_func, init_func, get_func, update_func, is_config,
):
    # init exp/config
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, description='1', schema='',
    )

    await init_func(taxi_exp_client, experiment_body, allow_empty_schema=True)
    # add schema draft
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=experiment.DEFAULT_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200
    # publish schema
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200

    experiment_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)

    assert experiment_body['schema_id'] == 1
    # init exp/config
    another_experiment_body = gen_func(
        name=ANOTHER_EXPERIMENT_NAME, schema='', schema_id=1,
    )

    response = await init_func(
        taxi_exp_client,
        another_experiment_body,
        raw_answer=True,
        allow_empty_schema=True,
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'LINK_SCHEMA_WITH_WRONG_DEDICATED_TO',
        'message': (
            'The schema you are trying to link is dedicated to '
            'a different experiment/config'
        ),
    }

    another_experiment_body.pop('schema_id')

    await init_func(
        taxi_exp_client, another_experiment_body, allow_empty_schema=True,
    )

    another_experiment_body['schema_id'] = 1
    another_experiment_body['last_modified_at'] = 1

    response = await update_func(
        taxi_exp_client, another_experiment_body, raw_answer=True,
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'LINK_SCHEMA_WITH_WRONG_DEDICATED_TO',
        'message': (
            'The schema you are trying to link is dedicated to '
            'a different experiment/config'
        ),
    }
