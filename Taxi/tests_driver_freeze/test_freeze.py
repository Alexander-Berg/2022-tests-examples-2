import datetime

import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        (
            {
                'unique_driver_id': 'id1',
                'freeze_time': 10,
                'car_id': '',
                'order_id': '',
            },
            200,
        ),
        (
            {
                'unique_driver_id': 'id1',
                'freeze_time': 10,
                'car_id': '123',
                'order_id': '',
            },
            200,
        ),
        (
            {
                'unique_driver_id': 'id1',
                'freeze_time': 10,
                'car_id': '',
                'order_id': '22',
            },
            200,
        ),
        (
            {
                'unique_driver_id': 'id1',
                'freeze_time': 10,
                'car_id': '123',
                'order_id': '22',
            },
            200,
        ),
    ],
)
async def test_freeze_mongo_params(
        taxi_driver_freeze, mongodb, request_body, response_code,
):
    response = await taxi_driver_freeze.post('freeze', json=request_body)
    assert response.status_code == response_code

    response_data = response.json()
    assert response_data['freezed']

    data = mongodb.frozen_contractors.find_one({})
    assert data['o'] == request_body['order_id']
    assert data['n'] == request_body['car_id']
    assert data['l'] == request_body['unique_driver_id']

    freeze_time = (data['t'] - datetime.datetime.utcnow()).total_seconds()
    assert request_body['freeze_time'] - freeze_time < 3


@pytest.mark.parametrize(
    'driver_id, car_id, order_id,freeze_status',
    [
        ('id1', 'car1', 'order1', True),
        ('id1', 'car2', 'order1', False),
        ('id1', 'car1', 'order2', False),
        ('id1', '', 'order2', False),
        ('id1', 'car2', '', False),
    ],
)
async def test_already_freeze(
        taxi_driver_freeze, driver_id, car_id, order_id, freeze_status,
):
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
            {
                'unique_driver_id': 'id3',
                'car_id': 'car3',
                'order_id': 'order3',
                'freeze_time': 30,
            },
        ],
    }
    response = await taxi_driver_freeze.post('freeze-bulk', json=params)
    assert response.status_code == 200
    assert response.json()['drivers'][0]['freezed']

    params = {
        'unique_driver_id': driver_id,
        'car_id': car_id,
        'order_id': order_id,
        'freeze_time': 30,
    }
    response = await taxi_driver_freeze.post('freeze', json=params)
    assert response.status_code == 200
    assert response.json()['freezed'] == freeze_status


async def test_idempotent_freeze(taxi_driver_freeze):
    params = {
        'unique_driver_id': 'id1',
        'car_id': 'car1',
        'order_id': 'order1',
        'freeze_time': 60,
    }
    response = await taxi_driver_freeze.post('freeze', json=params)
    assert response.status_code == 200
    assert response.json()['freezed']

    response = await taxi_driver_freeze.post('freeze', json=params)
    assert response.status_code == 200
    assert response.json()['freezed']

    params['order_id'] = 'order2'
    response = await taxi_driver_freeze.post('freeze', json=params)
    assert response.status_code == 200
    assert not response.json()['freezed']
