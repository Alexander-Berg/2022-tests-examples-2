import pytest


@pytest.mark.config(
    CHILDSEAT_MAPPING=[{'groups': [1, 2, 3], 'categories': [1, 3, 7]}],
    CANDIDATES_SEARCHABLE_REQUIREMENTS=[
        'animaltransport',
        'check',
        'conditioner',
        'universal',
        'bicycle',
        'yellowcarnumber',
        'ski',
    ],
)
async def test_fetch_profile_classes(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'filters': ['infra/fetch_profile_classes'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert set(drivers[0]['classes']) == {
        'econom',
        'minivan',
        'uberx',
        'uberkids',
    }
