# pylint: disable=import-error
import json

from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils

from tests_driver_route_watcher import watches_lb_channel


def _to_dbid_uuid(driver_id):
    uuid = driver_id['uuid']
    dbid = driver_id['dbid']
    return '_'.join([dbid, uuid])


def get_route(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    return redis_store.hget(key, 'route')


def get_output(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    return redis_store.hget(key, 'output')


def get_current_state(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    return redis_store.hget(key, 'fsm_current_state')


def get_current_state_time_start(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    return redis_store.hget(key, 'fsm_current_state_start_time')


def get_driver_position(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    return redis_store.hget(key, 'driver_position')


async def request_ping(taxi_driver_route_watcher):
    return await taxi_driver_route_watcher.get('ping')


async def request_timeleft(
        driver_id,
        taxi_driver_route_watcher,
        meta=None,
        order_id=None,
        with_route=False,
        force_log=False,
):
    body = {
        'driver': driver_id,
        'with_route': with_route,
        'verbose_log': force_log,
    }
    if meta is not None:
        body.update({'meta': meta})
    if order_id is not None:
        body.update({'order_id': order_id})
    return await taxi_driver_route_watcher.post('timeleft', json=body)


async def request_diag(driver_id, taxi_driver_route_watcher):
    if driver_id:
        body = {'driver': driver_id}
    else:
        body = {}
    return await taxi_driver_route_watcher.post('diag-driver', json=body)


async def request_timeleft_as_string(
        driver_id, taxi_driver_route_watcher, meta=None, order_id=None,
):
    return await request_timeleft(
        _to_dbid_uuid(driver_id), taxi_driver_route_watcher, meta, order_id,
    )


async def request_start_watch(
        driver_id,
        destination,
        taxi_driver_route_watcher,
        router_type='car',
        toll_roads=False,
        service_id='driving',
):
    body = {
        'driver': driver_id,
        'metainfo': {'order_id': '12345', 'taxi_status': 'driving'},
        'router_type': router_type,
        'toll_roads': toll_roads,
        'service_id': service_id,
    }
    if isinstance(destination[0], list):
        body.update({'destinations': destination})
    else:
        body.update({'destination_point': destination})
    return await taxi_driver_route_watcher.post('start-watch', json=body)


async def request_stop_watch(
        driver_id, destination, taxi_driver_route_watcher,
):
    body = {'driver': driver_id, 'service_id': 'driving'}
    if isinstance(destination[0], list):
        body.update({'destinations': destination})
    else:
        body.update({'destination_point': destination})
    return await taxi_driver_route_watcher.post('stop-watch', json=body)


def publish_position(
        driver_id, position, redis_store, now, direction=0, channel=None,
):
    timestamp = int(utils.timestamp(now))
    dbid_uuid = '_'.join([driver_id['dbid'], driver_id['uuid']])
    message = geobus.serialize_positions_v2(
        [
            {
                'driver_id': dbid_uuid,
                'position': position,
                'direction': direction,
                'timestamp': timestamp,
                'speed': 42,
                'accuracy': 0,
                'source': 'Gps',
            },
        ],
        now,
    )
    channel = channel or 'channel:yagr:position'
    redis_store.publish(channel, message)


def publish_edge_position(
        driver_id, position, redis_store, now, direction=0, channel=None,
):
    timestamp = int(utils.timestamp(now) * 1000)
    dbid_uuid = '_'.join([driver_id['dbid'], driver_id['uuid']])
    message = geobus.serialize_edge_positions_v2(
        [
            {
                'driver_id': dbid_uuid,
                'edge_id': 255,
                'position': position,
                'position_on_edge': 1.0,
                'direction': direction,
                'probability': 1.0,
                'speed': 42.0,
                'timestamp': timestamp,
                'log_likelihood': -1.5,
            },
        ],
        now,
    )
    channel = channel or 'channel:yaga:edge_positions'
    redis_store.publish(channel, message)


def subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


def get_message(listener, redis_store, max_tries=30, retry_action=None):
    """
    @param retry_action function to call to force service to publish
    """
    # wait while driver-route-watcher pass eta messages to output channel
    for _ in range(max_tries):
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'message':
            return message
        if retry_action is not None:
            # do something to force message publishing
            retry_action()
    return None


def read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message(timeout=0.2) is not None:
            print('**********')


def wrap_with_env(
        taxi_driver_route_watcher,
        redis_store,
        logbroker_helper,
        taxi_driver_route_watcher_aiohttp,
        testpoint,
):
    # wrapper for taxi_driver_route_watcher with required environment:
    # databases and logbroker
    class TaxiDriverRouteWatcher(taxi_driver_route_watcher.__class__):
        def __init__(self):
            # construct object:
            # taxi_driver_route_watcher is our base class.
            # add a member to it
            taxi_driver_route_watcher.__class__.__init__(
                self, taxi_driver_route_watcher_aiohttp,
            )
            self.watches_lb_channel = watches_lb_channel.WatchesLbChannel(
                logbroker_helper(taxi_driver_route_watcher),
            )
            self.redis_store = redis_store

            # pylint: disable=unused-variable
            @testpoint('logbroker_publish')
            async def logbroker_publish_testpoint(data):
                print('!!!!!! got publish {}'.format(data))
                await self.watches_lb_channel.send(json.loads(data['data']))

        async def start_watch(
                self,
                driver_id,
                destination,
                service='',
                meta='',
                destinations=None,
                order_id=None,
                router_type='car',
                toll_roads=False,
                timestamp=None,
                nearest_zone=None,
                country=None,
        ):
            @testpoint('logbroker-event-done')
            def logbroker_event_done(data):
                pass

            # WatchList.start_watch(
            #     self.redis_store,
            #     driver_id,
            #     destination,
            #     service=service,
            #     meta=meta,
            #     destinations=destinations,
            #     order_id=order_id,
            #     router_type=router_type,
            #     toll_roads=toll_roads,
            #     timestamp=timestamp,
            #     nearest_zone=nearest_zone,
            #     country=country,
            # )
            await self.watches_lb_channel.start_watch(
                driver_id,
                destination,
                service_id=service,
                metainfo=meta,
                destinations=destinations,
                order_id=order_id,
                transport_type=router_type,
                toll_roads=toll_roads,
                timestamp=timestamp,
                nearest_zone=nearest_zone,
                country=country,
            )

            await logbroker_event_done.wait_call()

        async def stop_watch(self, driver_id, destination, service=''):
            @testpoint('logbroker-event-done')
            def logbroker_event_done(data):
                del data

            # WatchList.stop_watch(
            #     self.redis_store, driver_id, destination, service,
            # )
            await self.watches_lb_channel.stop_watch(
                driver_id, destination, service_id=service,
            )

            await logbroker_event_done.wait_call()

        async def stop_watch_by_orders(
                self, driver_id, order_ids, service='test-service', meta='',
        ):
            @testpoint('logbroker-event-done')
            def logbroker_event_done(data):
                del data

            # WatchList.stop_watch_by_orders(
            #     self.redis_store,
            #     driver_id,
            #     order_ids,
            #     service=service,
            #     meta=meta,
            # )
            await self.watches_lb_channel.stop_watch_by_orders(
                driver_id, order_ids, service_id=service,
            )

            await logbroker_event_done.wait_call()

        async def stop_watch_all(self, driver_id, service):
            @testpoint('logbroker-event-done')
            def logbroker_event_done(data):
                del data

            # WatchList.stop_watch_all(self.redis_store, driver_id, service)
            await self.watches_lb_channel.stop_watch_all(driver_id, service)

            await logbroker_event_done.wait_call()

    return TaxiDriverRouteWatcher()
