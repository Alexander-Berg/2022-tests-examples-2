import psycopg2

from tests_eats_catalog_storage.helpers import helpers


async def test_disable_place(taxi_eats_catalog_storage, pgsql, load_json):
    place_id = 3
    place_json = load_json('place_request.json')
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    req_revision = response['revision']
    right_revision = req_revision + 1
    response = await helpers.place_enabled(
        taxi_eats_catalog_storage, place_id, False, req_revision, 200,
    )
    assert response['revision'] == right_revision

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute("""SELECT id, enabled FROM storage.places""")

    place = cursor.fetchone()
    assert place['id'] == place_id
    assert not place['enabled']


async def test_disable_place_no_id(taxi_eats_catalog_storage):
    place_id = 2
    right_revision = 0
    response = await helpers.place_enabled(
        taxi_eats_catalog_storage, place_id, False, right_revision, 404,
    )

    assert response['code'] == 'place_not_exists'


async def test_disable_place_wrong_revision(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    right_revision = response['revision']
    wrong_revision = response['revision'] + 10
    response = await helpers.place_enabled(
        taxi_eats_catalog_storage, place_id, False, wrong_revision, 409,
    )

    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == right_revision
