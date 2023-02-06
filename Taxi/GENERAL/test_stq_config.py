from stq import config

import ordered_object


def test_worker_config():
    NODE_ID = 'host_one'
    _STQ_AGENT_CONFIGS = {
        'processing': {
            'shards': [{'index': 4, 'worker_type': 'stq-agent'},
                       {'index': 5, 'worker_type': 'stq-agent'}, {'index': 6}],
            'shards_count': 10},
        'non_present_queue': {
            'shards': [],
            'shards_count': 2,
        }
    }

    config_obj = config.WorkerConfig(
        _STQ_AGENT_CONFIGS,
        {
            'processing': {
                'worker_param': 1,
                'task_function': 'some_function',
                'dbhandler_params': {'use_ng_handler': True},
            },
            'non_present_queue': {
                'task_function': 'some_function_2',
                'on_run_callback': 'some_function_3',
            },
        },
        common_shard_params={'agent_url': 'test_url'},
        host=NODE_ID,
    )

    ordered_object.assert_eq(
        config_obj.COMMON,
        {
            'queues': [{'queue': 'processing', 'shards': 10},
                       {'queue': 'non_present_queue', 'shards': 2}],
            'shards': [{'database': None, 'index': 4, 'params': {},
                        'queue': 'processing'},
                       {'database': None, 'index': 5, 'params': {},
                        'queue': 'processing'},
                       {'database': None,
                        'index': 6,
                        'params': {},
                        'queue': 'processing'}],
            'worker_nodes': [{'node_id': 'host_one',
                              'queues': [{'queue': 'processing',
                                          'shards': [{'index': 4},
                                                     {'index': 5},
                                                     {'index': 6}]}]}],
        },
        (
            'queues', 'shards', 'worker_nodes', 'worker_nodes.queues',
            'worker_nodes.queues.shards',
        ),
    )

    assert config_obj.WORKER == {
        'queues': {
            'non_present_queue': {'dbhandlers': {
                'backend': 'stq.server.dbhandlers.databases.stq_agent',
                'params': {
                    'dbhandler_params': {'use_ng_handler': True},
                    'stq_agent_init_params': {'agent_url': 'test_url'},
                }},
                'shards': {},
                'workers': {
                    'on_run_callback': 'some_function_3',
                    'task_function': 'some_function_2'}},
            'processing': {
                'dbhandlers': {
                    'backend': 'stq.server.dbhandlers.databases.stq_agent',
                    'params': {
                        'dbhandler_params': {'use_ng_handler': True},
                        'stq_agent_init_params': {'agent_url': 'test_url'},
                    }
                },
                'shards': {
                    4: {},
                    5: {},
                    6: {},
                },
                'workers': {'task_function': 'some_function',
                            'worker_param': 1}}},
    }
    wrapper = config.ConfigWrapper(config_obj, 'host_one')
    assert (wrapper.get_dbhandler_backend('non_present_queue') ==
            'stq.server.dbhandlers.databases.stq_agent')
    assert (wrapper.get_worker_task_function('non_present_queue') ==
            'some_function_2')
    assert (wrapper.get_worker_on_run_callback('non_present_queue') ==
            'some_function_3')
    assert (wrapper.get_dbhandler_common_params('non_present_queue') == {
            'dbhandler_params': {'use_ng_handler': True},
            'stq_agent_init_params': {'agent_url': 'test_url'}})
