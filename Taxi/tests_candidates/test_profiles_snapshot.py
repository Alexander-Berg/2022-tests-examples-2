import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'part': 4, 'parts': 4}, 400),
        ({'part': 0, 'parts': 0}, 400),
        ({'part': 3, 'parts': 4}, 200),
    ],
)
async def test_response_code(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post(
        'profiles-snapshot', json=request_body,
    )
    assert response.status_code == response_code


async def test_sample(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {'parts': 1, 'part': 0, 'data_keys': ['car_number']}
    response = await taxi_candidates.post(
        'profiles-snapshot', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'drivers': [
            {
                'position': [55.0, 35.0],
                'id': 'dbid0_uuid1',
                'dbid': 'dbid0',
                'uuid': 'uuid1',
                'car_number': 'Х495НК77',
            },
            {
                'position': [55.0, 35.0],
                'id': 'dbid0_uuid0',
                'dbid': 'dbid0',
                'uuid': 'uuid0',
                'car_number': 'Х492НК77',
            },
        ],
    }


async def test_parts(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    request_body = {'parts': 10, 'part': 2, 'data_keys': ['car_number']}
    response = await taxi_candidates.post(
        'profiles-snapshot', json=request_body,
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid0'

    request_body = {'parts': 10, 'part': 4, 'data_keys': ['car_number']}
    response = await taxi_candidates.post(
        'profiles-snapshot', json=request_body,
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid1'

    request_body = {'parts': 10, 'part': 0, 'data_keys': ['car_number']}
    response = await taxi_candidates.post(
        'profiles-snapshot', json=request_body,
    )
    assert response.status_code == 200
    assert not response.json()['drivers']
