import dateutil.parser
import pytest

from tests_eats_catalog_storage.helpers import helpers


async def search_zones_list(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/delivery-zones/list'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_list_with_empty_request(taxi_eats_catalog_storage):
    data = {}
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert 'not_found_delivery_zone_source_infos' not in response_data
    assert 'not_found_delivery_zone_ids' not in response_data
    assert 'not_found_place_ids' not in response_data
    assert not response_data['delivery_zones']


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_list_with_zone_ids(taxi_eats_catalog_storage):
    # There are 3 delivery zones in insert_places_and_zones.sql:
    # id=100, id=101, id=120

    data = {
        'delivery_zone_ids': [100, 121],
        'delivery_zone_source_infos': [
            {'source': 'eats_core', 'external_id': 'id-119'},
            {'source': 'eats_core', 'external_id': 'id-120'},
        ],
    }
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data['not_found_delivery_zone_source_infos']) == 1
    assert response_data['not_found_delivery_zone_source_infos'][0] == {
        'source': 'eats_core',
        'external_id': 'id-119',
    }

    assert len(response_data['not_found_delivery_zone_ids']) == 1
    assert response_data['not_found_delivery_zone_ids'][0] == 121

    assert 'not_found_place_ids' not in response_data

    assert len(response_data['delivery_zones']) == 2


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_list_with_place_ids(taxi_eats_catalog_storage):
    # There are 3 place_ids in insert_places_and_zones.sql: 10, 11, 20
    # Delivery zones reference 2 place_ids: 11, 20

    data = {'place_ids': [10, 11]}
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert 'not_found_delivery_zone_source_infos' not in response_data
    assert 'not_found_delivery_zone_ids' not in response_data

    assert len(response_data['not_found_place_ids']) == 1
    assert response_data['not_found_place_ids'][0] == 10

    assert len(response_data['delivery_zones']) == 1


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_list_with_shared_place_id(taxi_eats_catalog_storage):
    # 2 delivery zones reference place_id 20

    data = {'place_ids': [20]}
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert 'not_found_delivery_zone_source_infos' not in response_data
    assert 'not_found_delivery_zone_ids' not in response_data
    assert 'not_found_place_ids' not in response_data

    assert len(response_data['delivery_zones']) == 2


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_list_with_place_and_zone_ids(taxi_eats_catalog_storage):
    # There are 3 place_ids in insert_places_and_zones.sql: 10, 11, 20
    # There are 3 delivery zones in insert_places_and_zones.sql:
    # id=100, id=101, id=120

    data = {
        'delivery_zone_ids': [100, 121],
        'delivery_zone_source_infos': [
            {'source': 'eats_core', 'external_id': 'id-119'},
            {'source': 'eats_core', 'external_id': 'id-120'},
        ],
        'place_ids': [10, 20],
    }
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data['not_found_delivery_zone_source_infos']) == 1
    assert response_data['not_found_delivery_zone_source_infos'][0] == {
        'source': 'eats_core',
        'external_id': 'id-119',
    }

    assert len(response_data['not_found_delivery_zone_ids']) == 1
    assert response_data['not_found_delivery_zone_ids'][0] == 121

    assert len(response_data['not_found_place_ids']) == 1
    assert response_data['not_found_place_ids'][0] == 10

    assert len(response_data['delivery_zones']) == 3


@pytest.mark.parametrize('by_id', [True, False])
async def test_list_compare_fields(
        taxi_eats_catalog_storage, pgsql, load_json, by_id,
):
    # Insert place
    place_json = load_json('place_request.json')
    place_id = 3
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    # Insert delivery zone
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert response['revision'] == 1
    zone_json['revision'] = 1
    zone_id = helpers.get_delivery_zone_id(pgsql, zone_external_id)

    # Wait cache update
    await taxi_eats_catalog_storage.invalidate_caches(clean_update=False)

    # Get delivery zone info
    if by_id:
        data = {'delivery_zone_ids': [zone_id]}
    else:
        data = {
            'delivery_zone_source_infos': [
                {
                    'source': zone_json['source'],
                    'external_id': zone_external_id,
                },
            ],
        }
    response = await search_zones_list(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()

    assert 'not_found_delivery_zone_source_infos' not in response_data
    assert 'not_found_delivery_zone_ids' not in response_data
    assert 'not_found_place_ids' not in response_data

    assert len(response_data['delivery_zones']) == 1
    zone = response_data['delivery_zones'][0]

    # Compare received info and original info
    assert zone['delivery_zone_id'] == zone_id
    assert zone['created_at'] is not None
    assert zone['created_at'] == zone['updated_at']

    zone_info = zone['delivery_zone']

    for i in range(len(zone_json['working_intervals'])):
        # String values can differ if different time zone offsets are used.
        # Compare parsed time values.
        assert dateutil.parser.parse(
            zone_info['working_intervals'][i]['from'],
        ) == dateutil.parser.parse(zone_json['working_intervals'][i]['from'])
        assert dateutil.parser.parse(
            zone_info['working_intervals'][i]['to'],
        ) == dateutil.parser.parse(zone_json['working_intervals'][i]['to'])

    del zone_info['working_intervals']
    del zone_json['working_intervals']
    del zone_json['source']
    zone_json['polygon'] = {
        'coordinates': zone_json['polygons']['coordinates'][0],
    }
    del zone_json['polygons']
    del zone_json['updated_at']

    assert zone_info == zone_json
