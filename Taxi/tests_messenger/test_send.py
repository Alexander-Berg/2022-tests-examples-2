import datetime
import re

import aiohttp
import pytest


X_IDEMPOTENCY_TOKEN = 'token'
FROM = '+79259036787'
TO = '+70001112233'


async def test_ok(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        request_data = request.json
        request_data.pop('messageId')
        assert request.json == {
            'from': FROM,
            'to': TO,
            'content': {'text': 'Hello!'},
        }
        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 200

    assert not list(mongodb.messenger_messages.find({}))

    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_client_extra(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
            'service_message_id': '1234',
            'service_data': {
                'some_key': 'some_value',
                'some_complex_key': {'some_sub_key': 'some_value'},
            },
        },
    )

    messages_repo_item = next(mongodb.messenger_messages.find({}))
    assert re.fullmatch(r'([0-9a-f]{32})', messages_repo_item['message_id'])
    assert messages_repo_item == dict(
        load_json('mongo_messages.json')['sent'],
        **{
            '_id': messages_repo_item['_id'],
            'message_id': response.json()['message_id'],
            'provider_message_id': response.json()['message_id'],
        },
    )

    assert response.status_code == 200


@pytest.mark.config(MESSENGER_PHONES_ALLOWLIST=[])
async def test_phone_allowed_by_staff(taxi_messenger, mockserver, load_json):
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

    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 200


@pytest.mark.config(MESSENGER_PHONES_ALLOWLIST=[])
async def test_phone_not_allowed(taxi_messenger, mockserver, load_json):
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
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400


async def test_message_gateway_unauthorized(taxi_messenger, mockserver):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        return mockserver.make_response('', 401)

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )

    assert response.status_code == 500


async def test_message_gateway_too_many_requests(taxi_messenger, mockserver):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        return mockserver.make_response('', 429)

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )

    assert response.status_code == 429


async def test_bad_account(taxi_messenger, mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': '557f191e810c19729de860ea', 'value': TO}

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'unknown',
            'client': {'phone_id': 'phid'},
            'type': 'text',
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'personal_response_code,expected_code', [(500, 502), (404, 404)],
)
async def test_personal_errors(
        taxi_messenger, mockserver, personal_response_code, expected_code,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        return mockserver.make_response(
            status=personal_response_code,
            json={'code': 'not-found', 'message': 'error'},
        )

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'type': 'text',
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == expected_code


async def test_template_body(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/template')
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        assert len(request.json['messages']) == 1
        message = request.json['messages'][0]
        message.pop('messageId')

        assert message == {
            'content': {
                'language': 'en_GB',
                'templateData': {'body': {'placeholders': ['Marge', 'Test']}},
                'templateName': 'infobip_test_hsm_1',
            },
            'from': FROM,
            'to': TO,
        }
        return {'messages': [load_json('infobip_response.json')]}

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'locale': 'en_GB',
                'type': 'template',
                'template': {
                    'name': 'infobip_test_hsm_1',
                    'params': ['Marge', 'Test'],
                },
            },
        },
    )
    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id


async def test_template_text_header(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/template')
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        assert len(request.json['messages']) == 1
        message = request.json['messages'][0]
        message.pop('messageId')

        assert message == {
            'from': FROM,
            'to': TO,
            'content': {
                'templateName': 'header_text_template_name',
                'templateData': {
                    'body': {'placeholders': []},
                    'header': {
                        'placeholder': 'placeholder value',
                        'type': 'TEXT',
                    },
                },
                'language': 'en_GB',
            },
        }

        return {'messages': [load_json('infobip_response.json')]}

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'locale': 'en_GB',
                'type': 'template',
                'template': {
                    'name': 'header_text_template_name',
                    'params': [],
                },
                'header': {'type': 'text', 'params': ['placeholder value']},
            },
        },
    )
    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now('2021-02-20T00:00:00Z')
