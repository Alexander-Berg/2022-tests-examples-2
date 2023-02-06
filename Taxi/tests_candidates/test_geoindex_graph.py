import pytest


@pytest.mark.parametrize('max_route_time, driver_count', [(3600, 2), (200, 2)])
async def test_sample(
        taxi_candidates,
        driver_positions,
        mockserver,
        max_route_time,
        driver_count,
):
    @mockserver.json_handler('/maps-router/v2/route')
    def _mock(request):
        assert False, 'Should not be called'

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625172, 55.756506]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [37.625033, 55.761528]},
        ],
    )

    request_body = {
        'geoindex': 'graph',
        'limit': 2,
        'filters': ['infra/route_info'],
        'point': [37.625129, 55.757644],
        'max_route_time': max_route_time,
        'max_route_distance': 100000,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == driver_count


@pytest.mark.parametrize('max_route_time, driver_count', [(3600, 3), (420, 1)])
async def test_sample_with_chain(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        mockserver,
        max_route_time,
        driver_count,
):
    @mockserver.json_handler('/maps-router/v2/route')
    def _mock(request):
        assert False, 'Should not be called'

    # There are 3 drivers in this test:
    # uuid0 ,uuid1, uuid2, uuid3
    # uuid 0 is 420+ seconds away from target
    # uuid 1 is unrechable. It is actually not in index
    # uuid 2 is 0 seconds away, BUT he is also in chain and is moving AWAY -
    #        to position 420 seconds
    # uuid 3 is 145 seconds away, BUT he is in chain and is moving to
    #        position 0 seconds away
    # So, resulting positions for driver ARE:
    # uuid 0 - 420+
    # uuid 1 - unrechable because not in index
    # uuid 2 - 420+ (because chain will bring him there)
    # uuid 3 - 0 (because chain will bring him here)
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'destination': [37.625344, 55.755430],  # eta 423
                'left_distance': 100,
                'left_time': 100,
            },
            {
                'driver_id': 'dbid1_uuid3',
                'destination': [37.625129, 55.757644],  # eta - 0
                'left_distance': 10,
                'left_time': 10,
            },
        ],
    )

    await driver_positions(
        [
            {
                'dbid_uuid': 'dbid0_uuid0',
                'position': [37.625344, 55.755430],
            },  # eta 423
            {
                'dbid_uuid': 'dbid0_uuid1',
                'position': [37.625172, 55.756506],
            },  # eta inf, not in drivers index
            {
                'dbid_uuid': 'dbid0_uuid2',
                'position': [37.625129, 55.757644],
            },  # eta - 0
            {
                'dbid_uuid': 'dbid1_uuid3',
                'position': [37.625033, 55.761528],
            },  # eta - 145
        ],
    )

    request_body = {
        'geoindex': 'graph',
        'limit': 10,
        'filters': ['infra/route_info', 'efficiency/fetch_chain_info'],
        'point': [37.625129, 55.757644],
        'max_route_time': max_route_time,
        'max_route_distance': 100000,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == driver_count
