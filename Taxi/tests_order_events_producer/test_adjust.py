import asyncio
import json
import time

import pytest

_PIPELINE_CONFIG = [
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
                    'name': 'pre-request',
                    'operation_variant': {
                        'type': 'mapper',
                        'operation_name': 'orders-count-mapper',
                        'arguments': {},
                    },
                },
                {
                    'name': 'go-to-user-statistics',
                    'operation_variant': {
                        'operation_name': 'user_statistics_count_orders',
                        'type': 'mapper',
                        'arguments': {'destination': 'order_tariff_data'},
                    },
                },
                {
                    'name': 'post-request',
                    'operation_variant': {
                        'operation_name': 'orders-counter',
                        'type': 'mapper',
                        'arguments': {'source': 'order_tariff_data'},
                    },
                },
                {
                    'name': 'pre-request',
                    'operation_variant': {
                        'type': 'mapper',
                        'operation_name': 'orders-count-mapper',
                        'arguments': {'filter_by_tariff': 'abracadabra'},
                    },
                },
                {
                    'name': 'go-to-user-statistics',
                    'operation_variant': {
                        'operation_name': 'user_statistics_count_orders',
                        'type': 'mapper',
                        'arguments': {'destination': 'order_count_data'},
                    },
                },
                {
                    'name': 'post-request',
                    'operation_variant': {
                        'operation_name': 'orders-counter',
                        'type': 'mapper',
                        'arguments': {
                            'source': 'order_count_data',
                            'is_tariff_counter': 'wasssuuuuuuuup',
                        },
                    },
                },
                {
                    'name': 'add-event-types',
                    'operation_variant': {
                        'operation_name': 'add-event-types',
                        'type': 'mapper',
                        'arguments': {},
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
                    'name': 'copy-extra-data-fields',
                    'operation_variant': {
                        'arguments': {
                            'src_keys_mapping': ['user_id', 'event_types'],
                            'dst_key': ['extra_data'],
                        },
                        'operation_name': 'copy_fields_to_subobject',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'communal-events',
    },
]


@pytest.mark.skip(reason='TODO: remove or restore EFFICIENCYDEV-18554')
async def test_rms_sink(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        mockserver,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @mockserver.json_handler('/user-statistics/v1/orders')
    def handler(request):
        request = request.json
        assert request['identities'] == [
            {'type': 'phone_id', 'value': 'custom-user-phone-id'},
        ]
        # assert request['filters'] == [
        #     {'name': 'tariff_class', 'values': ['business']},
        # ]
        assert request['group_by'] == ['tariff_class']
        return mockserver.make_response(
            response=json.dumps(
                {
                    'data': [
                        {
                            'identity': {
                                'type': 'phone_id',
                                'value': 'custom-user-phone-id',
                            },
                            'counters': [
                                {
                                    'properties': [],
                                    'value': 0,
                                    'counted_from': '2019-12-11T09:00:00+0000',
                                    'counted_to': '2019-12-12T09:00:00+0000',
                                },
                                {
                                    'properties': [],
                                    'value': 1,
                                    'counted_from': '2019-12-11T09:00:00+0000',
                                    'counted_to': '2019-12-12T09:00:00+0000',
                                },
                            ],
                        },
                    ],
                },
            ),
        )

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _PIPELINE_CONFIG,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

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
                        performer_tariff_class='business',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_0'

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 1
    ):
        await asyncio.sleep(0.05)
    assert handler.has_calls

    assert taxi_rider_metrics_storage_mock.times_called == 1
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['extra_data'][
            'event_types'
        ]
        == [
            'success_first_order',
            'success_first_business_order',
            'success_order',
            'success_business_order',
        ]
    )
