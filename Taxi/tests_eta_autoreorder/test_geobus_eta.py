# pylint: disable=import-error
import datetime

import pytest

import tests_eta_autoreorder.utils as utils

ALL_ORDER_IDS = (
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'cccccccccccccccccccccccccccccccc',
    'dddddddddddddddddddddddddddddddd',
)
EXPECTED_INITIAL_ETA_SET_TIMES = len(ALL_ORDER_IDS) + 1


@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.parametrize(
    'etas_service_id, etas_message_number, expected_num_driving_drivers',
    [('processing:transporting', 5, 0), ('processing:driving', 5, 5)],
)
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True, ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
async def test_listener(
        taxi_eta_autoreorder,
        taxi_eta_autoreorder_monitor,
        testpoint,
        redis_store,
        now,
        etas_service_id,
        etas_message_number,
        expected_num_driving_drivers,
):
    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    await taxi_eta_autoreorder.enable_testpoints()
    cache = {}
    for i in range(etas_message_number):
        processed_result = await utils.publish_etas(
            redis_store,
            redis_eta_payload_processed,
            now,
            1,
            time_left=2500,
            distance_left=2500,
            driver_id='dbid_uuid{}'.format(i),
            cache_is_empty=False,
            service_id=etas_service_id,
        )
        cache.update(processed_result)

    num_driving_drivers = len(cache)
    assert num_driving_drivers == expected_num_driving_drivers

    geobus_listeners_metric = await taxi_eta_autoreorder_monitor.get_metric(
        'geobus-listeners',
    )
    queue_metric = geobus_listeners_metric['geobus']['channel:drw:timelefts'][
        'queue'
    ]
    assert queue_metric['skipped-msg-overload'] == 0


@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_MAX_ITEMS_PER_DRIVER=5,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
async def test_timelefts_cache_logic(
        taxi_eta_autoreorder, testpoint, redis_store, now,
):
    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('geobus_channel_timelefts_payload_processed')
    def timelefts_payload_processed(size):
        return size

    @testpoint('geobus_channel_etas_payload_processed')
    def etas_payload_processed(size):
        return size

    await taxi_eta_autoreorder.enable_testpoints()
    cache = {}
    for eta_num in range(10):
        cache.update(
            await utils.publish_etas(
                redis_store,
                redis_eta_payload_processed,
                now,
                1,
                delta_time=-eta_num,
                time_left=2500 + eta_num,
                distance_left=500 + eta_num,
                driver_id='dbid_uuid_1',
                cache_is_empty=False,
                service_id='processing:driving',
            ),
        )
        cache.update(
            await utils.publish_etas(
                redis_store,
                redis_eta_payload_processed,
                now,
                1,
                delta_time=-eta_num,
                time_left=2500 - eta_num,
                distance_left=500 - eta_num,
                driver_id='dbid_uuid_1',
                cache_is_empty=False,
                service_id='processing:driving',
                order_ids=('bbbbbbbbbbbbbbbbbbbbbbbbbbb',),
            ),
        )
        cache.update(
            await utils.publish_etas(
                redis_store,
                redis_eta_payload_processed,
                now,
                1,
                delta_time=-eta_num,
                time_left=2500 + 2 * eta_num,
                distance_left=500 + 2 * eta_num,
                driver_id='dbid_uuid_2',
                cache_is_empty=False,
                service_id='processing:driving',
            ),
        )
    assert etas_payload_processed.times_called == 0
    assert timelefts_payload_processed.times_called > 0

    assert len(cache) == 3
    assert cache == {
        'dbid_uuid_1_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa': [
            {
                'driver_eta': {'distance_left': 505.0, 'time_left': 2505},
                'timestamp': '2020-05-01T21:00:05+00:00',
            },
            {
                'driver_eta': {'distance_left': 506.0, 'time_left': 2506},
                'timestamp': '2020-05-01T21:00:06+00:00',
            },
            {
                'driver_eta': {'distance_left': 507.0, 'time_left': 2507},
                'timestamp': '2020-05-01T21:00:07+00:00',
            },
            {
                'driver_eta': {'distance_left': 508.0, 'time_left': 2508},
                'timestamp': '2020-05-01T21:00:08+00:00',
            },
            {
                'driver_eta': {'distance_left': 509.0, 'time_left': 2509},
                'timestamp': '2020-05-01T21:00:09+00:00',
            },
        ],
        'dbid_uuid_1_bbbbbbbbbbbbbbbbbbbbbbbbbbb': [
            {
                'driver_eta': {'distance_left': 495.0, 'time_left': 2495},
                'timestamp': '2020-05-01T21:00:05+00:00',
            },
            {
                'driver_eta': {'distance_left': 494.0, 'time_left': 2494},
                'timestamp': '2020-05-01T21:00:06+00:00',
            },
            {
                'driver_eta': {'distance_left': 493.0, 'time_left': 2493},
                'timestamp': '2020-05-01T21:00:07+00:00',
            },
            {
                'driver_eta': {'distance_left': 492.0, 'time_left': 2492},
                'timestamp': '2020-05-01T21:00:08+00:00',
            },
            {
                'driver_eta': {'distance_left': 491.0, 'time_left': 2491},
                'timestamp': '2020-05-01T21:00:09+00:00',
            },
        ],
        'dbid_uuid_2_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa': [
            {
                'driver_eta': {'distance_left': 510.0, 'time_left': 2510},
                'timestamp': '2020-05-01T21:00:05+00:00',
            },
            {
                'driver_eta': {'distance_left': 512.0, 'time_left': 2512},
                'timestamp': '2020-05-01T21:00:06+00:00',
            },
            {
                'driver_eta': {'distance_left': 514.0, 'time_left': 2514},
                'timestamp': '2020-05-01T21:00:07+00:00',
            },
            {
                'driver_eta': {'distance_left': 516.0, 'time_left': 2516},
                'timestamp': '2020-05-01T21:00:08+00:00',
            },
            {
                'driver_eta': {'distance_left': 518.0, 'time_left': 2518},
                'timestamp': '2020-05-01T21:00:09+00:00',
            },
        ],
    }


