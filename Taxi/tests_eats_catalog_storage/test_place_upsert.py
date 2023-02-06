import psycopg2
import pytest

from tests_eats_catalog_storage.helpers import helpers


async def test_insert_place_with_wrong_revision(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    data = load_json('place_request.json')
    place_id = 2
    data['revision'] = 555

    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, data, 409,
    )

    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == 0

    cursor = pgsql['eats_catalog_storage'].cursor()
    cursor.execute(f'SELECT * FROM storage.places')
    assert cursor.fetchone() is None


@pytest.mark.place_tags('tag1', 'foo', 'bar')
async def test_insert_place(taxi_eats_catalog_storage, pgsql, load_json):
    data = load_json('place_request.json')

    place_id = 2
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, data, 200,
    )
    assert response['revision'] == 1

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    psycopg2.extras.register_composite('storage.place_gallery', cursor)
    psycopg2.extras.register_composite('storage.place_brand_v2', cursor)
    psycopg2.extras.register_composite('storage.place_address', cursor)
    psycopg2.extras.register_composite('storage.place_country', cursor)
    psycopg2.extras.register_composite(
        'storage.place_country_currency', cursor,
    )

    psycopg2.extras.register_composite('storage.place_category', cursor)
    psycopg2.extras.register_composite('storage.place_quick_filter', cursor)
    psycopg2.extras.register_composite('storage.place_region', cursor)
    psycopg2.extras.register_composite('storage.place_price_category', cursor)
    cursor.execute(
        """SELECT pg_typeof(working_intervals) FROM storage.places""",
    )
    [working_intervals_type] = cursor.fetchone()
    assert working_intervals_type in [
        'storage.working_interval[]',
        'storage.delivery_zone_working_interval[]',
    ]
    psycopg2.extras.register_composite(working_intervals_type[:-2], cursor)

    def convert_work_intervals(work_intervals):
        res = []
        for work_interval in work_intervals:
            interval = dict(work_interval._asdict())
            res.append(
                {
                    'from': interval['interval_from'].isoformat(),
                    'to': interval['interval_to'].isoformat(),
                },
            )
        return res

    cursor.execute('SELECT * FROM storage.places')
    place = cursor.fetchone()

    assert place['id'] == place_id
    assert place['created_at'] is not None
    assert place['created_at'] == place['updated_at']
    assert place['slug'] == data['slug']
    assert place['enabled'] == place['enabled']
    assert place['name'] == data['name']
    assert place['type'] == data['type']
    assert place['business'] == data['business']
    assert place['launched_at'].isoformat() == data['launched_at']
    assert place['payment_methods'] == '{cash,taxi,card_post_payment}'
    assert place['address_comment'] == data['address_comment']
    assert place['contacts'] == data['contacts']
    assert (
        convert_work_intervals(place['working_intervals'])
        == data['working_intervals']
    )
    assert (
        place['allowed_couriers_types']
        == '{' + ','.join(data['allowed_couriers_types']) + '}'
    )
    assert place['origin_id'] == data['origin_id']

    gallery_list = [gallery._asdict() for gallery in place['gallery']]
    for gallery_item in gallery_list:
        if gallery_item['template'] is None:
            del gallery_item['template']
    assert gallery_list == data['gallery']

    assert place['brand']._asdict() == data['brand']
    assert place['address']._asdict() == data['address']
    assert place['assembly_cost'] == data['assembly_cost']

    country = place['country']._asdict()
    assert country['id'] == data['country']['id']
    assert country['name'] == data['country']['name']
    assert country['code'] == data['country']['code']

    currency = country['currency']._asdict()
    assert currency['code'] == data['country']['currency']['code']
    assert currency['sign'] == data['country']['currency']['sign']

    assert [category._asdict() for category in place['categories']] == data[
        'categories'
    ]

    quick_filters = [
        quick_filter._asdict() for quick_filter in place['quick_filters']
    ]
    assert quick_filters == data['quick_filters']['general']

    wizard_quick_filters = [
        quick_filter._asdict()
        for quick_filter in place['wizard_quick_filters']
    ]
    assert wizard_quick_filters == data['quick_filters']['wizard']

    region = place['region']._asdict()
    assert region['id'] == data['region']['id']
    assert region['time_zone'] == data['region']['time_zone']
    assert region['geobase_ids'] == data['region']['geobase_ids']
    assert region['name'] == data['region']['name']

    assert place['location'] == '(55.741,37.627)'
    assert place['price_category']._asdict() == data['price_category']

    assert place['rating'] == data['rating']
    assert place['extra_info'] == data['extra_info']
    assert place['features'] == data['features']
    assert place['timing'] == data['timing']
    assert place['sorting'] == data['sorting']
    assert set(place['tags']) == set(['tag1', 'foo', 'bar'])

    data['revision'] = response['revision']
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)
    cursor.execute("""SELECT id, created_at, updated_at FROM storage.places""")

    places = list(cursor)
    assert len(places) == 1
    place = places[0]
    assert place[0] == place_id
    assert place[1] != place[2]


