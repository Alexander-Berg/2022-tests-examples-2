import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,verb_init_func,update_func',
    [
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.verbose_init_exp_by_draft,
            helpers.update_exp_by_draft,
            id='create_update_exp_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            None,
            helpers.update_exp,
            id='create_update_exp_with_namespace_direct',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.verbose_init_config_by_draft,
            helpers.update_config_by_draft,
            id='create_update_config_with_namespace_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            None,
            helpers.update_config,
            id='create_update_config_with_namespace_direct',
        ),
    ],
)
@pytest.mark.parametrize(
    'use_id,service,wrong_namespace_service,non_existent_service',
    [
        pytest.param(True, 123456, 12345, 9001, id='by_service_id'),
        pytest.param(
            False,
            'service',
            'other_service',
            'different_service',
            id='by_service_name',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_service_not_in_namespace(
        taxi_exp_client,
        gen_func,
        init_func,
        verb_init_func,
        update_func,
        use_id,
        service,
        wrong_namespace_service,
        non_existent_service,
):
    # attempt to create exp in wrong namespace
    exp_kwargs = {'name': EXPERIMENT_NAME}
    if use_id:
        exp_kwargs['service_id'] = wrong_namespace_service
    else:
        exp_kwargs['service_name'] = wrong_namespace_service
    experiment_body = gen_func(**exp_kwargs)
    if verb_init_func:
        response_body = await verb_init_func(
            taxi_exp_client, experiment_body, namespace='market',
        )
    else:
        response = await init_func(
            taxi_exp_client,
            experiment_body,
            namespace='market',
            raw_answer=True,
        )
        assert response.status == 400
        response_body = await response.json()
    assert response_body == {
        'code': 'SERVICE_NOT_IN_NAMESPACE',
        'details': (
            'service id: 12345; provided namespace: market; '
            'actual namespace: not_market.'
        ),
        'message': 'Provided service does not belong to provided namespace',
    }

    # init exp in namespace
    if use_id:
        exp_kwargs['service_id'] = service
    else:
        exp_kwargs['service_name'] = service
    experiment_body = gen_func(**exp_kwargs)

    response_body = await init_func(
        taxi_exp_client, experiment_body, namespace='market',
    )

    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['namespace'] == 'market'
    assert response_body['service_id'] == 123456

    # change service to one that does not belong to namespace
    # on init and update
    if use_id:
        exp_kwargs['service_id'] = wrong_namespace_service
    else:
        exp_kwargs['service_name'] = wrong_namespace_service
    exp_kwargs['last_modified_at'] = 1
    experiment_body = gen_func(**exp_kwargs)

    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True, namespace='market',
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'SERVICE_NOT_IN_NAMESPACE',
        'details': (
            'service id: 12345; provided namespace: market; '
            'actual namespace: not_market.'
        ),
        'message': 'Provided service does not belong to provided namespace',
    }

    # change service_id to a wrong value
    if use_id:
        exp_kwargs['service_id'] = non_existent_service
    else:
        exp_kwargs['service_name'] = non_existent_service
    experiment_body = gen_func(**exp_kwargs)

    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True, namespace='market',
    )
    if use_id:
        assert response.status == 400
        assert (await response.json()) == {
            'code': 'WRONG_SERVICE_ID',
            'details': '9001',
            'message': (
                'Provided service_id does not refer to a service '
                'in clownductor'
            ),
        }
        return

    assert response.status == 400
    assert (await response.json()) == {
        'code': 'SERVICE_NOT_FOUND_BY_NAME',
        'message': 'Service with provided name is not found',
    }

    # test name and id not consistent
    exp_kwargs['service_id'] = 123456
    exp_kwargs['service_name'] = 'other_service'
    experiment_body = gen_func(**exp_kwargs)
    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True, namespace='market',
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'SERVICE_NAME_AND_ID_NOT_CONSISTENT',
        'details': (
            'service name: other_service; provided service_id: 123456; actual '
            'service_id: 12345.'
        ),
        'message': (
            'Id of the service with provided service_name is different from '
            'provided service_id'
        ),
    }

    # test correct update with service_name
    exp_kwargs.pop('service_id')
    exp_kwargs['service_name'] = 'service_to_test_search_1'
    experiment_body = gen_func(**exp_kwargs)
    response_body = await update_func(
        taxi_exp_client, experiment_body, namespace='market',
    )
    assert response_body['service_id'] == 1
