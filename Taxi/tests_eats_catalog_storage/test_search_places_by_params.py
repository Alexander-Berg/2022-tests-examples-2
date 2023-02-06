import pytest


async def search_places_by_params(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/places-by-params'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def test_get_with_body_with_projection_only(taxi_eats_catalog_storage):
    response = await search_places_by_params(
        taxi_eats_catalog_storage, {'projection': ['name']},
    )
    assert response.status_code == 400


async def test_get_non_existent_places(taxi_eats_catalog_storage):
    data = {'brand_id': 1, 'projection': ['name']}
    response = await search_places_by_params(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    assert response.json() == {'places': []}


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_get_places_by_brand_id(taxi_eats_catalog_storage):
    data = {'brand_id': 6, 'projection': ['enabled', 'name']}
    response = await search_places_by_params(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    places = response.json()['places']
    assert len(places) == 3
    for place in places:
        assert 'id' in place
        assert 'revision_id' in place
        assert 'updated_at' in place
        assert 'name' in place
        assert 'enabled' in place


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_get_places_by_brand_id_and_region_id(taxi_eats_catalog_storage):
    data = {'brand_id': 6, 'region_id': 1, 'projection': ['enabled', 'name']}
    response = await search_places_by_params(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    places = response.json()['places']
    assert len(places) == 2
    for place in places:
        assert 'id' in place
        assert 'revision_id' in place
        assert 'updated_at' in place
        assert 'name' in place
        assert 'enabled' in place

    data = {'brand_id': 5, 'region_id': 8, 'projection': ['name']}
    response = await search_places_by_params(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    assert response.json() == {'places': []}


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_get_places_by_brand_id_and_region_id_with_new_rating(
        taxi_eats_catalog_storage,
):
    data = {
        'brand_id': 1,
        'region_id': 1,
        'projection': ['enabled', 'name', 'new_rating'],
    }
    response = await search_places_by_params(taxi_eats_catalog_storage, data)
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
