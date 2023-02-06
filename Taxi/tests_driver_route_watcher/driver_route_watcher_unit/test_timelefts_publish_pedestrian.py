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
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_pedestrian_timelefts_publish_by_destination_type(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid100tpp', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [37.466104, 55.727191]
    destination = [37.454099, 55.718486]

    expected_adjusted = [37.466104, 55.727191]
    expected_route_id = (
        'yamaps:pedestrian:'  # there is no route_id in this mock
    )
    service_id = 'driving'

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/route')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('pedestrian_maps_response.pb'),
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
                    'destination_position': destination,
                    'service_id': service_id,
                    'time_distance_left': {'time': 1241.0, 'distance': 1724.0},
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
    Utils.publish_position(
        driver_id,
        raw_position,
        redis_store,
        now,
        channel='channel:yagr:pedestrian_positions',
    )

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # get start-watch
    await drw.start_watch(
        driver_id,
        destination,
        service_id,
        router_type='pedestrian',
        meta='{"order_id":"12345","taxi_status":"driving"}',
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
    assert watch['meta'] == {'order_id': '12345', 'taxi_status': 'driving'}
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

    # stop watch
    await Utils.request_stop_watch(driver_id, [destination], drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(ROUTER_MASSTRANSIT_MAPS_ENABLED=True)
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_masstransit_timelefts_publish_by_destination_type(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid200tpp', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [37.466104, 55.727191]
    destination = [37.454099, 55.718486]

    expected_adjusted = [37.466104, 55.727191]
    expected_route_id = (
        'yamaps:masstransit:'  # there is no route_id in this mock
    )
    service_id = 'driving'

    @mockserver.handler('/maps-pedestrian-router/masstransit/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('pedestrian_maps_response.pb'),
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
                    'destination_position': destination,
                    'service_id': service_id,
                    'time_distance_left': {'time': 1241.0, 'distance': 1724.0},
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
    Utils.publish_position(
        driver_id,
        raw_position,
        redis_store,
        now,
        channel='channel:yagr:pedestrian_positions',
    )

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # get start-watch
    await drw.start_watch(
        driver_id,
        destination,
        service_id,
        router_type='masstransit',
        meta='{"order_id":"12345","taxi_status":"driving"}',
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
    assert watch['meta'] == {'order_id': '12345', 'taxi_status': 'driving'}
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

    # stop watch
    await Utils.request_stop_watch(driver_id, [destination], drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(ROUTER_MASSTRANSIT_MAPS_ENABLED=True)
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_masstransit_timelefts_publish_shortest_path(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    """
    Test case with the shortest pedestrian route for masstransit router
    """
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid300tpp', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [37.535990, 55.749816]
    destination = [37.538694, 55.750979]

    expected_adjusted = [37.53599, 55.749816]
    expected_route_id = (
        'yamaps:masstransit:c51c5659-e7db-4e9d-a8c8-cd54b484b71d'
    )
    service_id = 'driving'

    @mockserver.handler('/maps-pedestrian-router/masstransit/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('masstransit_route_test.pb'),
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
                    'destination_position': destination,
                    'service_id': service_id,
                    'time_distance_left': {'time': 319.0, 'distance': 443.0},
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
    Utils.publish_position(
        driver_id,
        raw_position,
        redis_store,
        now,
        channel='channel:yagr:pedestrian_positions',
    )

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # get start-watch
    await drw.start_watch(
        driver_id,
        destination,
        service_id,
        router_type='masstransit',
        meta='{"order_id":"12345","taxi_status":"driving"}',
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
    assert watch['meta'] == {'order_id': '12345', 'taxi_status': 'driving'}
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

    # stop watch
    await Utils.request_stop_watch(driver_id, [destination], drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(ROUTER_MASSTRANSIT_MAPS_ENABLED=True)
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
async def test_masstransit_timelefts_publish_same_destinations(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    """
    Test case with 2 same destianation points at the end of route
    """
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid100samedst', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [37.451695, 55.723917]
    destinations = [[37.518952, 55.73629], [37.518952, 55.73629]]

    expected_adjusted = [37.451695, 55.723917]
    expected_route_id = (
        'yamaps:masstransit:4778e1b6-0900-4eff-a84f-dbea46eba9e4'
    )
    service_id = 'driving'

    @mockserver.handler('/maps-pedestrian-router/masstransit/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary(
                'maps_mass_transit_response-'
                '37.451695,55.723917'
                '~37.518952,55.73629'
                '~37.518952,55.73629.pb',
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
                    'service_id': service_id,
                    'time_distance_left': {'time': 792.0, 'distance': 4460.0},
                },
                {
                    'destination_position': destinations[1],
                    'service_id': service_id,
                    'time_distance_left': {'time': 792.0, 'distance': 4460.0},
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
    Utils.publish_position(
        driver_id,
        raw_position,
        redis_store,
        now,
        channel='channel:yagr:pedestrian_positions',
    )

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    # get start-watch
    await drw.start_watch(
        driver_id,
        destinations[-1],
        service_id,
        destinations=PointlistFbs.to_point_list(destinations),
        router_type='masstransit',
        meta='{"order_id":"12345","taxi_status":"driving"}',
    )
    await start_watch_message_processed.wait_call()

    # After start watch request must be added watchlist entry and watch command
    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    watch = watchlist[dbid_uuid][service_id]
    assert (
        WatchList.deserialize_watchlist_entry(watch['destination'])
        == destinations[-1]
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

    # stop watch
    await Utils.request_stop_watch(driver_id, destinations, drw)
    await stop_watch_message_processed.wait_call()
    await fsm_context_cleared.wait_call()
    await reset_watch_completed.wait_call()

    # After stop watch request watchlist entry must be deleted
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}
