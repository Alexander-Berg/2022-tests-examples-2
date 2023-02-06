import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_done_bulk(taxi_stq_dispatcher_sample, mockserver, testpoint):
    @mockserver.json_handler('/stq-agent/queues/config/')
    def _mock_fetch_configs_clear(request):
        return {'queues': []}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done(request):
        return {}

    @testpoint('queue-sample-done')
    def _mock_performer(request):
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_done')
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_done_bulk_task_id_1',
                        'args': [1, '2', {'3': '4'}],
                        'kwargs': {'1': 2, '3': '4'},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                    },
                    {
                        'task_id': 'test_done_bulk_task_id_2',
                        'args': [1, '2', {'3': '4'}],
                        'kwargs': {'1': 2, '3': '4'},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                    },
                ],
            }
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {
            'queues': [
                {
                    'queue': 'sample_queue_done',
                    'shards_count': 3,
                    'shards': [{'index': 0, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    perform_requests = []
    perform_requests.append((await _mock_performer.wait_call())['request'])
    perform_requests.append((await _mock_performer.wait_call())['request'])
    perform_requests.sort(key=lambda item: item['id'])
    assert perform_requests == [
        {
            'id': 'test_done_bulk_task_id_1',
            'args': [1, '2', {'3': '4'}],
            'kwargs': {'1': 2, '3': '4'},
        },
        {
            'id': 'test_done_bulk_task_id_2',
            'args': [1, '2', {'3': '4'}],
            'kwargs': {'1': 2, '3': '4'},
        },
    ]

    mark_done_requests = []
    mark_done_requests.append(
        await common.clean_agent_request(_mock_mark_done, take_id=True),
    )
    mark_done_requests.append(
        await common.clean_agent_request(_mock_mark_done, take_id=True),
    )
    mark_done_requests.sort(key=lambda item: item['task_id'])
    assert mark_done_requests == [
        {
            'queue_name': 'sample_queue_done',
            'shard_id': 0,
            'task_id': 'test_done_bulk_task_id_1',
        },
        {
            'queue_name': 'sample_queue_done',
            'shard_id': 0,
            'task_id': 'test_done_bulk_task_id_2',
        },
    ]
