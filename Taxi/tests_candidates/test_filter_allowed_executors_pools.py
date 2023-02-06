import pytest


@pytest.mark.config(
    CANDIDATES_ALLOWED_EXECUTORS_POOLS_FILTER_SETTINGS={
        'enabled': True,
        'known_pools_by_tags': ['lavka_pool'],
        'rules': [],
    },
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'west_world_pool'),
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_pool'),
    ],
)
async def test_basic(taxi_candidates, driver_positions):
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
        'filters': ['corp/allowed_executors_pools'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == {'uuid0', 'uuid2'}


@pytest.mark.config(
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'west_world_pool'),
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_pool'),
    ],
)
@pytest.mark.parametrize(
    'enabled, result_drivers',
    ((False, {'uuid0', 'uuid1', 'uuid2'}), (True, {'uuid1', 'uuid2'})),
)
async def test_enabled_disabled(
        taxi_candidates,
        driver_positions,
        taxi_config,
        enabled,
        result_drivers,
):

    taxi_config.set_values(
        dict(
            CANDIDATES_ALLOWED_EXECUTORS_POOLS_FILTER_SETTINGS={
                'enabled': enabled,
                'known_pools_by_tags': ['west_world_pool'],
                'rules': [],
            },
        ),
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/allowed_executors_pools'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers


@pytest.mark.config(
    CANDIDATES_ALLOWED_EXECUTORS_POOLS_FILTER_SETTINGS={
        'enabled': True,
        'known_pools_by_tags': ['lavka_pool', 'west_world_pool'],
        'rules': [
            {'corp_client_ids': ['corp_1'], 'allowed_pools': ['lavka_pool']},
            {
                'corp_client_ids': ['corp_2'],
                'allowed_pools': ['west_world_pool'],
            },
            {
                'corp_client_ids': ['corp_3'],
                'allowed_pools': ['lavka_pool', 'west_world_pool'],
            },
            {
                'corp_client_ids': ['corp_4'],
                'allowed_pools': ['west_world_pool', 'not_a_pool_in_config'],
            },
        ],
    },
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'west_world_pool'),
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_pool'),
        ('dbid_uuid', 'dbid0_uuid2', 'not_a_pool_in_driver'),
    ],
)
@pytest.mark.parametrize(
    'corp_client_id, result_drivers',
    (
        (None, {'uuid2'}),
        ('corp_1', {'uuid1', 'uuid2'}),
        ('corp_2', {'uuid0', 'uuid2'}),
        ('corp_3', {'uuid0', 'uuid1', 'uuid2'}),
        ('corp_4', {'uuid0', 'uuid2'}),
    ),
)
async def test_different_corps(
        taxi_candidates, driver_positions, corp_client_id, result_drivers,
):
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
        'filters': ['corp/allowed_executors_pools'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    if corp_client_id:
        request_body['order']['request'] = {
            'corp': {'client_id': corp_client_id},
        }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers
