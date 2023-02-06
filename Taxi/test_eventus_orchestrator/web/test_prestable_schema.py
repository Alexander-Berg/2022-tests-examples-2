import pytest

from .. import pipeline_tools


async def _make_failed_schema_get(
        taxi_eventus_orchestrator_web, expected_status,
):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline/schema',
        params={'instance_name': 'order-events-producer'},
    )

    assert response.status == expected_status

    req_json = pipeline_tools.get_test_pipeline_to_put(0, 'create')
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-order-events',
        },
        json=req_json,
        headers={'X-YaTaxi-Draft-Id': 'asdad'},
    )

    assert response.status == expected_status

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-order-events',
        },
        json=req_json,
        headers={'X-YaTaxi-Draft-Id': 'asdad'},
    )

    assert response.status == expected_status


@pytest.mark.filldb(eventus_instances='empty')
async def test_no_instances(taxi_eventus_orchestrator_web):
    await _make_failed_schema_get(taxi_eventus_orchestrator_web, 404)


@pytest.mark.filldb(eventus_instances='no_nanny_id')
async def test_no_nanny_service_id(taxi_eventus_orchestrator_web):
    await _make_failed_schema_get(taxi_eventus_orchestrator_web, 500)


@pytest.mark.filldb(
    eventus_instances='no_schema_for_prestable_host',
    eventus_pipeline_schemas='no_schema_for_prestable_host',
)
async def test_no_schema_for_pre_host(taxi_eventus_orchestrator_web):
    await _make_failed_schema_get(taxi_eventus_orchestrator_web, 500)


@pytest.mark.filldb(
    eventus_instances='no_prestable', eventus_pipeline_schemas='no_prestable',
)
async def test_get_schema_testing(taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline/schema',
        params={'instance_name': 'order-events-producer'},
    )

    assert response.status == 200
    body = await response.json()
    assert body == {
        'main_version': {
            'customs': [],
            'filters': [],
            'mappers': [
                {
                    'argument_schemas': [
                        {
                            'default_value': 'enum_value_1',
                            'description': (
                                'Set ' 'timestamp ' 'destination ' 'key 0'
                            ),
                            'enum_values': [
                                'enum_value_1',
                                'enum_value_2',
                                'enum_value_3',
                            ],
                            'is_required': True,
                            'name': 'dst_key_0',
                            'type': 'string',
                        },
                    ],
                    'description': 'Add now timestamp 0',
                    'name': 'add_timestamp_0',
                },
            ],
            'sinks': [
                {
                    'argument_schemas': [],
                    'description': 'Sink 0',
                    'name': 'sink_0',
                },
            ],
            'sources': [
                {
                    'argument_schemas': [],
                    'description': 'Source 0',
                    'name': 'source_name_0',
                },
            ],
        },
    }


@pytest.mark.filldb(
    eventus_instances='with_prestable',
    eventus_pipeline_schemas='with_prestable',
)
async def test_get_schema_prod(taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline/schema',
        params={'instance_name': 'order-events-producer'},
    )

    assert response.status == 200
    body = await response.json()
    assert body == {
        'main_version': {
            'customs': [],
            'filters': [],
            'mappers': [
                {
                    'argument_schemas': [
                        {
                            'default_value': 'enum_value_1',
                            'description': (
                                'Set ' 'timestamp ' 'destination ' 'key 0'
                            ),
                            'enum_values': [
                                'enum_value_1',
                                'enum_value_2',
                                'enum_value_3',
                            ],
                            'is_required': True,
                            'name': 'dst_key_66',
                            'type': 'string',
                        },
                    ],
                    'description': 'Add now timestamp 0',
                    'name': 'add_timestamp_66',
                },
            ],
            'sinks': [
                {
                    'argument_schemas': [],
                    'description': 'Sink 66',
                    'name': 'sink_66',
                },
            ],
            'sources': [
                {
                    'argument_schemas': [],
                    'description': 'Source 66',
                    'name': 'source_name_66',
                },
            ],
        },
        'prestable_version': {
            'customs': [],
            'filters': [],
            'mappers': [
                {
                    'argument_schemas': [
                        {
                            'default_value': 'enum_value_1',
                            'description': (
                                'Set ' 'timestamp ' 'destination ' 'key ' '0'
                            ),
                            'enum_values': [
                                'enum_value_1',
                                'enum_value_2',
                                'enum_value_3',
                            ],
                            'is_required': True,
                            'name': 'dst_key_0',
                            'type': 'string',
                        },
                    ],
                    'description': 'Add now timestamp 0',
                    'name': 'add_timestamp_0',
                },
            ],
            'sinks': [
                {
                    'argument_schemas': [],
                    'description': 'Sink 0',
                    'name': 'sink_0',
                },
            ],
            'sources': [
                {
                    'argument_schemas': [],
                    'description': 'Source 0',
                    'name': 'source_name_0',
                },
            ],
        },
    }


