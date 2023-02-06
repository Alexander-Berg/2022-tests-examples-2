# pylint: disable=import-error
import json  # noqa: F401

import pytest

import tests_driver_route_watcher.driver_position_fbs as DriverPositionFbs
import tests_driver_route_watcher.fsm_state_type_fbs as FsmStateTypeEntry
import tests_driver_route_watcher.output_entry_fbs as OutputEntryFbs
import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList

TRANSPORTING_POINTS = [
    {'point': [11.1, 22.1], 'wait_time': 1111, 'park_time': 10},
    {'point': [11.2, 22.2], 'wait_time': 1112, 'park_time': 20},
    {'point': [11.3, 22.3], 'wait_time': 1113, 'park_time': 30},
]
TRANSPORTING_DST = TRANSPORTING_POINTS[-1]['point']
DRIVING_POINTS = [[11.4, 22.4], [11.5, 22.5]]  # replace with some other
DRIVING_DST = DRIVING_POINTS[-1]
LAST_POSITION = {
    'position': [11.0, 22.0],
    'direction': 112,
    'timestamp': 1234567890,
    'transport_type': 'automobile',
}
INTERMEDIATE_POSITION = [11.05, 22.05]
MULTIPLIER = 0.5


@pytest.mark.now(1234567891)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
@pytest.mark.redis_store(
    ['flushall'],
    [
        'hmset',
        'w/{dbidrestore_uuidrestore}',
        {
            'processing:transporting/d': WatchList.serialize_watchlist_entry(
                TRANSPORTING_DST,
            ),
            'processing:transporting/m': json.dumps(
                {'order_id': 'orderid123', 'taxi_status': 'transporting'},
            ),
            'processing:transporting/o': 'orderid123',
            'processing:transporting/ps': PointlistFbs.serialize_pointslist(
                TRANSPORTING_POINTS,
            ),
            'processing:driving/d': WatchList.serialize_watchlist_entry(
                DRIVING_DST,
            ),
            'processing:driving/m': json.dumps(
                {'order_id': 'orderid100500', 'taxi_status': 'driving'},
            ),
            'processing:driving/ps': PointlistFbs.serialize_pointslist(
                PointlistFbs.to_point_list(DRIVING_POINTS),
            ),
            'processing:driving/o': 'orderid100500',
            'processing:driving/rt': 'masstransit',
            'processing:driving/trs': 1,
            'processing:driving/em': MULTIPLIER,
            'processing:transporting/aaaa1/dos': 0,
            'processing:transporting/aaaa2/dos': 0,
            'processing:transporting/nz': 'Mordor',
            'processing:transporting/cntr': 'Gondor',
        },
    ],
    [
        'hset',
        'output:{dbidrestore_uuidrestore}',
        'fsm_current_state',
        FsmStateTypeEntry.serialize_fsm_state_type_entry('tracking'),
    ],
    [
        'hset',
        'output:{dbidrestore_uuidrestore}',
        'fsm_current_state_start_time',
        1234567890,
    ],
    [
        'hset',
        'output:{dbidrestore_uuidrestore}',
        'driver_position',
        DriverPositionFbs.serialize_driver_position_entry(LAST_POSITION),
    ],
    [
        'hset',
        'output:{dbidrestore_uuidrestore}',
        'route',
        OutputEntryFbs.serialize_route_entry(
            {
                'route': {
                    'route': [
                        {
                            'position': LAST_POSITION['position'],
                            'time': 0,
                            'distance': 0,
                        },
                        {
                            'position': TRANSPORTING_POINTS[0]['point'],
                            'time': 100,
                            'distance': 1000,
                        },
                        {
                            'position': TRANSPORTING_POINTS[1]['point'],
                            'time': 200,
                            'distance': 2000,
                        },
                        {
                            'position': TRANSPORTING_POINTS[2]['point'],
                            'time': 300,
                            'distance': 3000,
                        },
                        {
                            'position': DRIVING_POINTS[0],
                            'time': 400,
                            'distance': 4000,
                        },
                        {
                            'position': DRIVING_POINTS[1],
                            'time': 500,
                            'distance': 5000,
                        },
                    ],
                    'distance': 5000,
                    'time': 500,
                    'closures': False,
                    'dead_jams': False,
                    'toll_roads': False,
                    'route_id': 'some_route_id',
                },
                'timestamp': 1234567890,
            },
        ),
    ],
    ['hset', 'output:{dbidrestore_uuidrestore}', 'force_log', '1234567890'],
)
async def test_restore_tracking_state(
        driver_route_watcher_ng_adv, redis_store, mockserver, testpoint, now,
):
    drw = driver_route_watcher_ng_adv

    # use uuid not used in other tests
    # inner master_epoch must be 0 yet
    driver_id = {'uuid': 'uuidrestore', 'dbid': 'dbidrestore'}
    dbid_uuid = 'dbidrestore_uuidrestore'

    @testpoint('restore-from-storage-ok')
    def restore_from_storage_ok(data):
        assert data == {
            'current_state': 1,  # tracking state
            'current_state_start_time': '1234567890',
            'destinations_count': 2,
            'driver_position': [11.0, 22.0],
            'force_log': 1234567890,
        }

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # Must not request router
        return mockserver.make_response(
            response='Ffuuu',
            status=500,
            content_type='application/x-protobuf',
        )

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        for i in range(len(data['timeleft_data'])):
            data['timeleft_data'][i]['time_distance_left']['distance'] = int(
                data['timeleft_data'][i]['time_distance_left']['distance'],
            )
        data['adjusted_pos'][0] = round(data['adjusted_pos'][0], 2)
        data['adjusted_pos'][1] = round(data['adjusted_pos'][1], 2)
        assert data == {
            'adjusted_pos': INTERMEDIATE_POSITION,
            'adjusted_segment_index': 0,
            'contractor_id': dbid_uuid,
            'route_id': 'some_route_id',
            'timestamp': 1234567891000,
            'update_timestamp': 1234567891000,
            'tracking_type': 'RouteTracking',
            'timeleft_data': [
                {
                    'destination_position': TRANSPORTING_POINTS[0]['point'],
                    'order_id': 'orderid123',
                    'service_id': 'processing:transporting',
                    'time_distance_left': {'time': 59.0, 'distance': 500.0},
                },
                {
                    'destination_position': TRANSPORTING_POINTS[1]['point'],
                    'order_id': 'orderid123',
                    'service_id': 'processing:transporting',
                    'time_distance_left': {'time': 1290.0, 'distance': 1500.0},
                },
                {
                    'destination_position': TRANSPORTING_POINTS[2]['point'],
                    'order_id': 'orderid123',
                    'service_id': 'processing:transporting',
                    'time_distance_left': {'time': 2532.0, 'distance': 2500.0},
                },
                {
                    'destination_position': DRIVING_POINTS[0],
                    'order_id': 'orderid100500',
                    'service_id': 'processing:driving',
                    'time_distance_left': {'time': 3695.0, 'distance': 3500.0},
                },
                {
                    'destination_position': DRIVING_POINTS[1],
                    'order_id': 'orderid100500',
                    'service_id': 'processing:driving',
                    'time_distance_left': {'time': 3745.0, 'distance': 4500.0},
                },
            ],
        }

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    # wait to acquire master lock before writing route
    await Utils.request_ping(drw)
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # timeout means that for some reason restore from db failed
    await restore_from_storage_ok.wait_call()

    # publish intermediate position
    Utils.publish_edge_position(
        driver_id, INTERMEDIATE_POSITION, redis_store, now,
    )

    # wait and check timelefts publish for intermediate position
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # cleanup to do not interfere other tests
    redis_store.delete('w/{dbidrestore_uuidrestore}')

    # after cleanup watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # if we successfuly restored from db then no reason to use router
    assert _mock_route.times_called < 1
