import json

import pytest

from tests_order_events_producer import pipeline_tools

LAVKA_DST_POINT_WITHIN = [37.66593397, 55.79496673]
LAVKA_DST_POINT_OUTSIDE = [37.46593397, 55.79496673]

POLIGON_VALUES = {
    'coordinates': [
        {
            'points': [
                {'lon': 37.56593397, 'lat': 55.89496673},
                {'lon': 37.56593397, 'lat': 55.69496673},
                {'lon': 37.76593397, 'lat': 55.69496673},
                {'lon': 37.76593397, 'lat': 55.89496673},
            ],
        },
    ],
    'enabled': True,
    'groups': ['lavka'],
    'metadata': {},
    'polygon_id': 'polygon-id',
}


SWITCH_OPTIONS = [
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
            'value': (
                '{"name": "transporting", '
                '"tags": ["transporting_to_lavka_zone"]}'
            ),
            'policy': 'set',
        },
        'filters': [
            {
                'arguments': {
                    'src': 'event_key',
                    'match_with': 'handle_transporting',
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {'src': 'nz', 'match_with': 'moscow'},
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {
                    'src': 'destination_polygon_groups',
                    'policy': 'contains_any',
                    'match_with': ['lavka'],
                },
                'operation_name': 'string_array',
                'type': 'filter',
            },
        ],
    },
    {
        'arguments': {
            'dst_key': 'event.descriptor',
            'value': '{"name": "transporting", "tags": ["from_lavka_zone"]}',
            'policy': 'set',
        },
        'filters': [
            {
                'arguments': {
                    'src': 'event_key',
                    'match_with': 'handle_transporting',
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {'src': 'nz', 'match_with': 'moscow'},
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {
                    'src': 'source_polygon_groups',
                    'policy': 'contains_any',
                    'match_with': ['lavka'],
                },
                'operation_name': 'string_array',
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

RMS_PIPELINE = pipeline_tools.get_oe_pipeline_for_orch(
    'rms_sink', SWITCH_OPTIONS,
)
OEP_PIPELINES = [RMS_PIPELINE]

SWITCH_OPTIONS_FOR_EVENT_REASON = [
    {
        'arguments': {
            'dst_key': 'event.descriptor',
            'value': '{"name": "not_created"}',
            'policy': 'set',
        },
        'filters': [
            {
                'arguments': {
                    'src': 'event_key',
                    'match_with': 'handle_transporting',
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {'src': 'event_reason', 'match_with': 'create'},
                'operation_name': 'string_equal',
                'type': 'filter',
            },
        ],
    },
    {
        'arguments': {
            'dst_key': 'event.descriptor',
            'value': '{"name": "created"}',
            'policy': 'set',
        },
        'filters': [
            {
                'arguments': {'src': 'event_reason', 'match_with': 'create'},
                'operation_name': 'string_equal',
                'type': 'filter',
            },
        ],
    },
]


@pytest.mark.suspend_periodic_tasks('send_statistics')
async def test_out_of_destination_geozone(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, POLIGON_VALUES,
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('remote-sink-sender::commit-filtered::rms_sink')
    def no_event_processed(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(0)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        destinations_geopoint=[LAVKA_DST_POINT_OUTSIDE],
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await no_event_processed.wait_call()

    assert taxi_rider_metrics_storage_mock.verify()


@pytest.mark.parametrize(
    'is_source_geopoint,expected_tags',
    [(True, 'from_lavka_zone'), (False, 'transporting_to_lavka_zone')],
)
async def test_inside_geozone(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        is_source_geopoint,
        expected_tags,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, POLIGON_VALUES,
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def event_processed(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(1)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        source_geopoint=(
                            LAVKA_DST_POINT_WITHIN
                            if is_source_geopoint
                            else LAVKA_DST_POINT_OUTSIDE
                        ),
                        destinations_geopoint=[
                            LAVKA_DST_POINT_WITHIN
                            if not is_source_geopoint
                            else LAVKA_DST_POINT_OUTSIDE,
                        ],
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await event_processed.wait_call()

    assert taxi_rider_metrics_storage_mock.verify()
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['descriptor'][
            'name'
        ]
        == 'transporting'
    )
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['descriptor'][
            'tags'
        ][0]
        == expected_tags
    )


async def test_several_destination_points(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, POLIGON_VALUES,
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def event_processed(data):
        assert len(data['events']) == 1

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(1)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        destinations_geopoint=[
                            LAVKA_DST_POINT_WITHIN,
                            LAVKA_DST_POINT_OUTSIDE,
                            LAVKA_DST_POINT_WITHIN,
                        ],
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await event_processed.wait_call()

    assert taxi_rider_metrics_storage_mock.verify()
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['descriptor'][
            'name'
        ]
        == 'transporting'
    )
    assert (
        taxi_rider_metrics_storage_mock.calls[0]['events'][0]['descriptor'][
            'tags'
        ][0]
        == 'transporting_to_lavka_zone'
    )


@pytest.mark.suspend_periodic_tasks('send_statistics')
async def test_no_destination_points(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, POLIGON_VALUES,
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('remote-sink-sender::commit-filtered::rms_sink')
    def no_event_processed(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(0)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        destinations_geopoint=None,
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await no_event_processed.wait_call()

    assert taxi_rider_metrics_storage_mock.verify()


async def test_reason_filter(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, POLIGON_VALUES,
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def events_processed(data):
        pass

    pipelines_config = [
        pipeline_tools.get_oe_pipeline_for_orch(
            'rms_sink', SWITCH_OPTIONS_FOR_EVENT_REASON,
        ),
    ]
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
                    make_order_event(event_key='handle_transporting'),
                    make_order_event(
                        event_key='handle_default', event_reason='create',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await events_processed.wait_call()

    assert taxi_rider_metrics_storage_mock.verify()
    assert len(taxi_rider_metrics_storage_mock.calls[0]['events']) == 2

    events = taxi_rider_metrics_storage_mock.calls[0]['events']
    descriptor = ''
    if 'descriptor' in events[0]:
        descriptor = events[0]['descriptor']['name']
    elif 'descriptor' in events[1]:
        descriptor = events[1]['descriptor']['name']

    assert descriptor == 'created'
