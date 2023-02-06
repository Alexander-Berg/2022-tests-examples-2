import json

import pytest


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_add_pin(taxi_pin_storage, redis_store, load_json):
    # invalid body
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(42),
    )
    assert response.status_code == 400

    # missing pin
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps({}),
    )
    assert response.status_code == 400

    # invalid pin
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps({'pin': 42}),
    )
    assert response.status_code == 400

    # missing experiment_by_id
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    # 'experiment_by_id': {},
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid experiments
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': 42,
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid order_id (optional)
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    'order_id': 42,
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # missing phone_id
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    # 'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid phone_id
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 42,
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # missing point
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    # 'point': {'lon':12.3,'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid point
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid trip (optional)
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    'trip': 42,
                    'type': 'test_type',
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # missing user_id
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    # 'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid user_id
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 42,
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # missing classes
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    # 'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 400

    # invalid classes
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'type': 'test_type',
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': 42,
                },
            },
        ),
    )
    assert response.status_code == 400

    # insert
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    # 'order_id': 'test_order_id', (optional)
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    # 'trip': { (optional)
                    #     'distance': 1.0,
                    #     'point_b': {'lon': 12.3, 'lat': 45.6},
                    #     'time': 2.0,
                    # },
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'classes': [],
                },
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data

    assert redis_store.keys() == [b'1552003200']
    pins_in_redis = redis_store.lrange('1552003200', 0, -1)
    assert len(pins_in_redis) == 1
    pin_from_redis = json.loads(pins_in_redis[0])
    del pin_from_redis['pin']['trace_id']
    assert pin_from_redis == load_json('pin.json')


@pytest.mark.config(
    PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0},
    PIN_STORAGE_LOGBROKER={
        'tags_excluded': [],
        'tags_included': [],
        'timeout': 500,
    },
)
async def test_add_pin_logbroker(taxi_pin_storage, testpoint, load_json):
    actual_request = {}

    @testpoint('yt-logger')
    def _logbroker(request):
        nonlocal actual_request
        actual_request = request

    pin = {
        'experiments': [],
        # 'order_id': 'test_order_id', (optional)
        'personal_phone_id': 'test_phone_id',
        'point': {'lon': 12.3, 'lat': 45.6},
        # 'trip': { (optional)
        #     'distance': 1.0,
        #     'point_b': {'lon': 12.3, 'lat': 45.6},
        #     'time': 2.0,
        # },
        'user_id': 'test_user_id',
        'user_layer': 'default',
        'classes': [],
        'extra': {'is_lightweight_routestats': True},
    }
    response = await taxi_pin_storage.put(
        'v1/add_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps({'pin': pin}),
    )
    assert response.status_code == 200
    data = response.json()
    data_request = actual_request
    expected = pin
    expected['is_fake'] = False
    # user_layer from request is ignored - only from calculation
    del expected['user_layer']

    # randomized trace_id
    assert 'trace_id' in data_request['pin']
    del data_request['pin']['trace_id']

    assert 'timestamp' in data
    assert (
        data_request
        and data_request['pin'] == expected
        and 'timestamp' in data_request
    )
