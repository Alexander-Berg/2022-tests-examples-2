import eventus_orchestrator.generated.service.swagger.models.api as gen_api


def get_test_pipeline(pipeline_name, with_pipeline_add_info=True):
    arg_map_test = gen_api.ArgumentsMap(
        {
            'field_1': 'field_value',
            'field_2': 'field_value_2',
            'field_3': True,
        },
    )
    source_arg_map = gen_api.ArgumentsMap(
        {
            'field_1': 'field_value',
            'field_10': [12.1, 666, 222],
            'field_11': [True, False, True],
            'field_2': 'field_value_2',
            'field_3': True,
            'field_5': 12.1,
            'field_6': 122,
            'field_7': ['asd_', 'edfg_1', 'asdaaa=1фывфывф'],
            'field_8': [12, 11, 2],
            'field_9': [12.1, 11.1, 2.3],
        },
    )
    retry_policy = gen_api.RetryPolicy(
        attempts=3, min_delay_ms=10, max_delay_ms=50, delay_factor=2,
    )

    error_handling_policy = gen_api.ErrorHandlingPolicy(
        retry_policy=retry_policy,
        action_after_erroneous_execution='propagate',
    )
    error_policy_wo_action = gen_api.ErrorHandlingPolicy(
        retry_policy=retry_policy,
    )
    error_policy_wo_retry = gen_api.ErrorHandlingPolicy(
        action_after_erroneous_execution='propagate',
    )
    error_policy_with_err_level = gen_api.ErrorHandlingPolicy(
        retry_policy=retry_policy,
        action_after_erroneous_execution='propagate',
        erroneous_statistics_level='error',
    )
    error_policy_with_warn_level = gen_api.ErrorHandlingPolicy(
        retry_policy=retry_policy,
        action_after_erroneous_execution='propagate',
        erroneous_statistics_level='warning',
    )

    sink_1 = gen_api.Sink(sink_name='sink_name_1')
    sink_2 = gen_api.Sink(
        sink_name='sink_name_2',
        arguments=arg_map_test,
        error_handling_policy=error_policy_with_err_level,
    )

    operation_66 = gen_api.Operation(
        operation_name='filter_name_66', type='mapper', arguments=arg_map_test,
    )
    operation_67 = gen_api.Operation(
        operation_name='filter_name_67', type='mapper', arguments=arg_map_test,
    )
    operation_for_group_1 = gen_api.OperationNodeBody(
        name='filter_66',
        is_disabled=False,
        operation_variant=operation_66,
        error_handling_policy=error_handling_policy,
    )
    operation_for_group_2 = gen_api.OperationNodeBody(
        name='filter_67',
        is_disabled=False,
        operation_variant=operation_67,
        error_handling_policy=error_handling_policy,
    )
    named_op_list = gen_api.NamedOperationList(
        name='named_operation_list_1',
        operations=[operation_for_group_1, operation_for_group_2],
    )

    filter_1 = gen_api.Operation(
        operation_name='filter_name_1', type='filter', arguments=arg_map_test,
    )
    filter_2 = gen_api.Operation(
        operation_name='filter_name_2', type='filter', arguments=arg_map_test,
    )
    filters_disjunction = gen_api.FiltersDisjunction(
        filters=[filter_1, filter_2],
    )
    node_body_3 = gen_api.OperationNodeBody(
        name='filters_disjunction',
        is_disabled=False,
        operation_variant=filters_disjunction,
        error_handling_policy=error_policy_wo_retry,
    )

    operation_list_3 = gen_api.OperationList(
        operations=[node_body_3, named_op_list], output=sink_1,
    )

    filter_3 = gen_api.Operation(
        operation_name='filter_name_3', type='filter', arguments=arg_map_test,
    )
    filter_4 = gen_api.Operation(
        operation_name='filter_name_4', type='filter', arguments=arg_map_test,
    )

    switch_item_1 = gen_api.SwitchOperationItem(filters=[filter_1, filter_2])
    switch_item_2 = gen_api.SwitchOperationItem(
        arguments=arg_map_test, filters=[filter_3, filter_4],
    )
    switch_operation = gen_api.SwitchOperation(
        operation_name='mapper_name_1',
        type='mapper',
        options=[switch_item_1, switch_item_2],
    )
    node_body_4 = gen_api.OperationNodeBody(
        name='switch_operation',
        is_disabled=False,
        operation_variant=switch_operation,
        error_handling_policy=error_policy_with_warn_level,
    )

    operation_list_2 = gen_api.OperationList(
        operations=[node_body_4], output=sink_2,
    )

    fanout = gen_api.FanOut([operation_list_3, operation_list_2])

    operation_2 = gen_api.Operation(
        operation_name='filter_name', type='mapper', arguments=arg_map_test,
    )
    node_body_2 = gen_api.OperationNodeBody(
        name='filter_1',
        is_disabled=False,
        operation_variant=operation_2,
        error_handling_policy=error_policy_wo_action,
    )

    operation_1 = gen_api.Operation(
        operation_name='mapper_name', type='mapper',
    )
    node_body_1 = gen_api.OperationNodeBody(
        name='mapper_1', operation_variant=operation_1,
    )

    operation_list_1 = gen_api.OperationList(
        operations=[node_body_1, node_body_2], output=fanout,
    )

    add_info = {}
    if with_pipeline_add_info:
        add_info = {'is_disabled': False}

    pipeline = gen_api.PipelineConfiguration(
        **add_info,
        description='description',
        st_ticket='st_ticket',
        source=gen_api.Source(
            name=pipeline_name,
            arguments=(source_arg_map if with_pipeline_add_info else None),
        ),
        root=operation_list_1,
    )

    return pipeline.serialize()


