import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT1 = 'exp1'
EXPERIMENT2 = 'exp2'
EXPERIMENT3 = 'exp3'


@pytest.mark.parametrize(
    'gen_func,init_func,get_list_func,key',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.get_experiments_list,
            'experiments',
            id='create_update_exp_with_namespace_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.get_configs_list,
            'configs',
            id='create_update_config_with_namespace_direct',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_search_by_namespace(
        taxi_exp_client, gen_func, init_func, get_list_func, key,
):
    # generate experiments in different namespaces
    experiment_body = gen_func(
        name=EXPERIMENT1, namespace='market', last_modified_at=1,
    )
    await init_func(taxi_exp_client, experiment_body, namespace='market')
    experiment_body = gen_func(name=EXPERIMENT2, last_modified_at=1)
    await init_func(taxi_exp_client, experiment_body, namespace=None)
    experiment_body = gen_func(
        name=EXPERIMENT3, namespace='not_market', last_modified_at=1,
    )
    await init_func(taxi_exp_client, experiment_body, namespace='not_market')
    # test queries
    response = await get_list_func(taxi_exp_client, namespace='market')
    assert response.status == 200
    res_exps = [item['name'] for item in (await response.json())[key]]
    assert res_exps == [EXPERIMENT1]

    response = await get_list_func(taxi_exp_client, namespace=None)
    assert response.status == 200
    res_exps = [item['name'] for item in (await response.json())[key]]
    assert res_exps == [EXPERIMENT2]

    response = await get_list_func(taxi_exp_client, namespace='not_market')
    assert response.status == 200
    res_exps = [item['name'] for item in (await response.json())[key]]
    assert res_exps == [EXPERIMENT3]
