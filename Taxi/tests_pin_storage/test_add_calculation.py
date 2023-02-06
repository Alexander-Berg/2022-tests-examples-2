import json

import pytest


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_add_calculation(taxi_pin_storage, redis_store, load_json):
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
    assert redis_store.keys() == [b'calculation:some_calculation_id']
    calculation_from_redis = redis_store.get('calculation:some_calculation_id')
    assert json.loads(calculation_from_redis) == calculation

    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [
                        {
                            'cost': 99,
                            'estimated_waiting': 5,
                            'name': 'econom',
                            'surge': {'value': 8},
                            'value_raw': 9,
                        },
                    ],
                    'calculation_id': 'some_calculation_id',
                },
            },
        ),
    )
    assert response.status_code == 200
    assert b'1552003200' in redis_store.keys()
    pins_in_redis = redis_store.lrange('1552003200', 0, -1)
    assert len(pins_in_redis) == 1
    pin = json.loads(pins_in_redis[0])
    # in pin we store class info from calculation and cost from pin
    calculation['classes'][0]['cost'] = 99
    calculation['classes'][0]['estimated_waiting'] = 5
    assert pin['pin']['classes'] == calculation['classes']
    assert pin['pin']['experiments'] == calculation['experiments']
    assert pin['pin']['zone_id'] == calculation['zone_id']
    assert pin['pin']['user_layer'] == calculation['user_layer']