@pytest.mark.now('2020-01-01T12:01:10')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_MAX_ITEMS_PER_DRIVER=5,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
async def test_multiple_orders_timelefts(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        taxi_config,
        stq_runner,
        mockserver,
        load_json,
        redis_store,
        now,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    taxi_config.set(ETA_AUTOREORDER_GEOBUS_SETTINGS={'use_timelefts': True})
    await taxi_eta_autoreorder.enable_testpoints()
    #  check that order 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' is not reordered
    #  until the eta for this order arrives
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 0
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )
    order_ids = ('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',)
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        time_left=400,
        distance_left=5500,
        cache_is_empty=False,
        service_id='processing:driving',
        order_ids=order_ids,
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 1
    data = possible_reorder_detected.next_call()
    assert data['order_id'] == order_ids[0]

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        time_left=400,
        distance_left=5500,
        cache_is_empty=False,
        service_id='processing:driving',
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 2
    reordered_ids = sorted(
        [possible_reorder_detected.next_call()['order_id'] for _ in range(2)],
    )
    assert reordered_ids == [
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    ]


@pytest.mark.now('2020-01-01T12:01:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True, ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.parametrize('use_timelefts', [True, False])
@pytest.mark.parametrize(
    'abs_dist_diff, rel_dist_diff, abs_eta_diff, rel_eta_diff, fail',
    [
        (None, None, None, None, False),
        (1000, None, None, None, False),
        (None, None, None, 3, False),
        (None, 1.05, None, None, True),
        (None, None, 50, None, True),
        (250, 1.05, 50, 1.1, True),
        (250, 3, 50, None, False),
        (250, 1.05, 150, 1.1, False),
    ],
)
async def test_timelefts_difference_logging(
        taxi_eta_autoreorder,
        taxi_config,
        testpoint,
        mockserver,
        load_json,
        stq_runner,
        redis_store,
        now,
        use_timelefts,
        abs_dist_diff,
        rel_dist_diff,
        abs_eta_diff,
        rel_eta_diff,
        fail,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @testpoint('processing_and_timelefts_differ')
    def processing_and_timelefts_differ(driver_id_order_id):
        return driver_id_order_id

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    config = {
        'use_timelefts': use_timelefts,
        'absolute_distance_difference': abs_dist_diff,
        'relative_distance_difference': rel_dist_diff,
        'absolute_eta_difference': abs_eta_diff,
        'relative_eta_difference': rel_eta_diff,
    }
    config = {
        name: value for name, value in config.items() if value is not None
    }
    taxi_config.set(ETA_AUTOREORDER_GEOBUS_SETTINGS=config)

    await taxi_eta_autoreorder.enable_testpoints()

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        time_left=400,
        distance_left=5500,
        cache_is_empty=False,
        service_id='processing:driving',
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    if fail:
        assert processing_and_timelefts_differ.times_called == 1
    else:
        assert processing_and_timelefts_differ.times_called == 0


@pytest.mark.now('2020-01-01T12:01:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'published_eta, initial_eta, cached_eta_info',
    [
        # no published eta, processing doesn't fail
        ([], [], []),
        (
            [{'eta': 100, 'distance': 1000, 'time_delta': 10}],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
            ],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
            ],
        ),
        # only the first eta stays
        (
            [
                {'eta': 100, 'distance': 1000, 'time_delta': 10},
                {'eta': 200, 'distance': 2000, 'time_delta': 10},
                {'eta': 300, 'distance': 3000, 'time_delta': 10},
            ],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
            ],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
                {
                    'eta': 200,
                    'distance': 2000,
                    'timestamp': '2020-01-01T12:01:10+00:00',
                },
                {
                    'eta': 300,
                    'distance': 3000,
                    'timestamp': '2020-01-01T12:01:20+00:00',
                },
            ],
        ),
        # after the cache is cleared we change the eta we consider initial
        (
            [
                {'eta': 100, 'distance': 1000, 'time_delta': 30},
                {'eta': 200, 'distance': 2000, 'time_delta': 80},
                {'eta': 300, 'distance': 3000, 'time_delta': 10},
                {'eta': 400, 'distance': 4000, 'time_delta': 10},
            ],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
                {
                    'eta': 200,
                    'distance': 2000,
                    'timestamp': '2020-01-01T12:02:50+00:00',
                },
            ],
            [
                {
                    'eta': 100,
                    'distance': 1000,
                    'timestamp': '2020-01-01T12:01:00+00:00',
                },
                {
                    'eta': 200,
                    'distance': 2000,
                    'timestamp': '2020-01-01T12:02:50+00:00',
                },
                {
                    'eta': 300,
                    'distance': 3000,
                    'timestamp': '2020-01-01T12:02:50+00:00',
                },
                {
                    'eta': 400,
                    'distance': 4000,
                    'timestamp': '2020-01-01T12:03:00+00:00',
                },
            ],
        ),
    ],
)
async def test_initial_geobus_eta_set(
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        taxi_config,
        mocked_time,
        mockserver,
        load_json,
        stq_runner,
        published_eta,
        initial_eta,
        cached_eta_info,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['econom']['estimated_time'] = 200
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('geobus-eta_queue_cleanup')
    def redis_eta_queue_cleanup(data):
        return data

    @testpoint('set_initial_driver_info')
    def set_initial_driver_info(data):
        return data

    @testpoint('emplaced_into_driver_etas')
    def emplaced_into_driver_etas(data):
        return data

    await taxi_eta_autoreorder.enable_testpoints()
    await taxi_eta_autoreorder.invalidate_caches()

    cache_ttl = taxi_config.get('ETA_AUTOREORDER_ETA_CACHE_TTL')
    for eta_item in published_eta:
        mocked_time.sleep(eta_item['time_delta'])
        now = now + datetime.timedelta(seconds=eta_item['time_delta'])
        if eta_item['time_delta'] > cache_ttl:
            await taxi_eta_autoreorder.run_task('cleanup_driver_eta_cache')
            assert redis_eta_queue_cleanup.times_called == 1

        await utils.publish_etas(
            redis_store,
            redis_eta_payload_processed,
            now,
            1,
            time_left=eta_item['eta'],
            distance_left=eta_item['distance'],
        )

        await stq_runner.eta_autoreorder_run_order_processing.call(
            task_id='test_task',
        )

    assert set_initial_driver_info.times_called == len(initial_eta)
    for initial in initial_eta:
        data = set_initial_driver_info.next_call()['data']
        assert (
            data['driver_id'] == '00000000000000000000000000000000_'
            '11111111111111111111111111111111'
        )
        assert data['eta'] == initial['eta']
        assert data['distance'] == initial['distance']
        assert data['update_timestamp'] == initial['timestamp']

    assert emplaced_into_driver_etas.times_called == len(cached_eta_info)
    for eta_info in cached_eta_info:
        data = emplaced_into_driver_etas.next_call()['data']
        assert (
            data['driver_id'] == '00000000000000000000000000000000_'
            '11111111111111111111111111111111'
        )
        assert data['eta'] == eta_info['eta']
        assert data['distance'] == eta_info['distance']
        assert data['update_timestamp'] == eta_info['timestamp']


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'initial_geobus_etas_orders_ids, geobus_etas_orders_ids, '
    'initial_eta, eta, initial_dist, dist, reorder_rules',
    [
        ([], [], 300, 600, 5000, 5000, []),
        (['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'], [], 150, 300, 5000, 5000, []),
        (
            ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'],
            ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'],
            150,
            300,
            5000,
            5000,
            ['eta_rel_check'],
        ),
        (
            ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'],
            ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'],
            300,
            302,
            2500,
            5000,
            ['dist_rel_check'],
        ),
        (
            ['cccccccccccccccccccccccccccccccc'],
            ['cccccccccccccccccccccccccccccccc'],
            150,
            302,
            2500,
            5000,
            ['eta_rel_check', 'dist_rel_check'],
        ),
    ],
)
async def test_initial_driver_eta_taken_from_geobus(
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        initial_geobus_etas_orders_ids,
        geobus_etas_orders_ids,
        initial_eta,
        eta,
        initial_dist,
        dist,
        reorder_rules,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['econom']['estimated_time'] = 200
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('using_first_geobus_eta_as_initial')
    def using_first_geobus_eta(order_id):
        return order_id

    @testpoint('set_initial_driver_info')
    def set_initial_driver_info(data):
        return data

    @testpoint('reorder_rule_applied_checks')
    def reorder_rule_applied_checks(applied_checks):
        return applied_checks

    await taxi_eta_autoreorder.enable_testpoints()
    await taxi_eta_autoreorder.invalidate_caches()

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        1,
        time_left=initial_eta,
        distance_left=initial_dist,
        order_ids=initial_geobus_etas_orders_ids,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        1,
        time_left=eta,
        distance_left=dist,
        order_ids=geobus_etas_orders_ids,
    )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert set_initial_driver_info.times_called == len(
        initial_geobus_etas_orders_ids,
    )
    assert initial_geobus_etas_orders_ids == utils.get_sorted_testpoint_calls(
        using_first_geobus_eta, 'order_id',
    )

    if geobus_etas_orders_ids:
        applied_checks = reorder_rule_applied_checks.next_call()[
            'applied_checks'
        ]
        assert applied_checks == reorder_rules


