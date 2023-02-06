# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521
import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    ROUTER_SELECT=[
        {'routers': ['google'], 'ids': ['berlin']},
        {'routers': ['yamaps']},
    ],
    ROUTER_GOOGLE_ENABLED=True,
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_google_router_by_destination_type(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid100berlin', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [-87.65126, 41.85073]
    destination = [-87.64843, 41.85388]
    expected_adjusted = [-87.65141, 41.85258]
    expected_route_id = 'google:car:dbid_uuid100berlin_1234567890000000'
    service_id = 'driving'

    @mockserver.handler('/maps-google-router/google/maps/api/directions/json')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('google_router_response.json'),
            status=200,
            content_type='application/json',
        )

    @testpoint('route-message-processed')
    def route_message_processed(data):
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

    @testpoint('start-watch-message-processed')
    def start_watch_message_processed(request):
        pass

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        for i in range(len(data['timeleft_data'])):
            data['timeleft_data'][i]['time_distance_left']['distance'] = int(
                data['timeleft_data'][i]['time_distance_left']['distance'],
            )
        assert data == {
            'adjusted_pos': expected_adjusted,
            'adjusted_segment_index': 0,
            'contractor_id': dbid_uuid,
            'route_id': expected_route_id,
            'timestamp': 1234567890000,
            'update_timestamp': 1234567890000,
            'tracking_type': 'RouteTracking',
            'timeleft_data': [
                {
                    'destination_position': destination,
                    'service_id': service_id,
                    'time_distance_left': {'time': 96.0, 'distance': 389.0},
                },
            ],
        }

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    @testpoint('fsm-context-cleared')
    def fsm_context_cleared(data):
        pass

    @testpoint('reset-watch-completed')
    def reset_watch_completed(data):
        pass

    # wait to become master before writing route
    await Utils.request_ping(drw)
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # publish position in yaga channel
    Utils.publish_edge_position(driver_id, raw_position, redis_store, now)

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # get start-watch
    await drw.start_watch(
        driver_id, destination, nearest_zone='berlin', service=service_id,
    )
    await start_watch_message_processed.wait_call()

    # After start watch request must be added watchlist entry and watch command
    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    watch = watchlist[dbid_uuid][service_id]
    assert (
        WatchList.deserialize_watchlist_entry(watch['destination'])
        == destination
    )
    assert watch['service'] == service_id
    assert watch['points'] == PointlistFbs.to_point_list([destination])

    # wait route processed
    await route_message_processed.wait_call()
    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()

    # wait and check publish timelefts
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # check route is written to redis
    stored_route = Utils.get_route(redis_store, driver_id)
    assert stored_route is not None

    # route_id can be found in logs "received route <route_id>"
    stored_full_route = redis_store.hget(f'{{{expected_route_id}}}', 'route')
    assert stored_full_route is not None

    # check delete output in redis
    stored_output = Utils.get_output(redis_store, driver_id)
    assert stored_output is None

    # check restore data
    current_state = Utils.get_current_state(redis_store, driver_id)
    current_state_start_time = Utils.get_current_state_time_start(
        redis_store, driver_id,
    )
    driver_position = Utils.get_driver_position(redis_store, driver_id)
    assert current_state is not None
    assert current_state_start_time is not None
    assert driver_position is not None

    # stop watch
    await Utils.request_stop_watch(driver_id, [destination], drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}
