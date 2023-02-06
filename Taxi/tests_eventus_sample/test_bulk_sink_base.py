import asyncio
import json

import pytest

from tests_eventus_sample import pipeline_tools


def _get_pipelines_config(
        sink_name,
        bulk_size_threshold,
        bulk_duration,
        input_queue_size,
        output_queue_size,
):
    return [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'lbkx_test_events'},
            'root': {
                'sink_name': sink_name,
                'arguments': {
                    'bulk_size_threshold': bulk_size_threshold,
                    'bulk_duration_of_data_collection_ms': bulk_duration,
                    'input_queue_size': input_queue_size,
                    'output_queue_size': output_queue_size,
                },
            },
            'name': 'lbkx_test_events_pipeline',
        },
    ]


async def _make_test(
        testpoint,
        taxi_eventus_orchestrator_mock,
        taxi_eventus_sample,
        sink_name,
        idx,
):
    @testpoint(f'bulk_aggregator_constructor::{sink_name}')
    def bulk_aggr_constructor(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_eventus_sample,
        _get_pipelines_config(sink_name, idx, idx + 1, idx + 2, idx + 3),
    )

    bulk_settings = (await bulk_aggr_constructor.wait_call())['data']

    expected = {
        'bulk_size_threshold': idx,
        'bulk_duration_of_data_collection': idx + 1,
        'input_queue_size': idx + 2,
        'output_queue_size': idx + 3,
    }

    assert bulk_settings == expected


@pytest.mark.parametrize(
    'sink_idx, sink_name', [p for p in enumerate(['bulk-sink'])],
)
async def test_bulk_settings_from_args(
        testpoint,
        taxi_eventus_orchestrator_mock,
        taxi_eventus_sample,
        sink_idx,
        sink_name,
):
    args = [
        testpoint,
        taxi_eventus_orchestrator_mock,
        taxi_eventus_sample,
        sink_name,
        sink_idx + 100,
    ]
    await _make_test(*args)


async def test_bulk_size_from_args(
        testpoint, taxi_eventus_orchestrator_mock, taxi_eventus_sample,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('bulk-sink::sendbulk')
    def bulk_sink_mock(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_eventus_sample,
        _get_pipelines_config('bulk-sink', 10, 100000, 500, 50),
    )

    for i in range(10):
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'lbkx_test_events',
                    'data': json.dumps(pipeline_tools.create_event(i)),
                    'topic': 'smth',
                    'cookie': f'cookie_for_test_bulk_size_sink_{i}',
                },
            ),
        )
        assert response.status_code == 200

    commit_msgs = []
    for i in range(10):
        commit_msgs.append((await commit.wait_call())['data'])
    assert sorted(commit_msgs) == [
        f'cookie_for_test_bulk_size_sink_{i}' for i in range(10)
    ]

    bulk_sink_call = (await bulk_sink_mock.wait_call())['data']
    assert len(bulk_sink_call['events']) == 10
    assert bulk_sink_mock.times_called == 0

    for i in range(10, 19):
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'lbkx_test_events',
                    'data': json.dumps(pipeline_tools.create_event(i)),
                    'topic': 'smth',
                    'cookie': f'cookie_for_test_bulk_size_sink_{i}',
                },
            ),
        )
        assert response.status_code == 200

    await asyncio.sleep(1)
    assert bulk_sink_mock.times_called == 0

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(19)),
                'topic': 'smth',
                'cookie': f'cookie_for_test_bulk_size_sink_{19}',
            },
        ),
    )
    assert response.status_code == 200

    commit_msgs = []
    for i in range(10, 20):
        commit_msgs.append((await commit.wait_call())['data'])
    assert sorted(commit_msgs) == [
        f'cookie_for_test_bulk_size_sink_{i}' for i in range(10, 20)
    ]

    rms_call = (await bulk_sink_mock.wait_call())['data']
    assert len(rms_call['events']) == 10
    assert bulk_sink_mock.times_called == 0


async def test_bulk_duration_from_args(
        testpoint, taxi_eventus_orchestrator_mock, taxi_eventus_sample,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('bulk-sink::sendbulk')
    def bulk_sink_mock(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_eventus_sample,
        _get_pipelines_config('bulk-sink', 10, 100000, 500, 50),
    )

    for i in range(9):
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'lbkx_test_events',
                    'data': json.dumps(pipeline_tools.create_event(i)),
                    'topic': 'smth1',
                    'cookie': f'cookie_for_test_bulk_size_sink_{i}',
                },
            ),
        )
        assert response.status_code == 200

    await asyncio.sleep(1)
    assert bulk_sink_mock.times_called == 0

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(9)),
                'topic': 'smth1',
                'cookie': 'cookie_for_test_bulk_size_sink_9',
            },
        ),
    )
    assert response.status_code == 200

    commit_msgs = []
    for i in range(10):
        commit_msgs.append((await commit.wait_call())['data'])
    assert sorted(commit_msgs) == [
        f'cookie_for_test_bulk_size_sink_{i}' for i in range(10)
    ]

    rms_call = (await bulk_sink_mock.wait_call())['data']
    assert len(rms_call['events']) == 10
    assert bulk_sink_mock.times_called == 0

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_eventus_sample,
        _get_pipelines_config('bulk-sink', 10, 1, 500, 50),
    )

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(10)),
                'topic': 'smth1',
                'cookie': 'cookie_for_test_bulk_size_sink_10',
            },
        ),
    )
    assert response.status_code == 200
    assert (await commit.wait_call())[
        'data'
    ] == 'cookie_for_test_bulk_size_sink_10'
    rms_call = (await bulk_sink_mock.wait_call())['data']
    assert len(rms_call['events']) == 1
    assert bulk_sink_mock.times_called == 0