@pytest.mark.now('2020-01-01T12:01:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'order_id, etas, dists, expect_log',
    [
        (
            'cccccccccccccccccccccccccccccccc',
            [250, 500, 501, 502, 503, 504, 505, 506],
            [2500, 5000, 5001, 5002, 5003, 5004, 5005, 5006],
            True,
        ),
        (
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            [250, 500, 501],
            [2500, 5000, 5001],
            False,
        ),
    ],
)
async def test_yt_log_first_jump_only(
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        order_id,
        etas,
        dists,
        expect_log,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('log_first_jump_detection')
    def log_first_jump_detection(data):
        return data

    await taxi_eta_autoreorder.enable_testpoints()
    await taxi_eta_autoreorder.invalidate_caches()

    for eta, dist in zip(etas, dists):
        now = now + datetime.timedelta(seconds=5)
        await utils.publish_etas(
            redis_store,
            redis_eta_payload_processed,
            now,
            1,
            time_left=eta,
            distance_left=dist,
            order_ids=[order_id],
        )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    if expect_log:
        assert log_first_jump_detection.times_called == 1
        assert log_first_jump_detection.next_call()['data'] == [
            '00000000000000000000000000000000_'
            '11111111111111111111111111111111_' + order_id,
            {
                'time_left': 504,
                'distance_left': 5004.0,
                'geobus_timestamp': '2020-01-01T12:01:30+00:00',
                'eta_autoreorder_timestamp': '2020-01-01T12:01:00+00:00',
            },
        ]
    else:
        assert log_first_jump_detection.times_called == 0
