def get_oe_event(ev_id):
    return {
        'order_id': f'order_id_{ev_id}',
        'event_index': ev_id,
        'event_key': f'event_key_{ev_id}',
        'user_phone_id': f'user_phone_id_{ev_id}',
        'user_id': f'user_id_{ev_id}',
        'nz': f'nz_{ev_id}',
        'status_updated': 1571253356.368,
        'field_test_1': 'asdasd',
        'field_test_2': 'asdasdasd',
    }


def get_oep_pipelines_config(pipelines):
    return {'pipelines': pipelines}


def get_oe_pipeline(
        sink_name,
        switch_options,
        pipeline_name=None,
        add_ops_before_sink=None,
        sink_arguments=None,
):
    if add_ops_before_sink is None:
        add_ops_before_sink = []
    if sink_arguments is None:
        sink_arguments = []

    return {
        'name': (
            'order-events_' + sink_name
            if pipeline_name is None
            else pipeline_name
        ),
        'operation_list': [
            {
                'name': 'add-proc-timestamp',
                'operation': {
                    'operation': {
                        'arguments': [],
                        'operation_name': 'set_proc_timestamp',
                        'type': 'mapper',
                    },
                },
            },
            {
                'name': 'set-polygon-groups',
                'operation': {
                    'operation': {
                        'arguments': [],
                        'operation_name': 'set_polygon_groups',
                        'type': 'mapper',
                    },
                },
            },
            {
                'name': 'switch',
                'operation': {
                    'switch_operation': {
                        'operation_name': 'set_json_value',
                        'options': switch_options,
                        'type': 'mapper',
                    },
                },
            },
            {
                'name': 'filter-after-switch',
                'operation': {
                    'operation': {
                        'arguments': [
                            {'name': 'key', 'value': 'event.filtered_out'},
                            {'name': 'policy', 'value': 'key_not_exists'},
                        ],
                        'operation_name': 'field_check',
                        'type': 'filter',
                    },
                },
            },
            {
                'name': 'set-uuid',
                'operation': {
                    'operation': {
                        'type': 'mapper',
                        'arguments': [
                            {'name': 'from', 'value': 'driver_id'},
                            {'name': 'to', 'value': 'uuid'},
                            {'name': 'separator', 'value': '_'},
                            {'name': 'fetch_index', 'value': 1},
                            {'name': 'expect_count', 'value': 2},
                        ],
                        'operation_name': 'split_string_and_fetch',
                    },
                },
            },
            {
                'name': 'set-event-type',
                'operation': {
                    'operation': {
                        'arguments': [
                            {'name': 'dst_key', 'value': 'event.type'},
                            {'name': 'value', 'value': 'order'},
                        ],
                        'operation_name': 'set_string_value',
                        'type': 'mapper',
                    },
                },
            },
            {
                'name': 'set-event-id',
                'operation': {
                    'operation': {
                        'arguments': [],
                        'operation_name': 'set_event_id',
                        'type': 'mapper',
                    },
                },
            },
            *add_ops_before_sink,
            {
                'name': 'out-to-sink',
                'operation': {
                    'output_to_sink': {
                        'name': sink_name,
                        'arguments': sink_arguments,
                    },
                },
            },
        ],
        'source': {'name': 'order-events'},
    }


def get_oe_pipeline_for_orch(
        sink_name,
        switch_options,
        pipeline_name=None,
        add_ops_before_sink=None,
        sink_arguments=None,
):
    if add_ops_before_sink is None:
        add_ops_before_sink = []
    if sink_arguments is None:
        sink_arguments = {}

    return {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {'sink_name': sink_name, 'arguments': sink_arguments},
            'operations': [
                {
                    'name': 'add-proc-timestamp',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_proc_timestamp',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-polygon-groups',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_polygon_groups',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'switch',
                    'operation_variant': {
                        'operation_name': 'set_json_value',
                        'options': switch_options,
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'filter-after-switch',
                    'operation_variant': {
                        'arguments': {
                            'key': 'event.filtered_out',
                            'policy': 'key_not_exists',
                        },
                        'operation_name': 'field_check',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'set-uuid',
                    'operation_variant': {
                        'type': 'mapper',
                        'arguments': {
                            'from': 'driver_id',
                            'to': 'uuid',
                            'separator': '_',
                            'fetch_index': 1,
                            'expect_count': 2,
                        },
                        'operation_name': 'split_string_and_fetch',
                    },
                },
                {
                    'name': 'set-event-type',
                    'operation_variant': {
                        'arguments': {
                            'dst_key': 'event.type',
                            'value': 'order',
                        },
                        'operation_name': 'set_string_value',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-event-id',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_event_id',
                        'type': 'mapper',
                    },
                },
                *add_ops_before_sink,
            ],
        },
        'name': (
            'order-events_' + sink_name
            if pipeline_name is None
            else pipeline_name
        ),
    }


def get_default_pipelines_config():
    return [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'communal-events'},
            'root': {
                'output': {'sink_name': 'log_sink'},
                'operations': [
                    {
                        'name': 'topic-filter',
                        'operation_variant': {
                            'arguments': {
                                'src': 'topic',
                                'match_with': '/topic/statistics',
                            },
                            'operation_name': 'string_equal',
                            'type': 'filter',
                        },
                    },
                    {
                        'name': 'add-seq-num',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_seq_num',
                            'type': 'mapper',
                        },
                    },
                    {
                        'name': 'add-proc-timestamp',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_proc_timestamp',
                            'type': 'mapper',
                        },
                    },
                ],
            },
            'name': 'communal-events//topic/statistics',
        },
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'communal-events'},
            'root': {
                'output': {'sink_name': 'log_sink'},
                'operations': [
                    {
                        'name': 'topic-filter',
                        'operation_variant': {
                            'arguments': {
                                'src': 'topic',
                                'match_with': 'smth',
                            },
                            'operation_name': 'string_equal',
                            'type': 'filter',
                        },
                    },
                    {
                        'name': 'add-seq-num',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_seq_num',
                            'type': 'mapper',
                        },
                    },
                    {
                        'name': 'add-proc-timestamp',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_proc_timestamp',
                            'type': 'mapper',
                        },
                    },
                ],
            },
            'name': 'communal-events/smth',
        },
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'cron-kd-drivers'},
            'root': {
                'output': {'sink_name': 'log_sink'},
                'operations': [
                    {
                        'name': 'add-seq-num',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_seq_num',
                            'type': 'mapper',
                        },
                    },
                    {
                        'name': 'add-proc-timestamp',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_proc_timestamp',
                            'type': 'mapper',
                        },
                    },
                ],
            },
            'name': 'cron-kd-drivers',
        },
    ]
