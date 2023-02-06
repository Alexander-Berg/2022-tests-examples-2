import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.watch_list as WatchList


# denerated via: `tvmknife unittest service -s 1234 -d 2345`
_MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYI0gkQqRI:HbmxAVGaPWnEC7_gBlt9Q'
    'tnCXMIwDUVeSrZEXzLp1RpifteB9yPf32ec9mMvt5zWTtOgiK8qr7n52'
    '8FbBTSaCWIHTjB8V_14LnjbaNTvPz-9SvEpQdqJjFRW9yvK3UPDull75'
    'fBLqGwfYp-SmeaxM6VKwWfXD0QZEjY8ZezV2r8'
)


@pytest.mark.servicetest
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher-ng', 'src': 'processing'}],
)
async def test_start_watch(
        driver_route_watcher_ng_adv, redis_store, testpoint,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        pass

    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    driver_id = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    dbid_uuid = '_'.join([driver_id['dbid'], driver_id['uuid']])
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
    await logbroker_event_done.wait_call()

    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid]['processing'].get('watched_since')
    assert watchlist[dbid_uuid]['processing'].get('destination')
    assert watchlist[dbid_uuid]['processing'].pop('watched_since')
    assert watchlist[dbid_uuid]['processing'].pop('destination')
    assert watchlist == {
        dbid_uuid: {
            'processing': {
                'meta': {'order_id': 'orderid123456'},
                'points': PointlistFbs.to_point_list([destination]),
                'service': 'processing',
                'router_type': 'car',
                'order_id': 'orderid123456',
            },
        },
    }


@pytest.mark.servicetest
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher-ng', 'src': 'processing'}],
)
async def test_start_watch_400(driver_route_watcher_ng_adv):
    drw = driver_route_watcher_ng_adv

    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    driver_id = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    body = {'driver': driver_id, 'metainfo': {'order_id': 'orderid123456'}}
    response = await drw.post('start-watch', json=body, headers=headers)
    # Status code must be checked for every request
    assert response.status_code == 400
    # Response content (even empty) must be checked for every request
    assert response.content == b'{}'


@pytest.mark.servicetest
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher-ng', 'src': 'processing'}],
)
async def test_start_watch_pedestrian(
        driver_route_watcher_ng_adv, redis_store, testpoint,
):
    drw = driver_route_watcher_ng_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    driver_id = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    dbid_uuid = '_'.join([driver_id['dbid'], driver_id['uuid']])
    destination = [37.37, 55.55]
    body = {
        'driver': driver_id,
        'destination_point': destination,
        'metainfo': {'order_id': 'orderid123456'},
        'router_type': 'pedestrian',
    }
    response = await drw.post('start-watch', json=body, headers=headers)
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b'{}'
    await logbroker_event_done.wait_call()

    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid]['processing'].get('watched_since')
    assert watchlist[dbid_uuid]['processing'].get('destination')
    assert watchlist[dbid_uuid]['processing'].pop('watched_since')
    assert watchlist[dbid_uuid]['processing'].pop('destination')
    assert watchlist == {
        dbid_uuid: {
            'processing': {
                'meta': {'order_id': 'orderid123456'},
                'points': PointlistFbs.to_point_list([destination]),
                'service': 'processing',
                'router_type': 'pedestrian',
            },
        },
    }
