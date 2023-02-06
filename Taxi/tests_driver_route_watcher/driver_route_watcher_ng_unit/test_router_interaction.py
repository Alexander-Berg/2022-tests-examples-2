# pylint: disable=import-error
import pytest

import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_router_direction(
        driver_route_watcher_ng_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = driver_route_watcher_ng_adv

    tested_direction = 42  # degrees north
    driver_id = {'uuid': 'uuid100', 'dbid': 'dbid'}
    dbid_uuid = 'dbid_uuid100'
    raw_position = [37.466104, 55.727191]
    raw_direction = tested_direction
    destination = [37.454099, 55.718486]

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # This is the main statement in this test - we check that direction
        # is passed to the router
        assert int(request.args['dir']) == tested_direction
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
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

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        assert data['contractor_id'] == dbid_uuid
        assert (
            data['route_id']
            == 'yamaps:car:5eb8e1ec-8fc2-4159-b06f-f32c6e974181'
        )
        assert data['timeleft_data'][0]['destination_position'] == destination

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    @testpoint('start-watch-message-processed')
    def start_watch_message_processed(data):
        pass

    # wait to become master before writing route
    await Utils.request_ping(drw)
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # publish position with our direction
    Utils.publish_edge_position(
        driver_id, raw_position, redis_store, now, raw_direction,
    )

    # start watching
    await drw.start_watch(driver_id, destination, 'reposition-watcher')
    await start_watch_message_processed.wait_call()

    # wait route message
    await route_message_processed.wait_call()

    # Check that everything is OK at the moment
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # stop watch
    await drw.stop_watch(driver_id, destination, 'reposition-watcher')
    await stop_watch_message_processed.wait_call()

    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}
