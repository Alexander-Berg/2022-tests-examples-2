import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'point': [55, 35], 'zone_id': 'moscow'}, 400),  # no limit
        ({'point': [55, 35], 'limit': 2}, 404),  # zone could not be detected
        ({'point': [55, 35], 'limit': 2, 'zone_id': 'zone'}, 200),
    ],
)
async def test_response_code(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == response_code


async def test_response_format(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    # minimal request
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert all(
        x in drivers[0]
        for x in ('uuid', 'dbid', 'free', 'classes', 'position', 'direction')
    )
    assert drivers[0]['uuid'] == 'uuid0'


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_free(taxi_candidates, driver_positions):
    # dbid0_uuid2 is on order, so should be skipped
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert all(x['uuid'] in ['uuid0', 'uuid1'] for x in drivers)


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_classes(taxi_candidates, driver_positions):
    # Search only for vip drivers (dbid0_uuid1 should pass)
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid1'


async def test_max_distance(taxi_candidates, driver_positions):
    # dbid0_uuid1 is too faw away
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [56, 36]},
        ],
    )
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'max_distance': 1000,
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid0'


async def test_viewport(taxi_candidates, driver_positions):
    # dbid0_uuid1 is too faw away
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [56, 36]},
        ],
    )
    request_body = {
        'limit': 3,
        'tl': [54.5, 34.5],
        'br': [55.5, 35.5],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid0'


async def test_params_parse(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    # excess parameters should be ignored
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'geoindex': 'wrong',
        'filters': ['test/disallow_all'],
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({'point': [37.62, 55.75], 'limit': 2}, 200),
        ({'tl': [37.62, 55.75], 'br': [37.62, 55.75], 'limit': 2}, 200),
    ],
)
async def test_zone_by_point(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == response_code
