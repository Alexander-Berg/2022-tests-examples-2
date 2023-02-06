import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'driver_ids': []}, 400),
        ({'data_keys': []}, 400),
        ({'driver_ids': [], 'data_keys': []}, 200),
        ({'driver_ids': [], 'data_keys': ['wrong_id']}, 200),
    ],
)
async def test_response_code(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == response_code


async def test_sample(taxi_candidates):
    request_body = {
        'driver_ids': ['dbid0_uuid0', 'dbid0_uuid1'],
        'data_keys': ['car_classes'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert drivers[0]['uuid'] == 'uuid0'
    assert drivers[0]['car_classes']
    assert drivers[1]['uuid'] == 'uuid1'
    assert drivers[1]['car_classes']


async def test_ids_object_format(taxi_candidates):
    request_body = {
        'driver_ids': [
            {'dbid': 'dbid0', 'uuid': 'uuid0'},
            {'dbid': 'dbid0', 'uuid': 'uuid1'},
        ],
        'data_keys': [],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert drivers[0]['uuid'] == 'uuid0'
    assert drivers[1]['uuid'] == 'uuid1'


async def test_without_zone_id(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.62, 55.75]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.62, 55.75]},
        ],
    )
    request_body = {
        'driver_ids': [
            {'dbid': 'dbid0', 'uuid': 'uuid0'},
            {'dbid': 'dbid0', 'uuid': 'uuid1'},
        ],
        'data_keys': ['classes'],
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert drivers[0]['uuid'] == 'uuid0'
    assert drivers[0]['classes']
    assert drivers[1]['uuid'] == 'uuid1'
    assert drivers[1]['classes']


async def test_without_zone_id_and_no_need(taxi_candidates, driver_positions):
    request_body = {
        'driver_ids': [
            {'dbid': 'dbid0', 'uuid': 'uuid0'},
            {'dbid': 'dbid0', 'uuid': 'uuid1'},
        ],
        'data_keys': ['license_id'],
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert drivers[0]['uuid'] == 'uuid0'
    assert drivers[0]['license_id']
    assert drivers[1]['uuid'] == 'uuid1'
    assert drivers[1]['license_id']
