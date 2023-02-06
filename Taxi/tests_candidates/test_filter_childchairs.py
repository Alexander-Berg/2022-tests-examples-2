import pytest


@pytest.mark.config(
    CHILDSEAT_MAPPING=[
        {'categories': [3], 'groups': [2]},
        {'categories': [7], 'groups': [3]},
        {'categories': [1, 3], 'groups': [1, 2]},
        {'categories': [3, 7], 'groups': [2, 3]},
        {'categories': [1, 3, 7], 'groups': [1, 2, 3]},
        {'categories': [0, 1, 3, 7], 'groups': [0, 1, 2, 3]},
    ],
)
@pytest.mark.parametrize(
    'childchair, drivers, expected_drivers',
    [
        # winphone
        # uuid1 with park 1 booster and 1 chair
        (True, ['dbid0_uuid1'], ['uuid1']),
        # uuid0 with park 1 booster and 0 chair
        (7, ['dbid0_uuid0'], ['uuid0']),
        # uuid1 with park 1 booster and 1 chair
        ([7], ['dbid0_uuid1'], ['uuid1']),
        # uuid2 with park 1 booster and 1 chair
        # uuid2 with own 1 booster and 1 chair
        ([7], ['dbid0_uuid2'], ['uuid2']),
        # uuid3 with park 1 booster and 1 chair
        # uuid3 with own 1 booster and 3 chairs
        (7, ['dbid0_uuid3'], ['uuid3']),
        # uuid1 with park 1 booster and 1 chair
        # uuid2 with park 1 booster and 1 chair
        # uuid2 with own 1 booster and 1 chair
        ([3], ['dbid0_uuid1', 'dbid0_uuid2'], ['uuid1', 'uuid2']),
        # uuid0 with park 1 booster and 0 chair
        # uuid3 with park 1 booster and 1 chair
        # uuid3 with own 1 booster and 3 chairs
        (1, ['dbid0_uuid0', 'dbid0_uuid3'], ['uuid3']),
        # uuid3 with park 1 booster and 1 chair
        # uuid3 with own 1 booster and 3 chairs
        ([1, 7], ['dbid0_uuid3'], ['uuid3']),
        # uuid3 with park 1 booster and 1 chair
        # uuid3 with own 1 booster and 3 chairs
        ([0, 1], ['dbid0_uuid3'], ['uuid3']),
        # uuid1 with park 1 booster and 1 chair
        # uuid3 with park 1 booster and 1 chair
        # uuid3 with own 1 booster and 3 chairs
        ([3, 3], ['dbid0_uuid1', 'dbid0_uuid3'], ['uuid3']),
        # uuid4 with park 1 booster and 0 chair
        ([3], ['dbid0_uuid4'], []),
        # uuid4 with park 1 booster and 0 chair
        ([7], ['dbid0_uuid4'], ['uuid4']),
    ],
)
async def test_filter_childchairs(
        taxi_candidates,
        driver_positions,
        childchair,
        drivers,
        expected_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': driver, 'position': [37.624252, 55.770587]}
            for driver in drivers
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'max_distance': 10000,
        'limit': 3,
        'filters': ['partners/childchairs'],
        'point': [37.611254, 55.752533],
        'zone_id': 'moscow',
        'requirements': {'childchair': childchair},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    assert len(drivers) == len(expected_drivers)
    for driver in json['drivers']:
        assert driver['uuid'] in expected_drivers
