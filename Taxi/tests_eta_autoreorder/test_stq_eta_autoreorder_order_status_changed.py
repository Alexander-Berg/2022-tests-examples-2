import copy
import datetime

import pytest

import tests_eta_autoreorder.order_status_change_utils as outils
import tests_eta_autoreorder.utils as utils


BASIC_EVENT = outils.BASIC_EVENT
EVENT_PERFORMER_CHANGED = outils.EVENT_PERFORMER_CHANGED
TEST_ITEMS = outils.TEST_ITEMS
ALL_ORDER_IDS = outils.ALL_ORDER_IDS


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_task_call(taxi_eta_autoreorder, stq_runner, testpoint):
    @testpoint('eta_autoreorder_order_status_changed')
    def testpoint_call(args):
        assert args == {
            'order_id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'event_key': 'handle_assigning',
            'event_timestamp': '2020-01-01T12:00:00+00:00',
            'performer': {
                'dbid': '00000000000000000000000000000000',
                'uuid': '11111111111111111111111111111111',
                'distance': 5000,
                'time': 300,
            },
            'point_a': [20, 30],
            'destinations': [],
            'requirements': {},
        }
        return {}

    await taxi_eta_autoreorder.enable_testpoints()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT,
    )
    await testpoint_call.wait_call()


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=False)
async def test_service_disabled(
        taxi_eta_autoreorder, stq_runner, stq, testpoint,
):
    @testpoint('eta_autoreorder_order_status_changed')
    def testpoint_call(args):
        return {}

    await taxi_eta_autoreorder.enable_testpoints()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT,
    )
    assert testpoint_call.times_called == 0


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
@pytest.mark.config(ETA_AUTOREORDER_ORDER_STATUS_EVENTS_TTL=5)
@pytest.mark.now('2020-01-01T12:04:00+00:00')
async def test_order_status_event_ttl(
        taxi_eta_autoreorder, stq_runner, stq, testpoint, mocked_time,
):
    @testpoint('eta_autoreorder_order_status_changed')
    def testpoint_call(args):
        return {}

    await taxi_eta_autoreorder.enable_testpoints()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT,
    )
    assert testpoint_call.times_called == 1

    mocked_time.sleep(120)
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT,
    )
    assert testpoint_call.times_called == 1


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
@pytest.mark.config(ETA_AUTOREORDER_ORDER_STATUS_CHANGED_MAX_ATTEMPTS=3)
async def test_max_attempts(taxi_eta_autoreorder, stq_runner, stq, testpoint):
    @testpoint('eta_autoreorder_order_status_changed')
    def testpoint_call(args):
        return {'inject_error': True}

    await taxi_eta_autoreorder.enable_testpoints()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT, expect_fail=True,
    )
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task',
        kwargs=BASIC_EVENT,
        exec_tries=3,
        expect_fail=False,
    )
    assert testpoint_call.times_called == 2


@pytest.mark.parametrize(
    'event_key', ['handle_transporting', 'handle_waiting', 'handle_finish'],
)
@pytest.mark.pgsql('eta_autoreorder', files=['default_orders.sql'])
@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_terminal_event(
        taxi_eta_autoreorder, stq_runner, stq, event_key,
):
    kwargs = copy.deepcopy(BASIC_EVENT)
    kwargs['event_key'] = event_key

    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert kwargs['order_id'] in {order['id'] for order in response.json()}

    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=kwargs,
    )

    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert kwargs['order_id'] not in {order['id'] for order in response.json()}


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_order_in_database(taxi_eta_autoreorder, stq_runner, testpoint):
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=BASIC_EVENT,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert BASIC_EVENT['order_id'] in {
        order['id'] for order in response.json()
    }
    assert len(response.json()) == 1


