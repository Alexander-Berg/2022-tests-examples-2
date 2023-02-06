import json

import pytest

from tests_order_events_producer import pipeline_tools


def _get_switch_options_with_filter(filters):
    return [
        {
            'arguments': {
                'dst_key': 'event.descriptor',
                'value': '{"name": "cancel_by_user"}',
                'policy': 'set',
            },
            'filters': [
                filters,
                {
                    'arguments': {
                        'src': 'event_key',
                        'match_with': 'handle_cancel_by_user',
                    },
                    'operation_name': 'string_equal',
                    'type': 'filter',
                },
                {
                    'arguments': {'src': 'nz', 'match_with': 'moscow'},
                    'operation_name': 'string_equal',
                    'type': 'filter',
                },
            ],
        },
        {
            'arguments': {
                'dst_key': 'event.descriptor',
                'value': '{"name": "cancel_by_user"}',
                'policy': 'set',
            },
            'filters': [
                {
                    'arguments': {
                        'src': 'event_key',
                        'match_with': 'handle_cancel_by_user',
                    },
                    'operation_name': 'string_equal',
                    'type': 'filter',
                },
            ],
        },
        {
            'arguments': {
                'dst_key': 'event.filtered_out',
                'value': '{}',
                'policy': 'set',
            },
            'filters': [],
        },
    ]


def _get_pipelines_with_filter(filters):
    switch_options = _get_switch_options_with_filter(filters)
    rms = pipeline_tools.get_oe_pipeline_for_orch('rms_sink', switch_options)
    clh = pipeline_tools.get_oe_pipeline_for_orch(
        'clickhouse_sink', switch_options,
    )
    return [rms, clh]


@pytest.mark.parametrize(
    'filters',
    [
        {
            'arguments': {
                'src': 'event_key',
                'salt': 'abc',
                'hash_from': 0,
                'hash_to': 0,
            },
            'operation_name': 'string_salt',
            'type': 'filter',
        },
        {
            'arguments': {
                'src': 'user_tags',
                'policy': 'contains_none',
                'match_with': ['user_tag'],
            },
            'operation_name': 'string_array',
            'type': 'filter',
        },
        {
            'arguments': {
                'src': 'user_tags',
                'policy': 'contains_all',
                'match_with': ['user_tag', 'non_exists_tag'],
            },
            'operation_name': 'string_array',
            'type': 'filter',
        },
        {
            'arguments': {
                'src': 'user_tags',
                'policy': 'contains_any',
                'match_with': ['non_exists_tag'],
            },
            'operation_name': 'string_array',
            'type': 'filter',
        },
    ],
)
@pytest.mark.suspend_periodic_tasks('send_statistics')
async def test_check_connecting(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        taxi_config,
        testpoint,
        filters,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('rms-bulk-sink-sender::rms_sink')
    def event_processed(data):
        pass

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::clickhouse_sink')
    def event_processed_clickhouse(data):
        pass

    pipelines_config = _get_pipelines_with_filter(filters)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(1)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(event_key='handle_cancel_by_user'),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await event_processed.wait_call()
    await event_processed_clickhouse.wait_call()
    assert taxi_rider_metrics_storage_mock.verify()
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['descriptor'][
            'name'
        ]
        == 'cancel_by_user'
    )
