import pytest


async def test_bad_request(taxi_client_notify):
    response = await taxi_client_notify.post('v1/subscribe', json={})

    assert response.status_code == 400

    # bad_service is not in CLIENT_NOTIFY_SERVICES config
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'bad_service',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400

    # bad client_id
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'bad_client_id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400

    # no client_id
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400

    # bad device_type
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'vedroid',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400

    # bad channel name
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'bad_name', 'token': 'token'},
        },
    )

    assert response.status_code == 400

    # no channel name
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'token': 'token'},
        },
    )

    assert response.status_code == 400

    # no app_name
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400


async def test_good_request(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'good-client-id'
        assert request.args['client'] == 'android'
        assert request.args['uuid'] == 'app_install_id'
        assert request.args['device'] == 'device_id'
        assert request.args['platform'] == 'fcm'

        assert request.get_data() == b'push_token=token'

        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 200


async def test_xiva_400_response(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('InternalServerError', 400)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 400


async def test_xiva_401_response(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('InternalServerError', 401)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 500


async def test_xiva_429_response(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('InternalServerError', 429)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 429


async def test_xiva_500_response(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('InternalServerError', 500)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 502


async def test_xiva_502_response(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('InternalServerError', 502)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
        },
    )

    assert response.status_code == 502


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'rest_app': {'description': 'RestApp', 'xiva_service': 'rest-app'},
    },
    CLIENT_NOTIFY_INTENTS={
        'rest_app': {'order_new': {'description': 'new order'}},
    },
)
async def test_apns_request(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        assert request.args['service'] == 'rest-app'
        assert request.args['user'] == 'good-client-id'
        assert request.args['client'] == 'ios'
        assert request.args['uuid'] == 'app_install_id'
        assert request.args['device'] == 'device_id'
        assert request.args['platform'] == 'apns'

        assert request.get_data() == b'push_token=apns_token'

        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'rest_app',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'ios',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'apns', 'token': 'apns_token'},
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'rest_app': {
            'description': 'RestApp',
            'xiva_service': 'rest-app',
            'subscribe_uuid_types': ['device_id', 'client_id'],
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'rest_app': {'order_new': {'description': 'new order'}},
    },
)
async def test_uuid_types(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        assert request.args['service'] == 'rest-app'
        assert request.args['user'] == 'good-client-id'
        assert request.args['client'] == 'ios'
        assert request.args['uuid'] == 'good-client-id'
        assert request.args['platform'] == 'apns'

        assert request.get_data() == b'push_token=apns_token'

        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'rest_app',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'ios',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'apns', 'token': 'apns_token'},
        },
    )

    assert response.status_code == 200


async def test_hms(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'good-client-id'
        assert request.args['client'] == 'android'
        assert request.args['uuid'] == 'app_install_id'
        assert request.args['device'] == 'device_id'
        assert request.args['platform'] == 'hms'

        assert request.get_data() == b'push_token=token'

        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'hms', 'token': 'token'},
        },
    )

    assert response.status_code == 200


async def test_push_settings(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        assert b'marketing' in request.get_data()
        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm', 'token': 'token'},
            'push_settings': {
                'included_tags': [],
                'excluded_tags': ['marketing'],
                'enabled_by_system': True,
            },
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'eda courier',
            'xiva_service': 'eda_courier',
            'subscribe_uuid_types': ['device_id'],
            'unsubscribe_uuid_types': ['device_id'],
        },
    },
)
async def test_webpush(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/webpush')
    def _subscribe_webpush(request):
        assert request.args['user'] == 'client-id'
        assert request.args['service'] == 'eda_courier'
        assert request.args['session'] == 'device_1'
        assert request.args['client'] == 'web'
        return {}

    subscription = {
        'endpoint': 'https://fcm.googleapis.com/fcm/send/id',
        'expirationTime': None,
        'keys': {
            'auth': '9pvIVgPVrXiT2gYizpdS-g222',
            'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
        },
    }

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'client-id',
                'device_type': 'web',
                'device_id': 'device_1',
                'app_install_id': 'app_install_id',
                'app_name': 'webpush_appname',
            },
            'channel': {'name': 'webpush'},
            'subscription': subscription,
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'eda courier',
            'xiva_service': 'eda_courier',
            'subscribe_uuid_types': ['device_id'],
            'unsubscribe_uuid_types': ['device_id'],
        },
    },
)
async def test_webpush_session(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/webpush')
    def _subscribe_webpush(request):
        assert request.args['user'] == 'client-id'
        assert request.args['service'] == 'eda_courier'
        assert request.args['session'] == 'session_id'
        assert request.args['client'] == 'web'
        return {}

    subscription = {
        'endpoint': 'https://fcm.googleapis.com/fcm/send/id',
        'expirationTime': None,
        'keys': {
            'auth': '9pvIVgPVrXiT2gYizpdS-g222',
            'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
        },
    }

    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'client-id',
                'device_type': 'web',
                'session_id': 'session_id',
                'app_name': 'webpush_appname',
            },
            'channel': {'name': 'webpush'},
            'subscription': subscription,
        },
    )

    assert response.status_code == 200


async def test_no_token(taxi_client_notify, mockserver):
    response = await taxi_client_notify.post(
        'v1/subscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'android',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'fcm'},
        },
    )

    assert response.status_code == 400