async def test_update_place(taxi_eats_catalog_storage, load_json):
    place_id = 3
    place_json = load_json('place_request.json')

    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    place_json['revision'] = response['revision']  # 1
    place_json['name'] = 'new_name'

    right_revision = response['revision'] + 1
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )

    assert response['revision'] == right_revision


async def test_places_insertion_independence(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id_1 = 3
    place_json = load_json('place_request.json')

    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_1, place_json, 200,
    )
    assert response['revision'] == 1

    place_id_2 = 5
    place_json = load_json('place_request.json')

    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_2, place_json, 200,
    )
    assert response['revision'] == 1

    assert helpers.place_exists(pgsql, place_id=place_id_1)
    assert helpers.place_exists(pgsql, place_id=place_id_2)


async def test_places_update_independence(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id_1 = 52
    place_id_2 = 273
    place_json = load_json('place_request.json')

    # insert place using place_id_1
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_1, place_json, 200,
    )
    assert response['revision'] == 1

    # try update place using place_id_2 with place_id_1 related revision
    place_json['revision'] = response['revision']
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_2, place_json, 409,
    )
    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == 0

    # update place using place_id_1
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_1, place_json, 200,
    )
    assert response['revision'] == 2

    # insert place using place_id_2
    place_json['revision'] = 0
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_2, place_json, 200,
    )
    assert response['revision'] == 1

    # update place using place_id_2
    place_json['revision'] = response['revision']
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id_2, place_json, 200,
    )
    assert response['revision'] == 2

    # check both records existence
    assert helpers.place_exists(pgsql, place_id=place_id_1)
    assert helpers.place_exists(pgsql, place_id=place_id_2)


async def test_update_zone_wrong_revision(
        taxi_eats_catalog_storage, load_json,
):
    place_id = 3
    place_json = load_json('place_request.json')

    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    assert response['revision'] == 1

    right_revision = response['revision']
    wrong_revision = 10
    place_json['revision'] = wrong_revision
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 409,
    )

    assert response['code'] == 'race_condition'
    assert response['details']['revision'] == right_revision


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_place.sql'])
async def test_upsert_place_check_revision_id(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT id, revision_id FROM storage.places where id = 10')
    place = cursor.fetchone()
    place_id = place['id']
    db_revision_id = place['revision_id']

    # upsert place again
    place_json = load_json('place_request.json')
    place_json['revision'] = 1
    response = await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )
    right_revision = response['revision']

    # check new revision_id
    cursor.execute('SELECT id, revision_id FROM storage.places where id = 10')
    new_db_revision_id = cursor.fetchone()['revision_id']
    assert new_db_revision_id == db_revision_id + 1

    # try to upsert with wrong revision
    place_json['revision'] = 999
    await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 409,
    )

    # upsert again with right revision
    place_json['revision'] = right_revision
    await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )

    # check new revision_id again
    cursor.execute('SELECT id, revision_id FROM storage.places where id = 10')
    new_db_revision_id_2 = cursor.fetchone()['revision_id']
    assert new_db_revision_id_2 == new_db_revision_id + 1


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_upsert_place_check_new_rating(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'SELECT id, revision_id, new_rating '
        'FROM storage.places where id = 10',
    )
    place = cursor.fetchone()
    place_id = place['id']
    db_revision_id = place['revision_id']
    db_new_rating = place['new_rating']

    place_json = load_json('place_request.json')
    place_json['revision'] = 1
    await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, place_json, 200,
    )

    # check new revision_id
    cursor.execute(
        'SELECT id, revision_id, new_rating '
        'FROM storage.places where id = 10',
    )
    new_place = cursor.fetchone()
    new_db_revision_id = new_place['revision_id']
    new_db_new_rating = new_place['new_rating']
    assert new_db_revision_id == db_revision_id + 1
    assert new_db_new_rating == db_new_rating
