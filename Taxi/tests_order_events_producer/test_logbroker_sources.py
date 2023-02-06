import json

import pytest

_SINK_BULK_ARGUMENTS = {
    'bulk_size_threshold': 1,
    'bulk_duration_of_data_collection_ms': 200,
    'input_queue_size': 500,
    'output_queue_size': 1000,
}


@pytest.mark.parametrize(
    'source_name',
    [
        # XXX: source 'communal-events' is tested in the appropriate test
        'cron-kd-drivers',
        'atlas-order-events',
        'order-events',
        'eventus-adjust-taxi',
        'grocery-adjust-events',
        'atlas-pin-storage',
        'atlas-surge-storage',
        'atlas-drivers',
        'atlas-grocery',
        'unique-drivers-merge-events',
    ],
)
async def test_logbroker_sources(
        taxi_order_events_producer,
        testpoint,
        taxi_eventus_orchestrator_mock,
        source_name,
):
    pipelines_config = [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': source_name},
            'root': {
                'output': {
                    'sink_name': 'clickhouse_sink',
                    'arguments': _SINK_BULK_ARGUMENTS,
                },
                'operations': [],
            },
            'name': 'test-source-' + source_name,
        },
    ]

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::clickhouse_sink')
    def sink(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': source_name,
                'data': json.dumps(
                    {'test-data-for-source': 'data ' + source_name},
                ),
                'topic': 'smth',
                'cookie': 'cookie_for_sink-' + source_name,
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())[
        'data'
    ] == 'cookie_for_sink-' + source_name

    assert (await sink.wait_call())['data'] == [
        {'test-data-for-source': 'data ' + source_name},
    ]