@pytest.mark.parametrize(
    'message_type,media_type,media_body',
    [
        (
            'document',
            'document',
            {'caption': 'Some caption', 'filename': 'some_file_1.ext'},
        ),
        ('image', 'image', {'caption': 'Some caption'}),
        ('audio', 'audio', {}),
        ('video', 'video', {'caption': 'Some caption'}),
        ('sticker', 'image', {}),
    ],
)
async def test_send_media(
        taxi_messenger,
        mockserver,
        load_json,
        message_type,
        media_type,
        media_body,
        mongodb,
):
    @mockserver.json_handler(
        '/test/infobip/whatsapp/1/message/' + message_type,
    )
    def _infobip_whatsapp_send(request):
        request.json.pop('messageId')
        request.json['content'].pop('mediaUrl')
        assert request.json == {'from': FROM, 'to': TO, 'content': media_body}
        return load_json('infobip_response.json')

    form = aiohttp.FormData()
    form.add_field(name='content', value=b'file binary \x00 data')
    form.add_field(name='media_type', value=media_type)
    form.add_field(
        name='content_file_name',
        value='some_file.ext'
        if 'filename' not in media_body
        else media_body['filename'],
    )
    form.add_field(name='service', value='chatterbox')
    response = await taxi_messenger.post('/v1/media/upload', data=form)
    media_id = response.json()['media_id']

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': message_type,
            },
        },
    )
    assert response.status_code == 200

    media = next(mongodb.messenger_media.find({}))
    assert re.fullmatch(r'([0-9a-f]{32})', media['media_id'])
    assert media == dict(
        load_json('mongo_media.json')['sent'],
        **{
            '_id': media['_id'],
            'file_name': (
                'some_file.ext'
                if 'filename' not in media_body
                else media_body['filename']
            ),
            'message_id': response.json()['message_id'],
            'media_id': media['media_id'],
            'media_type': media_type,
        },
    )


async def test_send_media_storage_object_not_found(taxi_messenger, mockserver):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        if request.method == 'PUT':
            return mockserver.make_response('', 200)
        # else GET
        empty_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            + '<ListBucketResult xmlns="'
            + 'http://s3.amazonaws.com/doc/2006-03-01/">'
            + '<Name>media</Name>'
            + '<Prefix>'
            + request.args.get('prefix')
            + '</Prefix>'
            + '<MaxKeys>1</MaxKeys>'
            + '<IsTruncated>false</IsTruncated>'
            + '<Marker></Marker>'
            + '</ListBucketResult>'
        )
        return mockserver.make_response(empty_response, 200)

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': '00000000000000000000000000000000',
                'media_type': 'document',
            },
        },
    )
    assert response.status_code == 404


