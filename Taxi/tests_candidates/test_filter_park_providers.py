import pytest


@pytest.mark.parametrize(
    ('providers', 'driver_found'),
    [
        (['yandex', 'park'], True),
        (['park'], False),
        ([], False),
        (None, False),
    ],
)
async def test_filter_park_providers(
        mongodb, taxi_candidates, driver_positions, providers, driver_found,
):
    if providers is not None:
        mongodb.dbparks.update_one(
            {'_id': 'dbid0'}, {'$set': {'providers': providers}},
        )
    else:
        mongodb.dbparks.update_one(
            {'_id': 'dbid0'}, {'$unset': {'providers': ''}},
        )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/park_providers'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']

    if driver_found:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid0'
    else:
        assert not drivers
