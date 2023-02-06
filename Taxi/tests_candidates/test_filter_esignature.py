import pytest


@pytest.mark.config(
    TAXIMETER_VERSION_FEATURES={
        'features': {
            'cargo': {'taximeter': {'android': '8.06', 'ios': '1.02'}},
        },
    },
)
async def test_esignature(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/esignature'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid2'


@pytest.mark.config(
    TAXIMETER_VERSION_FEATURES={
        'features': {'cargo': {'taximeter': {'android': '8.06'}}},
    },
)
async def test_empty_esignature(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/esignature'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 3


@pytest.mark.config(TAXIMETER_VERSION_FEATURES={})
async def test_bad_config_esignature(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/esignature'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 3
