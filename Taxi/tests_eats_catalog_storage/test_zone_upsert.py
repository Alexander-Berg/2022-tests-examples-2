from dateutil import parser
import psycopg2
import pytest

from tests_eats_catalog_storage.helpers import helpers

TEST_ENABLED_CONFIG = {'enabled': True}
TEST_DISABLED_CONFIG = {'enabled': False}


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_insert_zone_with_wrong_revision(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id = 235
    place_json = load_json('place_request.json')
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    zone_external_id = 'id-6123'
    zone_json = load_json('delivery_zone_request.json')

    zone_json['revision'] = 12512
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 409,
    )

    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == 0

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(f'SELECT * FROM storage.delivery_zones')
    assert cursor.fetchone() is None


@pytest.mark.parametrize('has_place_id', [True, False])
@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_insert_zone(
        taxi_eats_catalog_storage, pgsql, load_json, has_place_id,
):
    if has_place_id:
        place_id = 3
        place_json = load_json('place_request.json')
        response = await helpers.place_upsert(
            taxi_eats_catalog_storage, place_id, place_json, 200,
        )
        assert response['revision'] == 1

    right_revision = response['revision'] if has_place_id else 1
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    if not has_place_id:
        zone_json['source'] = 'yandex_rover'
        del zone_json['place_id']
        zone_json['places_ids'] = [3, 10, 3, 5]
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert response['revision'] == right_revision

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    psycopg2.extras.register_composite(
        'storage.delivery_zone_delivery_condition', cursor,
    )
    cursor.execute(
        """SELECT pg_typeof(working_intervals) FROM storage.delivery_zones""",
    )
    [working_intervals_type] = cursor.fetchone()
    assert working_intervals_type in [
        'storage.working_interval[]',
        'storage.delivery_zone_working_interval[]',
    ]
    psycopg2.extras.register_composite(working_intervals_type[:-2], cursor)

    cursor.execute("""SELECT * FROM storage.delivery_zones""")

    zone = cursor.fetchone()
    assert zone['id'] > 0
    assert zone['external_id'] == zone_external_id
    assert zone['source'] == zone_json['source']
    if has_place_id:
        assert zone['place_id'] == zone_json['place_id']
        assert zone['places_ids'] is None
    else:
        assert zone['place_id'] is None
        assert zone['places_ids'] == sorted(set(zone_json['places_ids']))
    assert zone['couriers_zone_id'] == zone_json['couriers_zone_id']
    assert zone['created_at'] is not None
    assert zone['created_at'] == zone['updated_at']
    assert zone['enabled'] == zone_json['enabled']
    assert zone['name'] == zone_json['name']
    assert zone['couriers_type'] == zone_json['couriers_type']
    assert zone['shipping_type'] == zone_json['shipping_type']
    assert zone['features'] == zone_json['features']
    assert zone['real_updated_at'] == parser.parse(zone_json['updated_at'])

    del_cons = zone['delivery_conditions']
    req_del_cons = zone_json['delivery_conditions']
    assert [del_con._asdict() for del_con in del_cons] == req_del_cons

    assert [
        {'value': zone['market_avg_time'], 'code': 'market_avg_time'},
        {'value': zone['arrival_time'], 'code': 'arrival_time'},
    ] == zone_json['timing']

    def convert_work_intervals(work_intervals):
        for work_interval in work_intervals:
            interval = dict(work_interval._asdict())
            yield {
                'from': interval['interval_from'].isoformat(),
                'to': interval['interval_to'].isoformat(),
            }

    assert (
        list(convert_work_intervals(zone['working_intervals']))
        == zone_json['working_intervals']
    )

    assert (
        zone['polygons']
        == '{"((0,0),(0,1),(1,1),(1,0),(0,0))",'
        + '"((20,20),(20,21),(21,21),(21,20),(20,20))"}'
    )


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone(taxi_eats_catalog_storage, load_json):
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

    zone_json['name'] = 'new_name'
    zone_json['revision'] = zone_response['revision']
    right_revision = zone_response['revision'] + 1
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )

    assert zone_response['revision'] == right_revision


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_not_affecting_id_sequence(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1
    zone_id = helpers.get_delivery_zone_id(pgsql, zone_external_id)

    for i in range(2):
        zone_json['name'] = f'new_name_{i}'
        zone_json['revision'] = zone_response['revision']
        zone_response = await helpers.delivery_zone_upsert(
            taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
        )

    other_zone_external_id = 'id-3'
    zone_json['revision'] = 0
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, other_zone_external_id, zone_json, 200,
    )
    assert zone_response['revision'] == 1
    other_zone_id = helpers.get_delivery_zone_id(pgsql, other_zone_external_id)
    assert other_zone_id == zone_id + 1


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_update_zone_wrong_revision(
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
    zone_json['revision'] = zone_response['revision'] + 10
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 409,
    )
    assert zone_response['code'] == 'race_condition'
    assert zone_response['details']['revision'] == right_revision


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_insert_zone_nonexistent_place_id(
        taxi_eats_catalog_storage, load_json,
):
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert response['code'] == 'place_not_exists_foreign_key'


