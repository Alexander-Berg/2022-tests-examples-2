import asyncio
import json
import time

import pytest


def get_streq_filter(key, value):
    return {
        'arguments': {'src': key, 'match_with': value},
        'operation_name': 'string_equal',
        'type': 'filter',
    }


def get_event_key_filter(value):
    return get_streq_filter('event_key', value)


def get_proc_timestamp_operation():
    return {
        'name': 'add-proc-timestamp',
        'operation_variant': {
            'arguments': {},
            'operation_name': 'set_proc_timestamp',
            'type': 'mapper',
        },
    }


def get_field_not_exists_filter(key):
    return {
        'arguments': {'key': key, 'policy': 'key_not_exists'},
        'operation_name': 'field_check',
        'type': 'filter',
    }


def get_event_descriptor_mapargs(value: dict):
    return {
        'dst_key': 'event.descriptor',
        'value': json.dumps(value),
        'policy': 'set',
    }


def get_destpoly_filter(polygon_name: str):
    return {
        'arguments': {
            'src': 'destination_polygon_groups',
            'policy': 'contains_any',
            'match_with': [polygon_name],
        },
        'operation_name': 'string_array',
        'type': 'filter',
    }


def get_event_type_order_node():
    return {
        'name': 'set-event-type',
        'operation_variant': {
            'arguments': {'dst_key': 'event.type', 'value': 'order'},
            'operation_name': 'set_string_value',
            'type': 'mapper',
        },
    }


def get_event_id_node():
    return {
        'name': 'set-event-id',
        'operation_variant': {
            'arguments': {},
            'operation_name': 'set_event_id',
            'type': 'mapper',
        },
    }


OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {'sink_name': 'log_sink'},
            'operations': [
                get_proc_timestamp_operation(),
                {
                    'name': 'list-of-filters',
                    'operation_variant': {
                        'filters': [
                            get_event_key_filter('handle_autoreordering'),
                            get_event_key_filter('handle_seen_timeout'),
                            get_event_key_filter('handle_offer_timeout'),
                            get_event_key_filter('handle_offer_reject'),
                            get_event_key_filter('handle_cancel_by_park'),
                            get_event_key_filter('handle_fail_by_park'),
                            get_event_key_filter('handle_complete'),
                            get_event_key_filter('handle_cancel_by_user'),
                        ],
                    },
                },
                {
                    'name': 'check-without-driver-id',
                    'operation_variant': get_field_not_exists_filter(
                        'driver_id',
                    ),
                },
            ],
        },
        'name': 'order-events_clickhouse_no-driver_id-log',
    },
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {
                'sink_name': 'clickhouse_sink',
                'arguments': {
                    'bulk_size_threshold': 800,
                    'bulk_duration_of_data_collection_ms': 1000,
                    'input_queue_size': 1000,
                    'output_queue_size': 100,
                },
            },
            'operations': [
                get_proc_timestamp_operation(),
                {
                    'name': 'list-of-filters',
                    'operation_variant': {
                        'filters': [
                            get_event_key_filter('handle_autoreordering'),
                            get_event_key_filter('handle_seen_timeout'),
                            get_event_key_filter('handle_offer_timeout'),
                            get_event_key_filter('handle_offer_reject'),
                            get_event_key_filter('handle_cancel_by_park'),
                            get_event_key_filter('handle_fail_by_park'),
                            get_event_key_filter('handle_complete'),
                            get_event_key_filter('handle_cancel_by_user'),
                        ],
                    },
                },
                {
                    'name': 'set-uuid',
                    'operation_variant': {
                        'operation_name': 'split_string_and_fetch',
                        'options': [
                            {
                                'arguments': {
                                    'from': 'driver_id',
                                    'to': 'driver_uuid',
                                    'separator': '_',
                                    'fetch_index': 1,
                                    'expect_count': 2,
                                },
                                'filters': [
                                    {
                                        'arguments': {
                                            'key': 'driver_id',
                                            'policy': 'key_exists',
                                        },
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                    },
                                    get_field_not_exists_filter('driver_uuid'),
                                ],
                            },
                        ],
                        'type': 'mapper',
                    },
                },
                get_event_type_order_node(),
                get_event_id_node(),
            ],
        },
        'name': 'order-events_clickhouse',
    },
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {
                'sink_name': 'rms_sink',
                'arguments': {
                    'bulk_size_threshold': 800,
                    'bulk_duration_of_data_collection_ms': 1000,
                    'input_queue_size': 1000,
                    'output_queue_size': 100,
                },
            },
            'operations': [
                {
                    'name': 'set-polygon-groups',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_polygon_groups',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'switch',
                    'operation_variant': {
                        'operation_name': 'set_json_value',
                        'options': [
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'driving',
                                        'tags': [
                                            (
                                                'driving_from_spb_'
                                                'gallery_mall'
                                            ),
                                        ],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_driving'),
                                    {
                                        'arguments': {
                                            'src': 'source_polygon_groups',
                                            'policy': 'contains_any',
                                            'match_with': ['spb_gallery_mall'],
                                        },
                                        'operation_name': 'string_array',
                                        'type': 'filter',
                                    },
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'transporting',
                                        'tags': [
                                            (
                                                'transporting_to_spb_'
                                                'gallery_mall'
                                            ),
                                        ],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter(
                                        'handle_transporting',
                                    ),
                                    get_destpoly_filter('spb_gallery_mall'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'transporting',
                                        'tags': [
                                            (
                                                'transporting_to_tech_'
                                                'store_for_gruzovoy'
                                            ),
                                        ],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter(
                                        'handle_transporting',
                                    ),
                                    get_destpoly_filter('stores_for_cargo'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'complete',
                                        'tags': ['finished_to_test_dima_home'],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                    get_destpoly_filter('test_dima_home'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'complete',
                                        'tags': [
                                            'finished_to_thermobag_zones',
                                        ],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                    get_destpoly_filter('thermobag_zones'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'complete',
                                        'tags': ['finished_in_lavka_zone_spb'],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                    get_streq_filter('nz', 'spb'),
                                    get_destpoly_filter('lavka_spb'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'complete',
                                        'tags': ['finished_in_lavka_zone_msc'],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                    get_streq_filter('nz', 'moscow'),
                                    get_destpoly_filter('moscow_lavka_zones'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {
                                        'name': 'complete',
                                        'tags': [
                                            'complete_in_army_forum_2020',
                                        ],
                                    },
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                    get_destpoly_filter('army_forum_2020'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'assigning'},
                                ),
                                'filters': [
                                    get_event_key_filter('handle_assigning'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'driving'},
                                ),
                                'filters': [
                                    get_event_key_filter('handle_driving'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'waiting'},
                                ),
                                'filters': [
                                    get_event_key_filter('handle_waiting'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'transporting'},
                                ),
                                'filters': [
                                    get_event_key_filter(
                                        'handle_transporting',
                                    ),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'cancel_by_user'},
                                ),
                                'filters': [
                                    get_event_key_filter(
                                        'handle_cancel_by_user',
                                    ),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'complete'},
                                ),
                                'filters': [
                                    get_event_key_filter('handle_complete'),
                                ],
                            },
                            {
                                'arguments': get_event_descriptor_mapargs(
                                    {'name': 'create'},
                                ),
                                'filters': [
                                    get_event_key_filter('handle_default'),
                                    get_streq_filter('event_reason', 'create'),
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
                        ],
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'filter-after-switch',
                    'operation_variant': get_field_not_exists_filter(
                        'event.filtered_out',
                    ),
                },
                get_event_type_order_node(),
                get_event_id_node(),
            ],
        },
        'name': 'order-events_rms',
    },
]


@pytest.mark.parametrize('cast_type', ['json'])
# This test checks for correct reconfiguration of pipeline while processing
# events without commit lost. At least once pipeline will be reconfigured
# during test run.
# It also may detect memory leak when service built with build-with-asan and
# configured with '{tests-logbroker-messages: {max_request_size: 134217728}}'
async def test_massive_pushups(
        taxi_order_events_producer,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        cast_type,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    chunk_size = 400

    # Change name of one pipeline to force config update
    def get_pipelines_config(cookie_id):
        pipelines_config = OEP_PIPELINES
        pipelines_config[0]['name'] = 'cookie-{}'.format(cookie_id)
        pipelines_config[0]['root']['operations'][0][
            'name'
        ] = f'add-proc-timestamp-{cookie_id}'
        return pipelines_config

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, get_pipelines_config(0),
    )

    @mockserver.json_handler('/rider-metrics-storage/v1/event/new/bulk')
    async def event_new_bulk(request):
        # XXX: simulate network request timings
        await asyncio.sleep(0.1)
        events = request.json['events']
        response_events = [
            {'idempotency_token': event['idempotency_token']}
            for event in events
        ]
        return mockserver.make_response(
            json.dumps({'events': response_events}), 200,
        )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def events_processed(data):
        pass

    await taxi_order_events_producer.enable_testpoints()

    total_count_messages = 1000 * 400
    chunks_sent = 0

    cookie_id = 1
    cookies = []
    next_config_change_delay = 5.0
    next_config_change = time.time() + next_config_change_delay

    send_deadline = time.time() + 15.0
    commit.flush()

    while send_deadline > time.time() and chunks_sent < total_count_messages:
        cookie_id += 1
        cookie = 'cookie-{}'.format(cookie_id)
        cookies.append(cookie)
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'order-events',
                    'data': order_events_gen(
                        *[
                            make_order_event(
                                event_key='handle_cancel_by_user',
                                user_id='user-1',
                                db_id='dbid1',
                                driver_uuid='driveruuid1',
                                user_phone_id='oneonethree',
                                destinations_geopoint=[
                                    [37.69411325, 55.78685382],
                                ],
                                tags=[
                                    'tags_pick1',
                                    'tags_pick2',
                                    'tags_skipped',
                                ],
                            )
                            for _ in range(0, chunk_size)
                        ],
                    ).cast(cast_type),
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )
        if time.time() > next_config_change:
            await taxi_eventus_orchestrator_mock.set_pipelines_config(
                testpoint,
                taxi_order_events_producer,
                get_pipelines_config(cookie_id),
                # Required for a longer time in teamcity for wait
                # pipeline configuration apply
                testpoint_timeout=30.0,
            )
            next_config_change = time.time() + next_config_change_delay

        assert response.status_code == 200
        chunks_sent += chunk_size
        await asyncio.sleep(0.05)

    # Continue changing pipelines configuration while
    # waiting for proccessed events
    processed_count = 0
    deadline = time.time() + 60.0
    while processed_count < chunks_sent and deadline > time.time():
        for _ in range(events_processed.times_called):
            processed_count += len(
                (await events_processed.wait_call())['data']['events'],
            )
        if time.time() > next_config_change:
            cookie_id += 1
            await taxi_eventus_orchestrator_mock.set_pipelines_config(
                testpoint,
                taxi_order_events_producer,
                get_pipelines_config(cookie_id),
                # Required for a longer time in teamcity for wait
                # pipeline configuration apply
                testpoint_timeout=30.0,
            )
            next_config_change = time.time() + next_config_change_delay
        await asyncio.sleep(0.1)
    print('\n\nCommited cookies {}\n\n'.format(commit.times_called))
    assert time.time() < deadline

    for _ in range(events_processed.times_called):
        processed_count += len(
            (await events_processed.wait_call())['data']['events'],
        )
    assert processed_count == chunks_sent

    times_called = commit.times_called
    for _ in range(commit.times_called):
        assert (await commit.wait_call())['data'] in cookies

    while times_called < len(cookies):
        assert (await commit.wait_call())['data'] in cookies
        times_called += 1
    assert event_new_bulk.times_called > 0
