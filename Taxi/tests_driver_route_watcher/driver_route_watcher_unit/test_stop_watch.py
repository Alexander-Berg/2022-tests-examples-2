import pytest

import tests_driver_route_watcher.watch_list as WatchList


@pytest.mark.servicetest
async def test_stop_watch(taxi_driver_route_watcher):
    driver = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    destination = [37.37, 55.55]
    response = await _request_stop_watch(
        driver, destination, taxi_driver_route_watcher,
    )
    assert response.status_code == 200
    assert response.content == b'{}'


@pytest.mark.servicetest
async def test_stop_watch_400(taxi_driver_route_watcher):
    driver = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    body = {'driver': driver}
    response = await taxi_driver_route_watcher.post('stop-watch', json=body)
    assert response.status_code == 400
    assert response.content == b'{}'


@pytest.mark.servicetest
async def test_unexpected_stop_watch(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    driver = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    destination = [37.37, 55.55]
    deleted_key = 'dw/{{{}_{}}}/'.format(driver['dbid'], driver['uuid'])

    # add destination
    response = await _request_start_watch(driver, destination, drw)
    assert response.status_code == 200
    assert response.content == b'{}'
    await logbroker_event_done.wait_call()

    # check redis contents
    # 1. watchlist
    # 2. reseted
    watch_list = WatchList.get_watchlist(redis_store)
    assert len(watch_list) == 1
    deleted_values = redis_store.smembers(deleted_key)
    assert deleted_values == set()

    # try reset destination with wrong expected value
    response = await _request_stop_watch(driver, [38.38, 60.60], drw)
    assert response.status_code == 200
    assert response.content == b'{}'
    await logbroker_event_done.wait_call()

    # failed to reset
    watch_list = WatchList.get_watchlist(redis_store)
    assert len(watch_list) == 1  # still holds watch
    deleted_values = redis_store.smembers(deleted_key)
    assert len(deleted_values) == 1  # added reseted position

    # try reset destination with correct expected value
    response = await _request_stop_watch(driver, destination, drw)
    assert response.status_code == 200
    assert response.content == b'{}'
    # it is done in start/stop-watch
    # await logbroker_event_done.wait_call()

    # succeded to reset
    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {}
    deleted_values = redis_store.smembers(deleted_key)
    assert len(deleted_values) == 2  # added reseted position


@pytest.mark.servicetest
async def test_reseted_values_prevent_start(
        taxi_driver_route_watcher_adv, redis_store, testpoint,
):
    drw = taxi_driver_route_watcher_adv

    @testpoint('logbroker-event-done')
    def logbroker_event_done(data):
        del data

    # if this test become flaky see ttl of deleted values

    driver = {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'}
    destination = [37.37, 55.55]
    deleted_key = 'dw/{{{}_{}}}/'.format(driver['dbid'], driver['uuid'])

    # try reset destination with correct expected value
    response = await _request_stop_watch(driver, destination, drw)
    assert response.status_code == 200
    assert response.content == b'{}'

    # succeded to reset
    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {}
    deleted_values = redis_store.smembers(deleted_key)
    assert len(deleted_values) == 1  # added reseted position

    # add reseted destination
    response = await _request_start_watch(driver, destination, drw)
    assert response.status_code == 200
    assert response.content == b'{}'
    await logbroker_event_done.wait_call()

    # check redis contents
    # no new watches cause previuous 'reset' prevent 'start'
    watch_list = WatchList.get_watchlist(redis_store)
    assert watch_list == {}

    # add new destination not listed in deleted_values
    response = await _request_start_watch(driver, [38.38, 60.60], drw)
    assert response.status_code == 200
    assert response.content == b'{}'
    await logbroker_event_done.wait_call()

    # failed to reset
    watch_list = WatchList.get_watchlist(redis_store)
    assert len(watch_list) == 1  # no holds watch
    deleted_values = redis_store.smembers(deleted_key)
    assert len(deleted_values) == 1


async def _request_start_watch(
        driver_id, destination, taxi_driver_route_watcher,
):
    body = {'driver': driver_id, 'destination_point': destination}
    return await taxi_driver_route_watcher.post('start-watch', json=body)


async def _request_stop_watch(
        driver_id, destination, taxi_driver_route_watcher,
):
    body = {'driver': driver_id, 'destination_point': destination}
    return await taxi_driver_route_watcher.post('stop-watch', json=body)
