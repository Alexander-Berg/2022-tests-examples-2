import copy

import pytest


def _create_pipelines_config_all_kinds():
    # FIXME: move that into static folder and load via json.load()
    # but currently there need for some investigate how it proceed for
    # sql presets
    fanout = {
        'outputs': [
            {
                'operations': [
                    {
                        'name': 'only-damnthing',
                        'operation_variant': {
                            'operation_name': 'string_equal',
                            'type': 'mapper',
                            'arguments': {
                                'key_name': 'damnthing',
                                'key_name_2': 'damnthing',
                            },
                        },
                    },
                ],
                'output': {'sink_name': 'log_event_sink'},
            },
            {'sink_name': 'log_event_sink'},
            {'sink_name': 'log_event_sink_2'},
        ],
    }
    add_proc_timestamp = {
        'operations': [
            {
                'name': 'add-proc-timestamp',
                # no disabled, used False by default
                'operation_variant': {
                    'operation_name': 'set_proc_timestamp',
                    'type': 'mapper',
                },
            },
        ],
        'output': {
            'sink_name': 'log_event_sink',
            'arguments': {
                'arg0': 123,
                'arg1': 123.5,
                'arg2': 'hgjhj',
                'arg3': ['asd', 'dfg', 'ghj'],
                'arg4': [12, 22, 222.2],
                'arg5': True,
                'arg6': [True, False, True],
            },
        },
    }
    filters_disjunction = {
        'filters': [
            {
                'operation_name': 'string_equal',
                'type': 'filter',
                'arguments': {
                    'arg1': 'extra.fleep_ship',
                    'arg2': 'icebreaker',
                },
            },
            {
                'operation_name': 'string_equal',
                'type': 'filter',
                'arguments': {
                    'arg1': 'icebreaker',
                    'arg2': 'extra.fleep_ship',
                },
            },
        ],
    }
    switch_operation = {
        'operations': [
            {
                'name': 'op-switch-operation',
                'operation_variant': {
                    'operation_name': 'set_string_value',
                    'type': 'mapper',
                    'options': [
                        {
                            'filters': [
                                {
                                    'operation_name': 'string_equal',
                                    'type': 'filter',
                                    'arguments': {
                                        'arg1': 'key_trigger',
                                        'source': 'need_a_strong_ship',
                                    },
                                },
                            ],
                            'arguments': {
                                'value1': 'extra.fleet_ship',
                                'value2': 'icebreaker',
                            },
                        },
                        {
                            'filters': [],
                            'arguments': {
                                'value1': 'extra.fleet_ship',
                                'value2': 'icebreaker',
                            },
                        },
                    ],
                },
            },
        ],
        'output': {
            'outputs': [
                fanout,
                {
                    'operations': [
                        {
                            'name': 'only-icebreaker',
                            'operation_variant': filters_disjunction,
                        },
                    ],
                    'output': {'sink_name': 'log_event_sink'},
                },
                {
                    'operations': [
                        {
                            'name': 'only-damnthing',
                            'operation_variant': {
                                'operation_name': 'string_equal',
                                'type': 'filter',
                                'arguments': {
                                    'value2': 'extra.fleep_ship',
                                    'value3': 'damnthing',
                                    'key_name': 'damnthing',
                                    'key_name_next': '1234',
                                },
                            },
                        },
                    ],
                    'output': {'sink_name': 'log_event_sink'},
                },  # operartion_node
            ],
        },  # output_variant
    }  # operation_node
    return [
        {
            'name': 'all-kinds-test-test',
            'is_disabled': False,
            'source': {'name': 'communal-events'},
            'root': {
                'operations': [
                    {
                        'name': 'add-seq-num',
                        'is_disabled': False,
                        'operation_variant': {
                            'operation_name': 'set_seq_num',
                            'type': 'mapper',
                        },
                        'error_handling_policy': {
                            'retry_policy': {'attempts': 5},
                        },
                    },
                    {
                        'name': 'add-seq-num-1',
                        'is_disabled': False,
                        'operation_variant': {
                            'operation_name': 'set_seq_num_1',
                            'type': 'mapper',
                        },
                        'error_handling_policy': {
                            'retry_policy': {'attempts': 4},
                        },
                    },
                    {
                        'name': 'add-seq-num-2',
                        'is_disabled': False,
                        'operation_variant': {
                            'operation_name': 'set_seq_num_2',
                            'type': 'mapper',
                        },
                        'error_handling_policy': {
                            'retry_policy': {'attempts': 2},
                        },
                    },
                    {
                        'name': 'add-seq-num-3',
                        'is_disabled': False,
                        'operation_variant': {
                            'operation_name': 'set_seq_num_3',
                            'type': 'mapper',
                        },
                        'error_handling_policy': {
                            'retry_policy': {'attempts': 1},
                        },
                    },
                ],
                'output': {
                    'outputs': [
                        {'sink_name': 'log_event_sink'},
                        add_proc_timestamp,
                        switch_operation,
                    ],  # outputs
                },  # output_variant
            },  # output_variant
        },  # pipeline
    ]


