import json

from tests_order_events_producer import pipeline_tools

ORDER_EVENTS_PRODUCER_POLYGONS_ORCH_VALUES = {
    'polygon_id': 'sbp_0_orch',
    'groups': ['spb_sweet_home'],
    'coordinates': [
        {
            'points': [
                {'lon': 30.227659074806706, 'lat': 59.85380501769856},
                {'lon': 30.270231096291088, 'lat': 59.83324585482987},
                {'lon': 30.345075456642654, 'lat': 59.83030779142921},
                {'lon': 30.37219795420124, 'lat': 59.83428275629072},
                {'lon': 30.363271562599667, 'lat': 59.85311416031549},
                {'lon': 30.349881975197334, 'lat': 59.87763078548141},
                {'lon': 30.297010271095782, 'lat': 59.87521445913262},
                {'lon': 30.265424577736407, 'lat': 59.88384338695448},
                {'lon': 30.247571794533286, 'lat': 59.869172872255135},
                {'lon': 30.227659074806706, 'lat': 59.85380501769856},
            ],
        },
    ],
    'enabled': True,
    'metadata': {},
}

SWITCH_OPTIONS = [
    {
        'arguments': {
            'dst_key': 'event.descriptor',
            'value': '{"name": "complete", "tags": ["test_south_spb"]}',
            'policy': 'set',
        },
        'filters': [
            {
                'arguments': {
                    'src': 'event_key',
                    'match_with': 'handle_complete',
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {
                    'src': 'source_polygon_groups',
                    'policy': 'contains_any',
                    'match_with': ['spb_sweet_home'],
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


async def test_check_tags_is_set(
        taxi_order_events_producer,
        taxi_eventus_orchestrator_mock,
        taxi_order_core_mock,
        taxi_rider_metrics_storage_mock,
        taxi_config,
        testpoint,
        make_order_event,
        order_events_gen,
):
    await taxi_eventus_orchestrator_mock.set_polygon_values(
        taxi_order_events_producer, ORDER_EVENTS_PRODUCER_POLYGONS_ORCH_VALUES,
    )
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def rms_sink_processed(data):
        pass

    # note: data got from testsing
    await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': json.dumps(
                    {
                        'driver_position': [30.281025, 59.850078],
                        'request_ip': '127.0.0.1',
                        'created': 1594999381.1590002,
                        'dispatch': 'short',
                        'status_updated': 1594999416.4169999,
                        'dispatch_id': '5f11c2607b28510039493561',
                        'performer_tariff_class': 'econom',
                        'user_agent': (
                            'yandex-taxi/3.124.0.110856 Android/10 '
                            '(samsung; SM-A705FN)'
                        ),
                        'driver_clid': '100500',
                        'alias': '22d292d7b3ac5565a8bbe96406d0d27c',
                        'lookup_eta': 1594999384.5219999,
                        'updated': 1594999417.669,
                        'udid': '5dc2c985b8e3f87968e6bf3c',
                        'properties': ['dispatch_short'],
                        'event_key': 'handle_complete',
                        'user_id': '89046c9a771f5cd9ef224bb1763ac155',
                        'payment_type': 'cash',
                        'source_geopoint': [30.2810273099, 59.8501063202],
                        'billing_currency_rate': '1',
                        'order_id': '57058124681b57f788c454409a48411c',
                        'calc_method': 'fixed',
                        'cost': 119.0,
                        'order_application': 'android',
                        'allowed_tariffs': {
                            '__park__': {
                                'ultimate': 699.0,
                                'business': 119.33333333333333,
                                'child_tariff': 49.0,
                                'night': 1000.0,
                                'econom': 79.33333333333333,
                                'express': 100.0,
                                'vip': 1.0,
                            },
                        },
                        'time': 1,
                        'driver_uuid': '6aa880cdee7751c004f693f12c893d91',
                        'paid_supply': False,
                        'user_locale': 'ru',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'tags': [
                            'test_block',
                            'check_trigered_context',
                            'test_lookup',
                            'damir',
                            '2orders',
                            'highspeeddriver',
                            'HadOrdersLast14Days',
                            'OrderCompleteTagPushv2',
                            'ManualActivityBlocking',
                            'park_test_1',
                            'individual_entrepreneur',
                            'bndrnk',
                            'ManualActivityLast24Hours2',
                            'high_activity',
                            'bronze',
                            'HadOrdersLast30Days',
                            'query_rule_tag_default',
                            'HadOrdersLast7Days',
                        ],
                        'nz': 'spb',
                        'user_phone_id': '5d31d10191272f03f664ec96',
                        'dist': 3,
                        'sp': 1.5,
                        'user_tags': ['damir'],
                        'tips_value': 5.0,
                        'user_has_yaplus': False,
                        'event_index': 7,
                        'user_uid': '4036065149',
                        'taxi_status': 'complete',
                        'source_country': 'Россия',
                        'user_uid_type': 'phonish',
                        'taximeter_version': '9.37 (1073872634)',
                        'transporting_distance_m': 0.6110320707772093,
                        'currency': 'RUB',
                        'status': 'finished',
                        'tips_type': 'percent',
                        'driver_license_personal_id': (
                            '525883cc35f64aaab8498ffadb8a8d6e'
                        ),
                        'request_classes': ['econom'],
                        'destinations_geopoint': [
                            [30.2810273099, 59.8501063198],
                        ],
                    },
                ),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    events = (await rms_sink_processed.wait_call())['data']['events']
    assert events[0]['descriptor'] == {
        'name': 'complete',
        'tags': ['test_south_spb'],
    }

    assert (await commit.wait_call())['data'] == 'cookie1'

    assert len(taxi_rider_metrics_storage_mock.calls) == 1
    assert len(taxi_rider_metrics_storage_mock.calls[0]['events']) == 1
    assert taxi_rider_metrics_storage_mock.calls[0]['events'][0][
        'descriptor'
    ] == {'name': 'complete', 'tags': ['test_south_spb']}
