import pytest


@pytest.mark.config(
    CLASSES_WITHOUT_PERMIT_BY_ZONES_FILTER_ENABLED=True,
    CLASSES_WITHOUT_PERMIT_BY_ZONES={
        '__default__': {
            'vip': ['econom', 'comfort', 'comfortplus', 'vip'],
            'comfortplus': ['comfort', 'comfortplus'],
            'cargo': ['cargo'],
            'express': ['express'],
        },
        'moscow': {
            '*': ['vip', 'express', 'cargo'],
            'vip': ['vip', 'business'],
            'comfort': ['comfort'],
        },
        'spb': {
            '*': ['vip', 'cargo', 'express'],
            'vip': ['vip', 'business', 'ultimate', 'comfortplus'],
            'business': ['business', 'vip'],
            'comfort': ['comfort'],
        },
    },
)
@pytest.mark.parametrize(
    'driver_candidates, zone_id, allowed_classes, expected_response',
    [
        (['dbid0_uuid0'], 'moscow', ['econom', 'vip'], ['uuid0']),
        (['dbid1_uuid3'], 'moscow', ['comfortplus'], None),
        (['dbid0_uuid0'], 'spb', ['econom'], None),
        (
            ['dbid0_uuid1', 'dbid1_uuid3', 'dbid0_uuid0'],
            'spb',
            ['econom', 'business'],
            ['uuid0', 'uuid3'],
        ),
    ],
)
async def test_filter_permits(
        taxi_candidates,
        taxi_config,
        driver_positions,
        driver_candidates,
        zone_id,
        allowed_classes,
        expected_response,
):

    await driver_positions(
        [
            {'dbid_uuid': driver, 'position': [55, 35]}
            for driver in driver_candidates
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/class', 'partners/fetch_permits_classes'],
        'point': [55, 35],
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    if expected_response:
        assert len(drivers) == len(expected_response)
        assert all([driver['uuid'] in expected_response for driver in drivers])
    else:
        assert not drivers