@pytest.mark.pgsql(
    'eta_autoreorder', files=['orders_with_reordering_order.sql'],
)
@pytest.mark.parametrize(
    'invalidate_cache_before_status_changed', [True, False],
)
@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_reorder_in_database(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        invalidate_cache_before_status_changed,
):
    if invalidate_cache_before_status_changed:
        await taxi_eta_autoreorder.invalidate_caches()
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=EVENT_PERFORMER_CHANGED,
    )

    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert len(response.json()) == 1
    order = response.json()[0]
    assert order['id'] == EVENT_PERFORMER_CHANGED['order_id']

    new_performer = EVENT_PERFORMER_CHANGED['performer']
    dbid_uuid = new_performer['dbid'] + '_' + new_performer['uuid']
    assert order['performer_dbid_uuid'] == dbid_uuid
    assert order['eta_autoreorders_count'] == 1
    assert order['performer_initial_distance'] == new_performer['distance']
    assert order['performer_initial_eta'] == new_performer['time']


@pytest.mark.pgsql(
    'eta_autoreorder', files=['orders_with_reordering_order.sql'],
)
@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_skipped_status_change(
        taxi_eta_autoreorder, stq_runner, testpoint,
):
    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert len(response.json()) == 1
    order_before_status_change = response.json()[0]

    date_in_the_past = '2020-01-01T11:05:00.000Z'
    EVENT_PERFORMER_CHANGED['event_timestamp']['$date'] = date_in_the_past
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=EVENT_PERFORMER_CHANGED,
    )

    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert len(response.json()) == 1
    order = response.json()[0]
    assert order == order_before_status_change


@pytest.mark.parametrize(
    'cp_id_by_performer_uuid',
    [
        {
            '00000000000000000000000000000000': None,
            '957600cda6b74ca58fe20963d61ff060': None,
            'ca5ed75b30de4a748da0db193a7092a2': None,
        },
        {
            '00000000000000000000000000000000': None,
            '957600cda6b74ca58fe20963d61ff060': 'test1',
            'ca5ed75b30de4a748da0db193a7092a2': 'test2',
        },
        {
            '00000000000000000000000000000000': None,
            '957600cda6b74ca58fe20963d61ff060': 'test1',
            'ca5ed75b30de4a748da0db193a7092a2': None,
        },
    ],
)
@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
async def test_all_events_task_call(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        pgsql,
        statistics,
        cp_id_by_performer_uuid,
):
    @testpoint('eta_autoreorder_order_status_changed')
    def testpoint_order_status_changed(args):
        return args

    await taxi_eta_autoreorder.run_task('reset_orders_statistics')

    async with statistics.capture(taxi_eta_autoreorder) as capture:
        statistics.fallbacks = ['eta-autoreorder.fallback-many-autoreorders']
        await taxi_eta_autoreorder.enable_testpoints()
        for test_item in TEST_ITEMS:
            kwargs = copy.deepcopy(test_item['event'])
            kwargs['performer']['cp_id'] = cp_id_by_performer_uuid[
                test_item['event']['performer']['uuid']
            ]
            await stq_runner.eta_autoreorder_order_status_changed.call(
                task_id='test_task', kwargs=kwargs,
            )
            order = outils.get_one_order_from_db_as_list(pgsql)
            expected_order = copy.deepcopy(test_item['database_order_state'])
            performer_dbid_uuid = test_item['database_order_state'][
                'performer_dbid_uuid'
            ]
            expected_order['performer_cp_id'] = cp_id_by_performer_uuid[
                performer_dbid_uuid[performer_dbid_uuid.rindex('_') + 1 :]
            ]
            assert order == outils.database_order_state_to_list(expected_order)

        assert testpoint_order_status_changed.times_called == len(TEST_ITEMS)

        for test_item in TEST_ITEMS:
            parametrized_event = copy.deepcopy(test_item['event'])
            cp_id = cp_id_by_performer_uuid[
                test_item['event']['performer']['uuid']
            ]
            if cp_id is not None:
                parametrized_event['performer']['cp_id'] = cp_id
            assert testpoint_order_status_changed.next_call()[
                'args'
            ] == outils.get_event_with_transformed_tp(parametrized_event)

    assert capture.statistics['eta-autoreorder.all_orders'] == 1


