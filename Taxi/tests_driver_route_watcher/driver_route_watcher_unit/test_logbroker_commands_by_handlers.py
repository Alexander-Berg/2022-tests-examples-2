import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.utils as Utils


# denerated via: `tvmknife unittest service -s 1234 -d 2345`
_MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYI0gkQqRI:IDbjEH-8IgZhNiGoxmKupt'
    '8nxnAhSmwbVU17XdmSJOhWpeskKng3K5M26Bj4nXmOAuiqYEVyFBYsa7K'
    'qqqo0IEzUqZeZcHCvGtx1ni1MBPWmNXpbBi74i1G3zGpbN4RH-63dUrK_'
    'ppS16MVIfIn0SLUbvTwVXf4NmCjXnFwr_JM'
)
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
@pytest.mark.experiments3(filename='exp3_use_logbroker_in_http_handlers.json')
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher', 'src': 'processing'}],
)
async def test_logbroker_by_start_watch(
        taxi_driver_route_watcher, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher

    @testpoint('sent-to-logbroker-channel')
    def sent_to_logbroker(data):
        assert data == {
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
                },
                'operation': 'start',
            },
        }

    await Utils.request_ping(drw)

    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    driver_id = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    # dbid_uuid = '_'.join([driver_id['dbid'], driver_id['uuid']])
    destination = [37.37, 55.55]
    body = {
        'driver': driver_id,
        'destination_point': destination,
        'metainfo': {'order_id': 'orderid123456'},
        'service_id': 'processing',
    }
    response = await drw.post('start-watch', json=body, headers=headers)
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b'{}'

    # just sent to logbroker
    await sent_to_logbroker.wait_call()


@pytest.mark.experiments3(filename='exp3_use_logbroker_in_http_handlers.json')
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher', 'src': 'processing'}],
)
@pytest.mark.servicetest
async def test_logbroker_by_stop_watch(taxi_driver_route_watcher, testpoint):
    drw = taxi_driver_route_watcher

    @testpoint('sent-to-logbroker-channel')
    def sent_to_logbroker(data):
        assert data == {
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
        }

    await Utils.request_ping(drw)

    driver = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    destination = [37.37, 55.55]
    body = {'driver': driver, 'destination_point': destination}
    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    response = await drw.post('stop-watch', json=body, headers=headers)
    assert response.status_code == 200
    assert response.content == b'{}'

    # just sent to logbroker
    await sent_to_logbroker.wait_call()


@pytest.mark.servicetest
@pytest.mark.experiments3(filename='exp3_use_logbroker_in_http_handlers.json')
async def test_logbroker_cargo_start_watch_by_position(
        taxi_driver_route_watcher, testpoint, mockserver,
):
    drw = taxi_driver_route_watcher

    raw_position = [37.455596, 55.719463]
    dbid_uuid = 'dbid_uuid'

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(data):
        return mockserver.make_response(status=200)

    @testpoint('sent-to-logbroker-channel')
    def sent_to_logbroker(data):
        assert data == {
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
                    'source_position': raw_position,
                },
                'operation': 'start_by_orders',
            },
        }

    await Utils.request_ping(drw)

    body = {
        'courier': dbid_uuid,
        'path': TRANSPORTING_POINTS,
        'position': raw_position,
        'transport_type': 'car',
        'service_id': 'cargo-dispatch',
    }
    response = await drw.post('cargo/start-watch', json=body)
    # Test response
    assert response.status_code == 200
    # just sent to logbroker
    await sent_to_logbroker.wait_call()


@pytest.mark.experiments3(filename='exp3_use_logbroker_in_http_handlers.json')
@pytest.mark.servicetest
async def test_logbroker_cargo_stop_watch_wo_orders(
        taxi_driver_route_watcher, testpoint, mockserver,
):
    drw = taxi_driver_route_watcher

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(data):
        return mockserver.make_response(status=200)

    @testpoint('sent-to-logbroker-channel')
    def sent_to_logbroker(data):
        assert data == {
            'driver_dbid': 'dbid',
            'driver_uuid': 'uuid',
            'internal': {
                'destination': {
                    'full_destinations': [],
                    'service_id': 'cargo-dispatch',
                },
                'operation': 'stop_by_orders',
            },
        }

    body = {'courier': 'dbid_uuid', 'service_id': 'cargo-dispatch'}
    response = await drw.post('cargo/stop-watch', json=body)
    assert response.status_code == 200
    assert response.json() == {}

    # just sent to logbroker
    await sent_to_logbroker.wait_call()


@pytest.mark.experiments3(filename='exp3_use_logbroker_in_http_handlers.json')
@pytest.mark.servicetest
async def test_logbroker_cargo_stop_watch_orders(
        taxi_driver_route_watcher, testpoint,
):
    drw = taxi_driver_route_watcher

    orders_to_stop = ['aaa', 'bbb']

    @testpoint('sent-to-logbroker-channel')
    def sent_to_logbroker(data):
        assert set(
            data['internal']['destination'].pop('inactive_orders'),
        ) == set(orders_to_stop)
        assert data == {
            'driver_dbid': 'dbid',
            'driver_uuid': 'uuid',
            'internal': {
                'destination': {
                    'full_destinations': [],
                    'service_id': 'cargo-dispatch',
                },
                'operation': 'stop_by_orders',
            },
        }

    body = {
        'courier': 'dbid_uuid',
        'service_id': 'cargo-dispatch',
        'orders': orders_to_stop,
    }
    response = await drw.post('cargo/stop-watch', json=body)
    assert response.status_code == 200
    assert response.json() == {}

    # just sent to logbroker
    await sent_to_logbroker.wait_call()
