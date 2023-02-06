import asyncio
import copy
import json

import pytest

from tests_eventus_sample import pipeline_tools

QUEUE_SIZE_PER_THREAD: int = 1
NUMBER_OF_THREADS: int = 1

PIPELINE_1 = {
    'description': 'pipeline_1',
    'st_ticket': '',
    'source': {'name': 'lbkx_test_events'},
    'root': {
        'output': {
            'sink_name': 'sink',
            'error_handling_policy': {
                'retry_policy': {
                    # emulate infinity delay fix in EFFICIENCYDEV-19178
                    'attempts': 100,
                    'min_delay_ms': 1000,
                    'max_delay_ms': 1000,
                    'delay_factor': 1,
                },
            },
        },
        'operations': [],
    },
    'name': 'lbkx_test_events_1',
    'number_of_threads': NUMBER_OF_THREADS,
}

PIPELINE_2 = {
    'description': 'pipeline_2',
    'st_ticket': '',
    'source': {'name': 'lbkx_test_events'},
    'root': {'output': {'sink_name': 'sink-2'}, 'operations': []},
    'name': 'lbkx_test_events_2',
    'number_of_threads': NUMBER_OF_THREADS,
}


@pytest.mark.config(
    EVENTUS_PIPELINE_QUEUE_SETTINGS={
        'event_queue_size_per_thread': QUEUE_SIZE_PER_THREAD,
    },
)
async def test_stats_seconds_since_pop_increase(
        taxi_eventus_sample,
        taxi_eventus_sample_monitor,
        testpoint,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('eventus-statistics::get_source_stats')
    def get_source_stats(data):
        pass

    inject_error = True

    @testpoint('sink::error-injector')
    def _sink_error_testpoint(data):
        nonlocal inject_error
        return {'inject_failure': inject_error}

    await taxi_eventus_sample.tests_control(reset_metrics=True)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, [PIPELINE_1],
    )

    await taxi_eventus_sample.run_task('invalidate-seq_num')
    # we need have non empty logbroker_consumer queue to make test work
    # so 1 message be in queue and on in fly to pipeline queue
    waiting_event_count = 2
    pipeline_queue_size = NUMBER_OF_THREADS * QUEUE_SIZE_PER_THREAD
    event_count = pipeline_queue_size + NUMBER_OF_THREADS + waiting_event_count

    for cookie_id in range(event_count):
        cookie = 'cookie{}'.format(cookie_id)
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'lbkx_test_events',
                    'data': json.dumps(pipeline_tools.create_event(cookie_id)),
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200

    await asyncio.sleep(1.1)

    _ = await taxi_eventus_sample_monitor.get_metrics()

    source_stats = (await get_source_stats.wait_call())['data']

    assert (
        source_stats['lbkx_test_events'][
            'seconds_since_last_pop_when_was_possible'
        ]
        > 0
    )

    inject_error = False

    for _ in range(event_count):
        await commit.wait_call()


async def test_stats_seconds_since_pop_normal_stop(
        taxi_eventus_sample,
        taxi_eventus_sample_monitor,
        testpoint,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('eventus-statistics::get_source_stats')
    def get_source_stats(data):
        pass

    pipelines = [PIPELINE_1, PIPELINE_2]

    await taxi_eventus_sample.tests_control(reset_metrics=True)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, pipelines,
    )

    await taxi_eventus_sample.run_task('invalidate-seq_num')

    for cookie_id in range(10):
        cookie = 'cookie{}'.format(cookie_id)
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'lbkx_test_events',
                    'data': json.dumps(pipeline_tools.create_event(cookie_id)),
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200

    for _ in range(10):
        await commit.wait_call()

    await asyncio.sleep(1.1)

    _ = await taxi_eventus_sample_monitor.get_metrics()
    source_stats = (await get_source_stats.wait_call())['data']
    assert (
        source_stats['lbkx_test_events'][
            'seconds_since_last_pop_when_was_possible'
        ]
        == 0
    )


@pytest.mark.parametrize('oe_pipeline_exists', [True, False])
async def test_stats_seconds_since_pop_when_pipeline_disabled(
        taxi_eventus_sample,
        taxi_eventus_sample_monitor,
        testpoint,
        taxi_eventus_orchestrator_mock,
        oe_pipeline_exists: bool,
):
    @testpoint('eventus-statistics::get_source_stats')
    def get_source_stats(data):
        pass

    await taxi_eventus_sample.tests_control(reset_metrics=True)

    pipelines_config = copy.deepcopy(PIPELINE_1)
    if oe_pipeline_exists:
        pipelines_config['is_disabled'] = True

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, [pipelines_config],
    )

    await asyncio.sleep(1.1)

    _ = await taxi_eventus_sample_monitor.get_metrics()
    source_stats = (await get_source_stats.wait_call())['data']
    assert (
        source_stats['lbkx_test_events'][
            'seconds_since_last_pop_when_was_possible'
        ]
        == 0
    )
