import pytest

from tests_client_notify import helpers


async def test_bad_request(taxi_client_notify, mock_xiva):
    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'bad_service',
            'client_id': 'courier1',
            'intent': 'test',
            'data': {},
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.json()['message'] is not None

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'intent': 'bad_intent',
            'data': {},
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'xiva_error_code,service_error_code', [(500, 502), (429, 502), (400, 400)],
)
async def test_xiva_500(
        taxi_client_notify, mockserver, xiva_error_code, service_error_code,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response(
            'OK', xiva_error_code, headers={'TransitID': 'id'},
        )

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'intent': 'order_new',
            'data': {'payload': {}},
        },
    )
    assert response.status_code == service_error_code


async def test_push(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.args['user'] == 'courier1'
        assert request.args['service'] == 'eda-courier-service'
        assert request.args['event'] == 'order_new'
        assert request.args['ttl'] == '91'
        assert request.json['subscriptions'][0]['uuid'] == ['app-install-id']
        assert request.json['payload']['content'] == {
            'title': 'My Push',
            'value': 10,
        }
        assert request.json['payload']['id'] is not None
        assert 'id' in request.json['repack']['fcm']['repack_payload']
        assert 'id' in request.json['repack']['apns']['repack_payload']

        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'app_install_id': 'app-install-id',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {'content': {'title': 'My Push', 'value': 10}},
                'repack': {
                    'fcm': {'repack_payload': ['content']},
                    'apns': {'repack_payload': ['content']},
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] is not None


async def test_push_repack_all(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json['repack'] == {
            'fcm': {'repack_payload': ['*']},
            'apns': {'repack_payload': ['*']},
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'app_install_id': 'app-install-id',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {'content': {'title': 'My Push', 'value': 10}},
                'repack': {
                    'fcm': {'repack_payload': ['*']},
                    'apns': {'repack_payload': ['*']},
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] is not None


async def test_regexp(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.args['user'] == 'c'
        assert request.json['subscriptions'][0]['uuid'] == ['1']
        assert request.json['subscriptions'][0]['device'] == ['device-1']

        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'c',
            'app_install_id': '1',
            'device_id': 'device-1',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {'content': {'title': 'My Push', 'value': 10}},
                'repack': {
                    'fcm': {'repack_payload': ['content']},
                    'apns': {'repack_payload': ['content']},
                },
            },
        },
    )
    assert response.status_code == 200


@helpers.TRANSLATIONS
async def test_push_localization(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json['payload']['cost'] == '100 руб.'
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'locale': 'ru',
            'app_install_id': 'app-install-id',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {
                    'cost': {
                        'key': 'key1',
                        'keyset': 'notify',
                        'params': {'cost': 100},
                    },
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] is not None


async def test_no_locale(taxi_client_notify):
    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'app_install_id': 'app-install-id',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {
                    'cost': {
                        'key': 'key1',
                        'keyset': 'notify',
                        'params': {'cost': 100},
                    },
                },
            },
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'test',
            'xiva_service': 'eda-courier-service',
            'parse_message_in_xiva_body': True,
        },
    },
)
@pytest.mark.parametrize(
    'xiva_response,expected_code',
    [
        ('OK', 200),
        (
            '{"code":200,"body":{"apns_message_id":"629F43D"},"id":"mob:7d"}',
            200,
        ),
        ('{"code":205, "body": {"error":"MismatchSenderId"}}', 400),
        ('{"code":204, "body": {"error":"no subscriptions"}}', 400),
        ('{"code":204, "body": "no subscriptions"}', 400),
    ],
)
async def test_parse_xiva_body(
        taxi_client_notify, mockserver, xiva_response, expected_code,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response(
            xiva_response, 200, headers={'TransitID': 'id'},
        )

    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'app_install_id': 'app-install-id',
            'intent': 'order_new',
            'ttl': 91,
            'data': {
                'payload': {'content': {'title': 'My Push', 'value': 10}},
                'repack': {
                    'fcm': {'repack_payload': ['content']},
                    'apns': {'repack_payload': ['content']},
                },
            },
        },
    )
    assert response.status_code == expected_code
