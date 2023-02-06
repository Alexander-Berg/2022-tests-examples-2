# pylint: disable=import-error
import datetime
import math

import bson
import pytest


import tests_eta_autoreorder.utils as utils


ALL_ORDER_IDS = (
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'cccccccccccccccccccccccccccccccc',
    'aaa',
    'bbb',
    'ccc',
    'ddd',
)


@pytest.mark.now('2020-01-01T12:02:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True, ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'initial_distance, initial_eta, delta_time, num_geobus_etas,'
    'expected_rule_applied, expected_applied_checks',
    [
        # all check fail
        (300, 101, 0, 5, False, []),
        # abs distance check
        (10, 101, 0, 5, True, ['dist_abs_check']),
        # abs distance check, but fail by etas number
        (10, 101, 0, 2, False, ['dist_abs_check']),
        # abs distance check, but fail by check period
        (10, 101, 40, 5, False, None),
        # abs eta check
        (300, 80, 0, 5, True, ['eta_abs_check']),
        # rel dist check
        (200, 201, 0, 5, True, ['dist_rel_check']),
        # rel eta check
        (300, 180, 0, 5, True, ['eta_rel_check']),
        # abs eta and dist check
        (10, 80, 0, 5, True, ['eta_abs_check', 'dist_abs_check']),
    ],
)
async def test_config(
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        initial_distance,
        initial_eta,
        delta_time,
        num_geobus_etas,
        expected_rule_applied,
        expected_applied_checks,
        pgsql,
        mockserver,
        load_json,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        return load_json('eta_response.json')

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('has_valid_reorder_rule')
    def has_valid_reorder_rule(data):
        return data

    @testpoint('reorder_rule_applied_checks')
    def reorder_rule_applied_checks(applied_checks):
        return applied_checks

    cursor = pgsql['eta_autoreorder'].cursor()
    cursor.execute(
        f'UPDATE eta_autoreorder.orders'
        f' SET performer_initial_eta = \'{initial_eta}\','
        f'     performer_initial_distance=\'{initial_distance}\''
        f' WHERE id = \'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\'',
    )
    await taxi_eta_autoreorder.enable_testpoints()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        num_etas=num_geobus_etas,
        time_left=200,
        distance_left=300,
        delta_time=delta_time,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/check_reorder_rules')
    assert response.status_code == 200
    assert has_valid_reorder_rule.times_called == 1
    if expected_applied_checks is None:
        assert reorder_rule_applied_checks.times_called == 1
    else:
        applied_checks = reorder_rule_applied_checks.next_call()[
            'applied_checks'
        ]
        assert sorted(applied_checks) == sorted(expected_applied_checks)
    orders_fitting_rule = response.json()
    if expected_rule_applied:
        assert len(orders_fitting_rule) == 1
        assert (
            orders_fitting_rule[0]['id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
    else:
        assert not orders_fitting_rule


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'reorder_detection_rule_name, call_autoreorder_rule_name, '
    'autoreorder_called',
    [
        # empty rules
        ('empty_rules', None, False),
        # no restriction in call_autoreorder, rule is named
        ('rule', None, True),
        # restriction, but rule is not named
        (None, 'rule', False),
        # different names
        ('rule', 'other_rule', False),
        # same names
        ('rule', 'rule', True),
    ],
)
async def test_rules_check_in_run_order_processing(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        experiments3,
        reorder_detection_rule_name,
        call_autoreorder_rule_name,
        autoreorder_called,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    # set eta_autoreorder_reorder_detection_rules config
    target_rule_number = 5
    reorder_rules_json = load_json('experiments3_reorder_detection_rules.json')
    if reorder_detection_rule_name == 'empty_rules':
        reorder_rules_json['configs'][0]['clauses'][0]['value'][
            'rules_by_eta'
        ] = []
    elif reorder_detection_rule_name is not None:
        reorder_rules_json['configs'][0]['clauses'][0]['value'][
            'rules_by_eta'
        ][target_rule_number]['eta_rule_name'] = reorder_detection_rule_name
    experiments3.add_experiments_json(reorder_rules_json)

    # set eta_autoreorder_call_autoreorder experiment
    if call_autoreorder_rule_name is not None:
        call_autoreorder_json = load_json('experiments3_call_autoreorder.json')
        call_autoreorder_json['experiments'][0]['clauses'][0]['predicate'][
            'init'
        ]['predicates'].append(
            {
                'init': {
                    'arg_name': 'eta_rule_name',
                    'arg_type': 'string',
                    'value': call_autoreorder_rule_name,
                },
                'type': 'eq',
            },
        )
        experiments3.add_experiments_json(call_autoreorder_json)

    await taxi_eta_autoreorder.enable_testpoints()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    if reorder_detection_rule_name == 'empty_rules':
        assert possible_reorder_detected.times_called == 0
    else:
        assert possible_reorder_detected.times_called == 1
        reorder_detected_data = possible_reorder_detected.next_call()
        detected_order_id = reorder_detected_data['order_id']
        assert detected_order_id == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    await taxi_eta_autoreorder.invalidate_caches()
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 0

    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    orders = sorted(response.json(), key=lambda order: order['id'])

    assert len(orders) == 3
    assert orders[0]['id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert orders[0]['autoreorder_in_progress'] == autoreorder_called
    assert (
        orders[0]['last_autoreorder_detected'] == '2020-01-01T12:00:00+00:00'
    )
    assert not orders[1]['autoreorder_in_progress']


BASIC_EVENT = {
    'order_id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'user_phone_id': '6141a81573872fb3b53037ed',
    'zone_id': 'moscow',
    'tariff_class': 'vip',
    'event_key': 'handle_driving',
    'event_timestamp': {'$date': '2020-01-01T12:01:01.000Z'},
    'performer': {
        'uuid': '11111111111111111111111111111112',
        'dbid': '00000000000000000000000000000001',
        'distance': 5000,
        'time': 300,
        'cp_id': None,
    },
    'point_a': [20, 30],
    'destinations': [],
    'requirements': {},
}


@pytest.mark.now('2020-01-01T12:01:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_CALL_AUTOREORDER_EXPERIMENT_FALLBACK=True,
    ETA_AUTOREORDER_API_PROXY_CONFIG_STATUS_INFO_ENABLED=True,
)
@pytest.mark.parametrize('is_experiment_caching_enabled', [False, True])
async def test_reorder_in_run_order_processing(
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
    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        await stq_runner.eta_autoreorder_order_status_changed.call(
            task_id='test_task', kwargs=BASIC_EVENT,
        )
        body = bson.BSON(request.get_data()).decode()
        assert body['extra_update']['$push']['autoreorder.decisions'] == {
            'created': datetime.datetime(2020, 1, 1, 12, 1),
            'reason': 'eta-autoreorder',
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('reorder_detection_rules_caching')
    def reorder_detection_rules_caching(caching):
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
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    await taxi_eta_autoreorder.invalidate_caches()
    if is_experiment_caching_enabled:
        assert reorder_detection_rules_caching.times_called == 5
    else:
        assert reorder_detection_rules_caching.times_called == 0

    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    cur_order = None
    for order in response.json():
        if order['id'] == BASIC_EVENT['order_id']:
            cur_order = order
    assert cur_order
    new_performer = BASIC_EVENT['performer']
    dbid_uuid = new_performer['dbid'] + '_' + new_performer['uuid']
    assert cur_order['performer_dbid_uuid'] == dbid_uuid
    assert cur_order['eta_autoreorders_count'] == 1


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'call_autoreorder_experiment, call_autoreorder_fallback,'
    'autoreorder_situations_happened, autoreorder_calls_expected',
    [
        # Experiment enables autoreorder, fallback value doesn't matter
        (True, False, 1, 1),
        # Experiment disables autoreorder, fallback value doesn't matter
        (False, True, 1, 0),
        # Experiment doesn't exist, fallback value enables autoreorder
        (None, True, 1, 1),
        # Experiment doesn't exist, fallback value disables autoreorder
        (None, False, 0, 0),
    ],
)
async def test_reorder_enabled_in_run_order_processing(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        taxi_config,
        mockserver,
        load_json,
        experiments3,
        stq_runner,
        call_autoreorder_experiment,
        call_autoreorder_fallback,
        autoreorder_situations_happened,
        autoreorder_calls_expected,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    experiment_json = load_json('experiments3_reorder_detection_rules.json')
    if call_autoreorder_experiment is not None:
        call_autoreorder_json = load_json('experiments3_call_autoreorder.json')
        experiment_json.update(call_autoreorder_json)
        clauses = experiment_json['experiments'][0]['clauses']
        clauses[0]['value']['enabled'] = call_autoreorder_experiment

    experiments3.add_experiments_json(experiment_json)
    taxi_config.set(
        ETA_AUTOREORDER_CALL_AUTOREORDER_EXPERIMENT_FALLBACK=(
            call_autoreorder_fallback
        ),
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
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert (
        possible_reorder_detected.times_called
        == autoreorder_situations_happened
    )
    assert mock_autoreorder.times_called == autoreorder_calls_expected


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize('call_autoreorder', [True, False])
async def test_experiment_filtration(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        taxi_config,
        mocked_time,
        mockserver,
        load_json,
        stq_runner,
        call_autoreorder,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    taxi_config.set(ETA_AUTOREORDER_CALL_AUTOREORDER=call_autoreorder)
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
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    expected_autoreorder_called = 1 if call_autoreorder else 0
    assert possible_reorder_detected.times_called == 1
    assert mock_autoreorder.times_called == expected_autoreorder_called

    mocked_time.sleep(1)
    await taxi_eta_autoreorder.invalidate_caches()

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 1
    assert mock_autoreorder.times_called == expected_autoreorder_called


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER_EXPERIMENT_FALLBACK=True,
)
async def test_statisctics_fallback_enabled(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        statistics,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    async with statistics.capture(taxi_eta_autoreorder) as capture:
        statistics.fallbacks = ['eta-autoreorder.fallback-many-autoreorders']
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
            order_ids=ALL_ORDER_IDS,
            cache_is_empty=False,
        )
        await stq_runner.eta_autoreorder_run_order_processing.call(
            task_id='test_task',
        )

    assert capture.statistics['eta-autoreorder.autoreorders'] == 1
    assert possible_reorder_detected.times_called == 1
    assert mock_autoreorder.times_called == 0


@pytest.mark.now('2020-01-01T12:00:00')
@pytest.mark.pgsql('eta_autoreorder', files=['reorder_limit_orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='reorder_limit.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
)
async def test_reorder_limit(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
):
    #  the test contains 4 orders with all parameters equal
    #  except for the eta_autoreorder_count
    total_orders = 4
    expected_reorder_number = 2
    #  orders eligible for reorder, eta_autoreorder_count < 3
    expected_ids = ['ccc', 'ddd']
    #  orders not eligible for reorder because their eta_autoreorder_count >= 3
    unexpected_ids = ['aaa', 'bbb']

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def _mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] in expected_ids
        return mockserver.make_response('', status=200)

    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        return load_json('eta_response.json')

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('has_reached_reorder_limit')
    def has_reached_reorder_limit(order_id):
        return order_id

    @testpoint('has_not_reached_reorder_limit')
    def has_not_reached_reorder_limit(order_id):
        return order_id

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    await taxi_eta_autoreorder.enable_testpoints()

    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )

    await taxi_eta_autoreorder.invalidate_caches()

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert (
        has_not_reached_reorder_limit.times_called == expected_reorder_number
    )
    assert expected_ids == sorted(
        [
            has_not_reached_reorder_limit.next_call()['order_id']
            for _ in range(expected_reorder_number)
        ],
    )
    assert (
        has_reached_reorder_limit.times_called
        == total_orders - expected_reorder_number
    )
    assert unexpected_ids == sorted(
        [
            has_reached_reorder_limit.next_call()['order_id']
            for _ in range(total_orders - expected_reorder_number)
        ],
    )
    assert possible_reorder_detected.times_called == expected_reorder_number
    assert expected_ids == sorted(
        [
            possible_reorder_detected.next_call()['order_id']
            for _ in range(expected_reorder_number)
        ],
    )


MINUTE = 1 / 60  # angular minute in degrees


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER_EXPERIMENT_FALLBACK=True,
)
@pytest.mark.parametrize(
    'driver_position, critial_distance, reorder, expected_distance',
    # 1 sea mile distance -> 1 angular minute -> 0.016666667 in degrees -
    # approx 1850m
    # distance is approximately 1/10 of a sea mile <= critical_distance = 200
    [
        (
            [
                37.49133517428459
                + MINUTE / 10 / 2 ** 0.5 / math.cos(55.66009198731399),
                55.66009198731399 - MINUTE / 10 / 2 ** 0.5,
            ],
            200,
            0,
            185,
        ),
        # distance is approximately 1 sea mile in latitude >
        # critical_distance = 200
        ([37.49133517428459, 55.66009198731399 + MINUTE], 200, 1, 1850),
    ],
)
async def test_close_driver(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        experiments3,
        stq_runner,
        driver_position,
        critial_distance,
        reorder,
        expected_distance,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    @testpoint('distance_check_passed')
    def distance_check_passed(info):
        assert (
            info['current_linear_distance'] >= info['critical_linear_distance']
        )
        return info

    @testpoint('driver_too_close_for_autoreorder')
    def driver_too_close_forautoreorder(info):
        assert (
            info['current_linear_distance'] < info['critical_linear_distance']
        )
        return info

    experiment_json = load_json('experiments3_reorder_detection_rules.json')
    experiment_json['configs'][0]['clauses'][0]['value'][
        'minimum_linear_distance'
    ] = critial_distance
    experiments3.add_experiments_json(experiment_json)
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
        position=driver_position,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == reorder
    assert mock_autoreorder.times_called == reorder
    assert distance_check_passed.times_called == reorder
    assert driver_too_close_forautoreorder.times_called == 1 - reorder
    # check distance calculated is approximately correct
    if reorder == 1:
        distance = distance_check_passed.next_call()['info'][
            'current_linear_distance'
        ]
    else:
        distance = driver_too_close_forautoreorder.next_call()['info'][
            'current_linear_distance'
        ]
    assert abs(distance - expected_distance) < 10


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER_EXPERIMENT_FALLBACK=True,
)
@pytest.mark.parametrize(
    'driver_position, critial_distance, reorder, expected_distance',
    [
        (
            [
                37.49133517428459
                + MINUTE / 10 / 2 ** 0.5 / math.cos(55.66009198731399),
                55.66009198731399 - MINUTE / 10 / 2 ** 0.5,
            ],
            200,
            1,
            185,
        ),
    ],
)
async def test_close_driver_fallback(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        experiments3,
        stq_runner,
        driver_position,
        critial_distance,
        reorder,
        expected_distance,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    @testpoint('no_driver_geobus_info')
    def no_driver_geobus_info(info):
        return info

    @testpoint('clear_driver_eta_cache_before_linear_distance_check')
    async def clear_driver_eta_cache(data):
        await taxi_eta_autoreorder.run_task('clear_driver_eta_cache')
        return data

    experiment_json = load_json('experiments3_reorder_detection_rules.json')
    experiment_json['configs'][0]['clauses'][0]['value'][
        'minimum_linear_distance'
    ] = critial_distance
    experiments3.add_experiments_json(experiment_json)
    await taxi_eta_autoreorder.enable_testpoints()
    await taxi_eta_autoreorder.invalidate_caches()
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        position=driver_position,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == reorder
    assert no_driver_geobus_info.times_called == reorder
    assert clear_driver_eta_cache.times_called == 1
    assert mock_autoreorder.times_called == 1


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['reorder_chain_orders.sql'])
@pytest.mark.experiments3(filename='reorder_chain.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
async def test_rules_for_chain_orders(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        stq_runner,
        experiments3,
):
    @testpoint('has_valid_reorder_rule')
    def has_valid_reorder_rule(data):
        return data

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert has_valid_reorder_rule.times_called == 1
    assert (
        has_valid_reorder_rule.next_call()['data']
        == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    )
