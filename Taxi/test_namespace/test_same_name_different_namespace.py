import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT = 'exp1'

NAMESPACES = ['market', 'not_market', None]

MOCKS = ['clown_cache_mocks']


@pytest.mark.parametrize(
    'gen_func,init_func,update_func,get_func,source',
    [
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.update_exp_by_draft,
            helpers.get_experiment,
            'experiments',
            id='create_update_exp_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            helpers.get_experiment,
            'experiments',
            id='create_update_exp_with_namespace_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.update_config_by_draft,
            helpers.get_config,
            'configs',
            id='create_update_config_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            helpers.get_config,
            'configs',
            id='create_update_config_with_namespace_direct',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_same_name_different_namespace(
        taxi_exp_client, gen_func, init_func, update_func, get_func, source,
):
    # init experiments with same names
    for idx, namespace in enumerate(NAMESPACES, 1):
        experiment_body = gen_func(name=EXPERIMENT, last_modified_at=idx)
        await init_func(taxi_exp_client, experiment_body, namespace=namespace)
    # confirm successful initialization
    for idx, namespace in enumerate(NAMESPACES, 1):
        resp_body = await get_func(
            taxi_exp_client, name=EXPERIMENT, namespace=namespace,
        )
        assert resp_body['last_modified_at'] == idx
    # check revisions do not overlap
    for idx, namespace in enumerate(NAMESPACES, 1):
        params = {'name': EXPERIMENT}
        if namespace is not None:
            params['tplatform_namespace'] = namespace
        response = await taxi_exp_client.get(
            f'/v1/{source}/revisions/',
            headers={'X-Ya-Service-Ticket': '123'},
            params=params,
        )
        resp_body = await response.json()
        assert len(resp_body['revisions']) == 1
