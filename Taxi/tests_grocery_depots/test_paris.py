import pytest


@pytest.mark.pgsql('grocery_depots', files=['paris_depots-n-zones.sql'])
async def test_paris(taxi_grocery_depots):
    await taxi_grocery_depots.invalidate_caches()
    response_depots = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/depots', json={'legacy_depot_ids': []},
    )
    depots = response_depots.json()['depots']
    assert len(depots) == 5
    depots_legacy_ids = [depot['legacy_depot_id'] for depot in depots]
    response_zones = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/zones',
        json={'legacy_depot_ids': depots_legacy_ids},
    )
    zones = response_zones.json()['zones']
    assert len(zones) == 5
