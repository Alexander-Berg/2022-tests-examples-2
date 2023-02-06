import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT = 'exp1'

NAMESPACES = ['market', 'not_market', None]


@pytest.mark.parametrize(
    'gen_func,init_func,on_off_func,get_func,updates_func,key',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.on_off_experiment,
            helpers.get_experiment,
            helpers.get_updates,
            'experiments',
            id='create_update_exp_with_namespace_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.on_off_config,
            helpers.get_config,
            helpers.get_configs_updates,
            'configs',
            id='create_update_config_with_namespace_direct',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {
                'departments': {'common': {'map_to_namespace': 'market'}},
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_on_off_with_namespace(
        taxi_exp_client,
        gen_func,
        init_func,
        on_off_func,
        get_func,
        updates_func,
        key,
):
    # init exp that will not be changed
    experiment_body = gen_func(name=EXPERIMENT)
    await init_func(taxi_exp_client, experiment_body, namespace='frozen')
    # init exps that will be turned off/on
    for idx, namespace in enumerate(NAMESPACES, 2):
        experiment_body = gen_func(name=EXPERIMENT, last_modified_at=idx)
        await init_func(taxi_exp_client, experiment_body, namespace=namespace)
    # turn exps off, then on
    for enable in (False, True):
        for idx, namespace in enumerate(NAMESPACES, 2):
            on_off_response = await on_off_func(
                taxi_exp_client,
                EXPERIMENT,
                idx + (3 if enable else 0),
                namespace=namespace,
                enable=enable,
            )
            resp_body = await get_func(taxi_exp_client, EXPERIMENT, namespace)
            if namespace is not None:
                assert 'tplatform_namespace' not in on_off_response
            else:
                assert on_off_response['tplatform_namespace'] == 'market'
            assert resp_body['match']['enabled'] == enable
            assert (
                resp_body['last_modified_at']
                == on_off_response['last_modified_at']
            )
    # attempt to turn off exp with wrong namespace
    response = await on_off_func(
        taxi_exp_client, EXPERIMENT, 1, enable=False, raw_answer=True,
    )
    assert response.status == 409
    # check that it was unchanged
    resp_body = await get_func(taxi_exp_client, EXPERIMENT, 'frozen')
    assert resp_body['last_modified_at'] == 1

    check_updates = (await updates_func(taxi_exp_client))[key]
    assert len(check_updates) == 4
