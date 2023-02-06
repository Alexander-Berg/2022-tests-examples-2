import copy

import pytest


def _get_pipeline_req_for_validation(action):
    arguments = {
        'field_1': 'field_value_2',
        'field_2': 12.1,
        'field_3': 12,
        'field_4': True,
        'field_5': ['asd_', 'edfg_1', 'asdaaa=1фывфывф'],
        'field_6': [12.1, 666, 222],
        'field_7': [True, False, True],
        'field_8': 'enum_value_1',
    }

    operation_list_1 = [
        {
            'name': 'mapper_1',
            'operation_variant': {
                'arguments': arguments,
                'operation_name': 'mapper_1',
                'type': 'mapper',
            },
        },
        {
            'name': 'filter_1',
            'operation_variant': {
                'arguments': arguments,
                'operation_name': 'filter_1',
                'type': 'filter',
            },
        },
        {
            'name': 'custom_1',
            'operation_variant': {
                'arguments': arguments,
                'operation_name': 'custom_1',
                'type': 'custom',
            },
        },
    ]

    named_operation_list = [
        {
            'is_disabled': False,
            'name': 'custom_2',
            'operation_variant': {
                'arguments': arguments,
                'operation_name': 'custom_2',
                'type': 'custom',
            },
        },
        {
            'is_disabled': False,
            'name': 'mapper_2',
            'operation_variant': {
                'arguments': arguments,
                'operation_name': 'mapper_2',
                'type': 'mapper',
            },
        },
    ]

    operation_list_2 = [
        {
            'error_handling_policy': {
                'action_after_erroneous_execution': 'propagate',
            },
            'is_disabled': False,
            'name': 'filters_disjunction',
            'operation_variant': {
                'filters': [
                    {
                        'arguments': arguments,
                        'operation_name': 'filter_2',
                        'type': 'filter',
                    },
                    {
                        'arguments': arguments,
                        'operation_name': 'filter_3',
                        'type': 'filter',
                    },
                ],
            },
        },
        {'name': 'named_operation_list_1', 'operations': named_operation_list},
    ]

    switch_operation = {
        'is_disabled': False,
        'name': 'switch_operation',
        'operation_variant': {
            'operation_name': 'mapper_3',
            'options': [
                {
                    'arguments': arguments,
                    'filters': [
                        {
                            'arguments': arguments,
                            'operation_name': 'filter_4',
                            'type': 'filter',
                        },
                        {
                            'arguments': arguments,
                            'operation_name': 'filter_5',
                            'type': 'filter',
                        },
                    ],
                },
                {
                    'arguments': arguments,
                    'filters': [
                        {
                            'arguments': arguments,
                            'operation_name': 'filter_6',
                            'type': 'filter',
                        },
                        {
                            'arguments': arguments,
                            'operation_name': 'filter_7',
                            'type': 'filter',
                        },
                    ],
                },
            ],
            'type': 'mapper',
        },
    }

    operation_list_3 = [switch_operation]

    return {
        'new_value': {
            'description': 'description',
            'is_disabled': False,
            'root': {
                'operations': operation_list_1,
                'output': {
                    'outputs': [
                        {
                            'operations': operation_list_2,
                            'output': {
                                'arguments': arguments,
                                'sink_name': 'sink_1',
                            },
                        },
                        {
                            'operations': operation_list_3,
                            'output': {
                                'arguments': arguments,
                                'sink_name': 'sink_2',
                            },
                        },
                    ],
                },
            },
            'source': {'arguments': arguments, 'name': 'source_1'},
            'st_ticket': 'st_ticket',
        },
        'action': action,
    }


def _get_correct_schema():
    argument_schemas = [
        {
            'name': 'field_1',
            'description': '',
            'type': 'string',
            'is_required': True,
        },
        {
            'name': 'field_2',
            'description': '',
            'type': 'number',
            'is_required': True,
        },
        {
            'name': 'field_3',
            'description': '',
            'type': 'number',
            'is_required': True,
        },
        {
            'name': 'field_4',
            'description': '',
            'type': 'bool',
            'is_required': True,
        },
        {
            'name': 'field_5',
            'description': '',
            'type': 'array_of_string',
            'is_required': True,
        },
        {
            'name': 'field_6',
            'description': '',
            'type': 'array_of_number',
            'is_required': True,
        },
        {
            'name': 'field_7',
            'description': '',
            'type': 'array_of_bool',
            'is_required': True,
        },
        {
            'name': 'field_8',
            'description': '',
            'type': 'string',
            'is_required': True,
            'enum_values': ['enum_value_1', 'enum_value_2', 'enum_value_3'],
        },
    ]

    return {
        'mappers': [
            {
                'name': f'mapper_{i}',
                'description': '',
                'argument_schemas': copy.deepcopy(argument_schemas),
            }
            for i in range(1, 4)
        ],
        'filters': [
            {
                'name': f'filter_{i}',
                'description': '',
                'argument_schemas': copy.deepcopy(argument_schemas),
            }
            for i in range(1, 8)
        ],
        'customs': [
            {
                'name': f'custom_{i}',
                'description': '',
                'argument_schemas': copy.deepcopy(argument_schemas),
            }
            for i in range(1, 3)
        ],
        'sources': [
            {
                'name': 'source_1',
                'description': '',
                'argument_schemas': copy.deepcopy(argument_schemas),
            },
        ],
        'sinks': [
            {
                'name': f'sink_{i}',
                'description': '',
                'argument_schemas': copy.deepcopy(argument_schemas),
            }
            for i in range(1, 3)
        ],
    }


