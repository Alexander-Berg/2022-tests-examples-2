import pytest

import tests_eta_autoreorder.utils as utils


@pytest.mark.now('2020-02-01T12:00:40')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=120,
)
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
async def test_metrics(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        taxi_eta_autoreorder_monitor,
        pgsql,
):
    order_ids = [
        'order_id1',  # autoreorder successful
        'order_id2',  # no call_autoreorder experiment
        'order_id3',  # no reorder rule
        'order_id4',  # added, no drivers from driver_eta
        'order_id5',  # autoreorder unsuccessful
    ]

    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] in ['order_id1', 'order_id5']
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    @testpoint('accounted_order')
    def accounted_order(order_id):
        return order_id

    await taxi_eta_autoreorder.run_task('reset_orders_statistics')
    await taxi_eta_autoreorder.invalidate_caches()
    await taxi_eta_autoreorder.enable_testpoints()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )
    #  check that the metric is counted only once
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task1',
        kwargs={
            'performer': {
                'uuid': 'uuid1',
                'dbid': 'dbid',
                'distance': 5000,
                'time': 230,
                'cp_id': None,
            },
            'event_key': 'new_driver_found',
            'order_id': 'order_id4',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2020-02-01T12:00:38.000Z'},
            'tariff_class': 'vip',
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        },
    )
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task1',
        kwargs={
            'performer': {
                'uuid': 'uuid1',
                'dbid': 'dbid',
                'distance': 5000,
                'time': 230,
                'cp_id': None,
            },
            'event_key': 'handle_driving',
            'order_id': 'order_id4',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2020-02-01T12:00:39.000Z'},
            'tariff_class': 'vip',
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        },
    )
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task1',
        kwargs={
            'performer': {
                'uuid': 'uuid2',
                'dbid': 'dbid',
                'distance': 5000,
                'time': 230,
                'cp_id': None,
            },
            'event_key': 'handle_driving',
            'order_id': 'order_id4',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2020-02-01T12:00:40.000Z'},
            'tariff_class': 'vip',
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        },
    )
    assert utils.get_all_order_ids_in_database(pgsql) == order_ids

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        driver_id='dbid_uuid1',
        time_left=240,
        distance_left=7000,
        order_ids=order_ids,
    )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert utils.get_sorted_testpoint_calls(
        possible_reorder_detected, 'order_id', None,
    ) == ['order_id1', 'order_id2', 'order_id5']
    assert mock_autoreorder.times_called == 2

    await taxi_eta_autoreorder.invalidate_caches(cache_names=['orders-cache'])

    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task2',
        kwargs={
            'performer': {
                'uuid': 'uuid2',
                'dbid': 'dbid',
                'distance': 5000,
                'time': 200,
                'cp_id': None,
            },
            'event_key': 'handle_driving',
            'order_id': 'order_id1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2020-02-01T12:00:50.000Z'},
            'tariff_class': 'econom',
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        },
    )
    await taxi_eta_autoreorder.invalidate_caches(cache_names=['orders-cache'])
    for order_id in order_ids:
        await stq_runner.eta_autoreorder_order_status_changed.call(
            task_id='test_task3',
            kwargs={
                'performer': {
                    'uuid': (
                        'uuid2'
                        if order_id in ['order_id1', 'order_id4']
                        else 'uuid1'
                    ),
                    'dbid': 'dbid',
                    'distance': 0,
                    'time': 0,
                    'cp_id': None,
                },
                'event_key': 'handle_finish',
                'order_id': order_id,
                'user_phone_id': '6141a81573872fb3b53037ed',
                'zone_id': 'moscow',
                'event_timestamp': {'$date': '2020-02-01T12:05:00.000Z'},
                'tariff_class': 'econom',
                'point_a': [20, 30],
                'destinations': [],
                'requirements': {},
            },
        )
    assert utils.get_sorted_testpoint_calls(accounted_order, 'order_id') == [
        'order_id4',
    ]
    metric = await taxi_eta_autoreorder_monitor.get_metric('orders-statistics')
    assert metric == {
        'orders': {
            'ekb': {
                'all_orders': 0,
                'jumps': 1,  # order_id2
                'orders_with_jumps': 0,
                'actual_time_arrival': {
                    'p5': 0,
                    'p50': 0,
                    'p95': 0,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'initial_eta': {
                    'p5': 0,
                    'p50': 0,
                    'p95': 0,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'abs_eta_diff': {
                    'p5': 0,
                    'p50': 0,
                    'p95': 0,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'rel_eta_diff': {
                    'p5': 0,
                    'p50': 0,
                    'p95': 0,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'autoreorders.success': 0,
                'autoreorders.all': 0,
                'autoreorders.percent': 100.0,
            },
            'moscow': {
                'all_orders': 1,  # order_id4
                'jumps': 2,
                'orders_with_jumps': 2,  # order_id1, order_id5
                'actual_time_arrival': {
                    'p5': 250,
                    'p50': 300,
                    'p95': 300,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'initial_eta': {
                    'p5': 200,
                    'p50': 220,
                    'p95': 220,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'abs_eta_diff': {
                    'p5': 50,
                    'p50': 80,
                    'p95': 80,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'rel_eta_diff': {
                    'p5': 25,
                    'p50': 36,
                    'p95': 36,
                    '$meta': {'solomon_children_labels': 'percentile'},
                },
                'autoreorders.success': 1,
                'autoreorders.all': 2,
                'autoreorders.percent': 50.0,
            },
        },
    }
