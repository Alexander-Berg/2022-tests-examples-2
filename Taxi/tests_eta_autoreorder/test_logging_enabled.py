import datetime as dt

import pytest

import tests_eta_autoreorder.utils as utils

BASE_ORDER_IDS = ('enabled_reorder_and_enabled_logging',)

ALL_ORDER_IDS = ['1', '2', '3', '4', '5', '6']

LOCAL_TIMEZONE = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo


@pytest.mark.now('2020-02-01T12:00:40')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=120,
)
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_logging_enabled_base.json')
@pytest.mark.pgsql('eta_autoreorder', files=['base_orders.sql'])
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_DRW_LOGGING_SETTINGS={
        'enabled': True,
        'orders_cache_check_interval': 5,
    },
)
@pytest.mark.parametrize('is_experiment_caching_enabled', [False, True])
async def test_reorder_at_logging_enabled(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        taxi_config,
        is_experiment_caching_enabled,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        return response

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_autoreorder_allowed_by_config')
    def allowed_by_config(flag):
        return flag

    @testpoint('logging_enabled')
    def logging_enabled(order_id):
        return order_id

    @testpoint('logging_enabled_caching')
    def logging_enabled_caching(caching):
        return caching

    taxi_config.set(
        ETA_AUTOREORDER_EXPERIMENT_CACHING_ENABLED={
            'logging_enabled': is_experiment_caching_enabled,
            'reorder_detection_rules': is_experiment_caching_enabled,
        },
    )
    await taxi_eta_autoreorder.invalidate_caches()

    await taxi_eta_autoreorder.enable_testpoints()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        order_ids=BASE_ORDER_IDS,
        cache_is_empty=False,
    )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    if is_experiment_caching_enabled:
        assert logging_enabled_caching.times_called == 1
    else:
        assert logging_enabled_caching.times_called == 0
    assert logging_enabled.times_called == 1
    logging_enabled_data = logging_enabled.next_call()
    logging_enabled_id = logging_enabled_data['order_id']
    assert logging_enabled_id == 'enabled_reorder_and_enabled_logging'

    assert allowed_by_config.times_called == 0


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['all_orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.experiments3(filename='experiments3_logging_enabled_full.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_DRW_LOGGING_SETTINGS={
        'enabled': True,
        'orders_cache_check_interval': 5,
    },
)
@pytest.mark.parametrize('turn_off_logging', [False, True])
async def test_logging_experiment(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        mocked_time,
        turn_off_logging,
        taxi_config,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response_all_orders.json')
        return response

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    @testpoint('log_response_to_yt')
    def log_response(response):
        return response

    @testpoint('get_experiment_value_in_geobus_eta')
    def get_experiment_geobus_eta(order_id):
        return order_id

    @testpoint('log_initial_driver_info')
    def log_initial_driver_info(order_id):
        return order_id

    # orders
    # 1 - log under experiment, do not reorder
    # 2 - wrong zone for experiment, reorder
    # 3 - wrong tariff for experiment, reorder
    # 4 - wrong phone_id for experiment, reorder
    # 5 - wrong order_id for experiment, reorder
    # 6 - log under experiment, but first eta from drw
    # received before the order is in cache
    # write first eta independently under experiment
    # do not reorder

    if turn_off_logging:
        taxi_config.set_values(
            {'ETA_AUTOREORDER_DRW_LOGGING_SETTINGS': {'enabled': False}},
        )
    await taxi_eta_autoreorder.enable_testpoints()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await taxi_eta_autoreorder.invalidate_caches()
    mocked_time.sleep(1)
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        1,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task_handle_driving',
        kwargs={
            'performer': {
                'uuid': '11111111111111111111111111111111',
                'dbid': '00000000000000000000000000000000',
                'distance': 982,
                'time': 296,
            },
            'event_key': 'handle_driving',
            'order_id': '6',
            'user_phone_id': '321',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2020-01-01T12:00:00+0000'},
            'tariff_class': 'econom',
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        },
    )
    await taxi_eta_autoreorder.invalidate_caches()
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        1,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    mocked_time.sleep(2)
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert possible_reorder_detected.times_called == (
        4 if not turn_off_logging else 5
    )
    assert (
        utils.get_sorted_testpoint_calls(possible_reorder_detected, 'order_id')
        == (
            ['2', '3', '4', '5']
            if not turn_off_logging
            else ['1', '2', '3', '4', '5']
        )
    )

    # check only 1 experiment request for every order in geobus_eta
    assert utils.get_sorted_testpoint_calls(
        get_experiment_geobus_eta, 'order_id',
    ) == (ALL_ORDER_IDS if not turn_off_logging else [])

    assert utils.get_sorted_testpoint_calls(
        log_initial_driver_info, 'order_id',
    ) == (['6'] if not turn_off_logging else [])

    def set_local_timezone(value):
        return (
            dt.datetime.fromisoformat(value)
            .astimezone(LOCAL_TIMEZONE)
            .isoformat()
        )

    etalon_log = []

    if not turn_off_logging:
        etalon_log = load_json('etalon_log.json')
        for order in etalon_log:
            order['timestamp'] = set_local_timezone(order['timestamp'])

    assert (
        utils.get_sorted_testpoint_calls(log_response, 'response', 'timestamp')
        == etalon_log
    )
