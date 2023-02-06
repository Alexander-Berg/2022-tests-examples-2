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
_ORDER_DRIVER_CANCELREQUEST_ITEMS = 'Order:Driver:CancelRequest:Items'
_ORDER_DRIVER_CANCELREQUEST_MD5 = 'Order:Driver:CancelRequest:MD5'

_ORDER_DRIVER_COMPLETEREQUEST_ITEMS = 'Order:Driver:CompleteRequest:Items'

_ORDER_SETCAR_DRIVER_RESERV_ITEMS = 'Order:SetCar:Driver:Reserv:Items'
_ORDER_SETCAR_ITEMS = 'Order:SetCar:Items'
_ORDER_SETCAR_GEOSHARING = 'Order:SetCar:Item:ClientGeoSharing:TrackIds'
_ORDER_SETCAR_XML = 'Order:SetCar:Xml'

_SELFREQUESTCAR_REQUESTCAR_DRIVERS = 'SelfRequestCar:Requestcar:drivers'
_REQUESTORDER_TAXIMETER_LIST = 'RequestOrder:Taximeter:List'
_REQUESTORDER_MD5 = 'RequestOrder:MD5'
_TAXIMETER_CURRENT_COST = 'TaximeterCurrentCost'

_ORDER_STATISTICS_EVENTS_QUEUE = 'Push:Events:Queue'
_ORDER_PUSH_MESSAGES_QUEUE = 'PushMessage:Queue'
_FNS_SELF_EMPLOYED_QUEUE = 'Fns:SelfEmployed:Requests:{Queue}'

_COMBO_ORDERS_STATUSES = 'ComboOrdersStatuses'

_STATUS_DRIVERS = 'STATUS_DRIVERS'

SELFREQUESTCAR_DRIVERS = {'dummy_driver_1', 'dummy_driver_2'}


def set_driver_for_order(redis_store, park_id, alias_id, driver_id):
    redis_store.hset(
        _ORDER_SETCAR_DRIVERS + ':' + park_id, alias_id, driver_id,
    )


def set_provider_for_order(redis_store, park_id, alias_id, provider_id):
    redis_store.hset(
        _ORDER_SETCAR_ITEMS_PROVIDERS + ':' + park_id, alias_id, provider_id,
    )


def get_setcar_item(redis_store, park_id, alias_id):
    return redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + park_id, alias_id)


def set_setcar_xml(redis_store, park_id, alias_id, xml_item):
    redis_store.set(
        '{}:{}:{}'.format(_ORDER_SETCAR_XML, park_id, alias_id), xml_item,
    )


def exists_setcar_xml(redis_store, park_id, alias_id):
    return redis_store.exists(
        '{}:{}:{}'.format(_ORDER_SETCAR_XML, park_id, alias_id),
    )


def check_setcar_xml(redis_store, park_id, alias_id, setcar_xml):
    got_setcar = redis_store.get(
        '{}:{}:{}'.format(_ORDER_SETCAR_XML, park_id, alias_id),
    )

    assert got_setcar
    assert got_setcar.decode('utf-8') == setcar_xml


def delete_setcar_xml(redis_store, park_id, alias_id):
    redis_store.delete('{}:{}:{}'.format(_ORDER_SETCAR_XML, park_id, alias_id))


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
        datetime.datetime.now(),
    )
    redis_store.sadd(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
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
    for driver in SELFREQUESTCAR_DRIVERS:
        redis_store.sadd(
            _SELFREQUESTCAR_REQUESTCAR_DRIVERS
            + ':'
            + park_id
            + ':'
            + alias_id,
            driver,
        )


def check_redis_order_cancelled(redis_store, park_id, alias_id, driver_id):
    check_update_status_cancelled(redis_store, park_id, alias_id)
    check_update_status_for_driver(redis_store, park_id, driver_id)
    check_driver_cancel_request(redis_store, park_id, alias_id, driver_id)
    check_remove_setcar(redis_store, park_id, alias_id, driver_id)
    check_cancel_park_request_cars(redis_store, park_id, alias_id)


def check_update_status_cancelled(redis_store, park_id, alias_id):
    assert not redis_store.hexists(
        _ORDER_REQUESTCONFIRM_ITEMS + ':' + park_id, alias_id,
    )
    assert not redis_store.hexists(
        _ORDER_REQUESTCONFIRM_LASTDATE + ':' + park_id, alias_id,
    )


def check_update_status_for_driver(redis_store, park_id, driver_id):
    assert redis_store.exists(_ORDER_SETCAR_MD5 + ':' + park_id)
    assert redis_store.exists(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + park_id + ':' + driver_id,
    )


def remove_setcar_driver_reserv(redis_store, park_id, driver_id, alias_id):
    redis_store.srem(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
    )


def check_setcar_driver_reserv(
        redis_store, park_id, driver_id, alias_id, exists=True,
):
    assert (
        redis_store.sismember(
            _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
            alias_id,
        )
        == exists
    )


def check_order_setcar_items(redis_store, park_id, alias_id, exists=True):
    assert (
        redis_store.hexists(
            _ORDER_SETCAR_ITEMS_PROVIDERS + ':' + park_id, alias_id,
        )
        == exists
    )


def check_driver_cancel_request(
        redis_store, park_id, alias_id, driver_id, exists=True,
):
    assert redis_store.llen(
        _ORDER_DRIVER_CANCELREQUEST_ITEMS + ':' + park_id + ':' + driver_id,
    ) == int(exists)
    if exists:
        assert (
            redis_store.lpop(
                _ORDER_DRIVER_CANCELREQUEST_ITEMS
                + ':'
                + park_id
                + ':'
                + driver_id,
            ).decode()
            == alias_id
        )
    if exists:
        assert redis_store.exists(
            _ORDER_DRIVER_CANCELREQUEST_MD5 + ':' + park_id + ':' + driver_id,
        )
    else:
        assert not redis_store.exists(
            _ORDER_DRIVER_CANCELREQUEST_MD5 + ':' + park_id + ':' + driver_id,
        )


def set_cancelrequested(redis_store, park_id, alias_id, driver_id):
    redis_store.lpush(
        _ORDER_DRIVER_CANCELREQUEST_ITEMS + ':' + park_id + ':' + driver_id,
        alias_id,
    )


def set_completerequested(redis_store, park_id, alias_id, driver_id):
    redis_store.lpush(
        _ORDER_DRIVER_COMPLETEREQUEST_ITEMS + ':' + park_id + ':' + driver_id,
        alias_id,
    )


def set_setcared(redis_store, park_id, driver_id, alias_id, value=None):
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + park_id, alias_id, json.dumps(value or {}),
    )
    redis_store.sadd(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
    )


