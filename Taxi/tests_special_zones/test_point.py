import pytest

ENDPOINT = 'zones/items/point'


async def _test_accessing_non_existing_zones_and_points_combinations(
        taxi_special_zones, mongodb,
):
    # Get nonexistent point
    response = await taxi_special_zones.get(
        f'{ENDPOINT}?zone_id=luzha_high&point_id=p1003',
    )
    assert response.status_code == 404

    # Get from nonexistent zone
    response = await taxi_special_zones.get(
        f'{ENDPOINT}?zone_id=luzha_highest&point_id=p1',
    )
    assert response.status_code == 404

    # Delete from nonexistent zone
    response = await taxi_special_zones.delete(
        ENDPOINT, json={'zone_id': 'luzha_highest', 'point_id': 'p1'},
    )
    assert response.status_code == 404

    # Put point to nonexistent zone
    response = await taxi_special_zones.put(
        ENDPOINT,
        json={
            'id': {'zone_id': 'luzha_highest', 'point_id': 'p0'},
            'point': {'geopoint': [0, 0], 'id': 'id'},
        },
    )

    assert response.status_code == 404

    # Put nonexistent point
    response = await taxi_special_zones.put(
        ENDPOINT,
        json={
            'id': {'zone_id': 'luzha', 'point_id': 'p200'},
            'point': {'geopoint': [0, 0], 'id': 'id'},
        },
    )
    assert response.status_code == 404

    # Post point to nonexistent zone
    response = await taxi_special_zones.post(
        ENDPOINT,
        json={
            'zone_id': 'nonexistent',
            'point_type': 'any',
            'point': {'geopoint': [0, 0], 'id': 'id'},
        },
    )
    assert response.status_code == 404


async def _test_point_source_type_creation_cycle(taxi_special_zones, mongodb):
    # Post source point
    response_json = {
        'zone_id': 'luzha',
        'point': {
            'geopoint': [37.58935025973962, 55.73423185102005],
            'id': 'source_point_id',
            'name': 'point_name',
            'alias': 'Самый худший пикаппойнт',
            'choice_id': 'badge_id',
            'enabled': True,
        },
        'point_type': 'a',
    }

    response = await taxi_special_zones.post(ENDPOINT, json=response_json)

    assert response.status_code == 200
    assert response.json() == {
        'point_id': 'source_point_id',
        'zone_id': 'luzha',
    }
    assert any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'source_points'
        ]
    )

    # Put point with removing point params
    del response_json['point']['alias']
    del response_json['point']['choice_id']

    response = await taxi_special_zones.put(
        ENDPOINT,
        json={
            'id': {'point_id': 'source_point_id', 'zone_id': 'luzha'},
            'point': response_json['point'],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'point_id': 'source_point_id',
        'zone_id': 'luzha',
    }
    assert any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'source_points'
        ]
    )

    # Get source point
    response = await taxi_special_zones.get(
        f'{ENDPOINT}?zone_id=luzha&point_id=source_point_id',
    )

    assert response.status_code == 200
    assert response.json() == response_json['point']

    # Remove source point from zone
    response = await taxi_special_zones.delete(
        ENDPOINT, json={'point_id': 'source_point_id', 'zone_id': 'luzha'},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    assert not any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'source_points'
        ]
    )


