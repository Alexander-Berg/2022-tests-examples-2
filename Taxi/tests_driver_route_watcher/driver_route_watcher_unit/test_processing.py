# pylint: disable=import-error,too-many-lines
import pytest

import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_processing_happy_path(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    await drw.enable_testpoints()

    redis_store.flushall()

    driver_id = {'uuid': 'uuidpedestrian', 'dbid': 'dbid'}
    dst1 = [37.45, 55.71]
    dst2 = [37.55, 55.71]
    driving = 'processing:driving'
    transporting = 'processing:transporting'
    processing = 'processing'
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])

    # start driving
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst1, service_id=driving,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {driving}
    assert watchlist[dbid_uuid][driving]['router_type'] == 'pedestrian'

    # start transporting
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst2, service_id=transporting,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {transporting, driving}

    # finish order
    await drw.watches_lb_channel.stop_watch_old(
        driver_id, [dst1, dst2], processing,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    redis_store.flushall()


@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_processing_chain_path(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    await drw.enable_testpoints()

    redis_store.flushall()

    driver_id = {'uuid': 'uuid0', 'dbid': 'dbid'}
    dst1 = [37.45, 55.71]
    dst2 = [37.55, 55.71]
    dst3 = [37.65, 55.71]
    driving = 'processing:driving'
    transporting = 'processing:transporting'
    processing = 'processing'
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    meta1 = '{"order_id":"1"}'
    meta2 = '{"order_id":"2"}'
    order1 = 'order_id_1'
    order2 = 'order_id_2'

    # start driving
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst1, service_id=driving, meta=meta1, order_id=order1,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {driving}

    # start transporting order1
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst2, service_id=transporting, meta=meta1, order_id=order1,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {transporting, driving}
    assert watchlist[dbid_uuid][transporting]['meta']['metainfo'] == meta1
    assert watchlist[dbid_uuid][transporting]['order_id'] == order1
    assert watchlist[dbid_uuid][driving]['meta']['metainfo'] == meta1
    assert watchlist[dbid_uuid][driving]['order_id'] == order1

    # start driving next order (order2)
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst3, service_id=driving, meta=meta2, order_id=order2,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {transporting, driving}
    assert watchlist[dbid_uuid][transporting]['meta']['metainfo'] == meta1
    assert watchlist[dbid_uuid][driving]['meta']['metainfo'] == meta2
    assert watchlist[dbid_uuid][transporting]['order_id'] == order1
    assert watchlist[dbid_uuid][driving]['order_id'] == order2

    # finish first order
    await drw.watches_lb_channel.stop_watch_old(
        driver_id, [dst1, dst2], processing,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {driving}
    assert watchlist[dbid_uuid][driving]['meta']['metainfo'] == meta2
    assert watchlist[dbid_uuid][driving]['order_id'] == order2
    redis_store.flushall()


@pytest.mark.experiments3(filename='exp3_all_drivers_enabled.json')
async def test_processing_change_destination_in_driving(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    await drw.enable_testpoints()

    redis_store.flushall()

    driver_id = {'uuid': 'uuid0', 'dbid': 'dbid'}
    dst1 = [37.45, 55.71]
    dst2 = [37.55, 55.71]
    driving = 'processing:driving'
    transporting = 'processing:transporting'
    processing = 'processing'
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])

    # start driving
    await drw.watches_lb_channel.start_watch_old(
        driver_id, dst1, service_id=driving, meta='{}', taxi_status='driving',
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {driving}

    # case when destination (B) changed by user while in 'driving' state
    await drw.watches_lb_channel.start_watch_old(
        driver_id,
        dst2,
        service_id=transporting,
        meta='{}',
        taxi_status='driving',
    )
    await logbroker_event_done.wait_call()

    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {
        # no more transporting in this case
        driving,
    }

    # case when status changed to 'transporting'
    await drw.watches_lb_channel.start_watch_old(
        driver_id,
        dst2,
        service_id=transporting,
        meta='{}',
        taxi_status='transporting',
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist[dbid_uuid].keys() == {transporting, driving}

    # finish order
    await drw.watches_lb_channel.stop_watch_old(
        driver_id, [dst1, dst2], processing,
    )
    await logbroker_event_done.wait_call()
    watchlist = WatchList.get_watchlist(redis_store)
    assert watchlist == {}

    redis_store.flushall()
