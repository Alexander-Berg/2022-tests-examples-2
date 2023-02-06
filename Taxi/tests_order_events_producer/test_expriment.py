import asyncio
import json
import time

import pytest

OEP_PIPELINES = [
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
                    'name': 'filter-by-exp',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'adjust_experiment',
                        'type': 'filter',
                    },
                },
            ],
        },
        'name': 'communal-events',
    },
]


@pytest.mark.experiments3(filename='exp3_config.json')
async def test_rms_sink(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    for i in range(2):
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
                            user_phone_id=f'custom-user-phone-id-{i}',
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

    for i in range(2):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_rms_sink_' + str(i)

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 2
    ):
        await asyncio.sleep(0.05)
    assert taxi_rider_metrics_storage_mock.times_called == 1
    assert taxi_rider_metrics_storage_mock.calls == [
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
                    'user_id': 'custom-user-phone-id-1',
                },
            ],
        },
    ]
