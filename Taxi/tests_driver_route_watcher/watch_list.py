# pylint: disable=import-error
import json

import flatbuffers
import watchlist_entry.fbs.WatchlistEntry as FbsWatchlistEntry

import tests_driver_route_watcher.points_list_fbs as PointlistFbs
import tests_driver_route_watcher.position_fbs as PositionFbs


def _parse_watch_entry_field(key, value):
    ret = dict()
    key_parts = key.split(b'/')
    if len(key_parts) == 2:
        service, postfix = key_parts
    elif len(key_parts) == 3:
        service, key_data, postfix = key_parts
    else:
        # invalid key
        assert False

    if postfix == b'd':
        ret['destination'] = value
    elif postfix == b'm':
        try:
            ret['meta'] = json.loads(value.decode())
        except json.decoder.JSONDecodeError:
            ret['meta'] = value.decode()
    elif postfix == b't':
        ret['watched_since'] = int(value.decode())
    elif postfix == b'ps' and value:
        ret['points'] = PointlistFbs.deserialize_pointslist(value)
    elif postfix == b'o' and value:
        ret['order_id'] = value.decode()
    elif postfix == b'nz' and value:
        ret['nearest_zone'] = value.decode()
    elif postfix == b'cntr' and value:
        ret['country'] = value.decode()
    elif postfix == b'rt' and value:
        ret['router_type'] = value.decode()
    elif postfix == b'dos':
        ret['deleted_orders'] = {key_data.decode()}
    ret['service'] = service.decode()
    return ret


def _get_watch_entry(redis_store, key):
    fields_raw = redis_store.hgetall(key)
    _, dbid_uuid = key.split(b'/')
    fields = [_parse_watch_entry_field(k, v) for k, v in fields_raw.items()]
    watch = dict()
    for field in fields:
        service = field['service']
        old_value = watch.get(service, field)

        # if current field is a delted_orders field
        # then if output value
        deleted_orders = field.get('deleted_orders')
        if deleted_orders:
            if old_value.get('deleted_orders'):
                old_value['deleted_orders'].update(deleted_orders)
            else:
                old_value['deleted_orders'] = deleted_orders
        else:
            old_value.update(field)
        watch[service] = old_value
    return {dbid_uuid[1:-1].decode(): watch}


def _get_watched_orders(redis_store, key):
    orders = redis_store.smembers(key)
    _, service_id, dbid_uuid = key.split(b'/')
    return (
        dbid_uuid[1:-1].decode(),
        service_id.decode(),
        {o.decode() for o in orders},
    )


def get_watchlist(redis_store):
    cursor = 0
    pattern = 'w/*'
    import collections
    ret = collections.defaultdict(dict)
    while True:
        cursor, keys = redis_store.scan(cursor=cursor, match=pattern)
        watch_entries = [_get_watch_entry(redis_store, key) for key in keys]
        for entry in watch_entries:
            ret.update(entry)
        if cursor == 0:
            break

    cursor = 0
    # watched orders for cargo
    pattern = 'wos/*'
    import pprint
    pprint.pprint(ret)
    while True:
        cursor, keys = redis_store.scan(cursor=cursor, match=pattern)
        watch_entries = [_get_watched_orders(redis_store, key) for key in keys]
        for dbid_uuid, service_id, orders in watch_entries:
            ret[dbid_uuid][service_id]['orders'] = orders
        if cursor == 0:
            break

    return ret


def deserialize_watchlist_entry(data):
    entry = FbsWatchlistEntry.WatchlistEntry.GetRootAsWatchlistEntry(data, 0)
    fbs_position = entry.Destination()
    return PositionFbs.deserialize_position(fbs_position)


