import json  # noqa: F401

import pytest

import tests_driver_route_watcher.driver_position_fbs as DriverPositionFbs
import tests_driver_route_watcher.fsm_state_type_fbs as FsmStateTypeEntry
import tests_driver_route_watcher.output_entry_fbs as OutputEntryFbs
import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.watch_list as WatchList

RAW_POSITION = [37.455596, 55.719463]

ADJUSTED_POSITION = [37.455434, 55.719437]
POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
TRANSPORTING_POINTS = [
    {
        'point': POINTS[0],
        'wait_time': 1000,
        'park_time': 10,
        'order_id': 'aaaa1',
        'point_id': 'bbbb1',
    },
    {
        'point': POINTS[1],
        'wait_time': 2000,
        'park_time': 20,
        'order_id': 'aaaa2',
        'point_id': 'bbbb2',
    },
    {
        'point': POINTS[2],
        'wait_time': 4000,
        'park_time': 40,
        'order_id': 'aaaa3',
        'point_id': 'bbbb3',
    },
]
TRANSPORTING_DST = TRANSPORTING_POINTS[-1]['point']
SERVICE_ID = 'cargo-dispatch'

REDIS_STATE = [
    ['flushall'],
    [
        'hmset',
        'w/{dbid_uuidcourierbyorder}',
        {
            f'{SERVICE_ID}/d': WatchList.serialize_watchlist_entry(
                TRANSPORTING_DST,
            ),
            f'{SERVICE_ID}/m': '',
            f'{SERVICE_ID}/ps': PointlistFbs.serialize_pointslist(
                TRANSPORTING_POINTS,
            ),
            # orders counter, set by cargo/start-watch with orders in pointlist
            f'{SERVICE_ID}/c': len(POINTS),
        },
    ],
    [
        # list of tracked orders by service and driver_id
        # used to determine when all orders stoped watch
        'sadd',
        f'wos/{SERVICE_ID}/{{dbid_uuidcourierbyorder}}',
        'aaaa1',
        'aaaa2',
        'aaaa3',
    ],
    [
        'hset',
        'output:{dbid_uuidcourierbyorder}',
        'fsm_current_state',
        FsmStateTypeEntry.serialize_fsm_state_type_entry('tracking'),
    ],
    [
        'hset',
        'output:{dbid_uuidcourierbyorder}',
        'fsm_current_state_start_time',
        1234567890,
    ],
    [
        'hset',
        'output:{dbid_uuidcourierbyorder}',
        'driver_position',
        DriverPositionFbs.serialize_driver_position_entry(
            {'position': ADJUSTED_POSITION, 'transport_type': 'automobile'},
        ),
    ],
    [
        'hset',
        'output:{dbid_uuidcourierbyorder}',
        'route',
        OutputEntryFbs.serialize_route_entry(
            {
                'route': {
                    'route': [
                        {
                            'position': RAW_POSITION,
                            'time': 43,
                            'distance': 100555,
                        },
                        {
                            'position': TRANSPORTING_POINTS[0]['point'],
                            'time': 42,
                            'distance': 100500,
                        },
                        {
                            'position': TRANSPORTING_POINTS[1]['point'],
                            'time': 42 // 2,
                            'distance': 100500 // 2,
                        },
                        {
                            'position': TRANSPORTING_POINTS[2]['point'],
                            'time': 0,
                            'distance': 0,
                        },
                    ],
                    'distance': 100500,
                    'time': 142,
                    'closures': False,
                    'dead_jams': False,
                    'toll_roads': False,
                    'legs': [
                        {'segment_index': 0, 'segment_position': 0},
                        {'segment_index': 1, 'segment_position': 0},
                        {'segment_index': 2, 'segment_position': 0},
                    ],
                },
                'timestamp': 1234567890,
            },
        ),
    ],
]


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.mark.servicetest
@pytest.mark.now(1234567890)
@pytest.mark.redis_store(*REDIS_STATE)
@pytest.mark.config(DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True)
async def test_cargo_stop_watch_by_order_id(
        taxi_driver_route_watcher_adv,
        testpoint,
        load_binary,
        mockserver,
        redis_store,
):
    drw = taxi_driver_route_watcher_adv

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [ADJUSTED_POSITION] + [POINTS[1]]
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463~37.473896,55.728358.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('restore-from-storage-ok')
    def restore_from_storage_ok(data):
        assert data == {
            'current_state': 1,  # tracking state
            'current_state_start_time': '1234567890',
            'destinations_count': 1,
            'driver_position': [37.455434, 55.719437],
        }

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('stop-watch-by-order-id-message-processed')
    def stop_by_order_id_processed(data):
        pass

    @testpoint('route-message-processed')
    def route_message_processed(data):
        pass

    @testpoint('publish-timelefts')
    def publish_timelefts(data):
        assert data == {
            'contractor': 'dbid_uuidcourierbyorder',
            'etas': [
                {
                    'time_left': 390 + TRANSPORTING_POINTS[1]['park_time'],
                    'distance_left': 2525,
                    'destination': POINTS[1],
                    'order_id': 'aaaa2',
                    'point_id': 'bbbb2',
                },
            ],
            'position': ADJUSTED_POSITION,
        }

    @testpoint('reset-watch-completed')
    def reset_watch_completed(data):
        pass

    await drw.enable_testpoints()

    # wait to acquire master lock before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()
    await restore_from_storage_ok.wait_call()

    # wait to become master before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    driver_id = {'dbid': 'dbid', 'uuid': 'uuidcourierbyorder'}
    await drw.stop_watch_by_orders(
        driver_id, ['aaaa1', 'aaaa3'], service=SERVICE_ID,
    )

    await stop_by_order_id_processed.wait_call()
    await drw.run_periodic_task('RestoreMessageAggregator0')
    await route_message_processed.wait_call()
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()

    # wait publish in drw:timelefts channel
    await publish_timelefts.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert len(watch_list) == 1
    assert (
        watch_list['dbid_uuidcourierbyorder'][SERVICE_ID].get('orders')
        is not None
    )
    assert (
        watch_list['dbid_uuidcourierbyorder'][SERVICE_ID].get('destination')
        is not None
    )
    assert (
        watch_list['dbid_uuidcourierbyorder'][SERVICE_ID].get('meta')
        is not None
    )
    assert watch_list['dbid_uuidcourierbyorder'][SERVICE_ID].get('orders') == {
        'aaaa2',
    }
    assert watch_list['dbid_uuidcourierbyorder'][SERVICE_ID].get(
        'deleted_orders',
    ) == {'aaaa1', 'aaaa3'}

    await drw.stop_watch_all(driver_id, SERVICE_ID)
    await stop_watch_message_processed.wait_call()
    await reset_watch_completed.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {
        'dbid_uuidcourierbyorder': {
            SERVICE_ID: {
                'deleted_orders': {'aaaa1', 'aaaa3'},
                'service': SERVICE_ID,
            },
        },
    }

    redis_store.flushall()