_SCHEMA = _get_correct_schema()


async def _update_schema(schema, taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.put(
        '/v1/eventus/pipeline/schema',
        params={'instance_name': 'order-events-producer'},
        json={
            'schema': schema,
            'build_version': '0.0.0',
            'hostname': 'asdfgvvvv.man.yp-c.yandex.net',
        },
    )
    assert response.status == 200


async def _call_put_and_check(
        pipeline, taxi_eventus_orchestrator_web, expected_status,
):
    check_response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json=pipeline,
    )

    assert check_response.status == expected_status

    update_response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json=pipeline,
        headers={'X-YaTaxi-Draft-Id': 'draft_id_0'},
    )

    assert update_response.status == expected_status


async def test_correct_pipeline(taxi_eventus_orchestrator_web):
    await _update_schema(_get_correct_schema(), taxi_eventus_orchestrator_web)
    await _call_put_and_check(
        _get_pipeline_req_for_validation('create'),
        taxi_eventus_orchestrator_web,
        200,
    )


_OP_TYPES = ['mappers', 'filters', 'customs', 'sinks', 'sources']


def get_action(first_update):
    return 'create' if first_update else 'update'


async def test_without_operation_in_schema(taxi_eventus_orchestrator_web):
    for op_type in _OP_TYPES:
        for i in range(len(_SCHEMA[op_type])):
            schema_copy = copy.deepcopy(_SCHEMA)
            schema_copy[op_type][i]['name'] = 'unused'

            await _update_schema(schema_copy, taxi_eventus_orchestrator_web)
            await _call_put_and_check(
                _get_pipeline_req_for_validation('create'),
                taxi_eventus_orchestrator_web,
                400,
            )


async def test_without_required_arg(taxi_eventus_orchestrator_web):
    for op_type in _OP_TYPES:
        for i in range(len(_SCHEMA[op_type])):
            schema_copy = copy.deepcopy(_SCHEMA)
            new_arg = copy.deepcopy(
                schema_copy[op_type][i]['argument_schemas'][0],
            )
            new_arg['name'] = 'unused'
            schema_copy[op_type][i]['argument_schemas'].append(new_arg)

            await _update_schema(schema_copy, taxi_eventus_orchestrator_web)
            await _call_put_and_check(
                _get_pipeline_req_for_validation('create'),
                taxi_eventus_orchestrator_web,
                400,
            )


async def test_incorrect_arg_type(taxi_eventus_orchestrator_web):
    arg_replace_types = [
        'array_of_string',
        'string',
        'bool',
        'number',
        'array_of_number',
        'array_of_bool',
        'array_of_number',
        'number',
    ]

    for op_type in _OP_TYPES:
        for i in range(len(_SCHEMA[op_type])):
            for j in range(len(_SCHEMA[op_type][i]['argument_schemas'])):
                schema_copy = copy.deepcopy(_SCHEMA)
                schema_copy[op_type][i]['argument_schemas'][j][
                    'type'
                ] = arg_replace_types[j]

                await _update_schema(
                    schema_copy, taxi_eventus_orchestrator_web,
                )
                await _call_put_and_check(
                    _get_pipeline_req_for_validation('create'),
                    taxi_eventus_orchestrator_web,
                    400,
                )


async def test_incorrect_enum(taxi_eventus_orchestrator_web):
    for op_type in _OP_TYPES:
        for i in range(len(_SCHEMA[op_type])):
            schema_copy = copy.deepcopy(_SCHEMA)
            schema_copy[op_type][i]['argument_schemas'][7]['enum_values'] = [
                'enum_value_10',
                'enum_value_11',
                'enum_value_12',
            ]

            await _update_schema(schema_copy, taxi_eventus_orchestrator_web)
            await _call_put_and_check(
                _get_pipeline_req_for_validation('create'),
                taxi_eventus_orchestrator_web,
                400,
            )


@pytest.mark.config(EVENTUS_ORCHESTRATOR_DISABLE_VALIDATION=['some-instance'])
async def test_disable_validation(taxi_eventus_orchestrator_web):
    schema_copy = copy.deepcopy(_SCHEMA)
    schema_copy['mappers'][0]['name'] = 'unused'

    await _update_schema(schema_copy, taxi_eventus_orchestrator_web)
    await _call_put_and_check(
        _get_pipeline_req_for_validation('create'),
        taxi_eventus_orchestrator_web,
        400,
    )


@pytest.mark.config(
    EVENTUS_ORCHESTRATOR_DISABLE_VALIDATION=['order-events-producer'],
)
async def test_disable_validation_2(taxi_eventus_orchestrator_web):
    schema_copy = copy.deepcopy(_SCHEMA)
    schema_copy['mappers'][0]['name'] = 'unused'

    await _update_schema(schema_copy, taxi_eventus_orchestrator_web)
    await _call_put_and_check(
        _get_pipeline_req_for_validation('create'),
        taxi_eventus_orchestrator_web,
        200,
    )