@pytest.mark.now('2019-09-10T03:23:37.733+0000')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=300,
    ETA_AUTOREORDER_ORDER_IN_DATABASE_TTL=100000,
)
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
async def test_new_driver_found_no_autoreorder(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        redis_store,
        now,
        mocked_time,
        mockserver,
        load_json,
        pgsql,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 50
        return response

    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        assert request.query['order_id'] == '1'
        return mockserver.make_response('', status=200)

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('run_order_processing_possible_reorder_situation_detected')
    def possible_reorder_detected(order_id):
        return order_id

    first_driver_found = 1
    second_driver_found = 3
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=TEST_ITEMS[first_driver_found]['event'],
    )
    await taxi_eta_autoreorder.invalidate_caches()

    #  check that order is in database after new_driver_found
    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            TEST_ITEMS[first_driver_found]['database_order_state'],
        )
    )

    first_driver_id = outils.make_driver_id(
        TEST_ITEMS[first_driver_found]['event']['performer']['dbid'],
        TEST_ITEMS[first_driver_found]['event']['performer']['uuid'],
    )
    second_driver_id = outils.make_driver_id(
        TEST_ITEMS[second_driver_found]['event']['performer']['dbid'],
        TEST_ITEMS[second_driver_found]['event']['performer']['uuid'],
    )
    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        driver_id=first_driver_id,
        time_left=700,
        distance_left=7000,
        order_ids=ALL_ORDER_IDS,
    )

    #  check that autoreorder is not called
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 0

    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            TEST_ITEMS[first_driver_found]['database_order_state'],
        )
    )

    #  add handle_driving event
    mocked_time.sleep(60)
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task',
        kwargs=TEST_ITEMS[first_driver_found + 1]['event'],
    )
    await taxi_eta_autoreorder.invalidate_caches()

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now + datetime.timedelta(seconds=50),
        5,
        delta_time=-60,
        driver_id=first_driver_id,
        time_left=700,
        distance_left=7000,
        cache_is_empty=False,
        order_ids=ALL_ORDER_IDS,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now + datetime.timedelta(seconds=50),
        5,
        driver_id=second_driver_id,
        time_left=TEST_ITEMS[second_driver_found]['event']['performer'][
            'time'
        ],
        distance_left=TEST_ITEMS[second_driver_found]['event']['performer'][
            'distance'
        ],
        cache_is_empty=False,
        order_ids=ALL_ORDER_IDS,
    )
    #  check that there is still one order in database
    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            TEST_ITEMS[first_driver_found + 1]['database_order_state'],
        )
    )

    #  check that autoreorder is now called
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )
    assert possible_reorder_detected.times_called == 1
    assert mock_autoreorder.times_called == 1

    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            {
                'order_id': '1',
                'zone_id': 'moscow',
                'tariff_class': 'vip',
                'last_event_handled': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'performer_dbid_uuid': (
                    'df98ffa680714291882343e7df1ca5ab_'
                    '957600cda6b74ca58fe20963d61ff060'
                ),
                'performer_assigned': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'performer_initial_eta': datetime.timedelta(seconds=296),
                'performer_initial_distance': 982.0,
                'first_performer_assigned': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'first_performer_initial_eta': datetime.timedelta(seconds=296),
                'first_performer_initial_distance': 982.0,
                'eta_autoreorders_count': 0,
                'last_autoreorder_detected': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'autoreorder_in_progress': True,
                'reorder_situation_detected': True,
                'last_event': 'handle_driving',
                'user_phone_id': '6141a81573872fb3b53037ed',
                'performer_cp_id': None,
                'point_a': [20.123123, 30.123123],
                'destinations': [[21.123123, 31.123123]],
                'requirements': '{"door_to_door":true}',
            },
        )
    )
    # find second driver
    mocked_time.sleep(60)
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task', kwargs=TEST_ITEMS[second_driver_found]['event'],
    )
    # check that autoreorder is still in progress
    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            {
                'order_id': '1',
                'zone_id': 'moscow',
                'tariff_class': 'vip',
                'last_event_handled': datetime.datetime(
                    2019, 9, 10, 3, 25, 37, 733000,
                ),
                'performer_dbid_uuid': (
                    'df98ffa680714291882343e7df1ca5ab_'
                    'ca5ed75b30de4a748da0db193a7092a2'
                ),
                'performer_assigned': None,
                'performer_initial_eta': datetime.timedelta(seconds=50),
                'performer_initial_distance': 200.0,
                'first_performer_assigned': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'first_performer_initial_eta': datetime.timedelta(seconds=296),
                'first_performer_initial_distance': 982.0,
                'eta_autoreorders_count': 0,
                'last_autoreorder_detected': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'autoreorder_in_progress': True,
                'reorder_situation_detected': True,
                'last_event': 'new_driver_found',
                'user_phone_id': '6141a81573872fb3b53037ed',
                'performer_cp_id': None,
                'point_a': [20.123123, 30.123123],
                'destinations': [[21.123123, 31.123123]],
                'requirements': '{"door_to_door":true}',
            },
        )
    )
    # assign second driver
    mocked_time.sleep(60)
    await stq_runner.eta_autoreorder_order_status_changed.call(
        task_id='test_task',
        kwargs=TEST_ITEMS[second_driver_found + 1]['event'],
    )
    # check that autoreorder is finished
    assert (
        outils.get_one_order_from_db_as_list(pgsql)
        == outils.database_order_state_to_list(
            {
                'order_id': '1',
                'zone_id': 'moscow',
                'tariff_class': 'vip',
                'last_event_handled': datetime.datetime(
                    2019, 9, 10, 3, 26, 37, 733000,
                ),
                'performer_dbid_uuid': (
                    'df98ffa680714291882343e7df1ca5ab_'
                    'ca5ed75b30de4a748da0db193a7092a2'
                ),
                'performer_assigned': datetime.datetime(
                    2019, 9, 10, 3, 26, 37, 733000,
                ),
                'performer_initial_eta': datetime.timedelta(seconds=50),
                'performer_initial_distance': 200.0,
                'first_performer_assigned': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'first_performer_initial_eta': datetime.timedelta(seconds=296),
                'first_performer_initial_distance': 982.0,
                'eta_autoreorders_count': 1,
                'last_autoreorder_detected': datetime.datetime(
                    2019, 9, 10, 3, 24, 37, 733000,
                ),
                'autoreorder_in_progress': False,
                'reorder_situation_detected': False,
                'last_event': 'handle_driving',
                'user_phone_id': '6141a81573872fb3b53037ed',
                'performer_cp_id': None,
                'point_a': [20.123123, 30.123123],
                'destinations': [[21.123123, 31.123123]],
                'requirements': '{"door_to_door":true}',
            },
        )
    )


