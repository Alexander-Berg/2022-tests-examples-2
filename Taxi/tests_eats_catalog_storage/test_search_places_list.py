import dateutil.parser
import pytest

from tests_eats_catalog_storage.helpers import helpers


async def search_places_list(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/places/list'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_list_with_empty_request(taxi_eats_catalog_storage):
    data = {}
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert 'not_found_place_ids' not in response_data
    assert 'not_found_place_slugs' not in response_data
    assert not response_data['places']


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_list_with_ids(taxi_eats_catalog_storage):
    # there are 3 place_ids in insert_places.sql: 10, 11, 20

    data = {'place_ids': [11, 20, 21]}
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data['not_found_place_ids']) == 1
    assert response_data['not_found_place_ids'][0] == 21

    assert 'not_found_place_slugs' not in response_data

    assert len(response_data['places']) == 2


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_list_with_slugs(taxi_eats_catalog_storage):
    # there are 3 place_slugs in insert_places.sql: slug10, slug11, slug20

    data = {'place_slugs': ['slug10', 'slug11', 'slug20', 'slug21']}
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert 'not_found_place_ids' not in response_data

    assert len(response_data['not_found_place_slugs']) == 1
    assert response_data['not_found_place_slugs'][0] == 'slug21'

    assert len(response_data['places']) == 3


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_list_with_ids_and_slugs(taxi_eats_catalog_storage):
    # there are 3 place_ids in insert_places.sql: 10, 11, 20
    # there are 3 place_slugs in insert_places.sql: slug10, slug11, slug20

    data = {
        'place_ids': [10, 11, 21],
        'place_slugs': ['slug11', 'slug20', 'slug21'],
    }
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data['not_found_place_ids']) == 1
    assert response_data['not_found_place_ids'][0] == 21

    assert len(response_data['not_found_place_slugs']) == 1
    assert response_data['not_found_place_slugs'][0] == 'slug21'

    assert len(response_data['places']) == 3


async def test_list_compare_fields(taxi_eats_catalog_storage, load_json):
    # Insert place
    json_data = load_json('place_request.json')
    place_id = 2
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, json_data, 200,
    )
    assert response['revision'] == 1
    json_data['revision'] = 1

    # Wait cache update
    await taxi_eats_catalog_storage.invalidate_caches(clean_update=False)

    # Get place info
    data = {'place_ids': [place_id]}
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert 'not_found_place_ids' not in response_data
    assert 'not_found_place_slugs' not in response_data

    assert len(response_data['places']) == 1
    place = response_data['places'][0]

    # Compare received info and original info
    assert place['place_id'] == place_id
    assert place['created_at'] is not None
    assert place['created_at'] == place['updated_at']

    place_info = place['place']

    # The returned value uses 0:00 time zone offset.
    # The strings are different but the time is equal.
    assert dateutil.parser.parse(
        place_info['launched_at'],
    ) == dateutil.parser.parse(json_data['launched_at'])

    del place_info['launched_at']
    del json_data['launched_at']
    del json_data['working_intervals']
    del json_data['allowed_couriers_types']
    del json_data['origin_id']

    assert place_info == json_data


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_list_with_id_with_new_zone(taxi_eats_catalog_storage):
    data = {'place_ids': [10]}
    response = await search_places_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    response_data = response.json()
    place = response_data['places'][0]['place']
    assert place['new_rating'] == {'rating': 5, 'show': True, 'count': 0}
