import asyncio
import json
import time

import pytest


_SINK_BULK_ARGUMENTS = {
    'bulk_size_threshold': 2,
    'bulk_duration_of_data_collection_ms': 200,
    'input_queue_size': 500,
    'output_queue_size': 1000,
}


def _create_rms_pipeline(rms_sink_name: str):
    return [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'communal-events'},
            'root': {
                'output': {
                    'sink_name': rms_sink_name,
                    'arguments': _SINK_BULK_ARGUMENTS,
                },
                'operations': [
                    {
                        'name': 'topic-filter',
                        'operation_variant': {
                            'arguments': {
                                'src': 'topic',
                                'match_with': 'smth',
                            },
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
    ]


@pytest.mark.parametrize('rms_sink_name', ['rms_sink', 'rms_sink_2'])
async def test_rms_sink(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        rms_sink_name,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    pipelines_config = _create_rms_pipeline(rms_sink_name)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for i in range(10):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'communal-events',
                    'data': order_events_gen(
                        make_order_event(
                            event_key='handle_transporting',
                            user_id='user-1',
                            db_id='dbid1',
                            driver_uuid='driveruuid1',
                            status_updated=1571253356.368,
                            user_phone_id='custom-user-phone-id',
                            destinations_geopoint=[[37.69411325, 55.78685382]],
                            topic='smth',
                        ),
                    ).cast('json'),
                    'topic': 'smth',
                    'cookie': 'cookie_for_rms_sink_' + str(i),
                },
            ),
        )
        assert response.status_code == 200

    for i in range(10):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_rms_sink_' + str(i)

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 5
    ):
        await asyncio.sleep(0.05)
    assert taxi_rider_metrics_storage_mock.times_called == 5
    assert (
        taxi_rider_metrics_storage_mock.calls
        == [
            {
                'events': [
                    {
                        'created': '2019-10-16T19:15:56+00:00',
                        'idempotency_token': (
                            'order/b2f366eb37ba19a88a14a35345c8af5a/1'
                            '/handle_transporting'
                        ),
                        'order_id': 'b2f366eb37ba19a88a14a35345c8af5a',
                        'tariff_zone': 'moscow',
                        'type': 'order',
                        'user_id': 'custom-user-phone-id',
                    },
                ] * 2,
            },
        ]
        * 5
    )


@pytest.mark.parametrize(
    'pipelines_config',
    [
        pytest.param(
            [
                {
                    'description': '',
                    'st_ticket': '',
                    'source': {'name': 'cron-kd-drivers'},
                    'root': {
                        'output': {
                            'sink_name': 'clickhouse_sink',
                            'arguments': _SINK_BULK_ARGUMENTS,
                        },
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
                                    'arguments': {'leave_keys_list': ['test']},
                                    'operation_name': 'filter_fields',
                                    'type': 'mapper',
                                },
                            },
                        ],
                    },
                    'name': 'cron-kd-drivers',
                },
            ],
            id='clickhouse_sink_pipelines_config',
        ),
    ],
)
async def test_clickhouse_sink(
        taxi_order_events_producer,
        testpoint,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        pipelines_config,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::clickhouse_sink')
    def sink_write(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for i in range(10):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'cron-kd-drivers',
                    'data': json.dumps({'test': 'clickhouse'}),
                    'topic': 'smth',
                    'cookie': 'cookie_for_clickhouse_sink_' + str(i),
                },
            ),
        )
        assert response.status_code == 200

    for i in range(10):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_clickhouse_sink_' + str(i)

    events = []
    deadline = time.time() + 1.0
    while deadline > time.time() and len(events) < 10:
        data = (await sink_write.wait_call())['data']
        assert isinstance(data, list)
        events += data

    assert events == [{'test': 'clickhouse'}] * 10


@pytest.mark.parametrize(
    'pipelines_config',
    [
        pytest.param(
            [
                {
                    'description': '',
                    'st_ticket': '',
                    'source': {'name': 'atlas-order-events'},
                    'root': {
                        'output': {
                            'sink_name': 'clickhouse_debug_sink',
                            'arguments': _SINK_BULK_ARGUMENTS,
                        },
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
                        ],
                    },
                    'name': 'atlas-order-events_clickhouse',
                },
                {
                    'description': '',
                    'st_ticket': '',
                    'source': {'name': 'atlas-order-events'},
                    'root': {
                        'output': {
                            'sink_name': 'rms_sink',
                            'arguments': _SINK_BULK_ARGUMENTS,
                        },
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
                        ],
                    },
                    'name': 'atlas-order-events_rms',
                },
            ],
            id='atlas-order-events',
        ),
    ],
)
async def test_atlas_order_events_with_branches(
        taxi_order_events_producer,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_rider_metrics_storage_mock,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        pipelines_config,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for i in range(10):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'atlas-order-events',
                    'data': order_events_gen(
                        make_order_event(
                            event_key='handle_transporting',
                            user_id='user-1',
                            db_id='dbid1',
                            driver_uuid='driveruuid1',
                            status_updated=1571253356.368,
                            user_phone_id='custom-user-phone-id',
                            destinations_geopoint=[[37.69411325, 55.78685382]],
                            topic='smth',
                        ),
                    ).cast('json'),
                    'topic': 'smth',
                    'cookie': 'cookie_for_atlas_order_events_' + str(i),
                },
            ),
        )
        assert response.status_code == 200

    for i in range(10):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_atlas_order_events_' + str(i)

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 5
    ):
        await asyncio.sleep(0.05)
    assert taxi_rider_metrics_storage_mock.times_called == 5
    assert (
        taxi_rider_metrics_storage_mock.calls
        == [
            {
                'events': [
                    {
                        'created': '2019-10-16T19:15:56+00:00',
                        'idempotency_token': (
                            'order/b2f366eb37ba19a88a14a35345c8af5a/1'
                            '/handle_transporting'
                        ),
                        'order_id': 'b2f366eb37ba19a88a14a35345c8af5a',
                        'tariff_zone': 'moscow',
                        'type': 'order',
                        'user_id': 'custom-user-phone-id',
                    },
                ] * 2,
            },
        ]
        * 5
    )