def check_remove_setcar(redis_store, park_id, alias_id, driver_id):
    assert not redis_store.sismember(
        _ORDER_SETCAR_DRIVER_RESERV_ITEMS + park_id + ':' + driver_id,
        alias_id,
    )
    assert redis_store.exists(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + park_id + ':' + driver_id,
    )  # compare to the previous value maybe?
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
    assert redis_store.exists(
        _ORDER_SETCAR_MD5 + ':' + park_id,
    )  # compare to the previous value maybe?


def check_cancel_park_request_cars(redis_store, park_id, alias_id):
    assert not redis_store.exists(
        _SELFREQUESTCAR_REQUESTCAR_DRIVERS + ':' + park_id + ':' + alias_id,
    )
    for driver in SELFREQUESTCAR_DRIVERS:
        assert (
            redis_store.llen(
                _REQUESTORDER_TAXIMETER_LIST + ':' + park_id + ':' + driver,
            )
            == 1
        )
        assert redis_store.exists(
            _REQUESTORDER_MD5 + ':' + park_id + ':' + driver,
        )


def set_order_status(redis_store, park_id, alias_id, status):
    if status is None:
        return
    redis_store.hset(
        _ORDER_REQUESTCONFIRM_ITEMS + ':' + park_id, alias_id, status.value,
    )


def get_event_queue_size(redis_store):
    return redis_store.llen(_ORDER_STATISTICS_EVENTS_QUEUE)


def get_event_queue_items(redis_store):
    return redis_store.lrange(_ORDER_STATISTICS_EVENTS_QUEUE, 0, 1000)


def get_self_employed_queue(redis_store):
    return redis_store.lrange(_FNS_SELF_EMPLOYED_QUEUE, 0, 1000)


def get_push_queue_size(redis_store):
    return redis_store.llen(_ORDER_PUSH_MESSAGES_QUEUE)


def redis_lock_not_exists(redis_store, park_id, alias_id):
    return not redis_store.exists(
        'Orders:Lock' + ':' + park_id + ':' + alias_id,
    )


def set_redis_lock(redis_store, park_id, alias_id):
    redis_store.set('Orders:Lock' + ':' + park_id + ':' + alias_id, '1')


def set_aggregator_name(redis_store, agg_id, agg_name):
    redis_store.hset('Aggregator:{}'.format(agg_id), 'Name', agg_name)


def _set_park_sms(redis_store, sms_type, park_id, event_type, msg):
    redis_store.hset(
        'SMS:{}:{}:All'.format(sms_type, park_id),
        event_type,
        json.dumps({'Template': msg, 'Enable': True}),
    )


def set_park_text(redis_store, park_id, event_type, msg):
    _set_park_sms(redis_store, 'Text', park_id, event_type, msg)


def set_park_voice(redis_store, park_id, event_type, msg):
    _set_park_sms(redis_store, 'Voice', park_id, event_type, msg)


def set_company_disable_sms(redis_store, park_id, company_id):
    redis_store.hset(
        'Companys:Items:{}'.format(park_id),
        company_id,
        json.dumps({'DisableSms': True}),
    )


def set_company_template(
        redis_store,
        park_id,
        company_id,
        event_type,
        company_emails,
        company_enabled,
        company_template,
):
    hash_key = 'SMS:Text:{}:{}'.format(park_id, company_id)
    redis_store.hset(
        hash_key,
        event_type,
        json.dumps(
            {
                'Enable': company_enabled,
                'Emails': company_emails,
                'Template': company_template,
            },
        ),
    )
    redis_store.hset(hash_key, 'Enable', json.dumps(company_enabled))


def create_apikey(redis_store, apikey, park_id):
    redis_store.hset(
        'Apikey',
        apikey,
        json.dumps(
            {
                'enable': True,
                'name': 'test',
                'db': park_id,
                'owner': 'a-konyshev',
            },
        ),
    )


def set_driver_status(redis_store, park_id, driver_id, status):
    redis_store.hset(
        '{}:{}'.format(park_id, _STATUS_DRIVERS), driver_id, status,
    )


def add_combo_orders_status_item(redis_store, driver_id, alias_id, status):
    return redis_store.hset(
        _COMBO_ORDERS_STATUSES + ':' + driver_id, alias_id, json.dumps(status),
    )


def get_combo_orders_status_items(redis_store, driver_id):
    orders = redis_store.hgetall(_COMBO_ORDERS_STATUSES + ':' + driver_id)
    return {
        key.decode(): json.loads(value.decode())
        for key, value in orders.items()
    }
