import pytest

QUEUE_NAME = 'sample_queue_client'

BASE_CONFIG = {
    'queues': [
        {
            'queue': QUEUE_NAME,
            'shards_count': 3,
            'shards': [{'index': 0, 'max_tasks': 100}],
            'worker_configs': {
                'instances': 1,
                'max_tasks': 100,
                'max_execution_time': 2.0,
            },
        },
    ],
}


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
@pytest.mark.parametrize(
    'request_json, headers, handler_base, handler_critical, test_api',
    [
        (
            {
                'queue': 'sample_queue_client',
                'task_id': 'task_id',
                'eta': '2019-09-09T15:00:00+0300',
            },
            {},
            '/stq-agent/queues/api/reschedule',
            '/stq-agent-taxi-critical/queues/api/reschedule',
            'reschedule',
        ),
        (
            {},
            {'task_id1': 'task_id1', 'task_id2': 'task_id2'},
            '/stq-agent/queues/api/add/' + QUEUE_NAME + '/bulk',
            '/stq-agent-taxi-critical/queues/api/add/' + QUEUE_NAME + '/bulk',
            'add_task_bulk',
        ),
        (
            {},
            {'task_id': 'task_id'},
            '/stq-agent/queues/api/add/' + QUEUE_NAME,
            '/stq-agent-taxi-critical/queues/api/add/' + QUEUE_NAME,
            'add_task',
        ),
    ],
)
async def test_cluster_header(
        taxi_stq_dispatcher_sample,
        mockserver,
        taxi_config,
        request_json,
        headers,
        handler_base,
        handler_critical,
        test_api,
):
    taxi_config.set_values(
        {
            'STQ_AGENT_CLUSTER_SETTINGS': {
                'stq-agent-taxi-critical': {
                    'url': mockserver.url('/stq-agent-taxi-critical'),
                    'tvm_name': 'stq-agent-taxi-critical',
                },
            },
        },
    )

    @mockserver.json_handler(handler_base)
    def _mock_handler_base_test_cluster_headers(request):
        return mockserver.make_response(
            json={},
            headers={'X-Redirect-Queue-Cluster': 'stq-agent-taxi-critical'},
            status=200,
        )

    @mockserver.json_handler(handler_critical)
    def _mock_handler_critical_test_cluster_headers(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_config_add_header(request):
        return BASE_CONFIG

    await taxi_stq_dispatcher_sample.invalidate_caches()
    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    await taxi_stq_dispatcher_sample.post(
        test_api, request_json, headers=headers,
    )
    await _mock_handler_base_test_cluster_headers.wait_call()

    await taxi_stq_dispatcher_sample.post(
        test_api, request_json, headers=headers,
    )
    await _mock_handler_critical_test_cluster_headers.wait_call()
