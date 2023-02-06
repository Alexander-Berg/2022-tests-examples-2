import datetime
import re

import pytest


@pytest.mark.parametrize(
    'time_now, answer',
    [
        (
            datetime.datetime(2018, 7, 11, 7, 00),
            ['dates_range1', 'dates_range2'],
        ),
        (datetime.datetime(2018, 7, 1, 7, 00), []),
        (datetime.datetime(2018, 9, 1, 7, 00), []),
        (datetime.datetime(2018, 7, 10, 13, 00), ['dates_range1']),
        (datetime.datetime(2018, 7, 15, 17, 00), ['dates_range2']),
        (datetime.datetime(2018, 8, 12, 17, 00), ['schedule1', 'schedule2']),
        (datetime.datetime(2018, 8, 12, 12, 00), ['schedule1']),
        (datetime.datetime(2018, 8, 12, 19, 00), ['schedule2']),
        (datetime.datetime(2018, 8, 13, 17, 00), ['schedule1', 'schedule2']),
        (datetime.datetime(2018, 8, 13, 12, 00), ['schedule1']),
        (datetime.datetime(2018, 8, 13, 19, 00), ['schedule2']),
        (datetime.datetime(2018, 8, 17, 17, 00), []),
        (datetime.datetime(2018, 8, 17, 12, 00), []),
        (datetime.datetime(2018, 8, 17, 19, 00), []),
        (datetime.datetime(2020, 10, 9, 23, 00), []),
        (datetime.datetime(2020, 10, 10, 1, 23), []),
        (datetime.datetime(2020, 10, 10, 23, 00), ['schedule3']),
        (datetime.datetime(2020, 10, 19, 22, 00), ['schedule3']),
        (datetime.datetime(2020, 10, 20, 1, 00), ['schedule3']),
        (datetime.datetime(2020, 10, 21, 3, 5), ['schedule3']),
        (datetime.datetime(2020, 10, 21, 9, 5), []),
    ],
)
async def test_zones_items_schedule(
        taxi_special_zones, mongodb, mocked_time, time_now, answer,
):
    mocked_time.set(time_now)
    await taxi_special_zones.invalidate_caches()
    answer = ['persistent'] + answer
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
    )

    assert response.status_code == 200
    zones = map(lambda x: x['id'], response.json()['zones'])
    assert sorted(zones) == sorted(answer)


@pytest.mark.parametrize(
    'item_json', ['zones_item.json', 'zones_item_with_empty_schedule.json'],
)
async def test_zones_items_create(
        item_json, taxi_special_zones, mongodb, load_json,
):
    zone_item = load_json(item_json)
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'luzhniki_forever'

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 200
    assert response.json() == zone_item
    # Zone and all its' points should be enabled by default.
    assert response.json()['enabled']
    assert response.json()['destination_points'][0]['enabled']

    response = await taxi_special_zones.get('zones/items?id=luzhniki_forever')
    assert response.status_code == 200
    assert response.json() == zone_item

    # Disable zone and a point in zone and test getting disabled values.
    zone_item['enabled'] = zone_item['destination_points'][0][
        'enabled'
    ] = False
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'luzhniki_disabled'

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 200
    assert response.json() == zone_item
    # Now its' points should be disabled.
    assert not response.json()['enabled']
    assert not response.json()['destination_points'][0]['enabled']

    response = await taxi_special_zones.get(
        f'zones/items?id={zone_item_post["id"]}',
    )
    assert response.status_code == 200
    assert response.json() == zone_item


async def test_zones_items_delete(taxi_special_zones, mongodb, load_json):
    zone_item = load_json('zones_item.json')
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'to_delete'

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.json() == zone_item

    response = await taxi_special_zones.delete('zones/items?id=to_delete')
    assert response.status_code == 200

    doc = mongodb.pickup_zone_items.find_one('to_delete')
    assert doc is None

    response = await taxi_special_zones.delete('zones/items?id=not_exists')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Couldn\'t find zone item with id \'not_exists\'',
    }


