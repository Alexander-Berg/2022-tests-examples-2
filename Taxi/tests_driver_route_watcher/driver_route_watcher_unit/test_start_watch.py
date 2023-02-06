import pytest

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.watch_list as WatchList


# denerated via: `tvmknife unittest service -s 1234 -d 2345`
_MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYI0gkQqRI:IDbjEH-8IgZhNiGoxmKupt'
    '8nxnAhSmwbVU17XdmSJOhWpeskKng3K5M26Bj4nXmOAuiqYEVyFBYsa7K'
    'qqqo0IEzUqZeZcHCvGtx1ni1MBPWmNXpbBi74i1G3zGpbN4RH-63dUrK_'
    'ppS16MVIfIn0SLUbvTwVXf4NmCjXnFwr_JM'
)


@pytest.mark.servicetest
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher', 'src': 'processing'}],
)
async def test_start_watch(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

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
    TVM_RULES=[{'dst': 'driver-route-watcher', 'src': 'processing'}],
)
async def test_start_watch_400(taxi_driver_route_watcher, redis_store):
    headers = {'X-Ya-Service-Ticket': _MOCK_TICKET}
    driver_id = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    body = {'driver': driver_id, 'metainfo': {'order_id': 'orderid123456'}}
    response = await taxi_driver_route_watcher.post(
        'start-watch', json=body, headers=headers,
    )
    # Status code must be checked for every request
    assert response.status_code == 400
    # Response content (even empty) must be checked for every request
    assert response.content == b'{}'


@pytest.mark.servicetest
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'driver-route-watcher', 'src': 'processing'}],
)
async def test_start_watch_pedestrian(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

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
