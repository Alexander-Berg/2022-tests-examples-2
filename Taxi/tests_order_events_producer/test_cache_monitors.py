import json

import pytest

_PIPELINES_CONFIG = [
    {
        'description': '',
        'st_ticket': '',
        'number_of_threads': 1,
        'source': {'name': 'eventus-adjust-taxi'},
        'root': {
            'output': {'sink_name': 'log_sink'},
            'operations': [
                {
                    'name': 'fetch-driver-orders-first-request',
                    'operation_variant': {
                        'arguments': {
                            'driver_profiles_src_key': (
                                'driver_orders_first_request'
                            ),
                            'driver_orders_dst_key': 'driver_orders_first',
                            'orders_booked_since_offset': '45d',
                            'orders_booked_until_offset': '1ms',
                            'order_statuses': ['complete'],
                            'limit': 2,
                            'cache_max_size': 100,
                        },
                        'operation_name': 'remote::fetch_driver_orders',
                        'type': 'mapper',
                    },
                    'is_disabled': False,
                    'error_handling_policy': {'retry_policy': {'attempts': 3}},
                },
            ],
        },
        'name': 'driver-orders-cache',
    },
]


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_cache_stats_monitor(
        taxi_order_events_producer,
        taxi_order_events_producer_monitor,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        taxi_rider_metrics_storage_mock,
        taxi_eventus_orchestrator_mock,
        metrics_snapshot,
        mockserver,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def driver_orders_parks_orders_list(data):
        return {
            'orders': [
                {
                    'id': '12345678901234567890123456789012',
                    'short_id': 12345,
                    'status': 'complete',
                    'created_at': '2021-01-01T11:00:00+0000',
                    'booked_at': '2021-01-01T11:00:00+0000',
                    'provider': 'platform',
                    'amenities': [],
                    'address_from': {
                        'address': 'location address',
                        'lat': 0.0,
                        'lon': 0.0,
                    },
                    'events': [],
                    'route_points': [],
                    'db_id': 'park_id1',
                    'driver_uuid': 'driver_profile_id1',
                },
            ],
            'limit': 1,
        }

    await metrics_snapshot.take_snapshot()

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _PIPELINES_CONFIG,
    )

    for cookie_id in range(10):
        cookie = 'cookie{}'.format(cookie_id)
        event = make_order_event(
            event_key='handle_complete',
            driver_orders_first_request=[
                {
                    'park_id': 'park_id1',
                    'driver_profile_id': 'driver_profile_id1',
                },
            ],
        )
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'eventus-adjust-taxi',
                    'data': order_events_gen(event).cast('json'),
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200
    await driver_orders_parks_orders_list.wait_call()

    for i in range(10):
        assert (await commit.wait_call())['data'] == 'cookie' + str(i)

    metrics = await metrics_snapshot.get_metrics_diff()
    cache_metrics = metrics['cache-statistics']['driver-orders-cache']
    cache_metrics_diff = cache_metrics.get_diff()

    assert cache_metrics_diff['hits'] == 9
    assert cache_metrics_diff['misses'] == 1
    assert cache_metrics['size'].new_value() == 1
    assert cache_metrics['max_size'].new_value() == 100

    await taxi_order_events_producer.run_task('dump.driver-orders-cache')