async def test_zones_items_edit(taxi_special_zones, mongodb, load_json):
    zone_item = load_json('zones_item.json')
    zone_item_edit = load_json('zones_item_edit.json')
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'to_change'

    response = await taxi_special_zones.put(
        'zones/items?id=to_change', zone_item_edit,
    )
    assert response.status_code == 404

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 200
    assert response.json() == zone_item

    response = await taxi_special_zones.put(
        'zones/items?id=to_change', zone_item_edit,
    )
    assert response.status_code == 200
    assert response.json() == zone_item_edit

    zone_item_db = zone_item_edit.copy()
    zone_item_db['_id'] = 'to_change'
    doc = mongodb.pickup_zone_items.find_one({'_id': 'to_change'})
    assert doc is not None
    assert doc == zone_item_db

    response = await taxi_special_zones.get('zones/items?id=to_change')
    assert response.status_code == 200
    assert response.json() == zone_item_edit

    zone_item_edit.pop('name_tanker_key')
    response = await taxi_special_zones.put(
        'zones/items?id=to_change', zone_item_edit,
    )
    assert response.status_code == 200
    assert response.json() == zone_item_edit

    zone_item_edit.pop('schedule')
    response = await taxi_special_zones.put(
        'zones/items?id=to_change', zone_item_edit,
    )
    assert response.status_code == 200
    assert response.json() == zone_item_edit

    response = await taxi_special_zones.get('zones/items?id=to_change')
    assert response.status_code == 200
    assert response.json() == zone_item_edit

    response = await taxi_special_zones.put(
        'zones/items?id=not_exists', zone_item_edit,
    )
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Couldn\'t find zone item with id \'not_exists\'',
    }


async def test_zones_items_bad_request(taxi_special_zones, mongodb, load_json):
    zone_item = load_json('zones_item.json')

    zone_item_post = zone_item.copy()
    zone_item_post.pop('source_points')
    zone_item_post['id'] = 'bad'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 400

    zone_item_post = zone_item.copy()
    zone_item_post.pop('destination_points')
    zone_item_post['id'] = 'bad'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 400

    zone_item_post = zone_item.copy()
    zone_item_post.pop('name_tanker_key')
    zone_item_post['id'] = 'bad'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 200
    assert 'name_tanker_key' not in response.json()

    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'ok'
    zone_item_post['source_points'] = []
    zone_item_post['destination_points'] = []
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 200
    json = response.json()
    json['source_points'] = []
    json['destination_points'] = []

    zone_item_post = zone_item.copy()
    zone_item_post['type'] = 'bad_type'
    zone_item_post['id'] = 'new_id'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 409

    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'dates_range1'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 409
    assert response.json() == {
        'message': 'Zone item with id \'dates_range1\' already exists',
    }

    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'bad/id'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 409

    zone_item_post = load_json('zones_item.json')
    zone_item_post['id'] = 'new_zone_id'
    good_name_tanker_key = zone_item_post['name_tanker_key']
    zone_item_post['name_tanker_key'] = 'bad_tanker_key'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 409

    zone_item_post['name_tanker_key'] = good_name_tanker_key
    zone_item_post['source_points'][0]['name'] = 'bad_tanker_key'
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 409

    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'new_id'
    bad_schedule_range = {
        'type': 'dates_range',
        'time_zone': 'Europe/Moscow',
        'start': '2018-09-26T11:11:00+03:00',
        'end': '2018-09-28T22:22:00+03:00',
    }
    zone_item_post['schedule']['ranges'].append(bad_schedule_range)
    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'create_new, bad_geometry_json, expected_err_message_re',
    [
        (
            True,
            'zones_item_bad_geometry1.json',
            'Zone item bad geometry - self-intersection',
        ),
        (
            False,
            'zones_item_bad_geometry1.json',
            'Zone item bad geometry - self-intersection',
        ),
        (
            True,
            'zones_item_bad_geometry2.json',
            'Zone item bad geometry - inner ring isn\'t covered by outer',
        ),
        (
            False,
            'zones_item_bad_geometry2.json',
            'Zone item bad geometry - inner ring isn\'t covered by outer',
        ),
        (
            True,
            'zones_item_bad_geometry3.json',
            'Zone item bad geometry - inner ring isn\'t covered by outer',
        ),
        (
            False,
            'zones_item_bad_geometry3.json',
            'Zone item bad geometry - inner ring isn\'t covered by outer',
        ),
        (
            True,
            'zones_item_bad_geometry4.json',
            'Zone item bad geometry - inner rings intersect each other',
        ),
        (
            False,
            'zones_item_bad_geometry4.json',
            'Zone item bad geometry - inner rings intersect each other',
        ),
        (
            True,
            'zones_item_bad_geometry5.json',
            'Zone item bad geometry - inner ring intersects other outer',
        ),
        (
            False,
            'zones_item_bad_geometry5.json',
            'Zone item bad geometry - inner ring intersects other outer',
        ),
        (
            True,
            'zones_item_bad_geometry6.json',
            'Zone item bad geometry - outer rings intersect each other',
        ),
        (
            False,
            'zones_item_bad_geometry6.json',
            'Zone item bad geometry - outer rings intersect each other',
        ),
        (True, 'zones_item_good_geometry.json', ''),
        (False, 'zones_item_good_geometry.json', ''),
    ],
)
async def test_zones_items_check_geometry(
        create_new,
        bad_geometry_json,
        expected_err_message_re,
        taxi_special_zones,
        load_json,
):
    zone_item = load_json(bad_geometry_json)
    zone_item['id'] = 'just_id'

    if create_new:
        response = await taxi_special_zones.post('zones/items', zone_item)
    else:
        response = await taxi_special_zones.put(
            'zones/items?id=just_id', zone_item,
        )

    if not expected_err_message_re:
        if create_new:
            assert response.status_code == 200
        else:
            assert response.status_code == 404
    else:
        assert response.status_code == 400
        resp_json = response.json()
        assert re.fullmatch(expected_err_message_re, resp_json['message'])


