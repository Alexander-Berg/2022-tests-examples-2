import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


@pytest.mark.now('2019-09-09T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_conflict_max_execution_time(
        taxi_stq_dispatcher_sample, mockserver, testpoint, mocked_time,
):
    @mockserver.json_handler('/stq-agent/queues/api/free')
    def _mock_free(request):
        return {}

    @testpoint('queue-sample-infinite')
    async def _mock_performer(request):
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent/queues/api/take')
    async def _mock_take_ready(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_infinite')
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_conflict_max_execution_time_task_id',
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
                    'queue': 'sample_queue_infinite',
                    'shards_count': 1,
                    'shards': [{'index': 0, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_dispatcher_sample.invalidate_caches()
    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    assert (await _mock_performer.wait_call())['request'] == {
        'id': 'test_conflict_max_execution_time_task_id',
        'args': [1, '2', {'3': '4'}],
        'kwargs': {'1': 2, '3': '4'},
    }

    mocked_time.sleep(200)
    await taxi_stq_dispatcher_sample.invalidate_caches()
    await taxi_stq_dispatcher_sample.run_periodic_task(
        'sample_queue_infinite_0_prolong',
    )

    free_request = await common.clean_agent_request(
        _mock_free, exec_time=False,
    )
    assert free_request == {
        'queue_name': 'sample_queue_infinite',
        'shard_id': 0,
        'task_id': 'test_conflict_max_execution_time_task_id',
        'is_expired': True,
    }