async def test_insert_zone_neither_place_id_nor_places_ids(
        taxi_eats_catalog_storage, load_json,
):
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    del zone_json['place_id']
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert response['code'] == 'request_parameters_invalid'


async def test_insert_zone_both_place_id_and_places_ids(
        taxi_eats_catalog_storage, load_json,
):
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_json['places_ids'] = []
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert response['code'] == 'request_parameters_invalid'


async def test_insert_zone_both_polygon_and_polygons(
        taxi_eats_catalog_storage, load_json,
):
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    zone_json['polygon'] = {
        'coordinates': zone_json['polygons']['coordinates'][0],
    }
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert response['code'] == 'request_parameters_invalid'


async def test_update_zone_invalid_polygon_linear_ring_count(
        taxi_eats_catalog_storage, load_json,
):
    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    linear_ring = [[0, 0], [0, 1], [1, 1], [0, 0]]

    def make_data(coordinates):
        zone_json['polygons'] = {'coordinates': coordinates}
        return zone_json

    data = make_data(coordinates=[[]])
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, data, 400,
    )

    data = make_data(coordinates=[[linear_ring, linear_ring]])
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, data, 400,
    )

    data = make_data(coordinates=[[linear_ring] * 10])
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, data, 400,
    )


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_insert_zone_invalid_polygon(
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
    # no end point - to fail
    zone_json['polygons']['coordinates'] = [[[[0, 0], [0, 1], [1, 0], [1, 1]]]]

    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert zone_response['code'] == 'delivery_zone_invalid_polygon'

    zone_external_id = 'id-4'
    zone_json = load_json('delivery_zone_request.json')
    # self intersection inside polygon
    zone_json['polygons']['coordinates'] = [
        [[[0, 0], [0, 1], [1, 1], [1, 0], [0, -1], [1, -1], [0, 0]]],
    ]
    zone_response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 400,
    )
    assert zone_response['code'] == 'delivery_zone_invalid_polygon'


@pytest.mark.config(EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_ENABLED_CONFIG)
async def test_insert_zone_invalid_polygon_corrected(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')
    place_response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert place_response['revision'] == 1

    zone_external_id = 'id-1'
    zone_json = load_json('delivery_zone_request.json')
    # wrong clock wise orientation
    zone_json['polygons']['coordinates'] = [
        [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
    ]
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )

    zone_external_id = 'id-2'
    zone_json = load_json('delivery_zone_request.json')
    # not closed polygon, start point != end point
    zone_json['polygons']['coordinates'] = [[[[0, 0], [0, 1], [1, 1], [1, 0]]]]
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )

    zone_external_id = 'id-3'
    zone_json = load_json('delivery_zone_request.json')
    # wrong clock wise orientation and no closing point at the same time
    zone_json['polygons']['coordinates'] = [[[[0, 0], [1, 0], [1, 1], [0, 1]]]]
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )


@pytest.mark.config(
    EATS_CATALOG_STORAGE_VALIDATE_POLYGONS=TEST_DISABLED_CONFIG,
)
async def test_insert_zone_invalid_polygon_disabled_config(
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
    # no end point - to fail
    zone_json['polygons']['coordinates'] = [[[[0, 0], [0, 1], [1, 0], [1, 1]]]]

    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )

    zone_external_id = 'id-4'
    zone_json = load_json('delivery_zone_request.json')
    # self intersection inside polygon
    zone_json['polygons']['coordinates'] = [
        [[[0, 0], [0, 1], [1, 1], [1, 0], [0, -1], [1, -1], [0, 0]]],
    ]
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_place_and_zone.sql'])
async def test_upsert_delivery_zone_check_revision_id(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'SELECT external_id, revision_id, place_id '
        'FROM storage.delivery_zones where id = 100',
    )
    zone = cursor.fetchone()
    zone_external_id = zone['external_id']
    place_id = zone['place_id']
    db_revision_id = zone['revision_id']

    # upsert zone again
    zone_json = load_json('delivery_zone_request.json')
    zone_json['place_id'] = place_id
    zone_json['revision'] = 1
    response = await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )
    right_revision = response['revision']

    # check new revision_id
    cursor.execute(
        'SELECT revision_id FROM storage.delivery_zones where id = 100',
    )
    new_db_revision_id = cursor.fetchone()['revision_id']
    assert new_db_revision_id == db_revision_id + 1

    # try to upsert with wrong revision
    zone_json['revision'] = 999
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 409,
    )

    # upsert again with right revision
    zone_json['revision'] = right_revision
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_json, 200,
    )

    # check new revision_id again
    cursor.execute(
        'SELECT revision_id FROM storage.delivery_zones where id = 100',
    )
    new_db_revision_id_2 = cursor.fetchone()['revision_id']
    assert new_db_revision_id_2 == new_db_revision_id + 1
