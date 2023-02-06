import json  # noqa: F401

import pytest

import tests_driver_route_watcher.driver_position_fbs as DriverPositionFbs
import tests_driver_route_watcher.fsm_state_type_fbs as FsmStateTypeEntry
import tests_driver_route_watcher.output_entry_fbs as OutputEntryFbs
import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils
import tests_driver_route_watcher.watch_list as WatchList


POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]
TRANSPORTING_POINTS = [
    {
        'point': POINTS[0],
        'wait_time': 1000,
        'park_time': 0,
        'order_id': 'aaaa1',
        'point_id': 'bbbb1',
    },
    {
        'point': POINTS[1],
        'wait_time': 2000,
        'park_time': 0,
        'order_id': 'aaaa2',
        'point_id': 'bbbb2',
    },
    {
        'point': POINTS[2],
        'wait_time': 4000,
        'park_time': 0,
        'order_id': 'aaaa3',
        'point_id': 'bbbb3',
    },
]
TRANSPORTING_DST = TRANSPORTING_POINTS[-1]['point']
SERVICE_ID = 'cargo-dispatch'
POSITION = [37.0, 55.0]
MULTIPLIER = 1.5


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.mark.servicetest
@pytest.mark.now(1234567890)
@pytest.mark.redis_store(
    ['flushall'],
    [
        'hmset',
        'w/{dbid_uuid}',
        {
            f'{SERVICE_ID}/d': WatchList.serialize_watchlist_entry(
                TRANSPORTING_DST,
            ),
            f'{SERVICE_ID}/m': '',
            f'{SERVICE_ID}/ps': PointlistFbs.serialize_pointslist(
                TRANSPORTING_POINTS,
            ),
        },
    ],
    [
        'hset',
        'output:{dbid_uuid}',
        'fsm_current_state',
        FsmStateTypeEntry.serialize_fsm_state_type_entry('tracking'),
    ],
    ['hset', 'output:{dbid_uuid}', 'fsm_current_state_start_time', 1234567890],
    [
        'hset',
        'output:{dbid_uuid}',
        'driver_position',
        DriverPositionFbs.serialize_driver_position_entry(
            {'position': POSITION, 'transport_type': 'automobile'},
        ),
    ],
    [
        'hset',
        'output:{dbid_uuid}',
        'route',
        OutputEntryFbs.serialize_route_entry(
            {
                'route': {
                    'route': [
                        {'position': POSITION, 'time': 0, 'distance': 0},
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
                    ],
                    'distance': 3000,
                    'time': 300,
                    'closures': False,
                    'dead_jams': False,
                    'toll_roads': False,
                },
                'timestamp': 1234567890,
            },
        ),
    ],
)
@pytest.mark.config(DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True)
async def test_cargo_timelefts_publish_from_restore(
        driver_route_watcher_ng_adv, redis_store, testpoint, now,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('restore-from-storage-ok')
    def restore_from_storage_ok(data):
        pass

    @testpoint('publish-timelefts')
    def publish_timelefts(data):
        assert data == {
            'contractor': 'dbid_uuid',
            'etas': [
                {
                    'distance_left': 1000.0,
                    'order_id': 'aaaa1',
                    'destination': POINTS[0],
                    'point_id': 'bbbb1',
                    'time_left': 100.0,
                },
                {
                    'distance_left': 2000.0,
                    'order_id': 'aaaa2',
                    'destination': POINTS[1],
                    'point_id': 'bbbb2',
                    'time_left': 200.0 + TRANSPORTING_POINTS[0]['wait_time'],
                },
                {
                    'distance_left': 3000.0,
                    'order_id': 'aaaa3',
                    'destination': POINTS[2],
                    'point_id': 'bbbb3',
                    'time_left': (
                        300.0
                        + TRANSPORTING_POINTS[0]['wait_time']
                        + TRANSPORTING_POINTS[1]['wait_time']
                    ),
                },
            ],
            'position': POSITION,
        }

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        pass

    @testpoint('reset-watch-completed')
    def reset_watch_completed(data):
        pass

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    await drw.enable_testpoints()

    # wait to acquire master lock before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()
    await restore_from_storage_ok.wait_call()

    driver_id = {'uuid': 'uuid', 'dbid': 'dbid'}
    Utils.publish_edge_position(driver_id, POSITION, redis_store, now)

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()

    # wait publish in drw:timelefts channel and check correctness
    await publish_timelefts.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert len(watch_list) == 1

    body = {'courier': 'dbid_uuid', 'service_id': SERVICE_ID}
    response = await drw.post('cargo/stop-watch', json=body)
    assert response.status_code == 200
    assert response.json() == {}
    await logbroker_event_done.wait_call()
    await stop_watch_message_processed.wait_call()
    await reset_watch_completed.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {}
    redis_store.flushall()


@pytest.mark.servicetest
@pytest.mark.redis_store(['flushall'])
@pytest.mark.config(DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True)
async def test_cargo_timelefts_publish_eta_multiplier_wait_and_park_time(
        driver_route_watcher_ng_adv,
        load_binary,
        mockserver,
        testpoint,
        redis_store,
        now,
):
    drw = driver_route_watcher_ng_adv

    position = [37.455434, 55.719437]
    driver_id = {'uuid': 'uuid2', 'dbid': 'dbid2'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    transporting_points = [
        {
            'point': POINTS[0],
            'wait_time': 1000,
            'park_time': 100,
            'order_id': 'aaaa1',
            'point_id': 'bbbb1',
        },
        {
            'point': POINTS[1],
            'wait_time': 2000,
            'park_time': 200,
            'order_id': 'aaaa2',
            'point_id': 'bbbb2',
        },
        {
            'point': POINTS[2],
            'wait_time': 4000,
            'park_time': 500,
            'order_id': 'aaaa3',
            'point_id': 'bbbb3',
        },
    ]

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [position] + POINTS
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

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        pass

    @testpoint('publish-timelefts')
    def publish_timelefts(data):
        assert data == {
            'contractor': dbid_uuid,
            'etas': [
                {
                    'distance_left': 1043.0,
                    'order_id': 'aaaa1',
                    'destination': POINTS[0],
                    'point_id': 'bbbb1',
                    'time_left': (
                        int(225 * MULTIPLIER)
                        + transporting_points[0]['park_time']
                    ),
                },
                {
                    'distance_left': 2525.0,
                    'order_id': 'aaaa2',
                    'destination': POINTS[1],
                    'point_id': 'bbbb2',
                    'time_left': (
                        int(305 * MULTIPLIER)
                        + transporting_points[0]['park_time']
                        + transporting_points[0]['wait_time']
                        + transporting_points[1]['park_time']
                    ),
                },
                {
                    'distance_left': 5491.0,
                    'order_id': 'aaaa3',
                    'destination': POINTS[2],
                    'point_id': 'bbbb3',
                    'time_left': (
                        int(450 * MULTIPLIER)
                        + transporting_points[0]['park_time']
                        + transporting_points[0]['wait_time']
                        + transporting_points[1]['park_time']
                        + transporting_points[1]['wait_time']
                        + transporting_points[2]['park_time']
                    ),
                },
            ],
            'position': position,
        }

    @testpoint('reset-watch-completed')
    def reset_watch_completed(data):
        pass

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    await drw.enable_testpoints()

    # start watch with right position
    body = {
        'courier': dbid_uuid,
        'path': transporting_points,
        'position': position,
        'transport_type': 'car',
        'eta_multiplier': MULTIPLIER,
        'service_id': SERVICE_ID,
    }
    response = await drw.post('cargo/start-watch', json=body)
    assert response.status_code == 200
    await logbroker_event_done.wait_call()

    Utils.publish_position(
        driver_id,
        position,
        redis_store,
        now,
        channel='channel:yagr:world:positions',
    )

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()

    # wait publish in drw:timelefts channel and check correctness
    await publish_timelefts.wait_call()

    # stop watch
    response = await drw.post(
        'cargo/stop-watch',
        json={'courier': dbid_uuid, 'service_id': SERVICE_ID},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # process message
    await logbroker_event_done.wait_call()
    await stop_watch_message_processed.wait_call()
    await reset_watch_completed.wait_call()

    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {}
    redis_store.flushall()
