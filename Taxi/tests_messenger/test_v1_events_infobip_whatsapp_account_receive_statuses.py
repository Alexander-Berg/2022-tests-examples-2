import pytest


FROM = '+70001112233'
TO = '41793026731'
AUTH_HEADERS = {'Authorization': 'Bearer inbound_auth_token'}

"""
async def test_ok(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        request.json['channel'] = 'whatsapp'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'delivered',
            'description': 'Message delivered to handset',
            'phone_id': 'personal_id',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'NO_ERROR',
                        'description': 'No Error',
                        'groupId': 0,
                        'groupName': 'OK',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_client_extra(taxi_messenger, mockserver, mongodb, load_json):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert request.json['reports'][0]['service_message_id'] == '1234'
        assert request.json['reports'][0]['service_data'] == {
            'some_key': 'some_value',
            'some_complex_key': {'some_sub_key': 'some_value'},
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    mongodb.messenger_messages.insert(
        dict(
            load_json('mongo_messages.json')['sent'],
            **{
                'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
                'provider_message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            },
        ),
    )

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'NO_ERROR',
                        'description': 'No Error',
                        'groupId': 0,
                        'groupName': 'OK',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert _service_name_mock.times_called == 1

    assert list(mongodb.messenger_messages.find({}))
    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'seenAt': '2019-04-09T16:00:59.647-0300',
                    'to': TO,
                    'from': FROM,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert _service_name_mock.times_called == 2

    assert not list(mongodb.messenger_messages.find({}))


async def test_remove_media(taxi_messenger, mockserver, mongodb, load_json):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    mongodb.messenger_media.insert(
        dict(
            load_json('mongo_media.json')['sent'],
            **{
                'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
                'media_id': 'ad4469da27f4479e91fc064b8b5192f8',
            },
        ),
    )

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        assert request.method == 'DELETE'
        assert (
            request.path
            == '/mds-s3/public/chatterbox/ad4469da27f4479e91fc064b8b5192f8/'
            + 'some_file.ext'
        )
        return mockserver.make_response('', 200)

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'NO_ERROR',
                        'description': 'No Error',
                        'groupId': 0,
                        'groupName': 'OK',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert _service_name_mock.times_called == 1

    assert _mock_mds_s3.times_called == 1
    assert not list(mongodb.messenger_media.find({}))


@pytest.mark.config(
    MESSENGER_INFOBIP_AUTH_SETTINGS={'use_inbound_authentication': True},
)
async def test_authorized_ok(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'NO_ERROR',
                        'description': 'No Error',
                        'groupId': 0,
                        'groupName': 'OK',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert _service_name_mock.times_called == 1


@pytest.mark.parametrize(
    'auth_headers', [({}), ({'Authorization': 'invalid auth_token'})],
)
@pytest.mark.config(
    MESSENGER_INFOBIP_AUTH_SETTINGS={'use_inbound_authentication': True},
)
async def test_unauthorized(taxi_messenger, auth_headers):
    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        headers=auth_headers,
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'NO_ERROR',
                        'description': 'No Error',
                        'groupId': 0,
                        'groupName': 'OK',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )
    assert response.status_code == 401


async def test_error(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'
        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'error',
            'description': 'Rejected error',
            'phone_id': 'personal_id',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'DELIVERED',
                        'name': 'DELIVERED_TO_HANDSET',
                        'description': 'Message delivered to handset',
                    },
                    'error': {
                        'id': 0,
                        'name': 'UNDELIVERABLE_REJECTED_OPERATOR',
                        'description': 'Rejected error',
                        'groupId': 0,
                        'groupName': 'UNDELIVERABLE',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


async def test_unknown_status(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'bulkId': 'Delivered to the recipient"',
                    'price': {'pricePerMessage': 0.21, 'currency': 'BRL'},
                    'status': {
                        'id': 5,
                        'groupId': 3,
                        'groupName': 'UNKNOWN',
                        'name': 'SOME_CODE',
                        'description': 'Some description',
                    },
                    'error': {
                        'id': 0,
                        'name': 'UNDELIVERABLE_REJECTED_OPERATOR',
                        'description': 'Rejected error',
                        'groupId': 0,
                        'groupName': 'UNDELIVERABLE',
                        'permanent': False,
                    },
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'doneAt': '2019-04-09T16:01:56.494-0300',
                    'messageCount': 1,
                    'sentAt': '2019-04-09T16:00:58.647-0300',
                    'to': TO,
                    'channel': 'WHATSAPP',
                },
            ],
        },
    )
    assert response.status_code == 500


async def test_seen(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'seen',
            'description': 'Message seen at 2022-01-19T15:55:41.000+0300',
            'phone_id': 'personal_id',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'from': FROM,
                    'to': TO,
                    'sentAt': '2022-01-19T15:55:24.970+0300',
                    'seenAt': '2022-01-19T15:55:41.000+0300',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1

"""


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'webhooks': {
                'delivery_report': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {
                        '$mockserver': '/service_name/v1/status/delivered',
                    },
                },
            },
            'use_phone': {
                'reason': 'Can not use personal',
                'receive_enabled': True,
            },
        },
    },
)
async def test_phone_in_status_report(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'seen',
            'description': 'Message seen at 2022-01-19T15:55:41.000+0300',
            'phone_id': 'personal_id',
            'phone': f'+{TO}',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'from': FROM,
                    'to': TO,
                    'sentAt': '2022-01-19T15:55:24.970+0300',
                    'seenAt': '2022-01-19T15:55:41.000+0300',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'webhooks': {
                'delivery_report': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {
                        '$mockserver': '/service_name/v1/status/delivered',
                    },
                },
            },
            'use_phone': {
                'reason': 'Can not use personal',
                'receive_enabled': True,
            },
        },
    },
)
async def test_not_found(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'seen',
            'description': 'Message seen at 2022-01-19T15:55:41.000+0300',
            'phone_id': '',
            'phone': f'+{TO}',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'from': FROM,
                    'to': TO,
                    'sentAt': '2022-01-19T15:55:24.970+0300',
                    'seenAt': '2022-01-19T15:55:41.000+0300',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


async def test_no_personal(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/status/delivered')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        request.json['service'] = 'chatterbox'
        request.json['account'] = 'premium_support'
        assert len(request.json['reports']) == 1
        result = request.json['reports'][0]
        assert result == {
            'message_id': 'cd4469da27f4479e91fc064b8b5192f8',
            'status': 'seen',
            'description': 'Message seen at 2022-01-19T15:55:41.000+0300',
            'phone_id': '',
        }

        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    response = await taxi_messenger.post(
        '/v1/events/infobip/whatsapp/premium_support/receive/statuses',
        json={
            'results': [
                {
                    'messageId': 'cd4469da27f4479e91fc064b8b5192f8',
                    'from': FROM,
                    'to': TO,
                    'sentAt': '2022-01-19T15:55:24.970+0300',
                    'seenAt': '2022-01-19T15:55:41.000+0300',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1
