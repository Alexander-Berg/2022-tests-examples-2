# pylint: disable=wrong-import-order, import-error, import-only-modules
import datetime
import json

# pylint: disable=wrong-import-order, import-error, import-only-modules
from tests_driver_status.enum_constants import DriverStatus
from tests_driver_status.enum_constants import OrderStatus
import tests_driver_status.utils as utils
# pylint: enable=wrong-import-order, import-error, import-only-modules

STATUS_EVENT_QUEUE = 'STATUS_EVENT_QUEUE'
MASTER_ORDER_QUEUE = 'MASTER_ORDER_QUEUE'


def _convert_timestamp(timestamp):
    if isinstance(timestamp, str):
        return utils.date_str_to_ms(timestamp)
    if isinstance(timestamp, datetime.datetime):
        return utils.date_to_ms(timestamp)
    return int(timestamp)


def clear(redis_store, queue_name):
    redis_store.delete(queue_name)
    assert not redis_store.zcard(queue_name)


def to_storage_status_event(event):
    result = event.copy()
    result['updated_ts'] = _convert_timestamp(event['updated_ts'])
    return result


def to_storage_master_order_event(event):
    result = event.copy()
    result['event_ts'] = _convert_timestamp(event['event_ts'])
    return result


def to_comparable_status_repr(events):
    def _convert_orders(orders):
        result_orders = {}
        for order in orders:
            order_id = order.get('order_id')
            alias_id = order.get('alias_id')
            order_status = order.get('status')
            provider = order.get('provider')

            if (
                    not alias_id
                    or not order_status
                    or not OrderStatus.contains(order_status)
            ):
                return None

            order_value = {'status': order_status}
            if order_id is not None:
                order_value['order_id'] = order_id
            if provider is not None:
                order_value['provider'] = provider
            result_orders[alias_id] = order_value
        return result_orders

    if not events:
        return {}

    converted = {}
    for event in events:
        profile_id = event.get('profile_id')
        park_id = event.get('park_id')
        status = event.get('status')
        updated_ts = _convert_timestamp(event.get('updated_ts'))
        orders = event.get('orders')

        if None in [profile_id, park_id, status, updated_ts]:
            continue

        if not DriverStatus.contains(status):
            continue

        key = (profile_id, park_id)

        result_orders = None
        if orders is not None:
            result_orders = _convert_orders(orders)
            if not result_orders:
                continue

        if key not in converted:
            converted[key] = {}
        if 'statuses' not in converted[key]:
            converted[key]['statuses'] = {}

        converted[key]['statuses'][updated_ts] = status

        if result_orders is not None:
            if 'orders' not in converted[key]:
                converted[key]['orders'] = {}
            converted[key]['orders'][updated_ts] = result_orders

    return converted


def to_comparable_master_order_repr(events):
    if not events:
        return {}

    converted = {}
    for event in events:
        alias_id = event.get('alias_id')
        profile_id = event.get('profile_id')
        park_id = event.get('park_id')
        order_id = event.get('order_id')
        status = event.get('status')
        provider = event.get('provider')
        event_ts = _convert_timestamp(event.get('event_ts'))

        if None in [alias_id, profile_id, park_id, status, provider, event_ts]:
            continue

        if not OrderStatus.contains(status):
            continue

        key = (alias_id, park_id, profile_id)
        converted[key] = {
            'order_id': order_id,
            'status': status,
            'provider': provider,
            'event_ts': event_ts,
        }
    return converted


def store_status_event(redis_store, queue_name, event):
    data = json.dumps(event)
    redis_store.zadd(queue_name, {data: event['updated_ts']})


def store_master_order_event(redis_store, queue_name, event):
    data = json.dumps(event)
    redis_store.zadd(queue_name, {data: event['event_ts']})


def size(redis_store, queue_name):
    return redis_store.zcard(queue_name)


def read_events(redis_store, queue_name):
    result = redis_store.zrange(queue_name, 0, -1)
    return [json.loads(item) for item in result]
