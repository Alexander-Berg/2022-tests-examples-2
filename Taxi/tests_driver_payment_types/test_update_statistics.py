import pytest


async def test_update_statistics(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    assert 'cash' not in mongo_doc
    assert 'order_ids' not in mongo_doc
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order1',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    updated_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    assert updated_doc['cash'] == {
        'travel_distance': 20.0,
        'travel_time': 10.0,
    }
    assert updated_doc['order_ids'] == ['order1']


async def test_update_online(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid5'})
    assert 'cash' not in mongo_doc
    assert 'order_ids' not in mongo_doc
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park3',
            'driver_profile_id': 'driver2',
            'order': {
                'id': 'order1',
                'nearest_zone': 'moscow',
                'payment_type': 'googlepay',
                'travel_time': 1000,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    updated_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid5'})
    assert updated_doc['online'] == {
        'travel_distance': 20.0,
        'travel_time': 1000.0,
    }
    assert updated_doc['order_ids'] == ['order1']


async def test_add_order(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid2'})
    assert len(mongo_doc['order_ids']) == 1
    assert mongo_doc['cash'] == {'travel_distance': 20.0, 'travel_time': 10.0}
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park2',
            'driver_profile_id': 'driver2',
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    updated_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid2'})
    assert updated_doc['cash'] == {
        'travel_distance': 40.0,
        'travel_time': 20.0,
    }
    assert len(updated_doc['order_ids']) == 2


async def test_new_driver(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_4'},
    )
    assert not mongo_doc
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park3',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    updated_doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_4'},
    )
    assert not updated_doc


async def test_add_order_over_limit(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid3'})
    assert len(mongo_doc['order_ids']) == 5
    assert mongo_doc['order_ids'] != 'order2'
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park2',
            'driver_profile_id': 'driver3',
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    updated_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid3'})
    assert len(updated_doc['order_ids']) == 5
    assert updated_doc['order_ids'][-1] == 'order2'


async def test_different_payment_type(taxi_driver_payment_types, mongodb):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': 'online',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    new_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    assert mongo_doc == new_doc


@pytest.mark.parametrize(
    'driver_id,payment_type,expected_code', [['some_driver_id', 'cash', 404]],
)
async def test_error(
        taxi_driver_payment_types, driver_id, payment_type, expected_code,
):
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park1',
            'driver_profile_id': driver_id,
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': payment_type,
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('enabled_count_limit_exceed', [True, False])
@pytest.mark.config(
    DRIVER_PAYMENT_TYPE_TRAVEL_LIMITS={
        '__default__': {
            'time': {'cash': 50, 'online': 50},
            'distance': {'cash': 50, 'online': 50},
        },
        'countries': {},
        'zones': {},
    },
)
async def test_travel_limit_exceed(
        taxi_driver_payment_types,
        mongodb,
        taxi_config,
        enabled_count_limit_exceed,
):
    if enabled_count_limit_exceed:
        taxi_config.set_values(dict(DRIVER_PAYMENT_TYPE_MAX_ENABLED_COUNT=3))
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order2',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 100,
                'travel_distance': 100,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    new_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    assert new_doc['payment_type'] == 'none'
    assert new_doc['cash'] == {'travel_time': 0, 'travel_distance': 0}
    if enabled_count_limit_exceed:
        assert not new_doc['enabled']


@pytest.mark.config(
    DRIVER_PAYMENT_TYPE_TRAVEL_LIMITS={
        '__default__': {
            'time': {'cash': 1000, 'online': 1000},
            'distance': {'cash': 1000, 'online': 1000},
        },
        'countries': {
            'rou': {
                'time': {'cash': 50, 'online': 50},
                'distance': {'cash': 50, 'online': 50},
            },
        },
        'zones': {},
    },
)
async def test_country_settings(taxi_driver_payment_types, parks, mongodb):
    parks.set_park_country('park2', 'rou')
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park2',
            'driver_profile_id': 'driver2',
            'order': {
                'id': 'order2',
                'payment_type': 'cash',
                'nearest_zone': 'moscow',
                'travel_time': 100,
                'travel_distance': 100,
            },
        },
    )
    assert response.json() == {}
    new_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid2'})
    assert new_doc['cash'] == {'travel_time': 0, 'travel_distance': 0}


@pytest.mark.config(
    DRIVER_PAYMENT_TYPE_UPDATE_STATISTICS_MODE_SETTINGS={
        'mode_types_disable': ['driver-fix'],
        'request_driver_mode_subscription': True,
    },
)
async def test_driver_modes_config(
        taxi_driver_payment_types, mongodb, driver_mode_subscription,
):
    mongo_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    driver_mode_subscription.set_mode_type('driver-fix')
    response = await taxi_driver_payment_types.post(
        'service/v1/update-statistics',
        json={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order1',
                'nearest_zone': 'moscow',
                'payment_type': 'cash',
                'travel_time': 10,
                'travel_distance': 20,
            },
        },
    )
    assert response.status_code == 200
    updated_doc = mongodb.driver_payment_type.find_one({'_id': 'some_uuid'})
    assert mongo_doc == updated_doc