def _add_default_policy(policy):
    if 'retry_policy' not in policy:
        policy['retry_policy'] = {}
    if 'action_after_erroneous_execution' not in policy:
        policy['action_after_erroneous_execution'] = 'propagate'
    if 'erroneous_statistics_level' not in policy:
        policy['erroneous_statistics_level'] = 'error'

    retry_policy = policy['retry_policy']
    if 'attempts' not in retry_policy:
        retry_policy['attempts'] = 1
    if 'min_delay' not in retry_policy:
        retry_policy['min_delay'] = 0
    if 'max_delay' not in retry_policy:
        retry_policy['max_delay'] = 2000000000
    if 'delay_factor' not in retry_policy:
        retry_policy['delay_factor'] = 1


def _add_disabled(config):
    if 'root' in config or 'operation_variant' in config:
        if 'is_disabled' not in config:
            config['is_disabled'] = False


def _add_number_of_threads(config):
    if 'root' in config:
        if 'number_of_threads' not in config:
            config['number_of_threads'] = 3


def _add_empty_args(config):
    if 'operation_name' in config and 'options' not in config:
        if 'arguments' not in config:
            config['arguments'] = {}

    if 'sink_name' in config:
        if 'arguments' not in config:
            config['arguments'] = {}

    if 'options' in config:
        for opt in config['options']:
            if 'arguments' not in opt:
                opt['arguments'] = {}


def _add_default_fields_and_fix_args(config):
    if isinstance(config, list):
        for elem in config:
            _add_default_fields_and_fix_args(elem)
    elif isinstance(config, dict):
        _add_disabled(config)
        _add_empty_args(config)
        _add_number_of_threads(config)

        for key, val in config.items():
            if key == 'error_handling_policy':
                _add_default_policy(val)
            else:
                _add_default_fields_and_fix_args(val)


def _replace_op_lists_with_linked_nodes(config):
    if isinstance(config, list):
        for elem in config:
            _replace_op_lists_with_linked_nodes(elem)
    elif isinstance(config, dict) and 'operations' in config:
        _replace_op_lists_with_linked_nodes(config['output'])
        outp = config['output']
        for operation in reversed(config['operations']):
            op_node = copy.deepcopy(operation)
            op_node['output'] = outp
            outp = op_node
        config.clear()
        config.update(outp)
    elif isinstance(config, dict):
        for _, elem in config.items():
            _replace_op_lists_with_linked_nodes(elem)


def _get_expected_result(pipelines_config):
    config_copy = copy.deepcopy(pipelines_config)
    _add_default_fields_and_fix_args(config_copy)
    _replace_op_lists_with_linked_nodes(config_copy)
    return config_copy


@pytest.mark.parametrize('number_of_threads', [1, 3, 7, 12])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_all_kind_pipelines(
        taxi_eventus_sample,
        testpoint,
        taxi_eventus_orchestrator_mock,
        number_of_threads,
):
    @testpoint('eventus_orchestrator_config::updated')
    def eventus_orchestrator_config(data):
        pass

    to_set = _create_pipelines_config_all_kinds()
    if number_of_threads != 3:
        to_set[0]['number_of_threads'] = number_of_threads

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, to_set, 10, False,
    )

    await taxi_eventus_sample.enable_testpoints()
    await taxi_eventus_sample.invalidate_caches()

    eventus_orchestrator_config.flush()

    await taxi_eventus_sample.run_task('eventus-orch-cfg-update')

    pipelines_from_oep = (await eventus_orchestrator_config.wait_call())[
        'data'
    ]

    assert pipelines_from_oep == _get_expected_result(to_set)
