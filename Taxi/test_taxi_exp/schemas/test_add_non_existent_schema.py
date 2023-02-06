import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,update_func',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            id='experiment',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            id='config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_add_non_existent_schema(
        taxi_exp_client, gen_func, init_func, update_func,
):
    # init exp/config with non-exist schema_id
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, description='1', schema_id=1,
    )

    response = await init_func(
        taxi_exp_client, experiment_body, raw_answer=True,
    )
    assert response.status == 404
    response_body = await response.json()
    assert response_body == {
        'code': 'SCHEMA_NOT_FOUND',
        'message': 'schema with given schema_id is not found',
    }
    # remove schema_id and init successfully
    experiment_body.pop('schema_id')
    await init_func(
        taxi_exp_client,
        experiment_body,
        allow_empty_schema=True,
        raw_answer=True,
    )
    # try to update with non-existent schema_id
    experiment_body['last_modified_at'] = 1
    experiment_body['schema_id'] = 1

    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True,
    )
    assert response.status == 404
    response_body = await response.json()
    assert response_body == {
        'code': 'SCHEMA_NOT_FOUND',
        'message': 'schema with given schema_id is not found',
    }