def _get_pipeline(i: int, operation_args: dict, for_prestable: bool):
    return {
        'new_value': {
            'description': f'pipeline description 0',
            'st_ticket': 'ticket',
            'is_disabled': False,
            'source': {'name': f'source_name_{i}', 'arguments': {}},
            'root': {
                'operations': [
                    {
                        'name': f'mapper_{i}',
                        'operation_variant': {
                            'operation_name': f'add_timestamp_{i}',
                            'type': 'mapper',
                            'arguments': operation_args,
                        },
                    },
                ],
                'output': {'sink_name': f'sink_{i}', 'arguments': {}},
            },
        },
        'for_prestable': for_prestable,
        'action': 'create',
    }


async def _make_update_reqs(
        taxi_eventus_orchestrator_web, i_for_name, req_body, expected_status,
):
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': f'test-order-events-{i_for_name}',
        },
        json=req_body,
        headers={'X-YaTaxi-Draft-Id': 'asdad'},
    )

    assert response.status == expected_status

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': f'test-order-events-{i_for_name}',
        },
        json=req_body,
        headers={'X-YaTaxi-Draft-Id': 'asdad'},
    )

    assert response.status == expected_status


@pytest.mark.filldb(
    eventus_instances='no_prestable', eventus_pipeline_schemas='no_prestable',
)
@pytest.mark.parametrize(
    'i_for_nodes,args_for_mapper,'
    'for_prestable,i_for_pipeline_name,expected_status',
    [
        (0, {'dst_key_0': 'enum_value_1'}, False, 0, 200),
        (1, {'dst_key': 'enum_value_1'}, False, 1, 400),
    ],
)
async def test_check_and_update_testing(
        taxi_eventus_orchestrator_web,
        i_for_nodes,
        args_for_mapper,
        for_prestable,
        i_for_pipeline_name,
        expected_status,
):
    req = _get_pipeline(i_for_nodes, args_for_mapper, for_prestable)
    await _make_update_reqs(
        taxi_eventus_orchestrator_web,
        i_for_pipeline_name,
        req,
        expected_status,
    )


@pytest.mark.filldb(
    eventus_instances='with_prestable',
    eventus_pipeline_schemas='with_prestable',
)
@pytest.mark.parametrize(
    'i_for_nodes,args_for_mapper,'
    'for_prestable,i_for_pipeline_name,expected_status',
    [
        (0, {'dst_key_0': 'enum_value_1'}, True, 0, 200),
        (1, {'dst_key': 'enum_value_1'}, True, 1, 400),
        (66, {'dst_key': 'enum_value_1'}, True, 1, 400),
    ],
)
async def test_check_and_update_prod_prestable(
        taxi_eventus_orchestrator_web,
        i_for_nodes,
        args_for_mapper,
        for_prestable,
        i_for_pipeline_name,
        expected_status,
):
    req = _get_pipeline(i_for_nodes, args_for_mapper, for_prestable)
    await _make_update_reqs(
        taxi_eventus_orchestrator_web,
        i_for_pipeline_name,
        req,
        expected_status,
    )


@pytest.mark.filldb(
    eventus_instances='with_prestable',
    eventus_pipeline_schemas='with_prestable',
)
@pytest.mark.parametrize(
    'i_for_nodes,args_for_mapper,'
    'for_prestable,i_for_pipeline_name,expected_status',
    [
        (66, {'dst_key_66': 'enum_value_1'}, False, 0, 200),
        (77, {'dst_key_77': 'enum_value_1'}, False, 1, 400),
        (0, {'dst_key_0': 'enum_value_1'}, False, 1, 400),
    ],
)
async def test_check_and_update_prod_stable(
        taxi_eventus_orchestrator_web,
        i_for_nodes,
        args_for_mapper,
        for_prestable,
        i_for_pipeline_name,
        expected_status,
):
    req = _get_pipeline(i_for_nodes, args_for_mapper, for_prestable)
    await _make_update_reqs(
        taxi_eventus_orchestrator_web,
        i_for_pipeline_name,
        req,
        expected_status,
    )
