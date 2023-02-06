import json

import pytest

from tests_order_events_producer import pipeline_tools

SWITCH_OPTIONS = [
    {
        'arguments': {
            'dst_key': 'event.descriptor',
            'value': '{"name": "cawabanga"}',
            'policy': 'set',
        },
        'filters': [],
    },
]

PERCENTILES = (
    'p0',
    'p50',
    'p90',
    'p95',
    'p98',
    'p99',
    'p99_6',
    'p99_9',
    'p100',
)

NODE_STATS_KEYS = [
    'add-proc-timestamp',
    'set-polygon-groups',
    'switch',
    'filter-after-switch',
    'set-uuid',
    'set-event-type',
    'set-event-id',
]

_SINK_BULK_ARGUMENTS = {
    'bulk_size_threshold': 2,
    'bulk_duration_of_data_collection_ms': 200,
    'input_queue_size': 500,
    'output_queue_size': 1000,
}

RMS_PIPELINE = pipeline_tools.get_oe_pipeline_for_orch(
    'rms_sink', SWITCH_OPTIONS, sink_arguments=_SINK_BULK_ARGUMENTS,
)
CLH_PIPELINE = pipeline_tools.get_oe_pipeline_for_orch(
    'clickhouse_sink', SWITCH_OPTIONS, sink_arguments=_SINK_BULK_ARGUMENTS,
)


def check_pipeline_stats(stats, pipeline_name, sink_names: list, val):
    assert pipeline_name in stats
    pipeline_stats = stats[pipeline_name]

    assert pipeline_stats['success'] >= 0
    assert pipeline_stats['errors'] >= 0
    assert pipeline_stats['aggregated_errors'] >= 0
    assert pipeline_stats['currently_processed'] >= 0
    assert pipeline_stats['queue_size'] >= 0
    assert pipeline_stats['pipeline_seconds_since_last_process'] >= 0
    assert all(k in pipeline_stats['pipeline_timings'] for k in PERCENTILES)

    assert len(pipeline_stats['sink_stats']) == len(sink_names)
    for sink in sink_names:
        sink_stats = pipeline_stats['sink_stats'][sink]
        assert sink_stats['bulk_sizes']['p100'] == val
        assert sink_stats['input_queue_size'] >= 0
        assert sink_stats['output_queue_size'] >= 0
        assert sink_stats['items_in_process'] >= 0
        assert sink_stats['old_items_in_process'] >= 0
        assert sink_stats['seconds_since_last_bulk'] >= 0
        assert sink_stats['seconds_since_last_process'] >= 0
        assert all(k in sink_stats['timings'] for k in PERCENTILES)

    assert len(pipeline_stats['node_stats']) == len(NODE_STATS_KEYS) * len(
        sink_names,
    )
    expected_node_names = [
        '[{}]{}'.format(idx, key)
        for idx, key in enumerate(NODE_STATS_KEYS * len(sink_names))
    ]
    assert sorted(pipeline_stats['node_stats'].keys()) == sorted(
        expected_node_names,
    )

    for _, node_stat in pipeline_stats['node_stats'].items():
        assert node_stat['success_count'] >= 0
        assert node_stat['warning_count'] >= 0
        assert node_stat['error_count'] >= 0


def check_processing_stats(stats):
    handle_cancel = stats['delay_timings_sec']['event_name']['order'][
        'event_key'
    ]['handle_cancel_by_user']
    assert all(k in handle_cancel for k in PERCENTILES)
    assert handle_cancel['p100'] == 4


def check_source_stats(stats):
    order_events = stats['order-events']
    assert order_events['parsing_errors'] >= 0
    assert order_events['processed_messages'] >= 0
    assert order_events['seconds_since_last_commit'] >= 0
    assert order_events['seconds_since_last_pop_when_was_possible'] >= 0


@pytest.mark.now('2019-10-16T19:16:00+0000')
@pytest.mark.parametrize(
    'pipelines_config, stat_names',
    [
        pytest.param(
            [RMS_PIPELINE, CLH_PIPELINE],
            ['clickhouse_sink', 'rms_sink'],
            id='clh+rms sinks',
        ),
        pytest.param([RMS_PIPELINE], ['rms_sink'], id='rms sinks'),
        pytest.param([CLH_PIPELINE], ['clickhouse_sink'], id='clh sinks'),
    ],
)
async def test_stats_monitor(
        taxi_order_events_producer,
        taxi_order_events_producer_monitor,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        taxi_rider_metrics_storage_mock,
        taxi_eventus_orchestrator_mock,
        pipelines_config,
        stat_names,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('eventus-statistics::get_pipeline_stats')
    def get_pipeline_stats(data):
        pass

    @testpoint('eventus-statistics::get_processing_stats')
    def get_processing_stats(data):
        pass

    @testpoint('eventus-statistics::get_source_stats')
    def get_source_stats(data):
        pass

    await taxi_order_events_producer.tests_control(reset_metrics=True)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for cookie_id in range(10):
        cookie = 'cookie{}'.format(cookie_id)
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'order-events',
                    'data': order_events_gen(
                        make_order_event(event_key='handle_cancel_by_user'),
                    ).cast('json'),
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200

    for _ in range(10):
        await commit.wait_call()

    _ = await taxi_order_events_producer_monitor.get_metrics()
    pipeline_stats = (await get_pipeline_stats.wait_call())['data']
    check_pipeline_stats(pipeline_stats, 'order-events', stat_names, 2)
    processing_stats = (await get_processing_stats.wait_call())['data']
    check_processing_stats(processing_stats)
    source_stats = (await get_source_stats.wait_call())['data']
    check_source_stats(source_stats)


@pytest.mark.parametrize('mute_errors', [True, False])
async def test_stats_erroneous_stats_ignoring(
        taxi_order_events_producer,
        taxi_order_events_producer_monitor,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        taxi_rider_metrics_storage_mock,
        taxi_eventus_orchestrator_mock,
        metrics_snapshot,
        mute_errors,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await metrics_snapshot.take_snapshot()

    pipelines_config = [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'order-events'},
            'root': {
                'output': {'sink_name': 'rms_sink'},
                'operations': [
                    {
                        'name': 'badaz',
                        'operation_variant': {
                            'arguments': {'throw_when': 'runtime'},
                            'operation_name': 'debug::throw_exception',
                            'type': 'mapper',
                        },
                        'error_handling_policy': {
                            'action_after_erroneous_execution': 'propagate',
                            'erroneous_statistics_level': (
                                'warning' if mute_errors else 'error'
                            ),
                            'retry_policy': {
                                'attempts': 1,
                                'min_delay_ms': 0,
                                'delay_factor': 1,
                            },
                        },
                    },
                ],
            },
            'name': 'order-events',
        },
    ]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(event_key='handle_cancel_by_user'),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie{}'.format(mute_errors),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    metrics = await metrics_snapshot.get_metrics_diff()
    assert (
        metrics['pipeline-statistics']['order-events']['node_stats'][
            '[0]badaz'
        ].get_diff()
        == {
            'success_count': 0,
            'warning_count': (1 if mute_errors else 0),
            'error_count': (0 if mute_errors else 1),
            'retry_count': 0,
        }
    )