def add_thread_num(pipeline, thread_num=3):
    pipeline['number_of_threads'] = thread_num


def get_test_pipeline_to_put(i, action):
    pipeline_json = {
        'new_value': {
            'description': f'pipeline description {i}',
            'st_ticket': 'ticket',
            'is_disabled': False,
            'source': {'name': f'source_name_{i}', 'arguments': {}},
            'root': {
                'sink_name': f'sink_{i}',
                'arguments': {},
                'error_handling_policy': {
                    'action_after_erroneous_execution': 'propagate',
                    'erroneous_statistics_level': 'error',
                    'retry_policy': {
                        'attempts': 1,
                        'min_delay_ms': 1,
                        'max_delay_ms': 10,
                        'delay_factor': 1,
                    },
                },
            },
        },
        'for_prestable': False,
        'action': action,
    }
    return pipeline_json


def get_schema_for_pipeline_to_put(i):
    return {
        'mappers': [],
        'filters': [],
        'customs': [],
        'sources': [
            {
                'name': f'source_name_{i}',
                'description': '',
                'argument_schemas': [],
            },
        ],
        'sinks': [
            {'name': f'sink_{i}', 'description': '', 'argument_schemas': []},
        ],
    }


async def update_schema_for_test(i, taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.put(
        '/v1/eventus/pipeline/schema',
        params={'instance_name': 'order-events-producer'},
        json={
            'schema': get_schema_for_pipeline_to_put(i),
            'build_version': '0.0.0',
            'hostname': 'asdfgvvvv.man.yp-c.yandex.net',
        },
    )
    assert response.status == 200


async def insert_new_version(
        i,
        action,
        taxi_eventus_orchestrator_web,
        pipeline_name='test-pipeline',
):
    pipeline_json = get_test_pipeline_to_put(i, action)
    draft_id = f'draft_id_{i}'

    await update_schema_for_test(i, taxi_eventus_orchestrator_web)

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': pipeline_name,
        },
        json=pipeline_json,
        headers={'X-YaTaxi-Draft-Id': draft_id},
    )

    assert response.status == 200
