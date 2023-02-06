# pylint: disable=import-error
import json  # noqa: F401

import pytest

import tests_driver_route_watcher.driver_position_fbs as DriverPositionFbs
import tests_driver_route_watcher.fsm_state_type_fbs as FsmStateTypeEntry
import tests_driver_route_watcher.points_list_fbs as PointlistFbs  # noqa: F401, E501
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.now(1234567895)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
@pytest.mark.redis_store(
    ['flushall'],
    [
        'hmset',
        'w/{dbidrestoreunkn_uuidrestoreunkn}',
        {
            'some-test-service/d': WatchList.serialize_watchlist_entry([0, 0]),
            'some-test-service/m': json.dumps(
                {'order_id': 'orderid123', 'taxi_status': 'driving'},
            ),
            'some-test-service/o': 'orderid123',
            'some-test-service/ps': PointlistFbs.serialize_pointslist(
                PointlistFbs.to_point_list([[0, 0]]),
            ),
        },
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn}',
        'fsm_current_state',
        FsmStateTypeEntry.serialize_fsm_state_type_entry(
            'unknown_destination',
        ),
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn}',
        'fsm_current_state_start_time',
        1234567890,
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn}',
        'driver_position',
        DriverPositionFbs.serialize_driver_position_entry(
            {'position': [11.0, 22.0], 'transport_type': 'automobile'},
        ),
    ],
)
async def test_restore_unknown_b_tracking_state(
        driver_route_watcher_ng_adv, redis_store, mockserver, testpoint, now,
):
    drw = driver_route_watcher_ng_adv

    destination = [0, 0]
    driver_id = {'uuid': 'uuidrestoreunkn', 'dbid': 'dbidrestoreunkn'}
    dbid_uuid = 'dbidrestoreunkn_uuidrestoreunkn'

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # Must not request router
        return mockserver.make_response(
            response='Ffuuu',
            status=500,
            content_type='application/x-protobuf',
        )

    @testpoint('restore-from-storage-ok')
    def restore_from_storage(data):
        assert data == {
            'current_state': 5,  # unknown_destination state
            'current_state_start_time': '1234567890',
            'destinations_count': 1,
            'driver_position': [11.0, 22.0],
        }

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        assert data == {
            'adjusted_pos': [33.0, 44.0],
            'contractor_id': dbid_uuid,
            'timestamp': 1234567895000,
            'update_timestamp': 1234567895000,
            'tracking_type': 'UnknownDestination',
            'adjusted_segment_index': 0,
            'route_id': '',
            'timeleft_data': [
                {
                    'destination_position': None,
                    'order_id': 'orderid123',
                    'service_id': 'some-test-service',
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
    await restore_from_storage.wait_call()

    # publish intermediate position
    Utils.publish_edge_position(driver_id, [33.0, 44.0], redis_store, now)

    # wait and check timelefts publish for intermediate position
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # if we successfuly restored from db then no reason to use router
    assert _mock_route.times_called < 1

    # cleanup to do not interfere other tests
    await drw.stop_watch(driver_id, destination)
    redis_store.delete('w/{dbidrestoreunkn_uuidrestoreunkn}')
    await stop_watch_message_processed.wait_call()


@pytest.mark.now(1234567897)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
@pytest.mark.redis_store(
    ['flushall'],
    [
        'hmset',
        'w/{dbidrestoreunkn_uuidrestoreunkn2}',
        {
            'some-test-service/d': WatchList.serialize_watchlist_entry([0, 0]),
            'some-test-service/m': json.dumps(
                {'order_id': 'orderid123', 'taxi_status': 'driving'},
            ),
            'some-test-service/o': 'orderid123',
            'some-test-service/ps': PointlistFbs.serialize_pointslist(
                PointlistFbs.to_point_list([]),
            ),
        },
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn2}',
        'fsm_current_state',
        FsmStateTypeEntry.serialize_fsm_state_type_entry(
            'unknown_destination',
        ),
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn2}',
        'fsm_current_state_start_time',
        1234567890,
    ],
    [
        'hset',
        'output:{dbidrestoreunkn_uuidrestoreunkn2}',
        'driver_position',
        DriverPositionFbs.serialize_driver_position_entry(
            {'position': [55.0, 66.0], 'transport_type': 'automobile'},
        ),
    ],
)
async def test_restore_unknown_b_tracking_state_empty_points(
        driver_route_watcher_ng_adv, redis_store, mockserver, testpoint, now,
):
    drw = driver_route_watcher_ng_adv

    destination = [0, 0]
    driver_id = {'uuid': 'uuidrestoreunkn2', 'dbid': 'dbidrestoreunkn'}
    dbid_uuid = 'dbidrestoreunkn_uuidrestoreunkn2'

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # Must not request router
        return mockserver.make_response(
            response='Ffuuu',
            status=500,
            content_type='application/x-protobuf',
        )

    @testpoint('restore-from-storage-ok')
    def restore_from_storage(data):
        assert data == {
            'current_state': 5,  # unknown_destination state
            'current_state_start_time': '1234567890',
            'destinations_count': 1,
            'driver_position': [55.0, 66.0],
        }

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        assert data == {
            'adjusted_pos': [77.0, 88.0],
            'contractor_id': dbid_uuid,
            'timestamp': 1234567897000,
            'update_timestamp': 1234567897000,
            'tracking_type': 'UnknownDestination',
            'adjusted_segment_index': 0,
            'route_id': '',
            'timeleft_data': [
                {
                    'destination_position': None,
                    'order_id': 'orderid123',
                    'service_id': 'some-test-service',
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
    await restore_from_storage.wait_call()

    # publish intermediate position
    Utils.publish_edge_position(driver_id, [77.0, 88.0], redis_store, now)

    # wait and check timelefts publish for intermediate position
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # if we successfuly restored from db then no reason to use router
    assert _mock_route.times_called < 1

    # cleanup to do not interfere other tests
    await drw.stop_watch(driver_id, destination)
    redis_store.delete('w/{dbidrestoreunkn_uuidrestoreunkn2}')
    await stop_watch_message_processed.wait_call()