async def test_zones_items_check_geometry_correction(
        taxi_special_zones, load_json,
):
    zone_item = load_json('zones_item_before_correction.json')
    zone_item['id'] = 'just_id'

    response = await taxi_special_zones.post('zones/items', zone_item)

    assert response.status_code == 200
    assert response.json() == load_json('zones_item.json')


async def test_zones_items_tariffs_in_pp(
        taxi_special_zones, mongodb, load_json,
):
    def _pop_empty_supported_tariffs(item):
        for point in item['source_points']:
            if 'supported_tariffs' in point and not point['supported_tariffs']:
                point.pop('supported_tariffs')

    zone_item = load_json('zones_item_tariffs_in_pp.json')
    zone_item['id'] = 'test_zone'

    response = await taxi_special_zones.post('zones/items', zone_item)

    zone_item.pop('id')
    _pop_empty_supported_tariffs(zone_item)

    assert response.status_code == 200
    assert response.json() == zone_item

    response = await taxi_special_zones.get('zones/items?id=test_zone')
    assert response.status_code == 200
    assert response.json() == zone_item

    zone_item['source_points'][0]['supported_tariffs'] = []
    zone_item['source_points'][1]['supported_tariffs'] = ['cargo']
    zone_item['source_points'].append(
        {
            'geopoint': [37.58935025973962, 55.73423185102006],
            'id': 'fbb68f7f0391464092812bcef420a829_5',
            'supported_tariffs': ['econom'],
            'enabled': True,
        },
    )

    response = await taxi_special_zones.put(
        'zones/items?id=test_zone', zone_item,
    )

    _pop_empty_supported_tariffs(zone_item)
    assert response.status_code == 200
    assert response.json() == zone_item

    response = await taxi_special_zones.get('zones/items?id=test_zone')
    assert response.status_code == 200
    assert response.json() == zone_item

    zone_item['source_points'][1].pop('supported_tariffs')

    response = await taxi_special_zones.put(
        'zones/items?id=test_zone', zone_item,
    )
    assert response.status_code == 200
    assert response.json() == zone_item

    response = await taxi_special_zones.get('zones/items?id=test_zone')
    assert response.status_code == 200
    assert response.json() == zone_item


@pytest.mark.config(SPECIAL_ZONES_BLOCK_DB=True)
async def test_zones_blocked_db(taxi_special_zones, mongodb, load_json):
    zone_item = load_json('zones_item.json')
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'luzhniki_forever'

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 500

    response = await taxi_special_zones.get('zones/items?id=luzhniki_forever')
    assert response.status_code == 404

    response = await taxi_special_zones.put(
        'zones/items?id=luzhniki_forever', zone_item_post,
    )
    assert response.status_code == 500

    response = await taxi_special_zones.delete(
        'zones/items?id=luzhniki_forever',
    )
    assert response.status_code == 500


@pytest.mark.config(
    SPECIAL_ZONES_POINT_HANDLE_ALLOWED_ZONE_TYPES={'types': ['fan_zone']},
)
async def test_zones_allowed_only_in_point_handle(
        taxi_special_zones, mongodb, load_json,
):
    zone_item = load_json('zones_item.json')
    zone_item_post = zone_item.copy()
    zone_item_post['id'] = 'luzhniki_forever'

    response = await taxi_special_zones.post('zones/items', zone_item_post)
    assert response.status_code == 403

    response = await taxi_special_zones.get('zones/items?id=luzhniki_forever')
    assert response.status_code == 404

    response = await taxi_special_zones.put(
        'zones/items?id=dates_range1', zone_item_post,
    )
    assert response.status_code == 403

    response = await taxi_special_zones.delete('zones/items?id=dates_range1')
    assert response.status_code == 403
