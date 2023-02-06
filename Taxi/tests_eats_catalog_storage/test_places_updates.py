import pytest


async def get_places_updates(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/places/updates'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def get_places_by_revision_ids(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/places/retrieve-by-revision-ids'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def get_places_by_ids(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/places/retrieve-by-ids'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_get_places_updates_by_revision_id(taxi_eats_catalog_storage):
    data = {
        'limit': 100,
        'last_known_revision': 1000,
        'projection': ['enabled', 'name'],
    }
    response = await get_places_updates(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    assert 'last_known_revision' in response.json()
    assert response.json()['last_known_revision'] == 1004

    places = response.json()['places']
    assert len(places) == 3
    assert 'id' in places[0]
    assert 'revision_id' in places[0]
    assert 'updated_at' in places[0]
    assert 'name' in places[0]
    assert 'enabled' in places[0]


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_get_places_by_revision_ids(taxi_eats_catalog_storage):
    data = {
        'revision_ids': [1000, 1001, 1002],
        'projection': ['enabled', 'name'],
    }
    response = await get_places_by_revision_ids(
        taxi_eats_catalog_storage, data,
    )
    assert response.status_code == 200

    places = response.json()['places']
    assert len(places) == 2
    assert 'id' in places[0]
    assert 'revision_id' in places[0]
    assert 'updated_at' in places[0]
    assert 'name' in places[0]
    assert 'enabled' in places[0]

    place_ids = []
    for place in places:
        place_ids.append(place['id'])
    assert 12 not in place_ids
    assert 10 in place_ids
    assert 11 in place_ids


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_get_places_by_ids(taxi_eats_catalog_storage):
    data = {'place_ids': [10, 11, 13], 'projection': ['enabled', 'name']}
    response = await get_places_by_ids(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    places = response.json()['places']
    assert len(places) == 2
    assert 'id' in places[0]
    assert 'revision_id' in places[0]
    assert 'updated_at' in places[0]
    assert 'name' in places[0]
    assert 'enabled' in places[0]

    place_ids = []
    for place in places:
        place_ids.append(place['id'])
    assert 13 not in place_ids
    assert 10 in place_ids
    assert 11 in place_ids

    not_found_place_ids = response.json()['not_found_place_ids']
    assert len(not_found_place_ids) == 1
    assert 13 in not_found_place_ids


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_get_places_by_ids_with_new_rating(taxi_eats_catalog_storage):
    data = {'place_ids': [10], 'projection': ['enabled', 'name', 'new_rating']}
    response = await get_places_by_ids(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    assert response.json() == {
        'not_found_place_ids': [],
        'places': [
            {
                'enabled': True,
                'id': 10,
                'name': 'Название10',
                'new_rating': {'rating': 5.0, 'show': True, 'count': 0},
                'revision_id': 1000,
                'updated_at': '2020-10-10T02:05:05+00:00',
            },
        ],
    }


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_get_places_by_revision_ids_with_new_rating(
        taxi_eats_catalog_storage,
):
    data = {
        'revision_ids': [1000, 1001, 1002],
        'projection': ['enabled', 'name', 'new_rating'],
    }
    response = await get_places_by_revision_ids(
        taxi_eats_catalog_storage, data,
    )
    assert response.status_code == 200

    assert response.json() == {
        'places': [
            {
                'enabled': True,
                'id': 10,
                'name': 'Название10',
                'new_rating': {'rating': 5.0, 'show': True, 'count': 0},
                'revision_id': 1000,
                'updated_at': '2020-10-10T02:05:05+00:00',
            },
        ],
    }


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_get_places_updates_with_new_rating(taxi_eats_catalog_storage):
    data = {
        'limit': 100,
        'last_known_revision': 999,
        'projection': ['enabled', 'name', 'new_rating'],
    }
    response = await get_places_updates(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    assert response.json() == {
        'last_known_revision': 1000,
        'places': [
            {
                'enabled': True,
                'id': 10,
                'name': 'Название10',
                'new_rating': {'rating': 5.0, 'show': True, 'count': 0},
                'revision_id': 1000,
                'updated_at': '2020-10-10T02:05:05+00:00',
            },
        ],
    }
