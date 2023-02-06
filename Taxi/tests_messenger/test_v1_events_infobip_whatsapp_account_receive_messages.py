import re

import pytest


FROM = '70001112233'
TO = '79259036787'
AUTH_HEADERS = {'Authorization': 'Bearer inbound_auth_token'}


async def test_ok(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        assert request.json == {
            'account': 'premium_support',
            'channel': 'whatsapp',
            'service': 'chatterbox',
            'payload': {'text': 'Support hello', 'type': 'text'},
            'phone_id': 'personal_id',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'TEXT', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


@pytest.mark.config(MESSENGER_PHONES_ALLOWLIST=[])
async def test_receive_phone_not_allowed(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.json_handler('staff-production/v3/persons')
    def _staff(request):
        return {
            'links': {},
            'page': 1,
            'limit': 1,
            'result': [],
            'total': 0,
            'pages': 0,
        }

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'TEXT', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
    )
    assert response.status_code == 200
    assert _service_name_mock.times_called == 0


@pytest.mark.config(MESSENGER_PHONES_ALLOWLIST=[])
async def test_receive_phone_allowed_by_staff(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.json_handler('staff-production/v3/persons')
    def _staff(request):
        return {
            'links': {},
            'page': 1,
            'limit': 1,
            'result': [
                {
                    'id': 123456,
                    'department_group': {'department': {'url': 'yandex'}},
                },
            ],
            'total': 1,
            'pages': 1,
        }

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'TEXT', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
    )
    assert response.status_code == 200
    assert _service_name_mock.times_called == 1


async def test_bad(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'premium_support',
            'channel': 'whatsapp',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
            'payload': {
                'error_message': 'unsupported_payload',
                'type': 'error',
            },
            'phone_id': 'personal_id',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'service': 'chatterbox',
        }

        return {}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        headers=dict(AUTH_HEADERS, **{'AdditionalInvalidHeader': 'some data'}),
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'NEW', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(
    MESSENGER_INFOBIP_AUTH_SETTINGS={'use_inbound_authentication': True},
)
async def test_unauthorized(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        headers={'Authorization': 'invalid auth_token'},
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'NEW', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
    )
    assert response.status_code == 401


@pytest.mark.config(
    MESSENGER_INFOBIP_AUTH_SETTINGS={'use_inbound_authentication': False},
)
async def test_authorisation_check_disabled(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': FROM}

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        return {}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'NEW', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
    )
    assert response.status_code == 200


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_receive_media_ok(
        taxi_messenger, mockserver, mongodb, load_json,
):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        url = request.json['payload'].pop('url')
        assert 'some_file.ext' in url

        media_id = request.json['payload'].pop('media_id')
        assert re.fullmatch(r'([0-9a-f]{32})', media_id)

        assert request.json == {
            'account': 'premium_support',
            'service': 'chatterbox',
            'channel': 'whatsapp',
            'payload': {
                'type': 'media',
                'media_type': 'document',
                'caption': 'Support hello',
                'file_name': 'some_file.ext',
            },
            'phone_id': 'personal_id',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.handler('/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {
                        'type': 'DOCUMENT',
                        'caption': 'Support hello',
                        'url': mockserver.url('some_file.ext'),
                    },
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    media = next(mongodb.messenger_media.find({}))
    assert re.fullmatch(r'([0-9a-f]{32})', media['media_id'])
    assert 'some_file.ext' in media['source_url']
    assert media == dict(
        load_json('mongo_media.json')['inbound_uploaded'],
        **{
            '_id': media['_id'],
            'message_id': media['message_id'],
            'media_id': media['media_id'],
            'source_url': media['source_url'],
        },
    )

    assert response.status_code == 200
    assert _service_name_mock.times_called == 1


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'webhooks': {
                'inbound_message': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {'$mockserver': '/service_name/v1/message/receive'},
                },
            },
            'media_storage': {
                's3_bucket_name': 'chatterbox',
                'is_write_s3_media_info_to_inbound_messages': True,
            },
        },
    },
)
@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_receive_media_service_s3(
        taxi_messenger, mockserver, mongodb, load_json,
):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        url = request.json['payload'].pop('url')
        assert 'some_file.ext' in url

        assert 's3' in request.json['payload']
        assert (
            request.json['payload']['s3']['media_id']
            == request.json['payload']['media_id']
        )

        media_id = request.json['payload']['s3'].pop('media_id')
        assert re.fullmatch(r'([0-9a-f]{32})', media_id)

        media_id = request.json['payload'].pop('media_id')
        assert re.fullmatch(r'([0-9a-f]{32})', media_id)

        assert request.json == {
            'account': 'premium_support',
            'service': 'chatterbox',
            'channel': 'whatsapp',
            'payload': {
                'type': 'media',
                'media_type': 'document',
                'caption': 'Support hello',
                'file_name': 'some_file.ext',
                's3': {'file_name': 'some_file.ext'},
            },
            'phone_id': 'personal_id',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.handler('/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response(
            b'Some data', 200, headers={'Content-Type': 'audio/webm'},
        )

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        assert request.content_type == 'audio/webm'
        assert request.get_data() == b'Some data'
        return mockserver.make_response('', 200)

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {
                        'type': 'DOCUMENT',
                        'caption': 'Support hello',
                        'url': mockserver.url('some_file.ext'),
                    },
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert _mock_media_server.times_called == 1
    assert _mock_mds_s3.times_called == 1
    assert _service_name_mock.times_called == 1


async def test_receive_media_error(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.handler('/image.jpeg')
    def _mock_media_server(request):
        return mockserver.make_response('', 500)

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {
                        'type': 'IMAGE',
                        'caption': 'Support hello',
                        'url': mockserver.url('image.jpeg'),
                    },
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 500


async def test_interactive_list_reply(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'
        request_data = request.json
        request_data.pop('message_id')
        assert request.json == {
            'account': 'premium_support',
            'payload': {
                'description': 'row description',
                'id': '2',
                'text': 'row title 2',
                'type': 'list',
            },
            'channel': 'whatsapp',
            'phone_id': 'personal_id',
            'received_at': '2022-04-22T09:41:54.126+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2022-04-22T09:41:54.126+0000',
                    'messageId': 'ABGGeSYRUENfAgo6ikTZ8d2Sfpza',
                    'pairedMessageId': '12345',
                    'callbackData': 'Callback data',
                    'message': {
                        'id': '2',
                        'title': 'row title 2',
                        'description': 'row description',
                        'context': {'from': '447860099299', 'id': '12345'},
                        'type': 'INTERACTIVE_LIST_REPLY',
                    },
                    'price': {'pricePerMessage': 0.000000, 'currency': 'RUB'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': -1,
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


async def test_location(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'
        request_data = request.json
        request_data.pop('message_id')
        assert request.json == {
            'account': 'premium_support',
            'payload': {
                'latitude': 55.597,
                'longitude': 38.113,
                'type': 'location',
            },
            'channel': 'whatsapp',
            'phone_id': 'personal_id',
            'received_at': '2022-04-22T09:41:54.126+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2022-04-22T09:41:54.126+0000',
                    'messageId': 'ABGGeSYRUENfAgo6ikTZ8d2Sfpza',
                    'pairedMessageId': '12345',
                    'callbackData': 'Callback data',
                    'message': {
                        'longitude': 38.113,
                        'latitude': 55.597,
                        'context': {'from': '447860099299', 'id': '12345'},
                        'type': 'LOCATION',
                    },
                    'price': {'pricePerMessage': 0.000000, 'currency': 'RUB'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': -1,
        },
        headers=AUTH_HEADERS,
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
                'inbound_message': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {'$mockserver': '/service_name/v1/message/receive'},
                },
            },
        },
    },
)
async def test_store_personal(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        assert request.json == {
            'account': 'premium_support',
            'channel': 'whatsapp',
            'service': 'chatterbox',
            'payload': {'text': 'Support hello', 'type': 'text'},
            'phone_id': 'stored_pdid',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _logins_store(request):
        return {'id': 'stored_pdid', 'value': FROM}

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'TEXT', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'use_phone': {
                'reason': 'Can not use personal',
                'receive_enabled': True,
            },
            'webhooks': {
                'inbound_message': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {'$mockserver': '/service_name/v1/message/receive'},
                },
            },
        },
    },
)
async def test_phone(taxi_messenger, mockserver):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        assert request.json == {
            'account': 'premium_support',
            'channel': 'whatsapp',
            'service': 'chatterbox',
            'payload': {'text': 'Support hello', 'type': 'text'},
            'phone_id': '',
            'phone': f'+{FROM}',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {'type': 'TEXT', 'text': 'Support hello'},
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert _service_name_mock.times_called == 1


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'media_storage': {'is_download_inbound_async': True},
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'webhooks': {
                'inbound_message': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {'$mockserver': '/service_name/v1/message/receive'},
                },
            },
        },
    },
)
@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_download_media_async(
        taxi_messenger, mockserver, mongodb, load_json, stq,
):
    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.headers['Content-Type'] == 'application/json'

        url = request.json['payload'].pop('url')
        assert 'some_file.ext' in url

        request.json['payload'].pop('media_id')

        assert request.json == {
            'account': 'premium_support',
            'service': 'chatterbox',
            'channel': 'whatsapp',
            'payload': {
                'type': 'media',
                'media_type': 'document',
                'caption': 'Support hello',
                'file_name': 'some_file.ext',
            },
            'phone_id': 'personal_id',
            'received_at': '2019-07-19T11:23:26.998+00:00',
            'message_id': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
            'message_type': 'new',
        }
        return {}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': f'+{FROM}'}

    @mockserver.handler('/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    response = await taxi_messenger.post(
        'v1/events/infobip/whatsapp/test_account/receive/messages',
        json={
            'results': [
                {
                    'from': FROM,
                    'to': TO,
                    'integrationType': 'WHATSAPP',
                    'receivedAt': '2019-07-19T11:23:26.998+00:00',
                    'messageId': 'ABEGOFl3VCQoAhBalbc6rTQT6mgS29EmGZ7a',
                    'message': {
                        'type': 'DOCUMENT',
                        'caption': 'Support hello',
                        'url': mockserver.url('some_file.ext'),
                    },
                    'contact': {'name': 'Frank'},
                    'price': {'pricePerMessage': 0, 'currency': 'EUR'},
                },
            ],
            'messageCount': 1,
            'pendingMessageCount': 0,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert _service_name_mock.times_called == 1

    assert stq.messenger_media_download.times_called == 1
    kwargs = stq.messenger_media_download.next_call()['kwargs']
    kwargs.pop('log_extra')
    kwargs.pop('media_id')

    assert kwargs == {
        'account': 'premium_support',
        'client_name': 'whatsapp',
        'file_name': 'some_file.ext',
        'service': 'chatterbox',
        'url': mockserver.url('some_file.ext'),
    }
