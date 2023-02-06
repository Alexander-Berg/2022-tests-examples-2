import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,update_func,namespace',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            None,
            id='create_update_exp_with_empty_department',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            None,
            id='create_update_config_with_empty_department',
        ),
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.update_exp_by_draft,
            'market',
            id='create_update_exp_with_empty_department_'
            'and_market_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.update_config_by_draft,
            'market',
            id='create_update_config_with_empty_department'
            'and_market_namespace_by_draft',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_create_update_exp_with_department(
        taxi_exp_client, gen_func, init_func, update_func, namespace,
):
    # create exp with no department
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, department='', last_modified_at=1,
    )
    response_body = await init_func(
        taxi_exp_client, experiment_body, namespace=namespace,
    )
    assert 'department' not in response_body
    # change department to non-empty
    experiment_body['department'] = 'common'
    response_body = await update_func(
        taxi_exp_client, experiment_body, namespace=namespace,
    )
    assert response_body['department']
    # update with no department
    experiment_body['department'] = ''
    experiment_body['last_modified_at'] = 2
    response_body = await update_func(
        taxi_exp_client, experiment_body, namespace=namespace,
    )
    assert 'department' not in response_body
