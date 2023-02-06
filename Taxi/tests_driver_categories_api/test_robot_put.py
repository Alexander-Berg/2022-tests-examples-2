import json

import pytest

from tests_driver_categories_api import category_utils

ENDPOINT = '/v1/robot'

HEADERS = {'Content-Type': 'application/json'}

PARK_ID = 'park_0'
DRIVER_ID = 'driver_0'


def config_sending_push_settings(use_client_notify):
    return {'DRIVER_CATEGORIES_API_SENDING_PUSH_SETTINGS': use_client_notify}


def check_push_request(request, message):
    assert json.loads(request['request'].get_data()) == {
        'action': 'RobotChange',
        'code': 450,
        'dbid': PARK_ID,
        'uuid': DRIVER_ID,
        'data': {'message': message},
    }


def check_push_request_new(request, message):
    assert json.loads(request['request'].get_data()) == {
        'service': 'taximeter',
        'intent': 'RobotChange',
        'client_id': PARK_ID + '-' + DRIVER_ID,
        'data': {'code': 450, 'message': message},
    }


async def test_enable_enabled(taxi_driver_categories_api, redis_store):
    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}
    data = {'is_enabled': True}

    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )

    response = await taxi_driver_categories_api.put(
        ENDPOINT, headers=HEADERS, params=params, json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}

    category_utils.check_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )


@pytest.mark.parametrize('use_client_notify', [False, True])
async def test_enable_disabled(
        taxi_driver_categories_api,
        mockserver,
        taxi_config,
        candidates,
        parks,
        redis_store,
        use_client_notify,
):
    taxi_config.set_values(config_sending_push_settings(use_client_notify))
    await taxi_driver_categories_api.invalidate_caches()

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert 'service' in request.json
        assert 'intent' in request.json
        assert 'client_id' in request.json
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler('/communications/driver/notification/push')
    def notification_push(request):
        pass

    parks.set_driver_profiles_search(idx=0)

    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['econom', 'business'],
    )

    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}
    data = {'is_enabled': True}

    response = await taxi_driver_categories_api.put(
        ENDPOINT, headers=HEADERS, params=params, json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}

    category_utils.check_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )

    if not use_client_notify:
        assert notification_push.times_called == 1
        check_push_request(notification_push.next_call(), 97)
    else:
        assert mock_client_notify.times_called == 1
        check_push_request_new(mock_client_notify.next_call(), 97)


@pytest.mark.parametrize('use_client_notify', [False, True])
async def test_disable_enabled(
        taxi_driver_categories_api,
        mockserver,
        taxi_config,
        candidates,
        parks,
        redis_store,
        use_client_notify,
):
    taxi_config.set_values(config_sending_push_settings(use_client_notify))
    await taxi_driver_categories_api.invalidate_caches()

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert 'service' in request.json
        assert 'intent' in request.json
        assert 'client_id' in request.json
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler('/communications/driver/notification/push')
    def notification_push(request):
        pass

    parks.set_driver_profiles_search(idx=0)

    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )

    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}
    data = {'is_enabled': False}

    response = await taxi_driver_categories_api.put(
        ENDPOINT, headers=HEADERS, params=params, json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}

    category_utils.check_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['econom', 'business'],
    )

    if not use_client_notify:
        assert notification_push.times_called == 1
        check_push_request(notification_push.next_call(), 96)
    else:
        assert mock_client_notify.times_called == 1
        check_push_request_new(mock_client_notify.next_call(), 96)


@pytest.mark.parametrize('use_client_notify', [False, True])
async def test_push_error(
        taxi_driver_categories_api,
        mockserver,
        taxi_config,
        candidates,
        parks,
        redis_store,
        use_client_notify,
):
    taxi_config.set_values(config_sending_push_settings(use_client_notify))
    await taxi_driver_categories_api.invalidate_caches()

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/communications/driver/notification/push')
    def notification_push(request):
        return mockserver.make_response(status=500)

    parks.set_driver_profiles_search(idx=0)

    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )

    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}
    data = {'is_enabled': False}

    response = await taxi_driver_categories_api.put(
        ENDPOINT, headers=HEADERS, params=params, json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}

    category_utils.check_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['econom', 'business'],
    )

    if not use_client_notify:
        assert notification_push.times_called >= 1
        check_push_request(notification_push.next_call(), 96)
    else:
        assert mock_client_notify.times_called >= 1
        check_push_request_new(mock_client_notify.next_call(), 96)
