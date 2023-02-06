import json

import pytest

_OEP_PIPELINES_FOR_ORCH = [
    {
        'name': 'communal-events-test-driver-orders',
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
                    'is_disabled': True,
                    'name': 'log-event',
                    'operation_variant': {
                        'operation_name': 'log_event',
                        'type': 'mapper',
                        'arguments': {
                            'marker': 'evevxx',
                            'log_level': 'debug',
                        },
                    },
                },
                {
                    'name': 'fetch-driver-orders',
                    'operation_variant': {
                        'operation_name': 'remote::fetch_driver_orders',
                        'type': 'mapper',
                        'arguments': {
                            'debug': 'true',
                            'driver_orders_dst_key': 'driver_orders_first',
                            'driver_profiles_src_key': (
                                'driver_orders_first_request'
                            ),
                            'limit': 2,
                            'order_statuses': ['complete'],
                            'orders_booked_since_offset': '365d',
                            'orders_booked_until_offset': '1ms',
                            'reference_time_point_key': 'created',
                        },
                    },
                    'error_handling_policy': {
                        'action_after_erroneous_execution': 'propagate',
                        'erroneous_statistics_level': 'error',
                        'retry_policy': {
                            'attempts': 3,
                            'delay_factor': 1,
                            'max_delay': 2000000000,
                            'min_delay': 0,
                        },
                    },
                },
                {
                    'name': 'log-event',
                    'operation_variant': {
                        'operation_name': 'log_event',
                        'type': 'mapper',
                        'arguments': {'marker': 'evev', 'log_level': 'debug'},
                    },
                },
            ],
        },
    },
]


# This identifiers insersects with response_orders.json
_DRIVER_ORDERS_REQ_DATA = [
    {
        'park_id': '7ad36bc7560449998acbe2c57a75c293',
        'driver_profile_id': '06f7a56e4afb7a67e6fabb0d26b32cd3',
        'park_driver_profile_id': (
            '7ad36bc7560449998acbe2c57a75c293_06f7a56e4afb7a67e6fabb0d26b32cd3'
        ),
    },
    {
        'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
        'driver_profile_id': 'd7488617409e4b0d83a008c8da8795c3',
        'park_driver_profile_id': (
            '7f74df331eb04ad78bc2ff25ff88a8f2_d7488617409e4b0d83a008c8da8795c3'
        ),
    },
    {
        'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
        'driver_profile_id': 'a69e9e2ba0b148fc82b9361b5bc0afb3',
        'park_driver_profile_id': (
            'a3608f8f7ee84e0b9c21862beef7e48d_a69e9e2ba0b148fc82b9361b5bc0afb3'
        ),
    },
    {
        'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
        'driver_profile_id': '2b55fa7cd997445e878a6985a8857b42',
        'park_driver_profile_id': (
            'a3608f8f7ee84e0b9c21862beef7e48d_2b55fa7cd997445e878a6985a8857b42'
        ),
    },
    {
        'park_id': '7ad36bc7560449998acbe2c57a75c293',
        'driver_profile_id': '4c57e098feb54995ba86d03cc588968f',
        'park_driver_profile_id': (
            '7ad36bc7560449998acbe2c57a75c293_4c57e098feb54995ba86d03cc588968f'
        ),
    },
]


@pytest.mark.now('2020-10-23T01:01:01+0000')
async def test_driver_orders_cache(
        taxi_order_events_producer,
        mockserver,
        testpoint,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        load_json,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @mockserver.json_handler('driver-orders/v1/parks/orders/list')
    def driver_order_handle(data):
        return load_json('response_orders.json')

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES_FOR_ORCH,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'communal-events',
                'data': json.dumps(
                    {
                        'topic': 'smth',
                        'driver_orders_first_request': _DRIVER_ORDERS_REQ_DATA,
                        'created': '2020-10-23T01:01:01+0000',
                    },
                ),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie1'
    assert driver_order_handle.times_called == 5
    for _ in range(5):  # clear state
        await driver_order_handle.wait_call()

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'communal-events',
                'data': json.dumps(
                    {
                        'topic': 'smth',
                        'driver_orders_first_request': _DRIVER_ORDERS_REQ_DATA,
                        'created': '2020-10-23T01:01:02+0000',
                    },
                ),
                'topic': 'smth',
                'cookie': 'cookie2',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie2'
    assert driver_order_handle.times_called == 0