async def _test_point_destination_type_creation_cycle(
        taxi_special_zones, mongodb,
):
    # Post destination point
    response_json = {
        'zone_id': 'luzha',
        'point': {
            'geopoint': [37.58935025973962, 55.73423185102005],
            'id': 'destination_point_id',
            'alias': 'Самый худший пикаппойнт',
            'choice_id': 'badge_id',
            'enabled': True,
        },
        'point_type': 'b',
    }

    response = await taxi_special_zones.post(ENDPOINT, json=response_json)

    assert response.status_code == 200
    assert response.json() == {
        'point_id': 'destination_point_id',
        'zone_id': 'luzha',
    }
    assert any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'destination_points'
        ]
    )

    # Put point with adding point params
    response_json['name'] = 'point_name'

    response = await taxi_special_zones.put(
        ENDPOINT,
        json={
            'id': {'point_id': 'destination_point_id', 'zone_id': 'luzha'},
            'point': response_json['point'],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'point_id': 'destination_point_id',
        'zone_id': 'luzha',
    }
    assert any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'destination_points'
        ]
    )

    # Get destination point
    response = await taxi_special_zones.get(
        f'{ENDPOINT}?zone_id=luzha&point_id=destination_point_id',
    )

    assert response.status_code == 200
    assert response.json() == response_json['point']

    # Remove destination point from zone
    response = await taxi_special_zones.delete(
        ENDPOINT,
        json={'point_id': 'destination_point_id', 'zone_id': 'luzha'},
    )

    assert response.status_code == 200
    assert not any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha')[
            'destination_points'
        ]
    )


async def _test_point_universal_type_creation_cycle(
        taxi_special_zones, mongodb,
):
    # Post universal point to zone that does not have universal type
    response_json = {
        'zone_id': 'luzha_high',
        'point': {
            'geopoint': [37.58935025973962, 55.73423185102005],
            'id': 'universal_point_id',
            'alias': 'Самый худший пикаппойнт',
            'choice_id': 'badge_id',
            'enabled': True,
        },
        'point_type': 'any',
    }

    response = await taxi_special_zones.post(ENDPOINT, json=response_json)

    assert response.status_code == 200
    assert response.json() == {
        'point_id': 'universal_point_id',
        'zone_id': 'luzha_high',
    }
    assert any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha_high')[
            'universal_points'
        ]
    )

    # Get universal point
    response = await taxi_special_zones.get(
        f'{ENDPOINT}?zone_id=luzha_high&point_id=universal_point_id',
    )

    assert response.status_code == 200
    assert response.json() == response_json['point']

    # Remove universal point from zone
    response = await taxi_special_zones.delete(
        ENDPOINT,
        json={'point_id': 'universal_point_id', 'zone_id': 'luzha_high'},
    )

    assert response.status_code == 200
    assert not any(
        point == response_json['point']
        for point in mongodb.pickup_zone_items.find_one('luzha_high')[
            'universal_points'
        ]
    )


async def _test_accessing_zone_not_stated_in_allowed_zone_types_config(
        taxi_special_zones, mongodb,
):
    # Try to post point to prohibited zone
    response_json = {
        'zone_id': 'non-sdc-zone',
        'point': {
            'geopoint': [37.58935025973962, 55.73423185102005],
            'id': 'source_point_id',
            'name': 'point_name',
            'alias': 'Самый худший пикаппойнт',
            'choice_id': 'badge_id',
        },
        'point_type': 'a',
    }

    response = await taxi_special_zones.post(ENDPOINT, json=response_json)

    assert response.status_code == 403

    # Try to put point to prohibited zone
    del response_json['point']['alias']
    del response_json['point']['choice_id']

    response = await taxi_special_zones.put(
        ENDPOINT,
        json={
            'id': {'point_id': 'source_point_id', 'zone_id': 'non-sdc-zone'},
            'point': response_json['point'],
        },
    )

    assert response.status_code == 403

    # Try to remove point from prohibited zone
    response = await taxi_special_zones.delete(
        ENDPOINT,
        json={'point_id': 'source_point_id', 'zone_id': 'non-sdc-zone'},
    )

    assert response.status_code == 403


@pytest.mark.filldb(pickup_zone_items='point')
async def test_point_full_creation_cycle(taxi_special_zones, mongodb):
    await _test_accessing_non_existing_zones_and_points_combinations(
        taxi_special_zones, mongodb,
    )
    await _test_accessing_zone_not_stated_in_allowed_zone_types_config(
        taxi_special_zones, mongodb,
    )
    await _test_point_source_type_creation_cycle(taxi_special_zones, mongodb)
    await _test_point_destination_type_creation_cycle(
        taxi_special_zones, mongodb,
    )
    await _test_point_universal_type_creation_cycle(
        taxi_special_zones, mongodb,
    )
