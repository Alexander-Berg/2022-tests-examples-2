import pytest


async def get_zones_updates(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/delivery_zones/updates'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def get_zones_by_revision_ids(taxi_eats_catalog_storage, data):
    path = (
        '/internal/eats-catalog-storage/v1/delivery_zones'
        '/retrieve-by-revision-ids'
    )
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def get_zones_by_ids(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/delivery_zones/retrieve-by-ids'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def get_zones_by_place_ids(taxi_eats_catalog_storage, data):
    path = (
        '/internal/eats-catalog-storage/v1/delivery_zones'
        '/retrieve-by-place-ids'
    )
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_and_zones.sql'],
)
async def test_get_zones_updates_by_revision_id(taxi_eats_catalog_storage):
    data = {
        'limit': 100,
        'last_known_revision': 1000,
        'projection': ['enabled', 'name'],
    }
    response = await get_zones_updates(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    assert 'last_known_revision' in response.json()
    assert response.json()['last_known_revision'] == 1004

    zones = response.json()['delivery_zones']
    assert len(zones) == 3
    assert 'id' in zones[0]
    assert 'revision_id' in zones[0]
    assert 'updated_at' in zones[0]
    assert 'name' in zones[0]
    assert 'enabled' in zones[0]


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_and_zones.sql'],
)
async def test_get_zones_by_revision_ids(taxi_eats_catalog_storage):
    data = {
        'revision_ids': [1000, 1001, 1002],
        'projection': ['enabled', 'name'],
    }
    response = await get_zones_by_revision_ids(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    zones = response.json()['delivery_zones']
    assert len(zones) == 2
    assert 'id' in zones[0]
    assert 'revision_id' in zones[0]
    assert 'updated_at' in zones[0]
    assert 'name' in zones[0]
    assert 'enabled' in zones[0]

    zone_ids = []
    for place in zones:
        zone_ids.append(place['id'])
    assert 102 not in zone_ids
    assert 100 in zone_ids
    assert 101 in zone_ids


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_and_zones.sql'],
)
async def test_get_zones_by_ids(taxi_eats_catalog_storage):
    data = {
        'delivery_zone_ids': [100, 101, 102],
        'projection': ['enabled', 'name'],
    }
    response = await get_zones_by_ids(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    zones = response.json()['delivery_zones']
    assert len(zones) == 2
    assert 'id' in zones[0]
    assert 'revision_id' in zones[0]
    assert 'updated_at' in zones[0]
    assert 'name' in zones[0]
    assert 'enabled' in zones[0]

    zone_ids = []
    for place in zones:
        zone_ids.append(place['id'])
    assert 102 not in zone_ids
    assert 100 in zone_ids
    assert 101 in zone_ids


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_and_zones.sql'],
)
async def test_get_zones_by_place_ids(taxi_eats_catalog_storage):
    data = {
        'place_ids': [10, 11],
        'projection': ['enabled', 'name', 'working_intervals'],
    }
    response = await get_zones_by_place_ids(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    not_found_place_ids = response.json()['not_found_place_ids']
    assert len(not_found_place_ids) == 1
    assert 11 in not_found_place_ids

    place_with_zones = response.json()['delivery_zones']
    assert len(place_with_zones) == 1
    assert place_with_zones[0]['place_id'] == 10

    zones = place_with_zones[0]['delivery_zones']
    assert len(zones) == 3
    assert 'id' in zones[0]
    assert 'revision_id' in zones[0]
    assert 'updated_at' in zones[0]
    assert 'name' in zones[0]
    assert 'enabled' in zones[0]
    assert 'working_intervals' in zones[0]

    zone_ids = []
    for zone in zones:
        zone_ids.append(zone['id'])
    assert 100 in zone_ids
    assert 101 in zone_ids
    assert 120 in zone_ids
