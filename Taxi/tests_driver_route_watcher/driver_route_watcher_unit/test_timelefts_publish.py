# pylint: disable=import-error,too-many-lines
import datetime

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


def test_serialize_deserialize():
    orig = [37.37, 55.55]
    buf = WatchList.serialize_watchlist_entry(orig)
    deserialized = WatchList.deserialize_watchlist_entry(buf)
    assert orig == deserialized


@pytest.mark.now(1234567890)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
)
async def test_timelefts_publish_intermediate_points(
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
):
    drw = taxi_driver_route_watcher_adv

    publish_counter = 0

    driver_id = {'uuid': 'uuid100tp', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])

    transporting_points = [
        [37.451695, 55.723917],
        [37.473896, 55.728358],
        [37.518952, 55.736290],
    ]
    transporting_dst = transporting_points[-1]
    raw_position = [37.455596, 55.719463]
    destinations = transporting_points
    service_id = 'driving'
    expected_route_id = 'yamaps:car:c26b493b-0559-45e8-8809-4dc8a1278a7a'

    def _cmp_points(x, y):
        assert abs(x[0] - y[0]) < 0.000002
        assert abs(x[1] - y[1]) < 0.000002

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        ref = [raw_position] + destinations
        map(lambda x: _cmp_points(x[0], x[1]), zip(rll, ref))
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

    @testpoint('timelefts-message-is-published')
    def publish_timelefts(data):
        nonlocal publish_counter

        for i in range(len(data['timeleft_data'])):
            data['timeleft_data'][i]['time_distance_left']['distance'] = int(
                data['timeleft_data'][i]['time_distance_left']['distance'],
            )

        if publish_counter == 0:
            assert data == {
                'adjusted_pos': [37.455434, 55.719437],
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
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 225.0,
                            'distance': 1043.0,
                        },
                    },
                    {
                        'destination_position': destinations[1],
                        'service_id': service_id,
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 305.0,
                            'distance': 2525.0,
                        },
                    },
                    {
                        'destination_position': destinations[2],
                        'service_id': service_id,
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 450.0,
                            'distance': 5491.0,
                        },
                    },
                ],
            }
        else:
            if publish_counter == 1:
                # Publish one more timelefts with old destination because StartWatch() triggers SetPosition() with position from cache
                publish_counter += 1
                assert data['timeleft_data'][0]['destination_position'] == [
                    37.451695,
                    55.723917,
                ]
                data['timeleft_data'][0][
                    'destination_position'
                ] = destinations[0]
            assert data == {
                'adjusted_pos': [37.45543417884857, 55.71943665153375],
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
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 224.0,
                            'distance': 1043.0,
                        },
                    },
                    {
                        'destination_position': destinations[1],
                        'service_id': service_id,
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 304.0,
                            'distance': 2526.0,
                        },
                    },
                    {
                        'destination_position': destinations[2],
                        'service_id': service_id,
                        'order_id': '12345',
                        'time_distance_left': {
                            'time': 449.0,
                            'distance': 5492.0,
                        },
                    },
                ],
            }

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        pass

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    # wait to become master before writing route
    await Utils.request_ping(drw)
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    Utils.publish_edge_position(driver_id, raw_position, redis_store, now)

    response = await Utils.request_timeleft(driver_id, drw)
    assert response.status_code == 404  # no destination
    response = await Utils.request_timeleft_as_string(driver_id, drw)
    assert response.status_code == 404  # no position no destination

    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    await Utils.request_start_watch(
        driver_id, transporting_points, drw, 'car', True,
    )
    await logbroker_event_done.wait_call()

    # After start watch request must be added watchlist entry and watch command
    # check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    service_id = 'driving'
    watch = watchlist[dbid_uuid][service_id]
    assert (
        WatchList.deserialize_watchlist_entry(watch['destination'])
        == transporting_dst
    )
    assert watch['meta'] == {'order_id': '12345', 'taxi_status': 'driving'}
    assert watch['service'] == service_id
    assert watch['points'] == PointlistFbs.to_point_list(transporting_points)

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()
    await route_message_processed.wait_call()

    # wait and check publish timelefts
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()
    publish_counter += 1

    # check route is written to redis
    stored_route = Utils.get_route(redis_store, driver_id)
    assert stored_route is not None

    # change intermediate points
    destinations[0][0] = destinations[0][0] + 0.000001
    await drw.start_watch(
        driver_id,
        destinations[-1],
        order_id='12345',
        destinations=PointlistFbs.to_point_list(destinations),
        router_type='car',
        toll_roads=True,
        service='driving',
    )

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()
    await route_message_processed.wait_call()

    # wait and check publish timelefts
    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # stop watch
    await drw.stop_watch(driver_id, destinations[-1], 'driving')
    await stop_watch_message_processed.wait_call()

    # After stop watch request watchlist entry must be deleted
    #  check watch list
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}


