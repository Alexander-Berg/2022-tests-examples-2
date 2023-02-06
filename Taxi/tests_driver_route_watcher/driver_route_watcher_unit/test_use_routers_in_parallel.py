# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521
import pytest

import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    ROUTER_GOOGLE_ENABLED=True,
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
@pytest.mark.parametrize('use_osm', [False, True])
@pytest.mark.parametrize(
    'google_times_called, yamaps_times_called, nearest_zone, uuid',
    [
        pytest.param(
            1,
            1,
            'berlin',
            'uuidparallel1',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
        pytest.param(
            1,
            0,
            'riga',
            'uuidparallel2',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
        pytest.param(
            0,
            1,
            None,
            'uuidparallel3',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
        pytest.param(1, 0, 'berlin', 'uuid'),
        pytest.param(1, 0, 'riga', 'uuid'),
        pytest.param(0, 1, None, 'uuid'),
        pytest.param(
            1,
            0,
            'berlin',
            'uuidnotinexp1',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
        pytest.param(
            1,
            0,
            'riga',
            'uuidnotinexp2',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
        pytest.param(
            0,
            1,
            None,
            'uuidnotinexp3',
            marks=pytest.mark.experiments3(
                filename='exp3_use_routers_in_parallel.json',
            ),
        ),
    ],
)
async def test_timeleft_use_routers_in_parallel(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
        google_times_called,
        yamaps_times_called,
        nearest_zone,
        uuid,
        use_osm: bool,
        taxi_config,
):
    yamaps_url = 'yamaps-over-osm' if use_osm else 'yamaps'
    taxi_config.set_values(
        dict(
            ROUTER_SELECT=[
                {'routers': ['google'], 'ids': ['berlin']},
                {'routers': ['google'], 'ids': ['riga']},
                {'routers': [yamaps_url]},
                {
                    'routers': ['google', yamaps_url],
                    'ids': ['berlin'],
                    'target': 'routing_experiment',
                    'service': 'driver-route-watcher',
                },
            ],
        ),
    )
    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': uuid, 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [-87.65126, 41.85073]
    destination = [-87.64843, 41.85388]
    service_id = 'some_service_id'

    @mockserver.handler('/maps-google-router/google/maps/api/directions/json')
    def _mock_route_google(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('google_router_response.json'),
            status=200,
            content_type='application/json',
        )

    yamaps_router_url = (
        '/maps-over-osm-router/v2/route'
        if use_osm
        else '/maps-router/v2/route'
    )

    @mockserver.handler(yamaps_router_url)
    def _mock_route_yandex(request):
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463~37.473896,55.728358.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        assert data['contractor_id'] == f'dbid_{uuid}'
        assert data['adjusted_segment_index'] == 0
        if yamaps_times_called > 0 and google_times_called == 0:
            assert 'yamaps' in data['route_id']
        elif yamaps_times_called == 0 and google_times_called > 0:
            assert 'google' in data['route_id']
        assert data['timestamp'] == 1234567890000
        assert data['update_timestamp'] == 1234567890000
        assert data['tracking_type'] == 'RouteTracking'
        assert data['timeleft_data'][0]['destination_position'] == destination
        assert data['timeleft_data'][0]['service_id'] == service_id
        assert 'time_distance_left' in data['timeleft_data'][0]

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    await drw.enable_testpoints()

    # wait to become master before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # publish positon
    Utils.publish_edge_position(driver_id, raw_position, redis_store, now)

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    if nearest_zone is not None:
        await drw.start_watch(
            driver_id,
            destination,
            nearest_zone=nearest_zone,
            service=service_id,
        )
    else:
        await drw.start_watch(driver_id, destination, service=service_id)

    # After start watch request must be added watchlist entry and watch command
    #  check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    watch = watchlist[dbid_uuid][service_id]
    assert (
        WatchList.deserialize_watchlist_entry(watch['destination'])
        == destination
    )
    assert watch['meta'] == ''
    assert watch['service'] == service_id

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()

    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # check route is written to redis
    stored_route = Utils.get_route(redis_store, driver_id)
    assert stored_route is not None

    # stop watch
    await drw.stop_watch_all(driver_id, service_id)
    await stop_watch_message_processed.wait_call()

    if google_times_called + yamaps_times_called < 2:
        assert _mock_route_google.times_called == google_times_called
        assert _mock_route_yandex.times_called == yamaps_times_called
