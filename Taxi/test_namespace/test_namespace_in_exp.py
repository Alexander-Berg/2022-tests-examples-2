import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,verb_init_func,update_func,get_func,restore_func',
    [
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.verbose_init_exp_by_draft,
            helpers.update_exp_by_draft,
            helpers.get_experiment,
            helpers.restore_experiment,
            id='create_update_exp_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            None,
            helpers.update_exp,
            helpers.get_experiment,
            helpers.restore_experiment,
            id='create_update_exp_with_namespace_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.verbose_init_config_by_draft,
            helpers.update_config_by_draft,
            helpers.get_config,
            helpers.restore_config,
            id='create_update_config_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            None,
            helpers.update_config,
            helpers.get_config,
            helpers.restore_config,
            id='create_update_config_with_namespace_direct',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_update_exp_with_namespace(
        taxi_exp_client,
        gen_func,
        init_func,
        verb_init_func,
        update_func,
        get_func,
        restore_func,
):
    # attempt to create exp in wrong namespace
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, namespace='market', last_modified_at=1,
    )
    if verb_init_func:
        response_body = await verb_init_func(
            taxi_exp_client, experiment_body, namespace='not_market',
        )
    else:
        response = await init_func(
            taxi_exp_client,
            experiment_body,
            namespace='not_market',
            raw_answer=True,
        )
        assert response.status == 400
        response_body = await response.json()
    assert response_body == {
        'code': 'ADD_TO_DIFFERENT_NAMESPACE',
        'message': (
            'Query namespace and experiment body namespace are not equal'
        ),
    }

    # init exp in namespace
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        namespace=None,
        last_modified_at=1,
        description='old',
        service_id=123456,
    )

    response_body = await init_func(
        taxi_exp_client, experiment_body, namespace='market',
    )

    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['namespace'] == 'market'
    assert response_body['service_id'] == 123456

    # attempt to change namespace

    experiment_body['namespace'] = 'not_market'

    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True, namespace='market',
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'ATTEMPT_NAMESPACE_CHANGE',
        'message': (
            'Namespace field cannot be changed '
            'for an existing experiment/config'
        ),
    }

    # attempt to update with wrong namespace

    experiment_body['namespace'] = 'market'

    response = await update_func(
        taxi_exp_client,
        experiment_body,
        raw_answer=True,
        namespace='not_market',
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'ATTEMPT_NAMESPACE_CHANGE',
        'message': (
            'Namespace field cannot be changed '
            'for an existing experiment/config'
        ),
    }

    # attempt to update in wrong namespace

    experiment_body['namespace'] = 'not_market'

    response = await update_func(
        taxi_exp_client,
        experiment_body,
        raw_answer=True,
        namespace='not_market',
    )
    assert response.status == 404

    # attempt to reset namespace (success but no changes to namespace)

    response_body = await get_func(
        taxi_exp_client, EXPERIMENT_NAME, namespace='market',
    )

    experiment_body.pop('namespace')

    await update_func(taxi_exp_client, experiment_body, namespace='market')

    # check that nothing changed

    response_body = await get_func(
        taxi_exp_client, EXPERIMENT_NAME, namespace='market',
    )

    assert response_body['last_modified_at'] == 2
    assert response_body['namespace'] == 'market'
    assert response_body['service_id'] == 123456

    # update with correct parameters

    experiment_body['namespace'] = 'market'
    experiment_body['last_modified_at'] = 2
    experiment_body['description'] = 'new'

    response_body = await update_func(
        taxi_exp_client, experiment_body, namespace='market',
    )

    assert response_body['last_modified_at'] == 3
    assert response_body['namespace'] == 'market'
    assert response_body['description'] == 'new'
    assert response_body['service_id'] == 123456

    response = await restore_func(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=3,
        revision=2,
        namespace='market',
    )
    assert response.status == 200
    response_body = await get_func(
        taxi_exp_client, EXPERIMENT_NAME, namespace='market',
    )
    assert response_body['last_modified_at'] == 4
    assert response_body['description'] == 'old'
    assert response_body['service_id'] == 123456
