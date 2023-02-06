import json
import time

_OEP_PIPELINES_FOR_ORCH = [
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'atlas-fleet-orders-statuses'},
        'number_of_threads': 1,
        'root': {
            'output': {'sink_name': 'atlas_saas_order_metrics'},
            'operations': [
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
                    'name': 'filter-fields-for-sink',
                    'operation_variant': {
                        'arguments': {
                            'leave_keys_list': [
                                'order_created_at',  # DateTime('UTC'),
                                'park_id',  # LowCardinality(String),
                                'order_id',  # String CODEC(ZSTD(1)),
                                'status',  # LowCardinality(String),
                                'tariff_class',  # LowCardinality(String),
                                'event_time',  # DateTime('UTC'),
                                'event_index',  # Float32
                            ],
                        },
                        'operation_name': 'filter_fields',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'atlas-fleet-orders-events',
    },
]


async def test_atlas_fleet_orders_statuses(
        taxi_order_events_producer,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        testpoint,
        mockserver,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::atlas_saas_order_metrics')
    def sink_write(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES_FOR_ORCH,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for i in range(10):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'atlas-fleet-orders-statuses',
                    'data': (
                        '{"park_id":"c5cdea22ad6b4e4da8f3fdbd4bddc2e7",'
                        + '"order_id":"7bc879bda461259b8e9a50449bf14fca",'
                        + '"order_created_at":"2022-02-25T15:26:46.093+00:00",'
                        + '"status":"completed_own",'
                        + '"tariff_class":"econom",'
                        + '"event_index":9.0,'
                        + '"event_time":"2022-02-26T15:34:14.925+00:00"}'
                    ),
                    'topic': 'smth',
                    'cookie': 'cookie_for_atlas_sink_' + str(i),
                },
            ),
        )
        assert response.status_code == 200

    for i in range(10):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_atlas_sink_' + str(i)

    events = []
    deadline = time.time() + 2.0
    while deadline > time.time() and len(events) < 10:
        req = await sink_write.wait_call()
        print(f'\n\n{req}\n\n')
        data = req['data']
        assert isinstance(data, list)
        events += data

    assert (
        events
        == [
            {
                'order_created_at': '2022-02-25T15:26:46.093+00:00',
                'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                'order_id': '7bc879bda461259b8e9a50449bf14fca',
                'status': 'completed_own',
                'tariff_class': 'econom',
                'event_time': '2022-02-26T15:34:14.925+00:00',
                'event_index': 9.0,
            },
        ]
        * 10
    )
