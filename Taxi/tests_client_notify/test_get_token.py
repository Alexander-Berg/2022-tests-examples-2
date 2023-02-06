import pytest


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'rest_app': {'description': 'RestApp', 'xiva_service': 'rest-app'},
    },
    CLIENT_NOTIFY_INTENTS={
        'rest_app': {'order_new': {'description': 'new order'}},
    },
)
async def test_get_token(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/secret_sign')
    def _send(request):
        assert request.args['service'] == 'rest-app'
        assert request.args['user'] == 'good-client-id'

        return mockserver.make_response(
            '{"ts": "1510268445", "sign": "00a1560f46a1953645c9dd9fbcba4836"}',
            200,
        )

    response = await taxi_client_notify.post(
        'v1/get_token',
        json={
            'service': 'rest_app',
            'client': {
                'client_id': 'good-client-id',
                'device_type': 'ios',
                'device_id': 'device_id',
                'app_install_id': 'app_install_id',
                'app_name': 'app_name',
            },
            'channel': {'name': 'xiva_websocket'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'token': {
            'sign': '00a1560f46a1953645c9dd9fbcba4836',
            'ts': '1510268445',
        },
    }
