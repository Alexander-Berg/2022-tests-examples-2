async def test_freeze_bulk(taxi_driver_freeze):
    params = {
        'drivers': [
            {
                'unique_driver_id': 'id1',
                'car_id': 'car1',
                'order_id': 'order1',
                'freeze_time': 30,
            },
            {
                'unique_driver_id': 'id2',
                'car_id': 'car2',
                'order_id': 'order2',
                'freeze_time': 30,
            },
        ],
    }
    response = await taxi_driver_freeze.post('freeze-bulk', json=params)
    assert response.status_code == 200
    data = response.json()
    assert data['drivers'][0]['freezed']
    assert data['drivers'][1]['freezed']
    assert data['drivers'][0]['unique_driver_id'] == 'id1'
    assert data['drivers'][1]['unique_driver_id'] == 'id2'


async def test_freeze_mongo_bulk(taxi_driver_freeze, mongodb):
    params = {
        'drivers': [
            {
                'unique_driver_id': 'id1',
                'car_id': 'car1',
                'order_id': 'order1',
                'freeze_time': 30,
            },
            {
                'unique_driver_id': 'id2',
                'car_id': 'car2',
                'order_id': 'order2',
                'freeze_time': 30,
            },
        ],
    }
    response = await taxi_driver_freeze.post('freeze-bulk', json=params)
    assert response.status_code == 200
    data = response.json()
    assert data['drivers'][0]['freezed']
    assert data['drivers'][1]['freezed']
    assert data['drivers'][0]['unique_driver_id'] == 'id1'
    assert data['drivers'][1]['unique_driver_id'] == 'id2'
    val = mongodb.frozen_contractors.find_one({'l': 'id1'})
    assert val['o'] == 'order1'
    assert val['n'] == 'car1'
    assert val['l'] == 'id1'
    val = mongodb.frozen_contractors.find_one({'l': 'id2'})
    assert val['o'] == 'order2'
    assert val['n'] == 'car2'
    assert val['l'] == 'id2'
    params['drivers'][0]['order_id'] = 'order3'
    params['drivers'][1]['order_id'] = 'order4'
    response = await taxi_driver_freeze.post('freeze-bulk', json=params)
    assert response.status_code == 200
    data = response.json()
    assert not data['drivers'][0]['freezed']
    assert not data['drivers'][1]['freezed']
    assert data['drivers'][0]['reason'] == 'not_freezed'
    assert data['drivers'][1]['reason'] == 'not_freezed'
    assert data['drivers'][0]['unique_driver_id'] == 'id1'
    assert data['drivers'][1]['unique_driver_id'] == 'id2'
