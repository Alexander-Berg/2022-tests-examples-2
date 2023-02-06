import psycopg2

from tests_eats_catalog_storage.helpers import helpers


async def test_disable_zone(taxi_eats_catalog_storage, pgsql, load_json):
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

    req_revision = zone_response['revision']
    right_revision = req_revision + 1
    zone_response = await helpers.delivery_zone_enabled(
        taxi_eats_catalog_storage, zone_external_id, False, req_revision, 200,
    )
    assert zone_response['revision'] == right_revision

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        """SELECT external_id, enabled FROM storage.delivery_zones""",
    )

    zone = cursor.fetchone()
    assert zone['external_id'] == zone_external_id
    assert not zone['enabled']


async def test_disable_zone_no_id(taxi_eats_catalog_storage):
    zone_external_id = 'id-2'
    right_revision = 0
    response = await helpers.delivery_zone_enabled(
        taxi_eats_catalog_storage,
        zone_external_id,
        False,
        right_revision,
        404,
    )

    assert response['code'] == 'delivery_zone_not_exists'


async def test_disable_zone_wrong_revision(
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
    response = await helpers.delivery_zone_enabled(
        taxi_eats_catalog_storage,
        zone_external_id,
        False,
        wrong_revision,
        409,
    )

    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == right_revision
