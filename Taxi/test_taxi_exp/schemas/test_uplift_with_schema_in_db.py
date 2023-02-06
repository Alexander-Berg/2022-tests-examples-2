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
"""

DEFAULT_VALUE = {'something': 'something'}


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_uplift_with_separate_schema(taxi_exp_client):
    # init exp/config
    experiment_body = experiment.generate(
        name=EXPERIMENT_NAME,
        default_value=DEFAULT_VALUE,
        clauses=[],
        schema='',
    )

    await helpers.init_exp(
        taxi_exp_client, experiment_body, allow_empty_schema=True,
    )

    response = await helpers.add_schema_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        schema_body=TEST_SCHEMA,
        is_config=False,
    )
    assert response.status == 200

    response = await helpers.publish_schema(taxi_exp_client, draft_id=1)
    assert response.status == 200

    await helpers.uplift_to_config(taxi_exp_client, name=EXPERIMENT_NAME)

    experiment_body = await helpers.get_config(
        taxi_exp_client, EXPERIMENT_NAME,
    )
    experiment_body['default_value'] = {}
    response = await helpers.update_config(
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