@pytest.mark.servicetest
@pytest.mark.redis_store(*REDIS_STATE)
@pytest.mark.config(DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True)
async def test_cargo_stop_watch_all_order_ids(
        taxi_driver_route_watcher_adv,
        redis_store,
        testpoint,
        load_binary,
        mockserver,
):
    drw = taxi_driver_route_watcher_adv

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [ADJUSTED_POSITION] + [POINTS[1]]
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463'
                '~37.451695,55.723917~'
                '37.473896,55.728358~'
                '37.518952,55.73629.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('restore-from-storage-ok')
    def restore_from_storage_ok(data):
        assert data == {
            'current_state': 1,  # tracking state
            'current_state_start_time': '1234567890',
            'destinations_count': 1,
            'driver_position': [37.455434, 55.719437],
        }

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('stop-watch-by-order-id-message-processed')
    def stop_by_order_id_processed(data):
        pass

    await drw.enable_testpoints()

    # wait to acquire master lock before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()
    await restore_from_storage_ok.wait_call()

    # wait to become master before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # request stop some orders
    driver_id = {'dbid': 'dbid', 'uuid': 'uuidcourierbyorder'}
    await drw.stop_watch_by_orders(
        driver_id, ['aaaa1', 'aaaa2', 'aaaa3'], service=SERVICE_ID,
    )

    await stop_by_order_id_processed.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {
        'dbid_uuidcourierbyorder': {
            SERVICE_ID: {
                'deleted_orders': {'aaaa1', 'aaaa2', 'aaaa3'},
                'service': SERVICE_ID,
            },
        },
    }

    redis_store.flushall()
