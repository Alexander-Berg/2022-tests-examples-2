import pytest
from tests_stq_dispatcher_sample.stq_dispatcher_sample.test_dispatcher import (
    common,
)


TASK_ID_YES = 'orange_herring'
TASK_ID_NO = 'red_moose'
PERCENT = 50

SOME_TASK_1 = {
    'args': [],
    'kwargs': {},
    'exec_tries': 1,
    'reschedule_counter': 0,
    'task_id': TASK_ID_YES,
}
SOME_TASK_2 = {
    'args': [],
    'kwargs': {},
    'exec_tries': 1,
    'reschedule_counter': 0,
    'task_id': TASK_ID_NO,
}

QUEUE_CONFIG_TEST = {
    'queue': 'queue_name',
    'shards_count': 3,
    'shards': [{'index': 0, 'max_tasks': 100}],
    'worker_configs': {
        'instances': 1,
        'max_tasks': 100,
        'max_execution_time': 2.0,
    },
    'cluster': 'stq-agent-taxi-critical',
}


async def test_split_values():
    assert common.send_to_cluster_from_config(PERCENT, TASK_ID_YES)
    assert not common.send_to_cluster_from_config(PERCENT, TASK_ID_NO)


def taxi_config_set_values(queue_name, mockserver, taxi_config):
    taxi_config.set_values(
        {
            'STQ_AGENT_CLUSTER_SETTINGS': {
                'stq-agent-taxi-critical': {
                    'url': mockserver.url('/stq-agent-taxi-critical'),
                    'tvm_name': 'stq-agent-taxi-critical',
                    'queues_in_process_of_cluster_switching': {
                        queue_name: {'percent': PERCENT},
                    },
                },
            },
        },
    )


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_add_bulk_percent_cluster(
        stq, taxi_stq_dispatcher_sample, mockserver, testpoint, taxi_config,
):
    queue_name = 'sample_queue_client'
    taxi_config_set_values(queue_name, mockserver, taxi_config)

    await taxi_stq_dispatcher_sample.invalidate_caches()

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/add/' + queue_name + '/bulk',
    )
    async def _mock_add_bulk_critical(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/' + queue_name + '/bulk',
    )
    async def _mock_add_bulk_base(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {'queues': [{**QUEUE_CONFIG_TEST, 'queue': queue_name}]}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    await taxi_stq_dispatcher_sample.post(
        'add_task_bulk',
        headers={
            'task_id1': SOME_TASK_1['task_id'],
            'task_id2': SOME_TASK_2['task_id'],
        },
    )
    await _mock_add_bulk_critical.wait_call()

    await taxi_stq_dispatcher_sample.post(
        'add_task_bulk',
        headers={
            'task_id1': SOME_TASK_2['task_id'],
            'task_id2': SOME_TASK_1['task_id'],
        },
    )
    await _mock_add_bulk_base.wait_call()


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_add_percent_cluster(
        stq, taxi_stq_dispatcher_sample, mockserver, testpoint, taxi_config,
):
    queue_name = 'sample_queue_client'
    taxi_config_set_values(queue_name, mockserver, taxi_config)

    await taxi_stq_dispatcher_sample.invalidate_caches()

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/add/' + queue_name,
    )
    async def _mock_add_critical(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/add/' + queue_name)
    async def _mock_add_base(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {'queues': [{**QUEUE_CONFIG_TEST, 'queue': queue_name}]}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')
    await taxi_stq_dispatcher_sample.post(
        'add_task', headers={'task_id': SOME_TASK_1['task_id']},
    )
    await _mock_add_critical.wait_call()

    await taxi_stq_dispatcher_sample.post(
        'add_task', headers={'task_id': SOME_TASK_2['task_id']},
    )
    await _mock_add_base.wait_call()


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_done_percent_cluster(
        stq, taxi_stq_dispatcher_sample, mockserver, testpoint, taxi_config,
):
    @mockserver.json_handler('/stq-agent/queues/config/')
    def _mock_fetch_configs_clear(request):
        return {'queues': []}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    queue_name = 'sample_queue_done'
    taxi_config_set_values(queue_name, mockserver, taxi_config)

    await taxi_stq_dispatcher_sample.invalidate_caches()

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/mark_as_done',
    )
    def _mock_mark_done_critical(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done_base(request):
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/take')
    def _mock_take_ready_from_critical(request):
        assert common.send_to_cluster_from_config(
            PERCENT, request.json['idempotency_token'],
        )
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == queue_name)
                and (request.json['shard_id'] == 0)
        ):
            should_send_task = False
            return {'tasks': [SOME_TASK_1, SOME_TASK_2]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready_from_default(request):
        assert not common.send_to_cluster_from_config(
            PERCENT, request.json['idempotency_token'],
        )
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == queue_name)
                and (request.json['shard_id'] == 0)
        ):
            should_send_task = False
            return {'tasks': [SOME_TASK_1, SOME_TASK_2]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {'queues': [{**QUEUE_CONFIG_TEST, 'queue': queue_name}]}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')
    await _mock_mark_done_base.wait_call()
    await _mock_mark_done_critical.wait_call()


@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_failed_percent_cluster(
        taxi_stq_dispatcher_sample, mockserver, testpoint, taxi_config,
):
    queue_name = 'sample_queue_failed'
    taxi_config_set_values(queue_name, mockserver, taxi_config)

    await taxi_stq_dispatcher_sample.invalidate_caches()

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/mark_as_failed',
    )
    def _mock_mark_failed_critical(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/mark_as_failed')
    def _mock_mark_failed_base(request):
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/take')
    def _mock_take_ready_from_critical(request):
        assert common.send_to_cluster_from_config(
            PERCENT, request.json['idempotency_token'],
        )
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == queue_name)
                and (request.json['shard_id'] == 0)
        ):
            should_send_task = False
            return {'tasks': [SOME_TASK_1, SOME_TASK_2]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready_from_default(request):
        assert not common.send_to_cluster_from_config(
            PERCENT, request.json['idempotency_token'],
        )
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == queue_name)
                and (request.json['shard_id'] == 0)
        ):
            should_send_task = False
            return {'tasks': [SOME_TASK_1, SOME_TASK_2]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {'queues': [{**QUEUE_CONFIG_TEST, 'queue': queue_name}]}

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    await _mock_mark_failed_critical.wait_call()
    await _mock_mark_failed_base.wait_call()


@pytest.mark.now('2019-09-09T15:00:00+0300')
@pytest.mark.suspend_periodic_tasks('configs_fetcher')
async def test_prolong_percent_cluster(
        taxi_stq_dispatcher_sample,
        mockserver,
        testpoint,
        taxi_config,
        mocked_time,
):
    queue_name = 'sample_queue_done'
    taxi_config_set_values(queue_name, mockserver, taxi_config)

    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done_base(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/mark_as_done',
    )
    def _mock_mark_done_critical(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/prolong')
    def _mock_prolong_base(request):
        return {'conflict_ids': []}

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/prolong')
    def _mock_prolong_critical(request):
        return {'conflict_ids': []}

    @testpoint('queue-sample-done')
    async def _mock_performer(request):
        mocked_time.sleep(50)
        await taxi_stq_dispatcher_sample.invalidate_caches()
        await taxi_stq_dispatcher_sample.run_periodic_task(
            'sample_queue_done_0_prolong',
        )
        return {}

    should_send_task = True
    chosen_task = SOME_TASK_1

    @mockserver.json_handler('/stq-agent/queues/api/take')
    async def _mock_take_ready_from_default(request):
        nonlocal should_send_task
        if (
                should_send_task
                and request.json['shard_id'] == 0
                and request.json['queue_name'] == queue_name
        ):
            should_send_task = False
            return {'tasks': [chosen_task]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent-taxi-critical/queues/api/take')
    async def _mock_take_ready_from_critical(request):
        nonlocal should_send_task
        if (
                should_send_task
                and request.json['shard_id'] == 0
                and request.json['queue_name'] == queue_name
        ):
            should_send_task = False
            return {'tasks': [chosen_task]}
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {
            'queues': [
                {
                    'queue': queue_name,
                    'shards_count': 3,
                    'shards': [{'index': 0, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 10000.0,
                    },
                    'cluster': 'stq-agent-taxi-critical',
                },
            ],
        }

    await taxi_stq_dispatcher_sample.run_periodic_task('configs_fetcher')

    await _mock_prolong_critical.wait_call()

    chosen_task = SOME_TASK_2
    should_send_task = True

    await _mock_prolong_base.wait_call()

    await _mock_mark_done_critical.wait_call()
    await _mock_mark_done_base.wait_call()
