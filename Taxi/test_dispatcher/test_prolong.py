import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


@pytest.mark.now('2019-09-09T15:00:00+0300')
@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_prolong(
        taxi_stq_dispatcher_sample, mockserver, testpoint, mocked_time,
):
    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/prolong')
    def _mock_prolong(request):
        return {'conflict_ids': []}

    @testpoint('queue-sample-done')
    async def _mock_performer(request):
        mocked_time.sleep(50)
        await taxi_stq_dispatcher_sample.invalidate_caches()
        await taxi_stq_dispatcher_sample.run_periodic_task(
            'sample_queue_done_2_prolong',
        )
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent/queues/api/take')
    async def _mock_take_ready(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_done')
                and (request.json['shard_id'] == 2)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_prolong_task_id',
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
                    'shards': [{'index': 2}],
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
        'id': 'test_prolong_task_id',
        'args': [1, '2', {'3': '4'}],
        'kwargs': {'1': 2, '3': '4'},
    }

    prolong_request = await common.clean_agent_request(
        _mock_prolong, exec_time=False,
    )
    assert prolong_request == {
        'queue_name': 'sample_queue_done',
        'shard_id': 2,
        'task_ids': ['test_prolong_task_id'],
    }

    mark_done_request = await common.clean_agent_request(
        _mock_mark_done, take_id=True,
    )
    assert mark_done_request == {
        'queue_name': 'sample_queue_done',
        'shard_id': 2,
        'task_id': 'test_prolong_task_id',
    }
