import datetime
import enum
import json


class OrderStatus(enum.Enum):
    None_ = 0
    Driving = 10
    Waiting = 20
    Calling = 30
    Transporting = 40
    Complete = 50
    Failed = 60
    Cancelled = 70
    Expired = 80


_ORDER_SETCAR_DRIVERS = 'Order:SetCar:Drivers'
_ORDER_SETCAR_ITEMS_PROVIDERS = 'Order:SetCar:Items:Providers'
_ORDER_REQUESTCONFIRM_ITEMS = 'Order:RequestConfirm:Items'
_ORDER_REQUESTCONFIRM_LASTDATE = 'Order:RequestConfirm:LastDate'

_ORDER_SETCAR_MD5 = 'Order:SetCar:MD5'
_ORDER_SETCAR_DRIVER_RESERV_MD5 = 'Order:SetCar:Driver:Reserv:MD5'

_ORDER_SETCAR_DRIVER_RESERV_ITEMS = 'Order:SetCar:Driver:Reserv:Items'
_ORDER_SETCAR_ITEMS = 'Order:SetCar:Items'
_ORDER_SETCAR_GEOSHARING = 'Order:SetCar:Item:ClientGeoSharing:TrackIds'
_ORDER_SETCAR_XML = 'Order:SetCar:Xml'


def set_driver_for_order(redis_store, park_id, alias_id, driver_id):
    redis_store.hset(
        _ORDER_SETCAR_DRIVERS + ':' + park_id, alias_id, driver_id,
    )


def exists_setcar_xml(redis_store, park_id, order_id):
    return redis_store.exists(
        '{}:{}:{}'.format(_ORDER_SETCAR_XML, park_id, order_id),
    )


def set_redis_for_order_cancelling(
        redis_store, park_id, alias_id, driver_id, setcar_item=None,
):
    if setcar_item is None:
        setcar_item = {}
    set_driver_for_order(redis_store, park_id, alias_id, driver_id)
    redis_store.hset(_ORDER_REQUESTCONFIRM_ITEMS + ':' + park_id, alias_id, 20)
    redis_store.hset(
        _ORDER_REQUESTCONFIRM_LASTDATE + ':' + park_id,
        alias_id,
        datetime.datetime.now().timestamp(),
    )
    redis_store.sadd(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
    )
    redis_store.set(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + park_id + ':' + driver_id,
        'md5_v0',
    )
    redis_store.hset(
        _ORDER_SETCAR_DRIVERS + ':' + park_id, alias_id, driver_id,
    )
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + park_id, alias_id, json.dumps(setcar_item),
    )
    redis_store.hset(
        _ORDER_SETCAR_ITEMS_PROVIDERS + ':' + park_id, alias_id, 'smth',
    )
    redis_store.hset(
        _ORDER_SETCAR_GEOSHARING + ':' + park_id + ':' + driver_id,
        alias_id,
        'smth',
    )
    redis_store.hset(_ORDER_SETCAR_XML + ':' + park_id, alias_id, 'smth')


def check_remove_setcar(redis_store, park_id, alias_id, driver_id):
    assert not redis_store.sismember(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
    )
    md5_reserv = redis_store.get(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + park_id + ':' + driver_id,
    )
    assert md5_reserv is not None and md5_reserv != 'md5_v0'
    assert not redis_store.hexists(
        _ORDER_SETCAR_DRIVERS + ':' + park_id, alias_id,
    )
    assert not redis_store.hexists(
        _ORDER_SETCAR_ITEMS + ':' + park_id, alias_id,
    )
    assert not redis_store.hexists(
        _ORDER_SETCAR_ITEMS_PROVIDERS + ':' + park_id, alias_id,
    )
    assert not redis_store.hexists(
        _ORDER_SETCAR_GEOSHARING + ':' + park_id + ':' + driver_id, alias_id,
    )
    assert not exists_setcar_xml(redis_store, park_id, alias_id)
    md5_setcar = redis_store.get(_ORDER_SETCAR_MD5 + ':' + park_id)
    assert md5_setcar is not None and md5_setcar != 'md5_v0'
