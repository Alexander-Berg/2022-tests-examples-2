import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_done_sharded(taxi_stq_dispatcher_sample, mockserver, testpoint):
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
                and (request.json['shard_id'] == 1)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_done_sharded_task_id',
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
                    'shards': [{'index': 1}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    assert (await _mock_performer.wait_call())['request'] == {
        'id': 'test_done_sharded_task_id',
        'args': [1, '2', {'3': '4'}],
        'kwargs': {'1': 2, '3': '4'},
    }

    mark_done_request = await common.clean_agent_request(
        _mock_mark_done, take_id=True,
    )
    assert mark_done_request == {
        'queue_name': 'sample_queue_done',
        'shard_id': 1,
        'task_id': 'test_done_sharded_task_id',
    }
