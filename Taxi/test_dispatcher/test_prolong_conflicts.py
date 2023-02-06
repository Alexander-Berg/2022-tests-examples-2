import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


@pytest.mark.now('2019-09-09T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_prolong_conflicts(
        taxi_stq_dispatcher_sample, mockserver, testpoint, mocked_time,
):
    conflict_ids = [
        'test_prolong_conflicts_task_id_1',
        'test_prolong_conflicts_task_id_2',
    ]

    @mockserver.json_handler('/stq-agent/queues/api/free')
    def _mock_free(request):
        return {}

    @testpoint('queue-sample-infinite')
    async def _mock_performer(request):
        return {}

    should_prolong_task = True

    @mockserver.json_handler('/stq-agent/queues/api/prolong')
    def _mock_prolong(request):
        nonlocal should_prolong_task
        if (
                should_prolong_task
                and (request.json['queue_name'] == 'sample_queue_infinite')
                and (sorted(request.json['task_ids']) == sorted(conflict_ids))
        ):
            should_prolong_task = False
        return {'conflict_ids': conflict_ids}

    should_send_task = True

    @mockserver.json_handler('/stq-agent/queues/api/take')
    async def _mock_take_ready(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_infinite')
                and (request.json['shard_id'] == 1)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_prolong_conflicts_task_id_1',
                        'args': [1, '2', {'3': '4'}],
                        'kwargs': {'1': 2, '3': '4'},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                    },
                    {
                        'task_id': 'test_prolong_conflicts_task_id_2',
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
                    'shards': [{'index': 1, 'max_tasks': 100}],
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

    performer_requests = []
    performer_requests.append((await _mock_performer.wait_call())['request'])
    performer_requests.append((await _mock_performer.wait_call())['request'])
    performer_requests.sort(key=lambda item: item['id'])
    assert performer_requests == [
        {
            'id': 'test_prolong_conflicts_task_id_1',
            'args': [1, '2', {'3': '4'}],
            'kwargs': {'1': 2, '3': '4'},
        },
        {
            'id': 'test_prolong_conflicts_task_id_2',
            'args': [1, '2', {'3': '4'}],
            'kwargs': {'1': 2, '3': '4'},
        },
    ]

    mocked_time.sleep(50)
    await taxi_stq_dispatcher_sample.invalidate_caches()
    await taxi_stq_dispatcher_sample.run_periodic_task(
        'sample_queue_infinite_1_prolong',
    )

    prolong_request = await common.clean_agent_request(
        _mock_prolong, exec_time=False,
    )
    prolonged_ids = prolong_request.pop('task_ids')
    assert prolong_request == {
        'queue_name': 'sample_queue_infinite',
        'shard_id': 1,
    }
    assert sorted(prolonged_ids) == sorted(conflict_ids)

    free_requests = []
    free_requests.append(
        await common.clean_agent_request(_mock_free, exec_time=False),
    )
    free_requests.append(
        await common.clean_agent_request(_mock_free, exec_time=False),
    )
    free_requests.sort(key=lambda item: item['task_id'])
    assert free_requests == [
        {
            'queue_name': 'sample_queue_infinite',
            'shard_id': 1,
            'task_id': 'test_prolong_conflicts_task_id_1',
            'is_expired': True,
        },
        {
            'queue_name': 'sample_queue_infinite',
            'shard_id': 1,
            'task_id': 'test_prolong_conflicts_task_id_2',
            'is_expired': True,
        },
    ]
