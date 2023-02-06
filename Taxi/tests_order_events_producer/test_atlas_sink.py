import json
import time

_OEP_PIPELINES_FOR_ORCH = [
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'communal-events'},
        'root': {
            'output': {'sink_name': 'log_sink'},
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
            ],
        },
        'name': 'communal-events',
    },
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'cron-kd-drivers'},
        'root': {
            'output': {'sink_name': 'atlas_clickhouse_sink'},
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
                                'id',
                                'timestamp',
                                'cnt',
                                'car_class',
                                'dt',
                                'dttm_utc_1_min',
                                'ts_1_min',
                                'city',
                                'lat',
                                'lon',
                                'driver_ids',
                                'udid',
                                'quadkey',
                            ],
                        },
                        'operation_name': 'filter_fields',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'cron-kd-drivers',
    },
]


async def test_atlas_sink(
        taxi_order_events_producer,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::atlas_clickhouse_sink')
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
                    'consumer': 'cron-kd-drivers',
                    'data': (
                        '{"timestamp": 1597611730, '
                        + '"id": "ee7daac8ad9cce62aeacbd7cb47f74e3", '
                        + '"cnt": 1, "car_class": "any", '
                        + '"dt": "2020-08-16", '
                        + '"dttm_utc_1_min": "2020-08-16 21:02:10", '
                        + '"ts_1_min": 1597611730, "city": "moscow", '
                        + '"lat": 55.6857209, "lon": 37.6227834, '
                        + '"driver_ids": ['
                        + '"400000140306_e61dad8faf4619586fe7ae84e4250208"], '
                        + '"udid": "5ead53ab8fe28d5ce44e314f", '
                        + '"quadkey": "120310101302022"}'
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
    deadline = time.time() + 1.0
    while deadline > time.time() and len(events) < 10:
        data = (await sink_write.wait_call())['data']
        assert isinstance(data, list)
        events += data

    assert (
        events
        == [
            {
                'timestamp': 1597611730,
                'id': 'ee7daac8ad9cce62aeacbd7cb47f74e3',
                'cnt': 1,
                'car_class': 'any',
                'dt': '2020-08-16',
                'dttm_utc_1_min': '2020-08-16 21:02:10',
                'ts_1_min': 1597611730,
                'city': 'moscow',
                'lat': 55.6857209,
                'lon': 37.6227834,
                'driver_ids': [
                    '400000140306_e61dad8faf4619586fe7ae84e4250208',
                ],
                'udid': '5ead53ab8fe28d5ce44e314f',
                'quadkey': '120310101302022',
            },
        ]
        * 10
    )
