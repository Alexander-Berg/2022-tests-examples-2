async def test_not_found(taxi_driver_profiles):
    response = await taxi_driver_profiles.put(
        '/v1/driver/login-info',
        params={
            'consumer': 'testsuite',
            'park_id': 'nonexistent',
            'driver_profile_id': 'nonexistent',
        },
        json={
            'taximeter_version': '9.22 (2222)',
            'taximeter_version_type': 'taximeter',
            'taximeter_platform': 'android',
            'taximeter_brand': 'yandex',
            'imei': 'imei',
            'device_model': 'device_model',
            'network_operator': 'network_operator',
            'metrica_device_id': 'metrica_device_id',
            'metrica_uuid': 'metrica_uuid',
            'locale': 'ru',
        },
    )

    assert response.status == 404
    assert response.json() == {}


async def test_ok(taxi_driver_profiles, mongodb):
    old_mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )

    response = await taxi_driver_profiles.put(
        '/v1/driver/login-info',
        params={
            'consumer': 'testsuite',
            'park_id': 'p1',
            'driver_profile_id': 'd1',
        },
        json={
            'taximeter_version': '9.22 (2222)',
            'taximeter_version_type': 'taximeter',
            'taximeter_platform': 'android',
            'taximeter_brand': 'yandex',
            'imei': 'imei',
            'device_model': 'device_model',
            'network_operator': 'network_operator',
            'metrica_device_id': 'metrica_device_id',
            'metrica_uuid': 'metrica_uuid',
            'locale': 'ru',
        },
    )

    assert response.status == 200
    assert response.json() == {}

    mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )

    assert mongo_entry['taximeter_version'] == '9.22 (2222)'
    assert mongo_entry['taximeter_version_type'] == 'taximeter'
    assert mongo_entry['taximeter_platform'] == 'android'
    assert mongo_entry['taximeter_brand'] == 'yandex'
    assert mongo_entry['imei'] == 'imei'
    assert mongo_entry['device_model'] == 'device_model'
    assert mongo_entry['network_operator'] == 'network_operator'
    assert mongo_entry['metrica_device_id'] == 'metrica_device_id'
    assert mongo_entry['metrica_uuid'] == 'metrica_uuid'
    assert mongo_entry['locale'] == 'ru'

    assert mongo_entry['modified_date'] != old_mongo_entry['modified_date']
    assert mongo_entry['updated_ts'] != old_mongo_entry['updated_ts']
    assert (
        mongo_entry['last_login_at_ts'] != old_mongo_entry['last_login_at_ts']
    )
