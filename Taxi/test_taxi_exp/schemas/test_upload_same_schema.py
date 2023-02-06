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
async def test_upload_same_schema(
        taxi_exp_client, gen_func, init_func, update_func, get_func, is_config,
):
    # init exp/config
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        default_value=TEST_DEFAULT_VALUE,
        clauses=[],
        schema=TEST_SCHEMA,
    )

    await init_func(taxi_exp_client, experiment_body)

    # add schema draft with test schema
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=TEST_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200

    # publish schema for exp
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200

    # add draft with same schema
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=TEST_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200
    assert (await response.json()) == {}
