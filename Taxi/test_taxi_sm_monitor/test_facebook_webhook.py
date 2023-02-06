# pylint: disable=inconsistent-return-statements,unused-variable
import http

import pytest

from taxi import discovery


@pytest.mark.parametrize(
    'params,answer',
    [
        (
            {
                'hub.mode': 'subscribe',
                'hub.challenge': '123',
                'hub.verify_token': 'fb_csrf_token',
            },
            http.HTTPStatus.OK,
        ),
        (
            {'hub.challenge': '123', 'hub.verify_token': 'fb_csrf_token'},
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            {
                'hub.mode': 'test',
                'hub.challenge': '123',
                'hub.verify_token': 'fb_csrf_token',
            },
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            {
                'hub.mode': 'subscribe',
                'hub.challenge': '123',
                'hub.verify_token': 'test_token',
            },
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            {'hub.mode': 'subscribe', 'hub.challenge': '123'},
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
async def test_facebook_webhook_get(taxi_sm_monitor_client, params, answer):
    response = await taxi_sm_monitor_client.get(
        '/webhook/facebook', params=params,
    )
    assert response.status == answer
    if answer == http.HTTPStatus.OK:
        assert await response.text() == params['hub.challenge']


@pytest.mark.parametrize(
    'data, message_metadata, message_hash',
    [
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                ],
            },
            [{}],
            '863a50b0fe6cfe715987ae6f15e05a3f44591be5',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'attachments': [
                                        {
                                            'payload': {'url': 'test_url'},
                                            'type': 'image',
                                        },
                                        {
                                            'payload': {
                                                'url': 'test_url_file',
                                            },
                                            'type': 'file',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            [
                {
                    'attachments': [
                        {
                            'type': 'image',
                            'source': 'facebook',
                            'link': 'test_url',
                        },
                        {
                            'type': 'file',
                            'source': 'facebook',
                            'link': 'test_url_file',
                        },
                    ],
                },
            ],
            '3c25b06934338999900d9589db38c27605a5b352',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id_loc',
                                    'seq': 42,
                                    'attachments': [
                                        {
                                            'payload': {
                                                'coordinates': {
                                                    'long': 12.12,
                                                    'lat': 13.14,
                                                },
                                            },
                                            'url': 'loc_url',
                                            'title': 'loc_title',
                                            'type': 'location',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            [
                {
                    'locations': [
                        {
                            'type': 'location',
                            'title': 'loc_title',
                            'lon': 12.12,
                            'lat': 13.14,
                            'url': 'loc_url',
                        },
                    ],
                },
            ],
            '51cf32041033e58b303a045d0e3d520ecf61e019',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                    {
                        'id': 'id2',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353514'},
                                'recipient': {'id': '563720454066048'},
                                'timestamp': 1544439250667,
                                'message': {
                                    'mid': 'message_id_1',
                                    'seq': 42,
                                    'text': 'test_text',
                                },
                            },
                        ],
                    },
                ],
            },
            [{}, {}],
            'cba5a1337456a322cb04f2b0bde099b74c110f37',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id5',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '563720454066049'},
                                'recipient': {'id': '1960892827353513'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'is_echo': True,
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                ],
            },
            [{'is_echo': True}],
            '8c4d35a50419485ddc4f484e558e08670bbe81fa',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id5',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '563720454066049'},
                                'recipient': {'id': '1960892827353513'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'metadata': 'own_message',
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                ],
            },
            [{}],
            '1a2fd7721f23bc200878b9ae9eb5166b1b2a7de6',
        ),
    ],
)
async def test_facebook_webhook_post(
        taxi_sm_monitor_client,
        data,
        message_metadata,
        message_hash,
        patch_aiohttp_session,
        response_mock,
):

    message_counter = 0

    @patch_aiohttp_session('https://graph.facebook.com/v6.0/', 'GET')
    def facebook(method, url, **kwargs):
        assert method == 'get'
        nonlocal message_counter
        message = data['entry'][message_counter]['messaging'][0]
        sender = message['sender']['id']
        recipient = message['recipient']['id']
        assert url in [
            'https://graph.facebook.com/v6.0/%s' % sender,
            'https://graph.facebook.com/v6.0/%s' % recipient,
        ]
        assert kwargs['params']['access_token'] == 'acc_token'
        assert kwargs['params']['fields'] == 'name'
        splitted_url = url.split('/')
        return response_mock(
            json={
                'id': splitted_url[-1],
                'name': 'name_%s' % splitted_url[-1],
            },
        )

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        nonlocal message_counter
        assert method == 'post'
        assert url.startswith('http://chatterbox.taxi.dev.yandex.net/v1/tasks')
        request_data = kwargs['json']
        message = data['entry'][message_counter]['messaging'][0]
        if url == 'http://chatterbox.taxi.dev.yandex.net/v1/tasks':
            assert request_data == {
                'type': 'chat',
                'external_id': 'chat_id_%s' % message_counter,
            }
            return response_mock(json={'id': 'task_id_%s' % message_counter})
        if 'task_id_%s/update_meta' % message_counter in url:
            request_data['update_meta'] = sorted(
                request_data['update_meta'],
                key=lambda record: record['field_name'],
            )
            if message['message'].get('is_echo'):
                page_id = message['sender']['id']
                user_id = message['recipient']['id']
            else:
                user_id = message['sender']['id']
                page_id = message['recipient']['id']
            assert request_data == {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'facebook_task'},
                ],
                'update_meta': sorted(
                    [
                        {
                            'change_type': 'set',
                            'field_name': 'page',
                            'value': page_id,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'page_name',
                            'value': 'name_%s' % page_id,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_name',
                            'value': 'name_%s' % user_id,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_id',
                            'value': user_id,
                        },
                    ],
                    key=lambda record: record['field_name'],
                ),
            }
            message_counter += 1
            return response_mock(json={})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat'
        request_data = kwargs['json']
        message = data['entry'][message_counter]['messaging'][0]
        assert request_data['request_id'] == message['message']['mid']
        if message['message'].get('is_echo'):
            owner_id = message['recipient']['id']
            page_id = message['sender']['id']
            sender_role = 'support'
        else:
            owner_id = message['sender']['id']
            page_id = message['recipient']['id']
            sender_role = 'facebook_user'
        assert request_data['owner'] == {
            'id': owner_id,
            'role': 'facebook_user',
        }
        assert request_data['message'] == {
            'metadata': message_metadata[message_counter],
            'text': message['message'].get('text', ''),
            'sender': {'id': message['sender']['id'], 'role': sender_role},
        }
        assert request_data['metadata'] == {'page': page_id}
        return response_mock(json={'id': 'chat_id_%s' % message_counter})

    response = await taxi_sm_monitor_client.post(
        '/webhook/facebook',
        json=data,
        headers={'X-Hub-Signature': 'sha1=%s' % message_hash},
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.parametrize(
    'data, bad_user, message_hash',
    [
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                ],
            },
            True,
            '863a50b0fe6cfe715987ae6f15e05a3f44591be5',
        ),
        (
            {
                'object': 'page',
                'entry': [
                    {
                        'id': 'id1',
                        'time': 1544439251061,
                        'messaging': [
                            {
                                'sender': {'id': '1960892827353513'},
                                'recipient': {'id': '563720454066049'},
                                'timestamp': 1544439250665,
                                'message': {
                                    'mid': 'message_id',
                                    'seq': 42,
                                    'text': 'test',
                                },
                            },
                        ],
                    },
                ],
            },
            False,
            '863a50b0fe6cfe715987ae6f15e05a3f44591be5',
        ),
    ],
)
async def test_facebook_no_user(
        taxi_sm_monitor_client,
        data,
        bad_user,
        message_hash,
        patch_aiohttp_session,
        response_mock,
):
    @patch_aiohttp_session('https://graph.facebook.com/v6.0/', 'GET')
    def facebook(method, url, **kwargs):
        splitted_url = url.split('/')
        user_id = data['entry'][0]['messaging'][0]['sender']['id']
        if bad_user and splitted_url[-1] == user_id:
            return response_mock(
                status=400, json={'error': {'code': 100, 'error_subcode': 33}},
            )
        return response_mock(json={'id': 'test_id', 'name': 'name'})

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        assert method == 'post'
        assert url.startswith('http://chatterbox.taxi.dev.yandex.net/v1/tasks')
        request_data = kwargs['json']
        message = data['entry'][0]['messaging'][0]
        if url == 'http://chatterbox.taxi.dev.yandex.net/v1/tasks':
            assert request_data == {'type': 'chat', 'external_id': 'chat_id_0'}
            return response_mock(json={'id': 'task_id_0'})
        if 'task_id_0/update_meta' in url:
            request_data['update_meta'] = sorted(
                request_data['update_meta'],
                key=lambda record: record['field_name'],
            )
            update_meta = [
                {
                    'change_type': 'set',
                    'field_name': 'page',
                    'value': message['recipient']['id'],
                },
                {
                    'change_type': 'set',
                    'field_name': 'page_name',
                    'value': 'name',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_id',
                    'value': message['sender']['id'],
                },
            ]
            if not bad_user:
                update_meta.append(
                    {
                        'change_type': 'set',
                        'field_name': 'user_name',
                        'value': 'name',
                    },
                )
            assert request_data == {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'facebook_task'},
                ],
                'update_meta': sorted(
                    update_meta, key=lambda record: record['field_name'],
                ),
            }
            return response_mock(json={})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        return response_mock(json={'id': 'chat_id_0'})

    response = await taxi_sm_monitor_client.post(
        '/webhook/facebook',
        json=data,
        headers={'X-Hub-Signature': 'sha1=%s' % message_hash},
    )
    assert response.status == http.HTTPStatus.OK


async def test_webhook_forbidden(taxi_sm_monitor_client):

    response = await taxi_sm_monitor_client.post(
        '/webhook/facebook',
        json={},
        headers={'X-Hub-Signature': 'sha1=test_hash'},
    )
    assert response.status == http.HTTPStatus.FORBIDDEN
