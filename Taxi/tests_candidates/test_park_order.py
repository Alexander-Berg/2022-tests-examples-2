import pytest


async def test_filter_park_order_mixed(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [55, 35],
        'zone_id': 'moscow',
        'geoindex': 'kdtree',
        'filters': ['infra/park_order'],
        'order': {
            'request': {
                'white_label_requirements': {
                    'source_park_id': 'dbid1',
                    'dispatch_requirement': 'source_park_and_all',
                },
            },
        },
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    candidates = response.json()['drivers']
    assert len(candidates) == 3


async def test_filter_park_order_exclusive(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [55, 35],
        'zone_id': 'moscow',
        'geoindex': 'kdtree',
        'filters': ['infra/park_order'],
        'order': {
            'request': {
                'white_label_requirements': {
                    'source_park_id': 'dbid1',
                    'dispatch_requirement': 'only_source_park',
                },
            },
        },
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    candidates = response.json()['drivers']
    assert len(candidates) == 1
    assert candidates[0]['dbid'] == 'dbid1'


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
)
async def test_order_search(
        taxi_candidates, driver_positions, dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [{'values': {'SAME_PARK_PREFERRED': 3}}],
            },
        ],
    )

    # dbid0_uuid0, dbid0_uuid2 and dbid1_uuid3 are close to search point, but
    # search should require at least three drivers from dbid0
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.623761, 55.754275]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.516917, 55.812292]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.627511, 55.753329]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [37.624771, 55.758790]},
        ],
    )
    request_body = {
        'limit': 3,
        'max_route_distance': 20000,
        'max_route_time': 3600,
        'point': [37.623761, 55.754275],
        'zone_id': 'moscow',
        'order': {
            'request': {
                'white_label_requirements': {
                    'source_park_id': 'dbid0',
                    'dispatch_requirement': 'source_park_and_all',
                },
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 3
    assert candidates[0]['id'] == 'dbid0_uuid0'
    assert candidates[1]['id'] == 'dbid0_uuid2'
    assert candidates[2]['id'] == 'dbid0_uuid1'


async def test_filter_empty_request(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [55, 35],
        'zone_id': 'moscow',
        'geoindex': 'kdtree',
        'filters': ['infra/park_order'],
        'order': {'request': {}},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    candidates = response.json()['drivers']
    assert len(candidates) == 3


async def test_filter_wrong_dr(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [55, 35],
        'zone_id': 'moscow',
        'geoindex': 'kdtree',
        'filters': ['infra/park_order'],
        'order': {
            'request': {
                'white_label_requirements': {
                    'source_park_id': 'dbid1',
                    'dispatch_requirement': 'any_park',
                },
            },
        },
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 400
