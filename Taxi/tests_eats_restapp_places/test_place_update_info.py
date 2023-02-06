# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture()
def get_entrance_by_place(get_cursor):
    def do_get_entrance_by_place(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_places.entrance_photo '
            'WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchall()

    return do_get_entrance_by_place


async def test_empty_update_info_204(
        taxi_eats_restapp_places, get_info_by_place,
):

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-info?place_id', json={'places': []},
    )

    assert response.status_code == 204


async def test_first_time_update_info_204(
        taxi_eats_restapp_places, get_info_by_place,
):

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-info?place_id',
        json={
            'places': [
                {
                    'place_id': 111,
                    'name': 'name111',
                    'address_full': 'address111',
                },
                {
                    'place_id': 222,
                    'name': 'name222',
                    'address_full': 'address222',
                    'address_comment': 'comment222',
                },
                {
                    'place_id': 333,
                    'name': 'name333',
                    'address_full': 'address333',
                    'address_comment': '',
                },
            ],
        },
    )

    assert response.status_code == 204

    place_info1 = get_info_by_place(111)
    place_info2 = get_info_by_place(222)
    place_info3 = get_info_by_place(333)

    assert place_info1['place_id'] == 111
    assert place_info1['name'] == 'name111'
    assert place_info1['address'] == 'address111'
    assert place_info1['address_comment'] is None
    assert place_info1['updated_address_at'] is None

    assert place_info2['place_id'] == 222
    assert place_info2['name'] == 'name222'
    assert place_info2['address'] == 'address222'
    assert place_info2['address_comment'] == 'comment222'
    assert place_info2['updated_address_at'] is None

    assert place_info3['place_id'] == 333
    assert place_info3['name'] == 'name333'
    assert place_info3['address'] == 'address333'
    assert place_info3['address_comment'] is None
    assert place_info3['updated_address_at'] is None


async def test_upsert_info_204(taxi_eats_restapp_places, get_info_by_place):

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-info?place_id',
        json={
            'places': [
                {
                    'place_id': 111,
                    'name': 'name111',
                    'address_full': 'address111',
                },
            ],
        },
    )

    assert response.status_code == 204

    place_info1 = get_info_by_place(111)

    assert place_info1['place_id'] == 111
    assert place_info1['name'] == 'name111'
    assert place_info1['address'] == 'address111'
    assert place_info1['address_comment'] is None
    assert place_info1['updated_address_at'] is None

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-info?place_id',
        json={
            'places': [
                {
                    'place_id': 111,
                    'name': 'name 111',
                    'address_full': 'address111',
                    'address_comment': 'comment111',
                },
            ],
        },
    )

    assert response.status_code == 204

    place_info1 = get_info_by_place(111)

    assert place_info1['place_id'] == 111
    assert place_info1['name'] == 'name 111'
    assert place_info1['address'] == 'address111'
    assert place_info1['address_comment'] == 'comment111'
    assert place_info1['updated_address_at'] is None


async def test_update_address_204(
        taxi_eats_restapp_places, get_info_by_place, get_entrance_by_place,
):

    place_info1 = get_info_by_place(222)

    assert place_info1['place_id'] == 222
    assert place_info1['permalink'] == '222'
    assert place_info1['name'] == 'name222'
    assert place_info1['address'] == 'address222'
    assert place_info1['address_comment'] is None
    assert place_info1['updated_address_at'] is None

    entrances = get_entrance_by_place(222)
    assert len(entrances) == 2
    assert entrances[0]['status'] == 'approved'
    assert entrances[1]['status'] == 'approved'

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-info?place_id',
        json={
            'places': [
                {
                    'place_id': 222,
                    'name': 'name 222',
                    'address_full': 'address 222',
                    'address_comment': 'comment222',
                },
            ],
        },
    )

    assert response.status_code == 204

    place_info1 = get_info_by_place(222)

    assert place_info1['place_id'] == 222
    assert place_info1['permalink'] is None
    assert place_info1['name'] == 'name 222'
    assert place_info1['address'] == 'address 222'
    assert place_info1['address_comment'] == 'comment222'
    assert place_info1['updated_address_at']

    entrances = get_entrance_by_place(222)
    assert len(entrances) == 2
    assert entrances[0]['status'] == 'deleted'
    assert entrances[1]['status'] == 'deleted'
