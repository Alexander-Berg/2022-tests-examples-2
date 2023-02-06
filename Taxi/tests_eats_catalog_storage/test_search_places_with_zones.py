import pytest


def assert_response_ids(response, place_ids, zone_ids):
    r_zone_ids = set()
    r_place_ids = set()

    assert 'places_and_zones' in response
    for place in response['places_and_zones']:
        r_place_ids.add(place['place']['id'])
        assert len(set(z['id'] for z in place['zones'])) == len(place['zones'])
        for zone in place['zones']:
            r_zone_ids.add(zone['id'])

    assert r_place_ids == place_ids
    assert r_zone_ids == zone_ids


async def search_places_with_zones(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/places-zones'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_empty_request(taxi_eats_catalog_storage):
    request_json = {}
    response = await search_places_with_zones(
        taxi_eats_catalog_storage, request_json,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert 'places_and_zones' in response_data
    assert not response_data['places_and_zones']


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_geo_point(taxi_eats_catalog_storage):
    # search by only geo_point is not supported
    data = {'geo_point': [0.5, 0.5]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 400
    assert response.json()['code'] == 'request_parameters_invalid'


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug(taxi_eats_catalog_storage):
    data = {'place_slug': 'slug20'}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 103, 104, 105})


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_brand_ids(taxi_eats_catalog_storage):
    data = {'brand_ids': [1, 2]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {10, 11}, {100, 105})


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_brand_ids_and_geo_point(taxi_eats_catalog_storage):
    data = {'brand_ids': [3, 4], 'geo_point': [0.5, 0.5]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 105})


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug_brand_ids_geo_point(
        taxi_eats_catalog_storage,
):
    data = {
        'place_slug': 'slug20',
        'brand_ids': [3, 4],
        'geo_point': [0.5, 0.5],
    }
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 105})


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug_brand_ids_geo_point_empty_resp(
        taxi_eats_catalog_storage,
):
    data = {
        'place_slug': 'slug10',
        'brand_ids': [3, 4],
        'geo_point': [0.5, 0.5],
    }
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert 'places_and_zones' in response_data
    assert not response_data['places_and_zones']


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_search_with_zone_with_new_rating(taxi_eats_catalog_storage):
    data = {'place_slug': 'slug10'}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['places_and_zones'][0]['place']['new_rating'] == {
        'rating': 5.0,
        'show': True,
        'count': 0,
    }
