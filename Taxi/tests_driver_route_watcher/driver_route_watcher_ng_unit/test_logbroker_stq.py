import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs


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


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_logbroker_stq_reset_all_destinations(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-removed-from-db')
    def _mock_db_remove(request):
        return {}

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    # add watched destination
    new_destination_kwargs = {
        'field': 'source',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'source': [37.37, 55.55],
        'event_timestamp': 1626954768.96,
        'msg_timestamp': 1626954768.96,
        'now': '2021-07-27T12:34:56.789+0000',
    }
    await drw.watches_lb_channel.send(new_destination_kwargs)
    assert (await _mock_performer.wait_call())['request'] == 'ok'

    # reset destination
    reset_destination_kwargs = {
        'field': 'all',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'destinations': [[11.11, 11.11], [37.37, 55.55], [22.22, 22.22]],
        'destinations_statuses': [True],
        'source': [0, 0],
        'reset': True,
        'event_timestamp': 1626954768.96,
        'msg_timestamp': 1626954768.96,
        'now': '2021-07-27T12:34:56.789+0000',
    }
    await drw.watches_lb_channel.send(reset_destination_kwargs)

    assert (await _mock_db_remove.wait_call())['request'] == 'ok'


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_logbroker_stq_destination_source(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'field': 'source',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'source': [37.37, 55.55],
    }
    await drw.watches_lb_channel.send(kwargs)

    assert (await _mock_performer.wait_call())['request'] == 'ok'


# turned off by config but enabled by experiment
@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=0)
@pytest.mark.experiments3(filename='exp3_use_logbroker.json')
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_logbroker_stq_destination_source_by_exp(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'field': 'source',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'source': [37.37, 55.55],
        'event': {'some_key': 'some_value'},
    }
    await drw.watches_lb_channel.send(kwargs)

    assert (await _mock_performer.wait_call())['request'] == 'ok'


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
async def test_logbroker_stq_destination_destinations(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    await drw.invalidate_caches()

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'field': 'destinations',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'destinations': [[37.37, 55.55]],
        'destinations_statuses': [False],
        'service_id': 'processing',
        'order_id': 'order_id0',
        'taxi_status': 'driving',
    }
    await drw.watches_lb_channel.send(kwargs)

    mock_result = (await _mock_performer.wait_call())['request']
    assert mock_result == 'ok'


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
async def test_logbroker_stq_do_not_sigsegv_on_missing_driver_id(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    await drw.invalidate_caches()

    @testpoint('logbroker-event-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'field': 'destinations',
        # 'driver_uuid': 'uuid0',
        # 'driver_dbid': 'dbid0',
        'destinations': [[37.37, 55.55]],
        'destinations_statuses': [False],
        'service_id': 'processing',
        'order_id': 'order_id0',
        'taxi_status': 'driving',
    }
    await drw.watches_lb_channel.send(kwargs)

    mock_result = (await _mock_performer.wait_call())['request']
    assert mock_result == 'failed-to-parse'


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
async def test_logbroker_destinations_direct_to_worker(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    await drw.invalidate_caches()

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    @testpoint('master-commands-channel-store')
    def _mock_master_channel_store(request):
        return {}

    @testpoint('start-watch-message-received')
    def _mock_start_watch_message_processed(request):
        # points precision truncated to 6 digits after point
        assert request['full_destinations'] == _to_full_destinations(
            [[37.37, 55.55]],
        )
        assert request['service_id'] == 'processing'
        return {}

    kwargs = {
        'field': 'destinations',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'destinations': [[37.370000123, 55.550000123]],
        'destinations_statuses': [False],
        'event': {'some_key': 'some_value'},
        'service_id': 'processing',
        'order_id': 'order_id0',
        'taxi_status': 'driving',
    }
    await drw.watches_lb_channel.send(kwargs)

    mock_result = (await _mock_performer.wait_call())['request']
    assert mock_result == 'ok'

    await _mock_start_watch_message_processed.wait_call()
    assert _mock_master_channel_store.times_called == 0


@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.parametrize(
    'kwargs',
    [
        {
            'field': 'source',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'source': [37.37, 55.55],
            'reset': True,
        },
        {
            # not visited point
            'field': 'destinations',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'destinations': [[37.37, 55.55]],
            'destinations_statuses': [False],
            'reset': True,
        },
        {
            # visited point
            'field': 'destinations',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'destinations': [[37.37, 55.55]],
            'destinations_statuses': [True],
            'reset': True,
        },
        {
            # Multiple points
            'field': 'all',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'destinations': [[37.37, 55.55]],
            'destinations_statuses': [True],
            'source': [37.37, 55.55],
            'reset': True,
        },
        {
            # Multiple points without destinations
            'field': 'all',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'destinations': [],
            'destinations_statuses': [True],
            'source': [37.37, 55.55],
            'reset': True,
        },
        {
            # Multiple points with empty source
            'field': 'all',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'destinations': [[37.37, 55.55]],
            'destinations_statuses': [True],
            'source': [0, 0],
            'reset': True,
        },
        {
            # no destinations, order with unknown B
            'field': 'destinations',
            'driver_uuid': 'uuid0',
            'driver_dbid': 'dbid0',
            'source': [37.37, 55.55],
            'reset': True,
        },
    ],
)
async def test_logbroker_stq_reset_destination(
        driver_route_watcher_ng_adv, testpoint, kwargs,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-reset-destination-done')
    def _mock_performer(request):
        return {}

    await drw.watches_lb_channel.send(kwargs)

    assert (await _mock_performer.wait_call())['request'] == 'ok'


# test that we have expected number of commands generated by each message
@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.parametrize(
    'kwargs,testpoint_name,min_stop_calls',
    [
        (
            {
                'field': 'source',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'source': [37.37, 55.55],
                'reset': True,
                'service_id': 'processing:driving',
            },
            'stop-watch-message-processed',
            1,
        ),
        (
            {
                # Multiple points
                'field': 'all',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'destinations': [[37.37, 55.55]],
                'destinations_statuses': [True],
                'source': [37.37, 55.55],
                'reset': True,
                'service_id': 'processing',
            },
            'stop-watch-message-processed',
            2,  # source + (source + destinations)
        ),
        (
            {
                # Multiple points without destinations
                'field': 'all',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'destinations': [],
                'destinations_statuses': [],
                'source': [37.37, 55.55],
                'reset': True,
                'service_id': 'processing',
            },
            'stop-watch-message-processed',
            2,  # source + unknown destiantion
        ),
        (
            {
                # no destinations, order with unknown B
                'field': 'all',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'source': [37.37, 55.55],
                'service_id': 'processing',
                'reset': True,
            },
            'stop-watch-message-processed',
            # source + 1 point [0, 0] for missing destination point
            2,
        ),
    ],
)
async def test_logbroker_stq_reset_destination_direct(
        driver_route_watcher_ng_adv,
        testpoint,
        kwargs,
        testpoint_name,
        min_stop_calls,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-reset-destination-done')
    def _mock_performer(request):
        return {}

    @testpoint(testpoint_name)
    def _mock_stop_watch_message_processed(request):
        return {}

    @testpoint('master-commands-channel-store')
    def _mock_master_channel_store(request):
        return {}

    await drw.watches_lb_channel.send(kwargs)

    assert (await _mock_performer.wait_call())['request'] == 'ok'

    for _ in range(min_stop_calls):
        await _mock_stop_watch_message_processed.wait_call()
    assert _mock_master_channel_store.times_called == 0


@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
async def test_logbroker_stq_reset_destination_direct_correct_2(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    # on stop all
    # we should cancel 'source' and each of 'destinations'.
    # now source is duplicated due to inperfection of normalizing algorithm
    # after source we cancell all points in message including 'source' again
    expected_points = [[33, 44], [33, 44], [77, 88], [99, 100]]
    expected_points_count = len(expected_points)
    kwargs = {
        'field': 'all',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'source': [33.0000001234, 44.0000000321],
        'destinations': [
            [77.0000002222, 88.000000222],
            [99.000000321, 100.000000123],
        ],
        'destinations_statuses': [],
        'taxi_status': 'transporting',
        'service_id': 'processing',
        'reset': True,
    }

    @testpoint('stq-event-reset-destination-done')
    def _mock_performer(request):
        return {}

    current_index = 0

    @testpoint('stop-watch-message-processed')
    def _mock_stop_watch_message_processed(request):
        nonlocal current_index
        point = request['full_destinations'][-1]['point']
        assert point == expected_points[current_index]
        current_index = current_index + 1
        return {}

    @testpoint('master-commands-channel-store')
    def _mock_master_channel_store(request):
        return {}

    await drw.watches_lb_channel.send(kwargs)
    assert (await _mock_performer.wait_call())['request'] == 'ok'
    for _ in range(expected_points_count):
        await _mock_stop_watch_message_processed.wait_call()
    assert _mock_master_channel_store.times_called == 0


@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
async def test_logbroker_stq_reset_destination_direct_correct_unknown(
        driver_route_watcher_ng_adv, testpoint,
):
    drw = driver_route_watcher_ng_adv

    # can be changed to [[33, 44], [0, 0]]
    expected_points = [[33, 44], [33, 44], [0, 0]]
    expected_points_count = len(expected_points)
    kwargs = {
        'field': 'all',
        'driver_uuid': 'uuid0',
        'driver_dbid': 'dbid0',
        'source': [33.000000123, 44.000000123],
        'destinations': [],
        'destinations_statuses': [],
        'taxi_status': 'transporting',
        'service_id': 'processing',
        'reset': True,
    }

    @testpoint('stq-event-reset-destination-done')
    def _mock_performer(request):
        return {}

    current_index = 0

    @testpoint('stop-watch-message-processed')
    def _mock_stop_watch_message_processed(request):
        nonlocal current_index
        expected_point = expected_points[current_index]
        if expected_point != [0, 0]:
            point = request['full_destinations'][-1]['point']
            assert point == expected_point
        else:
            assert request['full_destinations'] == []
        current_index = current_index + 1
        return {}

    @testpoint('master-commands-channel-store')
    def _mock_master_channel_store(request):
        return {}

    await drw.watches_lb_channel.send(kwargs)
    assert (await _mock_performer.wait_call())['request'] == 'ok'
    for _ in range(expected_points_count):
        await _mock_stop_watch_message_processed.wait_call()
    assert _mock_master_channel_store.times_called == 0


@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.parametrize(
    'kwargs,testpoint_name,expected_points,expected_point,expected_service_id',
    [
        (
            {
                'field': 'source',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'source': [11.000000123, 22.000000123],
                'service_id': 'processing:driving',
            },
            'start-watch-message-received',
            [[11, 22]],
            [11, 22],
            'processing:driving',
        ),
        (
            {
                # Multiple points
                'field': 'destinations',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'destinations': [
                    [33.000000123, 44.000000123],
                    [55.000000123, 66.000000123],
                ],
                'destinations_statuses': [],
                'source': [37.370000123, 55.550000123],
                'service_id': 'processing:transporting',
                'taxi_status': 'transporting',
            },
            'start-watch-message-received',
            [[33, 44], [55, 66]],
            [55, 66],
            'processing:transporting',
        ),
        (
            {
                # Multiple points, one passed
                'field': 'destinations',
                'driver_uuid': 'uuid0',
                'driver_dbid': 'dbid0',
                'destinations': [
                    [33.000000123, 44.000000123],
                    [55.000000123, 66.000000123],
                ],
                'destinations_statuses': [True],
                'source': [37.370000123, 55.550000123],
                'service_id': 'processing:transporting',
                'taxi_status': 'transporting',
            },
            'start-watch-message-received',
            [[55, 66]],
            [55, 66],
            'processing:transporting',
        ),
    ],
)
async def test_logbroker_new_destination_direct(
        driver_route_watcher_ng_adv,
        testpoint,
        kwargs,
        testpoint_name,
        expected_points,
        expected_point,
        expected_service_id,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    @testpoint(testpoint_name)
    def _mock_start_watch_message_processed(request):
        assert request['full_destinations'] == _to_full_destinations(
            expected_points,
        )
        assert request['service_id'] == expected_service_id
        return {}

    @testpoint('master-commands-channel-store')
    def _mock_master_channel_store(request):
        return {}

    await drw.watches_lb_channel.send(kwargs)

    assert (await _mock_performer.wait_call())['request'] == 'ok'

    await _mock_start_watch_message_processed.wait_call()
    assert _mock_master_channel_store.times_called == 0


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.parametrize(
    'kwargs',
    [
        {
            'driver_dbid': 'driver0_dbid',
            'driver_uuid': 'driver0_uuid',
            'internal': {
                'destination': {
                    'full_destinations': PointlistFbs.to_point_list(
                        [[37.37, 55.55]], compact=True,
                    ),
                    'metainfo': '{"order_id":"orderid123456"}',
                    'order_id': 'orderid123456',
                    'service_id': 'processing',
                    'transport_type': 'pedestrian',
                },
                'operation': 'start',
            },
        },
        {
            'driver_dbid': 'dbid',
            'driver_uuid': 'uuid',
            'internal': {
                'destination': {
                    'full_destinations': [
                        {
                            'point': x['point'],
                            'point_id': x['point_id'],
                            'order_id': x['order_id'],
                            'wait_time': x['wait_time'],
                            'park_time': x['park_time'],
                        }
                        for x in TRANSPORTING_POINTS
                    ],
                    'service_id': 'cargo-dispatch',
                    'source_position': [37.455596, 55.719463],
                    'transport_type': 'bicycle',
                },
                'operation': 'start_by_orders',
            },
        },
    ],
)
async def test_logbroker_start_watch_from_http(
        driver_route_watcher_ng_adv, testpoint, kwargs, mockserver,
):
    drw = driver_route_watcher_ng_adv

    await drw.invalidate_caches()

    @mockserver.handler('/maps-bicycle-router/v2/route')
    def _mock_route(data):
        return mockserver.make_response(status=200)

    @testpoint('logbroker-executing-by-operation')
    def _mock_performer(request):
        del request

    @testpoint('start-watch-message-processed')
    def _mock_start_watch_message_processed(request):
        del request

    await drw.watches_lb_channel.send(kwargs)

    mock_result = (await _mock_performer.wait_call())['request']
    assert mock_result == 'ok'
    await _mock_start_watch_message_processed.wait_call()


@pytest.mark.servicetest
@pytest.mark.config(DRIVER_ROUTE_WATCHER_LB_STQ_PERCENTAGE=100)
@pytest.mark.experiments3(filename='exp3_direct_to_worker.json')
@pytest.mark.parametrize(
    'kwargs,testpoint_name',
    [
        (
            {
                'driver_dbid': 'driver0_dbid',
                'driver_uuid': 'driver0_uuid',
                'internal': {
                    'destination': {
                        'full_destinations': PointlistFbs.to_point_list(
                            [[37.37, 55.55]], compact=True,
                        ),
                        'service_id': 'processing',
                    },
                    'operation': 'stop',
                },
                'reset': True,
            },
            'stop-watch-message-processed',
        ),
        (
            {
                'driver_dbid': 'dbid',
                'driver_uuid': 'uuid',
                'internal': {
                    'destination': {
                        'full_destinations': [],
                        'service_id': 'cargo-dispatch',
                    },
                    'operation': 'stop_by_orders',
                },
            },
            'stop-watch-message-processed',
        ),
        (
            {
                'driver_dbid': 'dbid',
                'driver_uuid': 'uuid',
                'internal': {
                    'destination': {
                        'full_destinations': [],
                        'service_id': 'cargo-dispatch',
                        'inactive_orders': ['aaa', 'bbb'],
                    },
                    'operation': 'stop_by_orders',
                },
            },
            'stop-watch-by-order-id-message-processed',
        ),
    ],
)
async def test_logbroker_stop_watch_from_http(
        driver_route_watcher_ng_adv, testpoint, kwargs, testpoint_name,
):
    drw = driver_route_watcher_ng_adv

    await drw.invalidate_caches()

    @testpoint('logbroker-executing-by-operation')
    def _mock_performer(request):
        del request

    @testpoint(testpoint_name)
    def _mock_stop_watch_message_processed(request):
        del request

    await drw.watches_lb_channel.send(kwargs)

    mock_result = (await _mock_performer.wait_call())['request']
    assert mock_result == 'ok'
    await _mock_stop_watch_message_processed.wait_call()


def _to_full_destinations(points):
    return [{'point': x} for x in points]
