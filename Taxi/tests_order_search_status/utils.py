import json


def generate_event(order_id, driver_id, multioffer_event, merge_json=None):
    event = {
        'order_id': order_id,
        'multioffer_id': f'multioffer_{order_id}',
        'park_id': 'dbid',
        'driver_profile_id': driver_id,
        'event': multioffer_event,
        'reason': 'reason',
    }

    if merge_json:
        event = {**event, **merge_json}
    return json.dumps(event)


def bid_related_event(
        bid_event,
        order_id,
        bid_id,
        driver_id,
        iteration,
        *,
        unique_driver_id=None,
        price=None,
        created_at=None,
        reason=None,
        timeout=None,
        driver_name=None,
        car_model=None,
        start_eta=None,
):
    event = {
        'event': bid_event,
        'order_id': order_id,
        'multioffer_id': f'multioffer_{order_id}',
        'bid_id': bid_id,
        'park_id': 'dbid',
        'driver_profile_id': driver_id,
        'auction': {'iteration': iteration},
    }
    if unique_driver_id:
        event['unique_driver_id'] = unique_driver_id
    if price:
        event['price'] = price
    if created_at:
        event['created_at'] = created_at
    if reason:
        event['reason'] = reason
    if timeout:
        event['timeout'] = timeout

    ui_fields = {}
    if driver_name:
        ui_fields['driver_name'] = driver_name
    if car_model:
        ui_fields['car_model'] = car_model
    if start_eta:
        ui_fields['start_eta'] = start_eta
    if ui_fields:
        event['ui_fields'] = ui_fields
    return json.dumps(event)


def sorted_auction_keys(redis_store):
    cursor = 0
    pattern = '*:auction:*'
    ret = []
    while True:
        cursor, keys = redis_store.scan(cursor=cursor, match=pattern)
        ret += keys
        if cursor == 0:
            break
    return sorted([key.decode('ascii') for key in ret])


def check_redis_auction_values(redis_store, etalon):
    keys = sorted_auction_keys(redis_store)
    assert keys == sorted(list(etalon.keys()))
    for key, val in etalon.items():
        smembers = sorted(
            [member.decode('ascii') for member in redis_store.smembers(key)],
        )
        assert smembers == val
