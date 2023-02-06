import pytest


async def test_zones_types(taxi_special_zones, mongodb):
    response = await taxi_special_zones.get('zones/types/list')
    assert response.status_code == 200

    docs = mongodb.pickup_zone_types.find({'deleted': {'$ne': True}})
    ids = [doc['_id'] for doc in docs]
    assert response.json() == {'zone_types': ids}


async def test_zones_types_get_one(taxi_special_zones, load_json):
    response = await taxi_special_zones.get('zones/types?id=fan_zone')
    expected_response = load_json('fan_zone.json')
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_zones_types_get_not_existing(taxi_special_zones):
    response = await taxi_special_zones.get('zones/types?id=not_exiting')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Couldn\'t find zone_type with id \'not_exiting\'',
    }


async def test_zones_types_create_existing(taxi_special_zones, load_json):
    existing = load_json('new_zone.json')
    existing['id'] = 'fan_zone'
    response = await taxi_special_zones.post('zones/types', existing)
    assert response.status_code == 409
    assert response.json() == {
        'message': 'Zone type with id \'fan_zone\' already exists',
    }


async def test_zones_types_create_empty(taxi_special_zones):
    response = await taxi_special_zones.post('zones/types', {})
    assert response.status_code == 400


async def test_zones_types_create_one(taxi_special_zones, load_json):
    new_zone = load_json('new_zone.json')
    response = await taxi_special_zones.post('zones/types', new_zone)
    assert response.status_code == 200
    assert response.json() == new_zone


async def test_zones_types_change_one(taxi_special_zones, mongodb, load_json):
    zone = load_json('to_change.json')
    response = await taxi_special_zones.put('zones/types?id=to_change', zone)
    assert response.status_code == 200
    assert response.json() == zone

    doc = mongodb.pickup_zone_types.find_one({'_id': 'to_change'})
    assert doc['options']['zoom_range'] == zone['options']['zoom_range']
    assert doc['options']['visible'] == zone['options']['visible']


async def test_zones_types_change_invalid(
        taxi_special_zones, mongodb, load_json,
):
    zone = load_json('to_change.json')
    zone['properties']['has_custom_points'] = False
    response = await taxi_special_zones.put('zones/types?id=to_change', zone)
    assert response.status_code == 400


async def test_zones_types_change_not_existing(taxi_special_zones, load_json):
    zone = load_json('to_change.json')
    response = await taxi_special_zones.put(
        'zones/types?id=not_existing', zone,
    )
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Couldn\'t find zone_type with id \'not_existing\'',
    }


async def test_zones_types_delete_one(taxi_special_zones, mongodb):
    response = await taxi_special_zones.delete('zones/types?id=to_delete')
    assert response.status_code == 200
    doc = mongodb.pickup_zone_types.find_one('to_delete')
    assert doc['deleted']


async def test_zones_types_delete_not_existing(taxi_special_zones, mongodb):
    response = await taxi_special_zones.delete('zones/types?id=not_existing')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Couldn\'t find zone_type with id \'not_existing\'',
    }


@pytest.mark.filldb(pickup_zone_types='custom_alerts')
async def test_zones_types_get_with_custom_alerts(
        taxi_special_zones, load_json,
):
    response = await taxi_special_zones.get('zones/types?id=fan_zone')
    expected_response = load_json('fan_zone_custom_alerts.json')
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_zones_types_create_custom_alerts(taxi_special_zones, load_json):
    new_zone = load_json('new_zone_custom_alerts.json')
    response = await taxi_special_zones.post('zones/types', new_zone)
    assert response.status_code == 200
    assert response.json() == new_zone


async def test_zones_types_change_custom_alerts(
        taxi_special_zones, mongodb, load_json,
):
    zone = load_json('to_change_custom_alerts.json')
    response = await taxi_special_zones.put('zones/types?id=to_change', zone)
    assert response.status_code == 200
    assert response.json() == zone

    doc = mongodb.pickup_zone_types.find_one({'_id': 'to_change'})
    assert doc['options']['zoom_range'] == zone['options']['zoom_range']
    assert doc['options']['visible'] == zone['options']['visible']
    assert doc['options'] == zone['options']
    assert doc['properties'] == zone['properties']


@pytest.mark.parametrize('zone_name', ['to_change', 'to_change_with_priority'])
@pytest.mark.parametrize('change_priority', [None, 1020])
async def test_zones_types_change_one_with_priority(
        taxi_special_zones, mongodb, zone_name, change_priority, load_json,
):
    expected_priority = change_priority if change_priority else 1000
    zone = load_json('to_change.json')
    zone['properties']['priority'] = change_priority
    response = await taxi_special_zones.put(
        'zones/types?id=' + zone_name, zone,
    )
    assert response.status_code == 200
    zone['properties']['priority'] = expected_priority
    assert response.json() == zone

    doc = mongodb.pickup_zone_types.find_one({'_id': zone_name})
    assert doc['properties']['priority'] == expected_priority
    assert doc['options'] == zone['options']
    assert doc['properties'] == zone['properties']


@pytest.mark.config(SPECIAL_ZONES_BLOCK_DB=True)
async def test_zones_blocked_db(taxi_special_zones, load_json):
    zone = load_json('new_zone.json')
    zone['id'] = 'fan_zone_100'

    response = await taxi_special_zones.post('zones/types', zone)
    assert response.status_code == 500

    response = await taxi_special_zones.get('zones/types?id=fan_zone_100')
    assert response.status_code == 404

    response = await taxi_special_zones.put('zones/types?id=fan_zone', zone)
    assert response.status_code == 500

    response = await taxi_special_zones.delete('zones/types?id=fan_zone')
    assert response.status_code == 500
