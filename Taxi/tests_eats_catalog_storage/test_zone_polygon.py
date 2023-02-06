import psycopg2
import pytest

from tests_eats_catalog_storage.helpers import helpers

TEST_ENABLED_CONFIG = {'enabled': True}
TEST_DISABLED_CONFIG = {'enabled': False}


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_polygon(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    place_response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert place_response['revision'] == 1

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1

    right_revision = zone_response['revision']
    data_polygon = {
        'source': 'eats_core',
        'revision': right_revision,
        'polygon': {'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]},
    }
    response = await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, zone_external_id, data_polygon, 200,
    )
    assert response['revision'] == right_revision + 1

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        """SELECT external_id, polygons FROM storage.delivery_zones""",
    )

    zone = cursor.fetchone()
    assert zone['external_id'] == zone_external_id
    assert zone['polygons'] == '{"((1,1),(1,2),(2,2),(2,1),(1,1))"}'


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_polygon_no_id(taxi_eats_catalog_storage):
    zone_external_id = 'id-2'
    right_revision = 0
    data_polygon = {
        'source': 'eats_core',
        'revision': right_revision,
        'polygon': {'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]},
    }
    response = await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, zone_external_id, data_polygon, 404,
    )

    assert response['code'] == 'delivery_zone_not_exists'


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_polygon_wrong_revision(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    place_response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert place_response['revision'] == 1

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1

    right_revision = zone_response['revision']
    wrong_revision = zone_response['revision'] + 10
    data_polygon = {
        'source': 'eats_core',
        'revision': wrong_revision,
        'polygon': {'coordinates': [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]},
    }
    zone_response = await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, zone_external_id, data_polygon, 409,
    )

    assert zone_response['code'] == 'race_condition'
    assert zone_response['details']['revision'] == right_revision


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_invalid_polygon(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    place_response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert place_response['revision'] == 1

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1

    right_revision = zone_response['revision']
    data_polygon = {
        'source': 'eats_core',
        'revision': right_revision,
        'polygon': {
            'coordinates': [
                [[0, 0], [0, 1], [1, 1], [1, 0], [0, -1], [1, -1], [0, 0]],
            ],
        },
    }
    response = await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, zone_external_id, data_polygon, 400,
    )
    assert response['code'] == 'delivery_zone_invalid_polygon'


@pytest.mark.config(
    EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_DISABLED_CONFIG,
)
async def test_update_zone_invalid_polygon_disabled_config(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    place_response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert place_response['revision'] == 1

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1

    right_revision = zone_response['revision']
    data_polygon = {
        'source': 'eats_core',
        'revision': right_revision,
        'polygon': {
            'coordinates': [
                [[0, 0], [0, 1], [1, 1], [1, 0], [0, -1], [1, -1], [0, 0]],
            ],
        },
    }
    await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, zone_external_id, data_polygon, 200,
    )


async def test_update_zone_invalid_polygon_linear_ring_count(
        taxi_eats_catalog_storage, load_json,
):
    linear_ring = [[0, 0], [0, 1], [1, 1], [0, 0]]

    def make_data(coordinates):
        return {
            'source': 'eats_core',
            'revision': 0,
            'polygon': {'coordinates': coordinates},
        }

    data = make_data(coordinates=[])
    await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, 'id-0', data, 400,
    )

    data = make_data(coordinates=[linear_ring, linear_ring])
    await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, 'id-0', data, 400,
    )

    data = make_data(coordinates=[linear_ring] * 10)
    await helpers.delivery_zone_polygon_update(
        taxi_eats_catalog_storage, 'id-0', data, 400,
    )
