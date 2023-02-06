import json

import pytest


PIN = {
    'pin': {
        'experiments': [],
        'personal_phone_id': 'test_phone_id',
        'point': {'lon': 12.3, 'lat': 45.6},
        'user_id': 'test_user_id',
        'user_layer': 'default',
        'classes': [
            {
                'cost': 49,
                'estimated_waiting': 5,
                'name': 'econom',
                'surge': {'value': 8},
                'value_raw': 9,
            },
        ],
        'calculation_id': 'some_calculation_id',
    },
}


@pytest.mark.suspend_periodic_tasks('try_save_pins')
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    PIN_STORAGE_PINS_WAIT_CALCULATION_QUEUE={
        'max_wait_ttl_ms': 1000,
        'max_queue_size': 2,
        'batch_size': 50,
        'enabled': True,
    },
)
async def test_add_calculation(taxi_pin_storage, redis_store, load_json):
    # would be displaced from queue
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(PIN),
    )
    assert response.status_code == 200

    # would not be saved, no calculation
    PIN['pin']['calculation_id'] = 'another_calculation_id'
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(PIN),
    )
    assert response.status_code == 200

    # would be processed
    PIN['pin']['calculation_id'] = 'some_calculation_id'
    PIN['pin']['classes'][0]['cost'] = 99
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(PIN),
    )
    assert response.status_code == 200
    # pin should not be saved without calculation
    assert b'1552003200' not in redis_store.keys()

    calculation = load_json('calculation.json')
    response = await taxi_pin_storage.put(
        'v1/add-calculation',
        headers={'Content-Type': 'application/json'},
        params={},
        json=calculation,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data
    # check calculation in redis
    assert b'calculation:some_calculation_id' in redis_store.keys()
    calculation_from_redis = redis_store.get('calculation:some_calculation_id')
    assert json.loads(calculation_from_redis) == calculation

    await taxi_pin_storage.run_periodic_task('try_save_pins')

    assert b'1552003200' in redis_store.keys()
    pins_in_redis = redis_store.lrange('1552003200', 0, -1)
    assert len(pins_in_redis) == 2
    pin_with_no_calculation = json.loads(pins_in_redis[0])
    assert not pin_with_no_calculation['pin']['classes'][0].get(
        'calculation_meta',
    )
    pin = json.loads(pins_in_redis[1])
    assert pin['pin']['classes'][0].get('calculation_meta')
    # in pin we store class info from calculation and cost from pin
    calculation['classes'][0]['cost'] = 99
    calculation['classes'][0]['estimated_waiting'] = 5
    assert pin['pin']['classes'] == calculation['classes']
    assert pin['pin']['experiments'] == calculation['experiments']
    assert pin['pin']['zone_id'] == calculation['zone_id']
    assert pin['pin']['user_layer'] == calculation['user_layer']
