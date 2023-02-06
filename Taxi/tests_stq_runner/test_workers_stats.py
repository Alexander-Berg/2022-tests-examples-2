import jsonschema


import tests_stq_runner.definitions_workers_stats as defs


async def test_workers_stats(taxi_stq_runner, taxi_config, mockserver):
    def _value_is_normal(request_json):
        cpu_used_total = 0
        for queue in request_json['queues']:
            cpu_used = queue['stat']['cpu_used']['value']
            assert cpu_used >= 0
            cpu_used_total += cpu_used
        return cpu_used_total == request_json['total']['cpu_used']['value']

    taxi_config.set_values(
        {
            'STQ_AGENT_CLUSTER_SETTINGS': {
                'stq-agent-base': {
                    'url': mockserver.url('/stq-agent-base'),
                    'tvm_name': 'stq-agent-base',
                },
                'stq-agent-taxi-critical': {
                    'url': mockserver.url('/stq-agent-taxi-critical'),
                    'tvm_name': 'stq-agent-taxi-critical',
                },
            },
        },
    )

    @mockserver.json_handler('/stq-agent-base/queues/api/mark_as_done')
    def _mock_mark_done(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/mark_as_done',
    )
    def _mock_mark_done_critical(request):
        return {}

    should_send_task1 = True
    should_send_task2 = True
    should_send_task3 = True
    take_id = None

    @mockserver.json_handler('/stq-agent-base/queues/api/take')
    def _mock_take_ready_base(request):
        nonlocal should_send_task1
        nonlocal take_id
        take_id = request.json['idempotency_token']
        if (
                should_send_task1
                and (
                    request.json['queue_name']
                    == 'sample_queue_test_workers_stats_py3_base'
                )
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task1 = False
            return {'tasks': [defs.test_task_ids['base']]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/take')
    def _mock_take_ready_critical(request):
        nonlocal should_send_task2
        nonlocal should_send_task3
        nonlocal take_id
        take_id = request.json['idempotency_token']
        if (
                should_send_task2
                and (
                    request.json['queue_name']
                    == 'sample_queue_test_workers_stats_py3_critical_1'
                )
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task2 = False
            return {'tasks': [defs.test_task_ids['critical_1']]}

        if (
                should_send_task3
                and (
                    request.json['queue_name']
                    == 'sample_queue_test_workers_stats_py3_critical_2'
                )
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task3 = False
            return {'tasks': [defs.test_task_ids['critical_2']]}

        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs_test_workers_stats(request):
        return defs.queues_configs

    await taxi_stq_runner.run_periodic_task('configs_fetcher')

    @mockserver.json_handler('/stq-agent-base/workers/stats')
    def _workers_stats_handler_base(request):
        return {}

    @mockserver.json_handler('/stq-agent-taxi-critical/workers/stats')
    def _workers_stats_handler_critical(request):
        return {}

    await _mock_mark_done.wait_call()
    await _mock_mark_done_critical.wait_call()
    await _mock_mark_done_critical.wait_call()

    await taxi_stq_runner.run_periodic_task('send_workers_stats')

    handlers_by_cluster = {
        'base': _workers_stats_handler_base,
        'critical': _workers_stats_handler_critical,
    }

    workers_stats_by_cluster = {
        'base': defs.test_workers_stats_base,
        'critical': defs.test_workers_stats_critical,
    }

    for cluster in {'base', 'critical'}:
        request_json = (await handlers_by_cluster[cluster].wait_call())[
            'request'
        ].json
        assert validate_json(request_json, defs.workers_stats_schema)
        assert (
            request_json['total'] == workers_stats_by_cluster[cluster]['total']
        )
        assert (
            request_json['queues']
            == workers_stats_by_cluster[cluster]['queues']
        )

    taxi_config.set_values(
        {
            'STQ_AGENT_CLUSTER_SETTINGS': {
                'stq-agent-base': {
                    'url': mockserver.url('/stq-agent'),
                    'tvm_name': 'stq-agent',
                },
                'stq-agent-taxi-critical': {
                    'url': mockserver.url('/stq-agent'),
                    'tvm_name': 'stq-agent',
                },
            },
        },
    )
    await taxi_stq_runner.invalidate_caches()
    await taxi_stq_runner.run_periodic_task('configs_fetcher')


def validate_json(instance, schema):
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True