async def test_send_media_storage_media_id_validation_error(
        taxi_messenger, mockserver,
):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': '00000000/000000000000000000000000',
                'media_type': 'document',
            },
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    MESSENGER_IDEMPOTENCY_SETTINGS={
        'enabled': True,
        'idempotency_token_ttl': 1000,
    },
)
async def test_send_idempotent(
        taxi_messenger, mockserver, mocked_time, load_json, mongodb,
):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send():
        return load_json('infobip_response.json')

    headers = {'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN}

    request = {
        'service': 'chatterbox',
        'account': 'premium_support',
        'client': {'phone_id': 'phid'},
        'payload': {'text': 'Hello!', 'type': 'text'},
    }

    # Request 1: executed
    response = await taxi_messenger.post(
        'v1/send', headers=headers, json=request,
    )
    assert response.status_code == 200
    message_id = response.json()['message_id']
    assert re.fullmatch(r'([0-9a-f]{32})', message_id)
    assert _infobip_whatsapp_send.times_called == 1

    print(next(mongodb.messenger_request_idempotency_tokens.find({})))

    # Request 2: not executed, return same message_id
    response = await taxi_messenger.post(
        'v1/send', headers=headers, json=request,
    )
    assert response.status_code == 200
    assert response.json()['message_id'] == message_id
    assert _infobip_whatsapp_send.times_called == 1

    # Request 3: executed because token ttl exceed, return new message_id
    mocked_time.sleep(1001)
    await taxi_messenger.invalidate_caches()

    response = await taxi_messenger.post(
        'v1/send', headers=headers, json=request,
    )
    assert response.status_code == 200
    assert response.json()['message_id'] != message_id
    assert _infobip_whatsapp_send.times_called == 2


@pytest.mark.now('2021-02-20T00:00:10Z')
@pytest.mark.config(
    MESSENGER_IDEMPOTENCY_SETTINGS={
        'enabled': True,
        'idempotency_token_ttl': 1000,
    },
)
async def test_send_idempotent_pending(taxi_messenger, mongodb):
    mongodb.messenger_request_idempotency_tokens.insert(
        {
            '_id': '0',
            'request_type': '/v1/send',
            'token': X_IDEMPOTENCY_TOKEN,
            'created': datetime.datetime(2021, 2, 20, 0, 0, 10),
            'delete_after': datetime.datetime(2021, 2, 20, 0, 0, 20),
            'status': 'pending',
            'user_data': {
                'payload_type': 'text',
                'message_id': 'c6b2700da2634cf2b6db18d8653ec4fe',
                'payload': {'text': 'Hello!'},
                'sender_phone': '+79259036787',
                'recipient_phone': '+70001112233',
            },
        },
    )

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 409


async def test_login_id(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        request_data = request.json
        request_data.pop('messageId')
        assert request.json == {
            'from': FROM,
            'to': TO,
            'content': {'text': 'Hello!'},
        }
        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'login_id': 'lid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 404


async def test_interactive_list(
        taxi_messenger, mockserver, load_json, mongodb,
):
    @mockserver.json_handler(
        '/test/infobip/whatsapp/1/message/interactive/list',
    )
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        request_data = request.json
        request_data.pop('messageId')

        assert request_data == {
            'content': {
                'header': {'text': 'Header', 'type': 'TEXT'},
                'footer': {'text': 'Footer'},
                'action': {
                    'sections': [
                        {
                            'rows': [
                                {
                                    'description': 'description 11',
                                    'id': '1',
                                    'title': 'title 11',
                                },
                                {
                                    'description': 'description 22',
                                    'id': '2',
                                    'title': 'title 22',
                                },
                            ],
                            'title': 'Section 1',
                        },
                        {
                            'rows': [
                                {
                                    'description': 'description 21',
                                    'id': '3',
                                    'title': 'title 21',
                                },
                            ],
                            'title': 'Section 2',
                        },
                    ],
                    'title': 'List title',
                },
                'body': {'text': 'Hello list'},
            },
            'from': '+79259036787',
            'to': '+70001112233',
        }

        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello list', 'type': 'text'},
            'allowed_replies': {
                'type': 'list',
                'title': 'List title',
                'header': 'Header',
                'footer': 'Footer',
                'sections': [
                    {
                        'header': 'Section 1',
                        'items': [
                            {
                                'id': '1',
                                'text': 'title 11',
                                'description': 'description 11',
                            },
                            {
                                'id': '2',
                                'text': 'title 22',
                                'description': 'description 22',
                            },
                        ],
                    },
                    {
                        'header': 'Section 2',
                        'items': [
                            {
                                'id': '3',
                                'text': 'title 21',
                                'description': 'description 21',
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 200

    assert not list(mongodb.messenger_messages.find({}))

    message_id = response.json().pop('message_id')
    assert message_id


async def test_reply_400(taxi_messenger, mockserver, load_json, mongodb):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone_id': 'phid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': '00000000/000000000000000000000000',
                'media_type': 'document',
            },
            'allowed_replies': {
                'type': 'list',
                'title': 'List title',
                'header': 'Header',
                'footer': 'Footer',
                'sections': [
                    {
                        'header': 'Section 1',
                        'items': [
                            {
                                'id': '1',
                                'text': 'title 11',
                                'description': 'description 11',
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'use_phone': {
                'reason': 'Can not use personal',
                'send_enabled': True,
            },
        },
    },
)
async def test_send_by_phone(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        assert False

    @mockserver.json_handler('/test/infobip/whatsapp/1/message/text')
    def _infobip_whatsapp_send(request):
        assert request.headers['Authorization'] == 'App auth_token'
        request_data = request.json
        request_data.pop('messageId')
        assert request.json == {
            'from': FROM,
            'to': TO,
            'content': {'text': 'Hello!'},
        }
        return load_json('infobip_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone': TO},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
        },
    },
)
async def test_send_by_phone_error(taxi_messenger):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {'phone': TO},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
            'use_phone': {
                'reason': 'Can not use personal',
                'send_enabled': True,
            },
        },
    },
)
async def test_no_client_error(taxi_messenger):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'premium_support',
            'client': {},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400