def serialize_watchlist_entry(pos):
    builder = flatbuffers.Builder(0)
    destination = PositionFbs.serialize_position(builder, pos)

    FbsWatchlistEntry.WatchlistEntryStart(builder)
    FbsWatchlistEntry.WatchlistEntryAddDestination(builder, destination)
    obj = FbsWatchlistEntry.WatchlistEntryEnd(builder)

    builder.Finish(obj)
    return bytes(builder.Output())


def store_watch_in_redis(
        redis_store,
        driver_id,
        destination,
        service='',
        meta='',
        destinations=None,
        order_id=None,
        router_type=None,
        toll_roads=None,
        nearest_zone=None,
        country=None,
):
    points = destinations
    if points is None or not points:
        points = PointlistFbs.to_point_list([destination])

    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    fields = {
        '{}/d'.format(service): serialize_watchlist_entry(destination),
        '{}/m'.format(service): meta,
        '{}/ps'.format(service): PointlistFbs.serialize_pointslist(points),
        '{}/o'.format(service): order_id or '',
        '{}/rt'.format(service): router_type or 'car',
        '{}/trs'.format(service): toll_roads or 'null',
    }
    if nearest_zone is not None:
        fields.update({'{}/nz'.format(service): nearest_zone})
    if country is not None:
        fields.update({'{}/cntr'.format(service): country})
    redis_store.hmset('w/{{{}}}'.format(dbid_uuid).encode(), fields)


# for internal fixture use only
def start_watch(
        redis_store,
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
    store_watch_in_redis(
        redis_store,
        driver_id,
        destination,
        service,
        meta,
        destinations,
        order_id,
        router_type,
        toll_roads,
        nearest_zone,
        country,
    )


# for internal fixture use only
def stop_watch_by_orders(
        redis_store, driver_id, order_ids, service='test-service', meta='',
):
    _reset_watch_by_order_id(redis_store, driver_id, service, order_ids)


def stop_watch_all(redis_store, driver_id, service):
    _reset_watch_in_redis(redis_store, driver_id, service)


def _reset_watch_in_redis(redis_store, driver_id, service):
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    redis_store.hdel(
        'w/{{{}}}'.format(dbid_uuid).encode(),
        '{}/d'.format(service),
        '{}/m'.format(service),
        '{}/t'.format(service),
        '{}/ps'.format(service),
        '{}/o'.format(service),
        '{}/rt'.format(service),
        '{}/trs'.format(service),
        '{}/em'.format(service),
        '{}/nz'.format(service),
        '{}/cntr'.format(service),
    )


def _reset_watch_by_order_id(redis_store, driver_id, service, order_ids):
    script = """
local key = KEYS[1];
local orders_key = KEYS[2];
local dof = ARGV[1];
local of = ARGV[2];
local oc = ARGV[3];
local d_field =ARGV[4];
redis.call('HSET', key, dof, 0);
local s = redis.call('SREM', orders_key, of);
if s == 1 then
  local c = redis.call('HINCRBY', key, oc, -1);
  if c == 0 then
    redis.call('HDEL', key, d_field, ARGV[5], ARGV[6], ARGV[7], ARGV[8],
               ARGV[9], ARGV[10], ARGV[11], ARGV[12], ARGV[13]);
  end
end
return 1;
    """
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
    key = 'w/{{{}}}'.format(dbid_uuid).encode()
    orders_key = 'wos/{}/{{{}}}'.format(service, dbid_uuid)
    for order_id in order_ids:
        args = [
            '{}/{}/dos'.format(service, order_id),
            order_id,
            '{}/c'.format(service),
            '{}/d'.format(service),
            '{}/m'.format(service),
            '{}/t'.format(service),
            '{}/ps'.format(service),
            '{}/o'.format(service),
            '{}/rt'.format(service),
            '{}/trs'.format(service),
            '{}/em'.format(service),
            '{}/nz'.format(service),
            '{}/cntr'.format(service),
        ]
        import pprint
        pprint.pprint(args)
        pprint.pprint([key, orders_key])
        redis_store.eval(script, 2, key, orders_key, *args)
