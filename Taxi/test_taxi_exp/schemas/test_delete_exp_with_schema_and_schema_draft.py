import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'

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
    'gen_func,init_func,is_config',
    [
        pytest.param(
            experiment.generate, helpers.init_exp, False, id='experiment',
        ),
        pytest.param(
            experiment.generate_config, helpers.init_config, True, id='config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_delete_exp_with_schema(
        taxi_exp_client, gen_func, init_func, is_config,
):
    # init exp/config
    experiment_body = gen_func(name=EXPERIMENT_NAME)

    await init_func(taxi_exp_client, experiment_body)
    # add schema draft
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=experiment.DEFAULT_SCHEMA,
        is_config=is_config,
    )
    assert response.status == 200
    # if successful, check with get
    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200
    # add schema draft
    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=experiment.DEFAULT_SCHEMA,
        is_config=is_config,
    )
    await db.remove_exp(taxi_exp_client.app, EXPERIMENT_NAME, 1)
