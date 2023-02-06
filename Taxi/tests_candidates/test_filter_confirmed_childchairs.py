import pytest


@pytest.mark.config(
    CHILDSEAT_MAPPING=[
        {'categories': [3], 'groups': [2]},
        {'categories': [7], 'groups': [3]},
        {'categories': [1, 3], 'groups': [1, 2]},
        {'categories': [3, 7], 'groups': [2, 3]},
        {'categories': [1, 3, 7], 'groups': [1, 2, 3]},
    ],
)
@pytest.mark.parametrize(
    'childchair, drivers, expected_drivers',
    [
        # winphone
        # old way confirmations
        # uuid1 with confirmed chairs [2, 3] -> [3, 7]
        #                             [] -> [7]
        (True, ['dbid0_uuid1'], ['uuid1']),
        # old way confirmations
        # uuid0 with confirmed chair [] -> [7]
        (7, ['dbid0_uuid0'], ['uuid0']),
        # old way confirmations
        # uuid1 with confirmed chairs [2, 3] -> [3, 7]
        #                             [] -> [7]
        ([7], ['dbid0_uuid1'], ['uuid1']),
        # new way confirmations
        # uuid2 with cconfirmed chair [] -> [7]
        ([7], ['dbid0_uuid2'], ['uuid2']),
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        (7, ['dbid0_uuid3'], ['uuid3']),
        # uuid1 with confirmed chairs [2, 3] -> [3, 7]
        #                             [] -> [7]
        # uuid2 with confirmed chair [] -> [7]
        ([3], ['dbid0_uuid1', 'dbid0_uuid2'], ['uuid1']),
        # uuid0 with confirmed chair [] -> [7]
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        (1, ['dbid0_uuid0', 'dbid0_uuid3'], ['uuid3']),
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        ([3, 3], ['dbid0_uuid3'], ['uuid3']),
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        ([3, 3, 3], ['dbid0_uuid3'], []),
        # new way confirmations
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        ([1, 7], ['dbid0_uuid3'], ['uuid3']),
        # uuid1 with confirmed chairs [2, 3] -> [3, 7]
        #                             [] -> [7]
        # uuid3 with confirmed chairs [1, 2, 3] -> [1, 3, 7]
        #                             [1, 2] -> [1, 3]
        ([3, 3], ['dbid0_uuid1', 'dbid0_uuid3'], ['uuid3']),
        # uuid1 with confirmed chairs [2, 3] -> [3, 7]
        #                             [] -> [7]
        ([3, 7], ['dbid0_uuid1'], ['uuid1']),
        # new way confirmations
        # uuid4 doesnt have any confirmed chair
        ([3], ['dbid0_uuid4'], []),
        # new way confirmations
        # uuid4 with confirmed chair [] -> [7]
        ([7], ['dbid0_uuid4'], ['uuid4']),
    ],
)
async def test_filter_confirmed_childchairs(
        taxi_candidates,
        driver_positions,
        childchair,
        drivers,
        expected_drivers,
):
    await driver_positions(
        [{'dbid_uuid': driver, 'position': [37, 55]} for driver in drivers],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/confirmed_childchairs'],
        'point': [37, 55],
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
