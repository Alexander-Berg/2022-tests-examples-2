test_workers_stats_base = {
    'datetime': '2022-01-28T03:18:00+0000',
    'host': 'hostname',
    'total': {'cpu_used': {'value': 1.0}},
    'queues': [
        {
            'queue': 'sample_queue_test_workers_stats_py3_base',
            'stat': {'cpu_used': {'value': 1.0}},
        },
    ],
}

test_workers_stats_critical = {
    'datetime': '2022-01-28T03:18:00+0000',
    'host': 'hostname',
    'total': {'cpu_used': {'value': 2.0}},
    'queues': [
        {
            'queue': 'sample_queue_test_workers_stats_py3_critical_1',
            'stat': {'cpu_used': {'value': 1.0}},
        },
        {
            'queue': 'sample_queue_test_workers_stats_py3_critical_2',
            'stat': {'cpu_used': {'value': 1.0}},
        },
    ],
}

queues_configs = {
    'queues': [
        {
            'queue': 'sample_queue_test_workers_stats_py3_base',
            'shards_count': 1,
            'shards': [{'index': 0, 'max_tasks': 100}],
            'worker_configs': {
                'instances': 1,
                'max_tasks': 100,
                'max_execution_time': 100.0,
            },
            'cluster': 'stq-agent-base',
        },
        {
            'queue': 'sample_queue_test_workers_stats_py3_critical_1',
            'shards_count': 1,
            'shards': [{'index': 0, 'max_tasks': 100}],
            'worker_configs': {
                'instances': 1,
                'max_tasks': 100,
                'max_execution_time': 100.0,
            },
            'cluster': 'stq-agent-taxi-critical',
        },
        {
            'queue': 'sample_queue_test_workers_stats_py3_critical_2',
            'shards_count': 1,
            'shards': [{'index': 0, 'max_tasks': 100}],
            'worker_configs': {
                'instances': 1,
                'max_tasks': 100,
                'max_execution_time': 100.0,
            },
            'cluster': 'stq-agent-taxi-critical',
        },
    ],
}

workers_stat_object = {
    'type': 'object',
    'properties': {
        'cpu_used': {
            'type': 'object',
            'properties': {
                'value': {'type': 'number', 'minimum': 0, 'maximum': 100},
            },
            'required': ['value'],
            'minProperties': 1,
            'maxProperties': 1,
            'additionalProperties': False,
        },
    },
    'additionalProperties': False,
}

workers_stats_schema = {
    'type': 'object',
    'properties': {
        'host': {'type': 'string'},
        'datetime': {'type': 'string', 'format': 'date-time-iso-basic'},
        'total': workers_stat_object,
        'queues': {
            'type': 'array',
            'item': {
                'type': 'object',
                'properties': {
                    'queue': {'type': 'string'},
                    'stat': workers_stat_object,
                },
                'required': ['queue', 'stat'],
                'minProperties': 2,
                'maxProperties': 2,
                'additionalProperties': False,
            },
        },
    },
    'required': ['total', 'queues', 'datetime', 'host'],
    'maxProperties': 4,
    'minProperties': 4,
    'additionalProperties': False,
}

test_task_ids = {
    'base': {
        'task_id': 'test_workers_stats_task_id_base',
        'args': [],
        'kwargs': {},
        'exec_tries': 1,
        'reschedule_counter': 0,
        'eta': '2018-12-01T14:00:01.123456Z',
    },
    'critical_1': {
        'task_id': 'test_workers_stats_task_id_critical_2',
        'args': [],
        'kwargs': {},
        'exec_tries': 1,
        'reschedule_counter': 0,
        'eta': '2018-12-01T14:00:01.123456Z',
    },
    'critical_2': {
        'task_id': 'test_workers_stats_task_id_critical_2',
        'args': [],
        'kwargs': {},
        'exec_tries': 1,
        'reschedule_counter': 0,
        'eta': '2018-12-01T14:00:01.123456Z',
    },
}
