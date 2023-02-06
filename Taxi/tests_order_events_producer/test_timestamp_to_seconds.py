import asyncio
import json
import time


_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'communal-events'},
        'root': {
            'output': {'sink_name': 'rms_sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'add-seq-num',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_seq_num',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'add-proc-timestamp',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_proc_timestamp',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'time_to_seconds',
                    'operation_variant': {
                        'arguments': {'field_name': 'status_updated'},
                        'operation_name': 'timestamp_to_seconds_from_epoch',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'communal-events',
    },
]


async def test_timestamp_to_seconds(
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_eventus_orchestrator_mock,
        taxi_order_events_producer,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'communal-events',
                'data': order_events_gen(
                    make_order_event(
                        order_id=None,
                        event_index=None,
                        idempotency_token='shablagoo',
                        topic='smth',
                        nz=None,
                        status_updated='2020-12-18T11:29:16.471163+03:00',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_'

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 1
    ):
        await asyncio.sleep(0.05)
    assert taxi_rider_metrics_storage_mock.times_called == 1
    assert taxi_rider_metrics_storage_mock.calls == [
        {
            'events': [
                {
                    'created': '2020-12-18T08:29:16+00:00',
                    'idempotency_token': 'shablagoo',
                    'type': 'order',
                    'user_id': '04def2593a934fd6489bbbeb',
                },
            ],
        },
    ]
