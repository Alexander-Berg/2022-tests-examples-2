import copy
import json

import pytest


PIN = {
    'pin': {
        'experiments': [],
        'personal_phone_id': 'test_phone_id',
        'point': {'lon': 11.1, 'lat': 22.2},
        'user_id': 'test_user_id',
        'user_layer': 'default',
        'classes': [],
    },
}


@pytest.mark.config(
    NON_FAKE_MIN_ORDERS_COMPLETE_BY_ZONE={'__default__': 1, 'moscow': 3},
    FAKE_PINS_EPS=100,
    FAKE_PINS=[[32.1, 45.6]],
    SURGE_POSITION_ACCURACY_LIMIT=50,
    INTERPRET_FAKE_PINS_WITH_ORDER_ID_DRIVER_ID_AS_CORRECT=True,
)
@pytest.mark.parametrize(
    'update_pin',
    [
        {'tariff_zone': 'moscow', 'orders_complete': 2},
        {'point': {'lon': 32.1, 'lat': 45.6}},
        {'position_accuracy': 100},
        {'due': '2019-03-08T60:00:00Z'},
        {'due': '2019-03-08T60:00:00Z', 'driver_id': 'test_driver_id'},
    ],
    ids=[
        'too few orders_complete in moscow',
        'fake pin position',
        'too big position_accuracy',
        'pin with due',
        'pin with due with driver_id',
    ],
)
async def test_add_fake_pin(taxi_pin_storage, redis_store, update_pin):
    await taxi_pin_storage.invalidate_caches()
    pin = copy.deepcopy(PIN)
    pin['pin'].update(update_pin)
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(pin),
    )
    assert response.status_code == 200
    assert redis_store.keys() == []


@pytest.mark.config(
    NON_FAKE_MIN_ORDERS_COMPLETE_BY_ZONE={'__default__': 1, 'moscow': 3},
    FAKE_PINS_EPS=100,
    FAKE_PINS=[[32.1, 45.6]],
    SURGE_POSITION_ACCURACY_LIMIT=50,
    INTERPRET_FAKE_PINS_WITH_ORDER_ID_DRIVER_ID_AS_CORRECT=True,
)
@pytest.mark.parametrize(
    'update_pin',
    [
        {
            'tariff_zone': 'moscow',
            'orders_complete': 2,
            'driver_id': 'test_driver_id',
        },
        {'point': {'lon': 32.1, 'lat': 45.6}, 'driver_id': 'test_driver_id'},
        {'position_accuracy': 100, 'driver_id': 'test_driver_id'},
        {
            'tariff_zone': 'moscow',
            'orders_complete': 2,
            'order_id': 'test_order_id',
        },
        {'point': {'lon': 32.1, 'lat': 45.6}, 'order_id': 'test_order_id'},
        {'position_accuracy': 100, 'order_id': 'test_order_id'},
        {
            'point': {'lon': 32.1, 'lat': 45.6},
            'driver_id': 'test_driver_id',
            'order_id': 'test_order_id',
        },
    ],
    ids=[
        'too few orders_complete in moscow but with driver_id',
        'fake pin position but with driver_id',
        'too big position_accuracy but with driver_id',
        'too few orders_complete in moscow but with order_id',
        'fake pin position but with order_id',
        'too big position_accuracy but with order_id',
        'fake pin position but with both driver_id and order_id',
    ],
)
async def test_add_semifake_pin(taxi_pin_storage, redis_store, update_pin):
    await taxi_pin_storage.invalidate_caches()
    pin = copy.deepcopy(PIN)
    pin['pin'].update(update_pin)
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(pin),
    )
    assert response.status_code == 200
    assert len(redis_store.keys()) == 1
