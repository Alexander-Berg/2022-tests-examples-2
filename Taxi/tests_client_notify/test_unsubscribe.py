import pytest


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'EdaCourier',
            'xiva_service': 'eda-courier-service',
            'unsubscribe_uuid_types': ['app_install_id'],
        },
    },
)
async def test_good_request(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'client-id'
        assert request.args['uuid'] == 'app-install-id'
        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'client-id',
                'app_install_id': 'app-install-id',
            },
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'xiva_error_code,expected_code',
    [(400, 500), (401, 500), (429, 429), (500, 502), (502, 502)],
)
async def test_xiva_errors(
        taxi_client_notify, mockserver, xiva_error_code, expected_code,
):
    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe(request):
        return mockserver.make_response('InternalServerError', xiva_error_code)

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'client-id',
                'app_install_id': 'app-install-id',
            },
        },
    )

    assert response.status_code == expected_code


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'EdaCourier',
            'xiva_service': 'eda-courier-service',
            'unsubscribe_uuid_types': ['device_id'],
        },
    },
)
async def test_unsubscribe_by_device_id(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'client-id'
        assert request.args['uuid'] == 'device_id'
        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'eda_courier',
            'client': {'client_id': 'client-id', 'device_id': 'device_id'},
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'rest_app': {
            'description': 'RestApp',
            'xiva_service': 'rest-app',
            'unsubscribe_uuid_types': [
                'device_id',
                'client_id',
                'app_install_id',
            ],
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'rest_app': {'order_new': {'description': 'new order'}},
    },
)
async def test_uuid_types(taxi_client_notify, mockserver):
    uuids = []

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe(request):
        assert request.args['service'] == 'rest-app'
        assert request.args['user'] == 'client1'
        uuids.append(request.args['uuid'])
        return mockserver.make_response('OK', 200)

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'rest_app',
            'client': {
                'client_id': 'client1',
                'device_id': 'device1',
                'app_install_id': 'app1',
            },
        },
    )

    assert response.status_code == 200
    assert _unsubscribe.times_called == 3
    assert uuids == ['device1', 'client1', 'app1']


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'EdaCourier',
            'xiva_service': 'eda-courier-service',
            'unsubscribe_uuid_types': ['app_install_id'],
        },
    },
)
async def test_webpush(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/unsubscribe/webpush')
    def _unsubscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'client-id'
        assert request.args['session'] == 'app-install-id'
        return {}

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'eda_courier',
            'client': {
                'client_id': 'client-id',
                'app_install_id': 'app-install-id',
            },
            'channel': {'name': 'webpush'},
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'EdaCourier',
            'xiva_service': 'eda-courier-service',
            'unsubscribe_uuid_types': ['app_install_id'],
        },
    },
)
async def test_webpush_session(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/unsubscribe/webpush')
    def _unsubscribe(request):
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['user'] == 'client-id'
        assert request.args['session'] == 'session_id'
        return {}

    response = await taxi_client_notify.post(
        'v1/unsubscribe',
        json={
            'service': 'eda_courier',
            'client': {'client_id': 'client-id', 'session_id': 'session_id'},
            'channel': {'name': 'webpush'},
        },
    )

    assert response.status_code == 200