@pytest.mark.now(1234567890)
@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(
    TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
    DRIVER_ROUTE_WATCHER_ENABLE_ROUTER_TIMELEFT_FALLBACK=True,
    DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
)
@pytest.mark.parametrize(
    'enable_router_fallback,time_left,distance_left,tracking_type,'
    'adjusted_pos,route_id',
    [
        (
            False,
            232.0,
            2438.0,
            'RouteTracking',
            [37.466111, 55.72718],
            'yamaps:car:5eb8e1ec-8fc2-4159-b06f-f32c6e974181',
        ),
        (
            True,
            176.0,
            1225.0,
            'LinearFallback',
            [37.466104, 55.727191],
            'linear:car:dbid_uuid101tp_1234567890000000',
        ),
    ],
)
@pytest.mark.redis_store(['flushall'])
async def test_timelefts_publish_linear_fallback(
        taxi_config,
        taxi_driver_route_watcher_adv,
        redis_store,
        now,
        mockserver,
        load_binary,
        testpoint,
        enable_router_fallback,
        time_left,
        distance_left,
        tracking_type,
        adjusted_pos,
        route_id,
):
    taxi_config.set_values(
        {
            'DRIVER_ROUTE_WATCHER_ENFORCE_ROUTER_FALLBACK': (
                enable_router_fallback
            ),
        },
    )

    drw = taxi_driver_route_watcher_adv

    driver_id = {'uuid': 'uuid101tp', 'dbid': 'dbid'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    raw_position = [37.466104, 55.727191]
    destination = [37.454099, 55.718486]
    service_id = 'transporting'

    @testpoint('route-message-processed')
    def route_message_processed(data):
        pass

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('route-failed-message-processed')
    def route_failed_message_processed(data):
        pass

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

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
            'adjusted_pos': adjusted_pos,
            'adjusted_segment_index': 0,
            'contractor_id': dbid_uuid,
            'route_id': route_id,
            'timestamp': 1234567890000,
            'tracking_type': tracking_type,
            'update_timestamp': 1234567890000,
            'timeleft_data': [
                {
                    'destination_position': destination,
                    'service_id': service_id,
                    'time_distance_left': {
                        'time': time_left,
                        'distance': distance_left,
                    },
                },
            ],
        }

    @testpoint('timelefts-message-was-published')
    def publish_timelefts_completed(data):
        pass

    Utils.publish_edge_position(driver_id, raw_position, redis_store, now)

    # start watch
    # set watched driver in watchlist in redis
    await drw.start_watch(driver_id, destination, service_id)

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()
    if not enable_router_fallback:
        await route_message_processed.wait_call()
    else:
        await route_failed_message_processed.wait_call()

    await publish_timelefts.wait_call()
    await publish_timelefts_completed.wait_call()

    # stop watch
    # remove watched driver from watchlist in redis
    redis_store.flushall()
    await drw.stop_watch(driver_id, destination, service_id)
    await stop_watch_message_processed.wait_call()
