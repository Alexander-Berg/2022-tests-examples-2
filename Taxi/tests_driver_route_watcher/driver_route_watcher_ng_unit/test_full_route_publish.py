# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521
import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.mark.now(1234567890)
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_route_publish(
        driver_route_watcher_ng_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = driver_route_watcher_ng_adv

    driver_id = {'uuid': 'uuidroutepublish', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    destinations = [
        [37.451695, 55.723917],
        [37.473896, 55.728358],
        [37.518952, 55.736290],
    ]
    destination = destinations[-1]
    raw_position = [37.455596, 55.719463]
    expected_adjusted = [37.455434, 55.719437]
    expected_route_id = 'yamaps:car:c26b493b-0559-45e8-8809-4dc8a1278a7a'
    expected_order_id = '12345'
    service_id = 'driving'

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [raw_position] + destinations
        assert 'avoid' not in request.args
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
                    'destination_position': destinations[0],
                    'order_id': expected_order_id,
                    'service_id': service_id,
                    'time_distance_left': {'time': 225.0, 'distance': 1043.0},
                },
                {
                    'destination_position': destinations[1],
                    'order_id': expected_order_id,
                    'service_id': service_id,
                    'time_distance_left': {'time': 305.0, 'distance': 2525.0},
                },
                {
                    'destination_position': destinations[2],
                    'order_id': expected_order_id,
                    'service_id': service_id,
                    'time_distance_left': {'time': 450.0, 'distance': 5491.0},
                },
            ],
        }

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
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
    await Utils.request_start_watch(
        driver_id, destinations, drw, 'car', True, service_id,
    )
    await logbroker_event_done.wait_call()
    await start_watch_message_processed.wait_call()

    # After start watch request must be added watchlist entry and watch command
    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    watch = watchlist[dbid_uuid][service_id]
    assert (
        WatchList.deserialize_watchlist_entry(watch['destination'])
        == destination
    )
    assert watch['meta'] == {'order_id': '12345', 'taxi_status': 'driving'}
    assert watch['service'] == service_id
    assert watch['points'] == PointlistFbs.to_point_list(destinations)

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
    await Utils.request_stop_watch(driver_id, destinations, drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}
