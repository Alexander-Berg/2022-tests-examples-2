import pytest


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_change_url(
        taxi_stq_dispatcher_sample, mockserver, testpoint, taxi_config,
):
    @mockserver.json_handler('/stq-agent/queues/config/')
    def _mock_fetch_configs_clear(request):
        return {'queues': []}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/mark_as_done',
    )
    def _mock_mark_done_critical(request):
        return {}

    @mockserver.json_handler('/other-stq-agent/queues/api/mark_as_done')
    def _mock_mark_done_other(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done_base(request):
        return {}

    @testpoint('queue-sample-done')
    def _mock_performer(request):
        return {}

    taxi_config.set_values(
        {
            'STQ_AGENT_CLUSTER_SETTINGS': {
                'other-stq-agent': {
                    'url': mockserver.url('/other-stq-agent'),
                    'tvm_name': 'other-stq-agent',
                },
                'stq-agent-taxi-critical': {
                    'url': mockserver.url('/stq-agent-taxi-critical'),
                    'tvm_name': 'stq-agent-taxi-critical',
                },
            },
        },
    )
    queue_name = 'sample_queue_done'
    base_config = {
        'queue': queue_name,
        'shards_count': 3,
        'shards': [{'index': 0, 'max_tasks': 100}],
        'worker_configs': {
            'instances': 1,
            'max_tasks': 100,
            'max_execution_time': 2.0,
        },
    }
    queue_config_critical = {
        'queues': [{**base_config, 'cluster': 'stq-agent-taxi-critical'}],
    }
    queue_config_other = {
        'queues': [{**base_config, 'cluster': 'other-stq-agent'}],
    }
    queue_config_base = {'queues': [base_config]}
    base_task = {
        'args': [],
        'kwargs': {},
        'exec_tries': 1,
        'reschedule_counter': 0,
    }
    some_task_1 = {**base_task, 'task_id': 'task_id_1'}
    some_task_2 = {**base_task, 'task_id': 'task_id_2'}
    some_task_3 = {**base_task, 'task_id': 'task_id_3'}
    should_send_task = False

    current_queue_config = queue_config_critical
    current_task = some_task_1

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/take')
    @mockserver.json_handler('/other-stq-agent/queues/api/take')
    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready_multiple(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == queue_name)
                and (request.json['shard_id'] == 0)
        ):
            should_send_task = False
            return {'tasks': [current_task]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return current_queue_config

    test_params = [
        [some_task_1, queue_config_critical, _mock_mark_done_critical],
        [some_task_2, queue_config_other, _mock_mark_done_other],
        [some_task_3, queue_config_base, _mock_mark_done_base],
    ]

    await taxi_stq_dispatcher_sample.invalidate_caches()
    for (task, queue_config, mock_handler) in test_params:
        current_queue_config = queue_config
        current_task = task
        await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')
        should_send_task = True
        await mock_handler.wait_call()
        await _mock_performer.wait_call()