@pytest.mark.now('2019-09-10T03:25:37.733+0000')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
    ETA_AUTOREORDER_ORDER_CHECKS_LOGS_ENABLED=True,
    ETA_AUTOREORDER_ETA_CACHE_TTL=60,
    ETA_AUTOREORDER_ORDER_IN_DATABASE_TTL=120,
)
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='experiments3_reorder_detection_rules.json')
@pytest.mark.parametrize('last_event_index', [3, 6, 7, 8])
async def test_new_driver_found_order_is_deleted_on_time(
        taxi_eta_autoreorder,
        stq_runner,
        taxi_config,
        mocked_time,
        mockserver,
        load_json,
        pgsql,
        last_event_index,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 50
        return response

    for driving in [True, False]:
        await taxi_eta_autoreorder.invalidate_caches()
        new_driver_found_index = 3
        await stq_runner.eta_autoreorder_order_status_changed.call(
            task_id='test_task',
            kwargs=TEST_ITEMS[new_driver_found_index]['event'],
        )

        if driving:
            mocked_time.sleep(60)
            await stq_runner.eta_autoreorder_order_status_changed.call(
                task_id='test_task',
                kwargs=TEST_ITEMS[new_driver_found_index + 1]['event'],
            )

        await taxi_eta_autoreorder.invalidate_caches()
        if last_event_index == new_driver_found_index:
            mocked_time.sleep(
                taxi_config.get('ETA_AUTOREORDER_ORDER_IN_DATABASE_TTL') * 60
                + TEST_ITEMS[new_driver_found_index]['event']['performer'][
                    'time'
                ]
                + 1,
            )
        else:
            await stq_runner.eta_autoreorder_order_status_changed.call(
                task_id='test_task',
                kwargs=TEST_ITEMS[last_event_index]['event'],
            )

        await stq_runner.eta_autoreorder_run_order_processing.call(
            task_id='test_task',
        )

        cursor = pgsql['eta_autoreorder'].cursor()
        cursor.execute('SELECT COUNT(1) from eta_autoreorder.orders')
        result = [row for row in cursor]
        assert result == [(0,)]
