import pytest


@pytest.mark.parametrize(
    'request_body',
    [
        ({'zone_id': 'moscow'}),
        ({'geoindex': 'kdtree', 'zone_id': 'moscow'}),
        ({'geoindex': 'kdtree', 'limit': 3, 'zone_id': 'moscow'}),
        (
            {
                'geoindex': 'kdtree',
                'limit': 3,
                'filters': [],
                'zone_id': 'moscow',
            }
        ),
        (
            {
                'geoindex': 'kdtree',
                'point': [55, 35],
                'limit': 3,
                'filters': ['unknown'],
                'zone_id': 'moscow',
            }
        ),
    ],
)
async def test_bad_request(taxi_candidates, request_body):
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 400


async def test_sample(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625172, 55.756506]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.625033, 55.761528]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'max_distance': 10000,
        'filters': [],
        'point': [37.625172, 55.756506],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert response.json()['drivers']


async def test_driver_order(taxi_candidates, driver_positions):
    # First three drivers are in 500m range from search point
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625172, 55.756506]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.625033, 55.761528]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'point': [37.625333, 55.754897],
        'max_distance': 500,
        'limit': 3,
        'filters': [],
        'zone_id': 'moscow',
    }
    response1 = await taxi_candidates.post('search', json=request_body)
    assert response1.status_code == 200

    request_body['max_distance'] = 1000
    # Now search range includes all 4 drivers, but only nearest three should be
    # returned
    response2 = await taxi_candidates.post('search', json=request_body)
    assert response2.status_code == 200
    assert response1.json() == response2.json()


async def test_driver_id_list_geoindex(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625172, 55.756506]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.625033, 55.761528]},
        ],
    )
    request_body = {
        'geoindex': 'driver-ids',
        'limit': 10,
        'driver_ids': ['dbid0_uuid0', 'dbid0_uuid2', 'dbid0_uuid4'],
        'filters': [],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    ids = {'{0}_{1}'.format(x['dbid'], x['uuid']) for x in drivers}
    assert ids == set(request_body['driver_ids'])


async def test_meta_data(taxi_candidates):
    meta_data = {'field1': 'value1', 'field2': 'value2'}
    request_body = {
        'geoindex': 'driver-ids',
        'limit': 10,
        'driver_ids': ['dbid0_uuid0', 'dbid0_uuid1'],
        'filters': ['test/add_meta_data'],
        'meta_data': meta_data,
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert all(
        x['metadata']['test/add_meta_data'] == meta_data for x in drivers
    )


async def test_pedestrian_kdtree(
        taxi_candidates, driver_positions, dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': False}}],
            },
        ],
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625172, 55.756506]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
        ],
    )
    request_body = {
        'geoindex': 'pedestrian-kdtree',
        'point': [37.625333, 55.754897],
        'limit': 3,
        'filters': [],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert len(json['drivers']) == 3
