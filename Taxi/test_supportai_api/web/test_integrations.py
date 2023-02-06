# pylint: disable=too-many-lines
# pylint: disable=cell-var-from-loop
import copy
import datetime
import json
import typing as tp

from aiohttp import web
import pytest

from supportai_api.integrations import usedesk

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql(
        'supportai_api_tokens', files=['integrations_tokens.sql'],
    ),
]


async def test_new_integration(web_app_client, mockserver):
    queries = [
        '/supportai-api/v1/external/new_integrator',
        '/supportai-api/v1/external/new_integrator/action_id',
        '/supportai-api/v1/external/new_integrator/action_id/new_project',
        '/supportai-api/v1/external/new_integrator/action_id?extra_param=1',
    ]

    for query in queries:
        for pass_project in (True, False):
            for pass_auth in (True, False):
                params = {}
                if pass_project:
                    params['project_id'] = 'new_project'
                headers = {'X-Real-IP': '185.39.80.146'}
                if pass_auth:
                    headers['X-Custom-Auth-Header'] = 'XXX'
                response = await web_app_client.post(
                    query,
                    params={'project_id': 'new_project'},
                    headers=headers,
                    data=json.dumps(
                        {
                            'someChatText': 'help',
                            'someUserId': '79029992330',
                            'someConversationId': (
                                'b7c3ef63-4d01-4fa7-a141-8528151115dd'
                            ),
                        },
                    ),
                )
                assert response.status == 200
                content = await response.json()
                assert content == {}


async def test_livetex(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/livetex?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'searchText': 'Bla bla',
            'channelType': 'channel',
            'visitorId': 'visitor',
            'conversationId': 'new',
        },
    )
    assert response.status == 200


async def test_alice_reply(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'hello', 'texts': ['hello']},
                'features': {
                    'most_probable_topic': 'topic',
                    'probabilities': [],
                    'features': [{'key': 'alice_state', 'value': 1}],
                },
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/alice?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'request': {'type': 'SimpleUtterance', 'command': 'Приветик'},
            'session': {
                'session_id': '12345',
                'application': {'application_id': '54321'},
            },
            'version': '1.0',
        },
    )

    assert response.status == 200
    data = await response.json()

    assert data['response']['tts'] == 'hello'
    assert data['response']['text'] == 'hello'
    assert data['state']['user_state_update'] == {'alice_state': 1}


async def test_alice_image(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': '12', 'texts': ['12']},
                'tag': {'add': ['image']},
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/alice?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'request': {'type': 'SimpleUtterance', 'command': 'Приветик'},
            'session': {
                'session_id': '12345',
                'application': {'application_id': '54321'},
            },
            'version': '1.0',
        },
    )

    assert response.status == 200
    data = await response.json()

    assert data['response']['text'] == ''
    assert data['response']['card']['type'] == 'BigImage'
    assert data['response']['card']['image_id'] == '12'
    assert data['response']['card']['button']['text'] == 'Продолжить'


async def test_pyrus_pulse(web_app_client, mockserver, monkeypatch):
    response = await web_app_client.get(
        '/supportai-api/v1/pyrus/pulse', headers={'x-pyrus-sig': '12345'},
    )

    assert response.status == 200


async def test_pyrus_authorize(web_app_client, mockserver, monkeypatch):
    monkeypatch.setattr('hmac.compare_digest', lambda x, y: True)

    response = await web_app_client.post(
        '/supportai-api/v1/pyrus/authorize',
        headers={'x-pyrus-sig': '12345'},
        json={
            'credentials': [
                {'code': 'project_slug', 'value': 'pyrus_project'},
                {'code': 'token', 'value': 'token'},
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'account_id': 'pyrus_project',
        'account_name': 'pyrus_project',
    }


async def test_pyrus_toggle(web_app_client, mockserver, monkeypatch):
    monkeypatch.setattr('hmac.compare_digest', lambda x, y: True)

    response = await web_app_client.post(
        '/supportai-api/v1/pyrus/toggle',
        headers={'x-pyrus-sig': '12345'},
        json={
            'credentials': [
                {'code': 'project_slug', 'value': 'pyrus_project'},
                {'code': 'token', 'value': 'token'},
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {}


@pytest.mark.config(
    SUPPORTAI_API_PYRUS_CLIENTS={
        'projects': [
            {'project_slug': 'pyrus_project', 'request_codes': ['Message']},
        ],
    },
)
async def test_pyrus_event(web_app_client, mockserver, monkeypatch):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    monkeypatch.setattr('hmac.compare_digest', lambda x, y: True)

    auth_call_counter = 0

    @mockserver.json_handler('/pyrus/auth')
    async def _(request):
        nonlocal auth_call_counter
        auth_call_counter += 1

        assert request.json['security_key'] == 'secret_key'
        assert request.json['login'] == 'test@mail.com'

        return web.json_response(status=200, data={'access_token': '12345'})

    addcomment_call_counter = 0

    @mockserver.json_handler('/pyrus/integrations/addcomment')
    async def _(request):
        nonlocal addcomment_call_counter
        addcomment_call_counter += 1

        assert request.headers['Authorization'] == 'Bearer 12345'
        assert request.json['account_id'] == 'pyrus_project'
        assert request.json['comment_text'] == 'hello'
        assert request.json['task_id'] == 87654321
        assert request.json['send_to_external_channels'] is True

        return web.json_response(status=200, data={'message_id': '111'})

    response = await web_app_client.post(
        '/supportai-api/v1/pyrus/event',
        headers={'x-pyrus-sig': '12345'},
        json={
            'credentials': [
                {'code': 'project_slug', 'value': 'pyrus_project'},
                {'code': 'token', 'value': 'token'},
            ],
            'task_id': 87654321,
            'mappings': [{'code': 'Message', 'value': 'Привет totalchest'}],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {}

    assert auth_call_counter == 1
    assert addcomment_call_counter == 1


@pytest.mark.parametrize(
    ['payload', 'text'],
    [
        ({'text': 'Привет', 'type': 'text'}, 'Привет'),
        ({'longitude': 1, 'latitude': 2, 'type': 'location'}, 'LOCATION'),
    ],
)
async def test_messenger_send(web_app_client, mockserver, payload, text):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert request.json['dialog']['messages'][0]['text'] == text
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    send_message_counter = 0

    @mockserver.json_handler('/messenger/v1/send')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1

        assert request.json['service'] == 'supportai'
        assert request.json['account'] == 'project'
        assert request.json['payload']['text'] == 'hello'

        return web.json_response(status=200, data={'message_id': '111'})

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal/messenger',
        json={
            'payload': payload,
            'received_at': '2018-12-19 09:26:03.478039',
            'phone_id': '12345',
            'account': 'project',
            'service': 'supportai',
            'channel': 'TotalChest',
            'message_id': '54321',
        },
    )
    assert response.status == 200
    assert send_message_counter == 1


async def test_messenger_buttons(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'hello', 'texts': ['hello']},
                'buttons_block': {
                    'buttons': [
                        {'text': 'totalchest 1'},
                        {'text': 'totalchest 2'},
                    ],
                },
                'features': {
                    'probabilities': [],
                    'features': [
                        {'key': 'buttons_list_title', 'value': 'Some title'},
                    ],
                },
            },
        )

    send_message_counter = 0

    @mockserver.json_handler('/messenger/v1/send')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1

        assert request.json['service'] == 'supportai'
        assert request.json['account'] == 'project'
        assert request.json['payload']['text'] == 'hello'
        assert request.json['allowed_replies']['type'] == 'list'
        assert request.json['allowed_replies']['title'] == 'Some title'
        assert (
            len(request.json['allowed_replies']['sections'][0]['items']) == 2
        )

        return web.json_response(status=200, data={'message_id': '111'})

    response = await web_app_client.post(
        '/supportai-api/v1/support_internal/messenger',
        json={
            'payload': {'text': 'Привет', 'type': 'text'},
            'received_at': '2018-12-19 09:26:03.478039',
            'phone_id': '12345',
            'account': 'project',
            'service': 'supportai',
            'channel': 'TotalChest',
            'message_id': '54321',
        },
    )
    assert response.status == 200
    assert send_message_counter == 1


async def test_freshdesk_reply(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    @mockserver.json_handler('/freshdesk/api/v2/tickets/123/reply')
    async def _(request):
        assert request.json['body'] == 'hello'

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/freshdesk?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '123',
            'dialog': {'messages': [{'text': 'привет', 'author': 'user'}]},
            'features': [],
        },
    )

    assert response.status == 200


async def test_freshdesk_forward(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data={'forward': {'line': '12'}})

    @mockserver.json_handler('/freshdesk/api/v2/tickets/123')
    async def _(request):
        assert request.json['responder_id'] == 12

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/freshdesk?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '123',
            'dialog': {'messages': [{'text': 'привет', 'author': 'user'}]},
            'features': [],
        },
    )

    assert response.status == 200


async def test_freshchat_reply(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    @mockserver.json_handler('freshchat/v2/conversations/12345/messages')
    async def _(request):
        assert request.json['message_parts'][0]['text']['content'] == 'hello'

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/freshchat?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'actor': {'actor_type': 'user'},
            'action': 'message_create',
            'data': {
                'message': {
                    'message_parts': [{'text': {'content': 'Привет'}}],
                    'conversation_id': '12345',
                },
            },
        },
    )

    assert response.status == 200


async def test_freshchat_forward(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data={'forward': {'line': '12'}})

    @mockserver.json_handler('freshchat/v2/conversations/12345')
    async def _(request):
        assert request.headers['Authorization'] == 'Bearer token'
        assert request.json['assigned_group_id'] == '12'
        assert request.json['status'] == 'assigned'

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/freshchat?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'actor': {'actor_type': 'user'},
            'action': 'message_create',
            'data': {
                'message': {
                    'message_parts': [{'text': {'content': 'Привет'}}],
                    'conversation_id': '12345',
                },
            },
        },
    )

    assert response.status == 200


async def test_freshchat_resolution_action(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        assert len(request.json['features']) == 1
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/external/freshchat?project_id=new_project',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'actor': {'actor_type': 'agent'},
            'action': 'conversation_resolution',
            'data': {
                'resolve': {'conversation': {'conversation_id': '12345'}},
            },
        },
    )

    assert response.status == 200


async def test_edna_init(web_app_client, mockserver):
    response = await web_app_client.post(
        '/supportai-api/v1/external/edna/init/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'action': 'INIT_CHAT',
            'threadsClientId': 1,
            'channelInfo': {'channelType': 'MOBILE', 'authorized': True},
            'platform': 'iOS',
            'deviceAddress': 'w19k86lcaqrk8zckbuvp3s466dchtl1u9',
            'clientData': {'phone': '88885553535'},
        },
    )
    assert response.status == 200


@pytest.mark.config(SUPPORTAI_API_CONTEXT={'projects': 'all'})
async def test_edna_idle_context_message(web_app_client, mockserver):

    context_storage = {}

    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    # pylint: disable=unused-variable
    async def context_handler(request):
        key = request.query['project_id'] + ':' + request.query['chat_id']
        if request.method == 'GET':
            if key in context_storage:
                return web.json_response(data=context_storage[key])
            return web.json_response(status=204)
        assert False, 'Unsupported method'

    @mockserver.json_handler('/supportai-context/v1/context/record')
    # pylint: disable=unused-variable
    async def context_record_handler(request):
        key = request.query['project_id'] + ':' + request.query['chat_id']

        if request.method == 'POST':

            if key not in context_storage:
                context_storage[key] = {
                    'chat_id': request.query['chat_id'],
                    'created_at': str(datetime.datetime.now()),
                    'dialog': {'messages': []},
                }

            _json = request.json

            context_storage[key]['dialog']['messages'].append(_json)
            return web.json_response(status=200)
        assert False, 'Unsupported method'

    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/edna/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'action': 'MESSAGE',
            'sessionId': '1',
            'questionId': 43,
            'questionIndex': None,
            'receivedAt': '2018-11-13T13:13:11.876Z',
            'text': 'Message',
            'channelInfo': {'channelType': 'MOBILE', 'authorized': True},
            'platform': 'Android',
            'attachments': [
                {
                    'url': 'http://...',
                    'name': 'test.jpg',
                    'type': 'image/jpeg',
                    'size': 256,
                },
            ],
            'clientData': {'phone': '88885553535'},
            'sender': 'ThreadsAPI',
        },
    )
    assert response.status == 200


async def test_edna_message(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/edna/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'action': 'MESSAGE',
            'threadsClientId': 1,
            'sessionId': '1',
            'questionId': 43,
            'questionIndex': None,
            'receivedAt': '2018-11-13T13:13:11.876Z',
            'text': 'Message',
            'channelInfo': {'channelType': 'MOBILE', 'authorized': True},
            'platform': 'Android',
            'attachments': [
                {
                    'url': 'http://...',
                    'name': 'test.jpg',
                    'type': 'image/jpeg',
                    'size': 256,
                },
            ],
            'clientData': {'phone': '88885553535'},
            'sender': 'ThreadsAPI',
        },
    )
    assert response.status == 200
    data = await response.json()
    assert 'text' in data
    assert 'code' in data
    assert data['code'] == 'SUCCESS'


@pytest.mark.parametrize('reply_provided', (True, False))
async def test_edna_buttons(web_app_client, mockserver, reply_provided):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        data = {
            'features': {
                'most_probable_topic': 'topic',
                'probabilities': [],
                'features': [
                    {'key': 'button_1', 'value': 'suggest text 1'},
                    {'key': 'button_2', 'value': 'suggest text 2'},
                    {'key': 'button_3', 'value': 'suggest text 3'},
                ],
            },
        }
        if reply_provided:
            data['reply'] = {'text': 'hello', 'texts': ['hello']}
        return web.json_response(data=data)

    response = await web_app_client.post(
        '/supportai-api/v1/external/edna/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'action': 'MESSAGE',
            'threadsClientId': 1,
            'sessionId': '1',
            'questionId': 43,
            'questionIndex': None,
            'receivedAt': '2018-11-13T13:13:11.876Z',
            'text': 'Message',
            'channelInfo': {'channelType': 'MOBILE', 'authorized': True},
            'platform': 'Android',
            'attachments': [
                {
                    'url': 'http://...',
                    'name': 'test.jpg',
                    'type': 'image/jpeg',
                    'size': 256,
                },
            ],
            'clientData': {'phone': '88885553535'},
            'sender': 'ThreadsAPI',
        },
    )
    assert response.status == 200
    data = await response.json()
    assert 'text' in data
    assert 'code' in data
    assert data['code'] == 'SUCCESS'
    assert 'quickReplies' in data
    assert len(data['quickReplies']) == 3
    for quick_reply in data['quickReplies']:
        assert quick_reply['type'] == 'TEXT'
        assert 'text' in quick_reply


async def test_edna_close(web_app_client, mockserver):
    response = await web_app_client.post(
        '/supportai-api/v1/external/edna/close/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'action': 'WEBVIEW_CLOSED',
            'threadsClientId': 100500,
            'uuid': '1',
            'sender': 'ThreadsAPI',
        },
    )
    assert response.status == 200


@pytest.mark.config(SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []})
async def test_usedesk_creation_ticket(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': None,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 1234,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'ok'


async def test_usedesk_emails_phones_extraction(web_context):
    integration = usedesk.UseDeskIntegration()

    error, supportai_request = await integration.preprocess(
        context=web_context,
        project_id='rencredit_dialog',
        action_id='message',
        body={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': None,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 17593,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [
                {'id': 54, 'name': 'Номер заказа', 'value': '123'},
            ],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )

    assert error is None
    assert supportai_request is not None
    assert supportai_request.features

    features_dict = {
        feature.key: feature.value for feature in supportai_request.features
    }
    assert 'usedesk_phones' in features_dict
    assert 'usedesk_emails' in features_dict
    assert features_dict['usedesk_phones'] == ['79254697403']
    assert features_dict['usedesk_emails'] == [
        'shy@usedesk.ru',
        'ylia-8322247@mail.ru',
    ]


@pytest.mark.parametrize('author', ('user', 'client'))
@pytest.mark.config(SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []})
async def test_usedesk_chat(web_app_client, mockserver, author):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 1962066,
            'text': 'привет',
            'client_id': 4476034,
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'from': author,
            'platform': 'usedesk_tg',
            'secret': '***',
            'ticket': {
                'id': 10264808,
                'status_id': 8,
                'subject': 'Арахис — это орех',
                'client_id': 4367802,
                'assignee_id': None,
                'group': None,
                'last_updated_at': '2018-05-11 14:17:12',
                'channel_id': 4242,
                'email': None,
                'published_at': '2018-05-11 14:17:12',
                'company_id': 155568,
                'additional_id': 23,
                'message': 'Необъяснимо, но факт.',
            },
            'state': 'some state',
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    if author == 'client':
        assert message_response['status'] == 'ok'
    else:
        assert message_response['status'] == 'fail by author'


@pytest.mark.parametrize('type_comment', ('private', 'public'))
@pytest.mark.parametrize('author', ('user', 'client'))
@pytest.mark.config(SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []})
async def test_usedesk_comment_ticket(
        web_app_client, mockserver, author, type_comment,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'comment': {
                'id': 2652657,
                'message': 'New message text',
                'type': type_comment,
                'from': author,
                'user_id': 545,
                'client_id': None,
                'ticket_id': 2261907,
                'is_first': 0,
                'delivered': 0,
                'readed': 0,
                'published_at': '2016-12-17 14:14:37',
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    if (author == 'client') and (type_comment == 'public'):
        assert message_response['status'] == 'ok'
    else:
        assert message_response['status'] == 'fail by author'


@pytest.mark.config(SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []})
async def test_usedesk_rate_ticket(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'csi': {
                'id': 2652657,
                'user_id': 545,
                'client_id': 123213,
                'ticket_id': 2261907,
                'rating': 3,
                'company_id': 456,
                'ticket_comment_id': 2321,
                'comment': 'New message text',
                'created_at': '2016-12-17 14:14:37',
                'updated_at': '2016-12-17 14:14:37',
            },
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'ok'


@pytest.mark.parametrize(
    'first_message',
    (
        'вопрос по заказу',
        'вопрос по наличию',
        'нужна консультация по товару',
        '/start',
    ),
)
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {
                'project_id': 'rencredit_dialog',
                'feature_filters': [],
                'banned_first_messages': [
                    'вопрос по заказу',
                    'вопрос по наличию',
                    'нужна консультация по товару',
                    '/start',
                ],
            },
        ],
    },
)
async def test_usedesk_chat_banned_first_message(
        web_app_client, mockserver, first_message,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 1962066,
            'text': first_message,
            'client_id': 4476034,
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'from': 'client',
            'platform': 'usedesk_tg',
            'secret': '***',
            'ticket': {
                'id': 10264808,
                'status_id': 8,
                'subject': 'Арахис — это орех',
                'client_id': 4367802,
                'assignee_id': None,
                'group': None,
                'last_updated_at': '2018-05-11 14:17:12',
                'channel_id': 4242,
                'email': None,
                'published_at': '2018-05-11 14:17:12',
                'company_id': 155568,
                'additional_id': 23,
                'message': 'Необъяснимо, но факт.',
            },
            'state': 'some state',
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'fail first message'


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {
                'project_id': 'rencredit_dialog',
                'feature_filters': [
                    {
                        'key': 'ticket_channel_id',
                        'forbidden_values': ['17591'],
                    },
                ],
                'banned_first_messages': ['/start'],
            },
        ],
    },
)
async def test_usedesk_chat_banned_channel_id(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '0.0.0.0'},
        json={
            'chat_id': 1962066,
            'text': 'привет',
            'client_id': 4476034,
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'from': 'client',
            'platform': 'usedesk_tg',
            'secret': '***',
            'ticket': {
                'id': 10264808,
                'status_id': 8,
                'subject': 'Арахис — это орех',
                'client_id': 4367802,
                'assignee_id': None,
                'group': None,
                'last_updated_at': '2018-05-11 14:17:12',
                'channel_id': 17591,
                'email': None,
                'published_at': '2018-05-11 14:17:12',
                'company_id': 155568,
                'additional_id': 23,
                'message': 'Необъяснимо, но факт.',
            },
            'state': 'some state',
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'fail by feature ticket_channel_id'


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {'project_id': 'rencredit_dialog', 'filter_by_assignee': True},
        ],
    },
)
async def test_usedesk_ticket_filter_assignee_id(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': 6666,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 17591,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'dialog not assigned to supportai'


@pytest.mark.parametrize('config_path', ['trigger_usedesk.json'])
@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {'project_id': 'rencredit_dialog', 'filter_by_assignee': True},
        ],
    },
)
async def test_usedesk_ticket_trigger(
        web_app_client, config_path, load_json, mockserver,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    json_raw = load_json(config_path)

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json=json_raw,
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'ok'


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {'project_id': 'rencredit_dialog', 'filter_by_assignee': True},
        ],
    },
)
async def test_usedesk_ticket_assignee_trigger(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'trigger': {
                'id': 44749222,
                'ticket_id': 94677581,
                'data': [
                    {
                        'target': 'assignee_id',
                        'value': '196336',
                        'old_value': None,
                    },
                ],
            },
            'secret': '7f8f37d1010ff338cf816206aa46bd34d3cfb968',
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'dialog was assigned not to supportai'


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {
                'project_id': 'rencredit_dialog',
                'feature_filters': [
                    {
                        'key': 'ticket_channel_id',
                        'forbidden_values': ['17591'],
                    },
                ],
                'banned_first_messages': ['/start'],
            },
        ],
    },
)
async def test_usedesk_ticket_banned_channel_id(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': None,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 17591,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'fail by feature ticket_channel_id'


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {
                'project_id': 'rencredit_dialog',
                'feature_filters': [
                    {
                        'key': 'ticket_channel_id',
                        'forbidden_values': ['17591'],
                    },
                ],
                'banned_first_messages': ['/start'],
            },
        ],
    },
)
async def test_usedesk_ticket_banned_channel_id_ok(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': None,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 17593,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert 'status' in message_response
    assert message_response['status'] == 'ok'


async def test_usedesk_transliterate_features_key(web_context):
    integration = usedesk.UseDeskIntegration()

    error, supportai_request = await integration.preprocess(
        context=web_context,
        project_id='rencredit_dialog',
        action_id='message',
        body={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'ticket': {
                'id': 2261907,
                'status_id': 1,
                'subject': 'First msg',
                'client_id': 242630,
                'assignee_id': None,
                'group': '0',
                'last_updated_at': '2016-12-17 14:07:33',
                'channel_id': 17593,
                'email': 'jon@bonjovi.com',
                'published_at': '2016-12-17 14:07:33',
                'company_id': 153561,
                'additional_id': '123Ca344',
                'message': 'Test',
            },
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
            'custom_fields': [
                {'id': 54, 'name': 'Номер заказа', 'value': '123'},
            ],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
        },
    )

    assert error is None
    assert supportai_request is not None
    assert supportai_request.features

    features_dict = {
        feature.key: feature.value for feature in supportai_request.features
    }
    assert 'usedesk_feature_Nomer_zakaza' in features_dict
    assert features_dict['usedesk_feature_Nomer_zakaza'] == '123'
    assert 'Номер заказа' not in features_dict


async def test_webim_several_replies(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello[NEW]how are you?',
                    'texts': ['hello[NEW]how are you?'],
                },
            },
        )

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'event': 'new_message',
            'chat_id': 12345,
            'message': {'kind': 'visitor', 'text': 'hello'},
        },
    )
    assert counter == 2
    assert response.status == 200
    message_response = await response.json()
    assert message_response['result'] == 'ok'


async def test_webim_single_reply(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
            },
        )

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'event': 'new_message',
            'chat_id': 12345,
            'message': {'kind': 'visitor', 'text': 'hello'},
        },
    )
    assert counter == 1
    assert response.status == 200
    message_response = await response.json()
    assert message_response['result'] == 'ok'


async def test_webim_close_chat(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
                'close': {},
            },
        )

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        return web.json_response(data={})

    @mockserver.json_handler('/detmir-webim/api/bot/v2/close_chat')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'event': 'new_message',
            'chat_id': 12345,
            'message': {'kind': 'visitor', 'text': 'hello'},
        },
    )
    assert response.status == 200
    message_response = await response.json()
    assert message_response['result'] == 'ok'

    assert counter == 1


async def test_webim_set_category(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
                'features': {
                    'features': [
                        {'key': 'webim_ticket_category', 'value': 'topic1'},
                        {'key': 'webim_ticket_subcategory', 'value': 'topic2'},
                    ],
                    'probabilities': [],
                },
            },
        )

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        return web.json_response(data={})

    @mockserver.json_handler('/detmir-webim/api/bot/v2/set_category')
    async def _(request):
        assert request.json['chat_id'] == 12345
        assert request.json['category'] == 'topic1'
        assert request.json['subcategory'] == 'topic2'
        return web.json_response(data={})

    response = await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'event': 'new_message',
            'chat_id': 12345,
            'message': {'kind': 'visitor', 'text': 'hello'},
        },
    )

    assert response.status == 200
    message_response = await response.json()
    assert message_response['result'] == 'ok'


async def test_omnidesk_single_reply(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
            },
        )

    @mockserver.json_handler('/omnidesk/api/cases/123/messages.json')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(status=201)

    response = await web_app_client.post(
        '/supportai-api/v1/external/omnidesk/_/justschool_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '123',
            'dialog': {'messages': [{'text': 'привет', 'author': 'user'}]},
            'features': [{'key': 'user_id', 'value': 123}],
        },
    )
    assert response.status == 200
    assert counter == 1


async def test_omnidesk_several_replies(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello[NEW] how are you?',
                    'texts': ['hello[NEW] how are you?'],
                },
            },
        )

    @mockserver.json_handler('/omnidesk/api/cases/123/messages.json')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(status=201)

    response = await web_app_client.post(
        '/supportai-api/v1/external/omnidesk/_/justschool_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '123',
            'dialog': {'messages': [{'text': 'привет', 'author': 'user'}]},
            'features': [{'key': 'user_id', 'value': 123}],
        },
    )
    assert response.status == 200
    assert counter == 2


async def test_true_chat_id_while_creating_response(
        web_app_client, mockserver,
):
    counter = 0
    ticket_id: tp.Optional[str] = None

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
            },
        )

    @mockserver.json_handler('/usedesk/create/comment')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    @mockserver.json_handler('/usedesk/update/ticket')
    async def _(request):
        nonlocal counter
        nonlocal ticket_id
        counter += 1

        request_body = request.json
        ticket_id = request_body['ticket_id']
        return web.json_response(data={'status': 'success'})

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/get_message/muztorg_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': 'pass',
            'comment': {
                'id': 2652657,
                'message': 'New message text',
                'type': 'public',
                'from': 'client',
                'user_id': 545,
                'client_id': None,
                'ticket_id': 2261907,
                'is_first': 0,
                'delivered': 0,
                'readed': 0,
                'published_at': '2016-12-17 14:14:37',
                'files': [],
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
        },
    )
    assert counter == 2
    assert ticket_id == '2261907'
    assert response.status == 200


async def test_usedesk_single_comment(web_app_client, mockserver):
    counter = 0
    topic_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
                'features': {
                    'probabilities': [],
                    'features': [
                        {'key': 'usedesk_ticket_topic', 'value': 'Тематика'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/usedesk/create/comment')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    @mockserver.json_handler('/usedesk/update/ticket')
    async def _(request):
        nonlocal counter
        nonlocal topic_counter
        counter += 1

        if 'subject' in request.json:
            topic_counter += 1
            assert request.json['subject'] == 'Тематика'

        return web.json_response(data={'status': 'success'})

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/get_message/muztorg_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 6514612,
            'text': 'Нет в наличии, к сожалению ',
            'client_id': 39837843,
            'client': {
                'id': 39837843,
                'name': 'Сергей Карасик',
                'avatar': None,
                'note': '',
                'emails': [],
                'phones': [],
                'additional_ids': [],
            },
            'from': 'client',
            'platform': 'vk',
            'secret': '1a6752f084f4a1e53f192b2f5f3e6dc7a42d43d1',
            'ticket': {
                'id': 56079864,
                'status_id': 1,
                'subject': 'Chat',
                'client_id': 39837843,
                'assignee_id': 7160,
                'group': 1128,
                'last_updated_at': '2021-07-19 16:44:14',
                'channel_id': 20381,
                'email': '',
                'published_at': '2021-07-19 16:43:31',
                'company_id': 153845,
                'additional_id': 'abc',
                'message': 'Здравствуйте',
            },
            'state': None,
        },
    )
    assert response.status == 200
    assert counter == 3
    assert topic_counter == 0


async def test_usedesk_several_comments(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello [NEW] how are you?',
                    'texts': ['hello [NEW] how are you?'],
                },
            },
        )

    @mockserver.json_handler('/usedesk/create/comment')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    @mockserver.json_handler('/usedesk/update/ticket')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/get_message/muztorg_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 6514612,
            'text': 'Нет в наличии, к сожалению ',
            'client_id': 39837843,
            'client': {
                'id': 39837843,
                'name': 'Сергей Карасик',
                'avatar': None,
                'note': '',
                'emails': [],
                'phones': [],
                'additional_ids': [],
            },
            'from': 'client',
            'platform': 'vk',
            'secret': '1a6752f084f4a1e53f192b2f5f3e6dc7a42d43d1',
            'ticket': {
                'id': 56079864,
                'status_id': 1,
                'subject': 'Chat',
                'client_id': 39837843,
                'assignee_id': 7160,
                'group': 1128,
                'last_updated_at': '2021-07-19 16:44:14',
                'channel_id': 20381,
                'email': '',
                'published_at': '2021-07-19 16:43:31',
                'company_id': 153845,
                'additional_id': 'abc',
                'message': 'Здравствуйте',
            },
            'state': None,
        },
    )
    assert response.status == 200
    assert counter == 3


async def test_usedesk_several_updates(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello [NEW] how are you?',
                    'texts': ['hello [NEW] how are you?'],
                    'tags': ['status_open', 'status_close'],
                },
            },
        )

    @mockserver.json_handler('/usedesk/create/comment')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    @mockserver.json_handler('/usedesk/update/ticket')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/get_message/muztorg_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 6514612,
            'text': 'Нет в наличии, к сожалению ',
            'client_id': 39837843,
            'client': {
                'id': 39837843,
                'name': 'Сергей Карасик',
                'avatar': None,
                'note': '',
                'emails': [],
                'phones': [],
                'additional_ids': [],
            },
            'from': 'client',
            'platform': 'vk',
            'secret': '1a6752f084f4a1e53f192b2f5f3e6dc7a42d43d1',
            'ticket': {
                'id': 56079864,
                'status_id': 1,
                'subject': 'Chat',
                'client_id': 39837843,
                'assignee_id': 7160,
                'group': 1128,
                'last_updated_at': '2021-07-19 16:44:14',
                'channel_id': 20381,
                'email': '',
                'published_at': '2021-07-19 16:43:31',
                'company_id': 153845,
                'additional_id': 'abc',
                'message': 'Здравствуйте',
            },
            'state': None,
        },
    )

    assert response.status == 200
    assert counter == 3


async def test_usedesk_several_comments_unsuccess(web_app_client, mockserver):
    counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello [NEW] how are you?',
                    'texts': ['hello [NEW] how are you?'],
                },
            },
        )

    @mockserver.json_handler('/usedesk/create/comment')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={})

    @mockserver.json_handler('/usedesk/update/ticket')
    async def _(request):
        nonlocal counter
        counter += 1
        return web.json_response(data={'status': 'success'})

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/get_message/muztorg_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': 6514612,
            'text': 'Нет в наличии, к сожалению ',
            'client_id': 39837843,
            'client': {
                'id': 39837843,
                'name': 'Сергей Карасик',
                'avatar': None,
                'note': '',
                'emails': [],
                'phones': [],
                'additional_ids': [],
            },
            'from': 'client',
            'platform': 'vk',
            'secret': '1a6752f084f4a1e53f192b2f5f3e6dc7a42d43d1',
            'ticket': {
                'id': 56079864,
                'status_id': 1,
                'subject': 'Chat',
                'client_id': 39837843,
                'assignee_id': 7160,
                'group': 1128,
                'last_updated_at': '2021-07-19 16:44:14',
                'channel_id': 20381,
                'email': '',
                'published_at': '2021-07-19 16:43:31',
                'company_id': 153845,
                'additional_id': 'abc',
                'message': 'Здравствуйте',
            },
            'state': None,
        },
    )
    assert response.status == 200
    assert counter == 2


async def test_helpdeskeddy_single_reply(web_app_client, mockserver):
    send_message_counter = 0
    forward_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?',
                    'texts': ['hello, how are you?'],
                },
            },
        )

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234/posts/')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1
        return web.json_response(status=200)

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234')
    async def _(request):
        nonlocal forward_counter
        forward_counter += 1
        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514610',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '1234'},
            ],
        },
    )
    assert response.status == 200
    assert send_message_counter == 1
    assert forward_counter == 0


async def test_helpdeskeddy_several_replies(web_app_client, mockserver):
    send_message_counter = 0
    forward_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello [NEW] how are you?',
                    'texts': ['hello [NEW] how are you?'],
                },
            },
        )

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234/posts/')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1
        return web.json_response(status=200)

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234')
    async def _(request):
        nonlocal forward_counter
        forward_counter += 1
        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514611',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '1234'},
            ],
        },
    )
    assert response.status == 200
    assert send_message_counter == 2
    assert forward_counter == 0


async def test_helpdeskeddy_forward_to_operator(web_app_client, mockserver):
    send_message_counter = 0
    forward_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(data={})

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234/posts/')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1
        return web.json_response(status=200)

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234')
    async def _(request):
        nonlocal forward_counter
        forward_counter += 1
        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514612',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '1234'},
            ],
        },
    )
    assert response.status == 200
    assert send_message_counter == 0
    assert forward_counter == 1


async def test_helpdeskeddy_set_topic(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'features': {
                    'most_probable_topic': '',
                    'probabilities': [],
                    'features': [
                        {
                            'key': 'hde_topic',
                            'value': (
                                '{"1":{"1":"1308", "2":"1309", "3":"2341"}}'
                            ),
                        },
                    ],
                },
            },
        )

    @mockserver.json_handler(
        '/helpdeskeddy-flysmartavia/api/v2/tickets/422439',
    )
    async def _(request):
        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/fly_smart_avia_dialog',  # noqa
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514612',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '422439'},
            ],
        },
    )
    assert response.status == 200


async def test_helpdeskeddy_line_forwarding(web_app_client, mockserver):

    send_message_counter = 0
    forward_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'хорошо, я вас понял, сейчас позову оператора',
                    'texts': ['хорошо, я вас понял, сейчас позову оператора'],
                },
                'forward': {'line': '1'},
            },
        )

    @mockserver.json_handler(
        '/helpdeskeddy-flysmartavia/api/v2/tickets/422439',
    )
    async def _(request):
        nonlocal forward_counter
        forward_counter += 1
        return web.json_response(status=200)

    @mockserver.json_handler(
        '/helpdeskeddy-flysmartavia/api/v2/tickets/422439/posts/',
    )
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1
        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/fly_smart_avia_dialog',  # noqa
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514612',
            'dialog': {
                'messages': [
                    {
                        'text': (
                            'А ну-ка железка переключи меня на оператора!'
                        ),  # noqa
                        'author': 'user',
                    },
                ],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '422439'},
            ],
        },
    )

    assert response.status == 200
    assert send_message_counter == 1
    assert forward_counter == 1


@pytest.mark.parametrize('is_public', [True, False])
async def test_zendesk(web_app_client, mockserver, is_public):
    send_message_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'hello, how are you?[NEW]Your problem is solved!',
                    'texts': [
                        'hello, how are you?',
                        'Your problem is solved!',
                    ],
                },
                'tag': {
                    'add': [] if is_public else ['zendesk_private_comment'],
                },
                'features': {
                    'most_probable_topic': '',
                    'probabilities': [],
                    'features': [
                        {'key': 'zendesk_custom_field_123', 'value': '123'},
                        {'key': 'zendesk_ticket_type', 'value': 'question'},
                        {'key': 'some_feature', 'value': 'some_value'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/zendesk/api/v2/tickets/6514610.json')
    async def _(request):
        nonlocal send_message_counter

        if send_message_counter == 0:
            assert 'custom_fields' in request.json['ticket']
            assert len(request.json['ticket']['custom_fields']) == 1
            assert request.json['ticket']['custom_fields'][0]['id'] == 123
            assert request.json['ticket']['custom_fields'][0]['value'] == '123'
            assert request.json['ticket']['type'] == 'question'
        else:
            assert 'comment' in request.json['ticket']
            assert request.json['ticket']['comment']['public'] == is_public

        send_message_counter += 1

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/zendesk/ticket/litres_dialog',
        headers={'X-Real-IP': '1.2.3.4'},
        json={
            'chat_id': '6514610',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [{'key': 'name', 'value': 'Александр'}],
        },
    )
    assert response.status == 200
    assert send_message_counter == 3


async def test_zendesk_only_features(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {'text': '', 'texts': ['']},
                'features': {
                    'most_probable_topic': '',
                    'probabilities': [],
                    'features': [
                        {'key': 'zendesk_custom_field_123', 'value': '123'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/zendesk/api/v2/tickets/6514610.json')
    async def _(request):
        assert 'custom_fields' in request.json['ticket']
        assert len(request.json['ticket']['custom_fields']) == 1
        assert request.json['ticket']['custom_fields'][0]['id'] == 123
        assert request.json['ticket']['custom_fields'][0]['value'] == '123'

        return web.json_response(status=200)

    response = await web_app_client.post(
        '/supportai-api/v1/external/zendesk/ticket/litres_dialog',
        headers={'X-Real-IP': '1.2.3.4'},
        json={
            'chat_id': '6514610',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [{'key': 'name', 'value': 'Александр'}],
        },
    )
    assert response.status == 200


@pytest.mark.parametrize(
    ('forward', 'message_for_forward', 'add_sender_data'),
    [
        (None, None, False),
        (None, None, True),
        ('some_line', '', False),
        ('some_line', 'please, wait for an agent\'s answer', False),
    ],
)
async def test_jivochat(
        web_app_client,
        mockserver,
        forward,
        message_for_forward,
        add_sender_data,
):
    project_id = 'jivochat_project'
    client_id = '12321'
    chat_id = '1111111'
    agents_online = False

    sender_url = 'some/url'
    sender_name = 'Somedict Nameberbatch'
    sender_has_contacts = False

    client_message = 'Hello! Help me!'
    bot_answer = 'Hello! How can I help you?'

    jivochat_request_body = {
        'event': 'CLIENT_MESSAGE',
        'id': '123e4567-e89b-12d3-a456-426655440000',
        'client_id': client_id,
        'chat_id': chat_id,
        'agents_online': agents_online,
        'message': {
            'type': 'TEXT',
            'text': client_message,
            'timestamp': 1583910736,
        },
    }

    if add_sender_data:
        jivochat_request_body['sender'] = {
            'id': int(client_id),
            'name': sender_name,
            'url': sender_url,
            'has_contacts': sender_has_contacts,
        }

    forward_events_stack = ['INVITE_AGENT']
    if forward and message_for_forward:
        forward_events_stack.append('BOT_MESSAGE')

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        assert request.json['dialog']['messages'][0]['text'] == client_message

        request_features = {
            item['key']: item['value'] for item in request.json['features']
        }

        assert request_features.pop('client_id') == client_id
        assert request_features.pop('chat_id') == chat_id
        assert request_features.pop('agents_online') is agents_online

        if add_sender_data:
            assert request_features.pop('sender_id') == int(client_id)
            assert request_features.pop('sender_name') == sender_name
            assert request_features.pop('sender_url') == sender_url
            assert (
                request_features.pop('sender_has_contacts')
                is sender_has_contacts
            )

        assert not request_features

        supportai_response = {
            'reply': {
                'text': bot_answer if not forward else message_for_forward,
            },
            'features': {
                'most_probable_topic': '',
                'probabilities': [],
                'features': [],
            },
        }
        if forward:
            supportai_response['forward'] = {'line': forward}
        return web.json_response(supportai_response)

    @mockserver.json_handler(
        f'jivochat/webhooks/some_bot_provider_id/{project_id}',
    )
    async def _(request):
        assert request.json['chat_id'] == chat_id
        assert request.json['client_id'] == client_id
        if forward:
            assert forward_events_stack
            current_event = forward_events_stack.pop()
            assert request.json['event'] == current_event
            if message_for_forward and current_event == 'BOT_MESSAGE':
                assert 'message' in request.json
                message = request.json['message']
                assert message['type'] == 'TEXT'
                assert message['text'] == message_for_forward
        else:
            assert request.json['event'] == 'BOT_MESSAGE'
            assert 'message' in request.json
            message = request.json['message']
            assert message['type'] == 'TEXT'
            assert message['text'] == bot_answer

        return {}

    response = await web_app_client.post(
        f'supportai-api/v1/jivochat/{project_id}', json=jivochat_request_body,
    )
    assert response.status == 200
    if forward:
        assert not forward_events_stack
    else:
        assert forward_events_stack


async def test_jivochat_forward(web_app_client, mockserver):
    project_id = 'jivochat_project'

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(_):
        assert False

    @mockserver.json_handler(
        f'jivochat/webhooks/some_bot_provider_id/{project_id}',
    )
    async def _(_):
        assert False

    jivochat_request_bodies = [
        {
            'event': 'AGENT_JOINED',
            'id': '123e4567-e89b-12d3-a456-426655440000',
            'chat_id': '1234',
            'client_id': '12321',
        },
        {
            'event': 'AGENT_UNAVAILABLE',
            'id': '123e4567-e89b-12d3-a456-426655440000',
            'chat_id': '1234',
            'client_id': '12321',
        },
        {
            'event': 'CHAT_CLOSED',
            'id': '123e4567-e89b-12d3-a456-426655440000',
            'chat_id': '1234',
            'client_id': '12321',
        },
    ]

    for jivochat_request_body in jivochat_request_bodies:
        response = await web_app_client.post(
            f'supportai-api/v1/jivochat/{project_id}',
            json=jivochat_request_body,
        )
        assert response.status == 200


@pytest.mark.config(
    SUPPORTAI_API_PROJECT_TO_HANDLER={'projects': []},
    SUPPORTAI_API_USEDESK_SETTINGS={
        'projects': [
            {
                'project_id': 'rencredit_dialog',
                'feature_filters': [
                    {
                        'key': 'ticket_channel_id',
                        'forbidden_values': ['17591'],
                    },
                ],
                'banned_first_messages': ['/start'],
            },
        ],
    },
    SUPPORTAI_API_CONTEXT={'projects': 'all'},
)
@pytest.mark.now('2016-12-17 14:14:38')
async def test_usedesk_duplicates(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(
            data={
                'chat_id': '999',
                'created_at': '2016-12-17 14:14:35',
                'dialog': {
                    'messages': [
                        {'text': 'hello, i need some help', 'author': 'user'},
                        {'text': 'how can i help u', 'author': 'ai'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/supportai-context/v1/context/record')
    # pylint: disable=unused-variable
    async def post_context_handler(request):
        return web.json_response(status=200)

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(
            data={
                'reply': {
                    'text': 'i am replying but i should not',
                    'texts': ['i am replying but i should not'],
                },
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/usedesk/message/rencredit_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'secret': '0e8f678d8327eb3292a28c8165957b282a1b2f8b',
            'comment': {
                'id': 2652657,
                'message': 'hello, i need some help',
                'type': 'public',
                'from': 'client',
                'user_id': 545,
                'client_id': None,
                'ticket_id': 2261907,
                'is_first': 0,
                'delivered': 0,
                'readed': 0,
                'published_at': '2016-12-17 14:14:37',
            },
            'custom_fields': [{'id': 54, 'name': 'new item 2', 'value': None}],
            'custom_blocks': [
                {
                    'name': 'Test',
                    'url': 'https://usedesk.ru/',
                    'secret_key': 'dsf4354f=-213sdfasdsa',
                },
            ],
            'client': {
                'id': 32917577,
                'name': 'Юля Шовгеня',
                'avatar': '/upload/avatars/123.jpg',
                'note': 'есть кредит',
                'emails': [
                    {'email': 'shy@usedesk.ru', 'client_id': 32917577},
                    {'email': 'ylia-8322247@mail.ru', 'client_id': 32917577},
                ],
                'phones': [
                    {
                        'phone': '79254697403',
                        'type': 'home',
                        'client_id': 32917577,
                    },
                    {'phone': '', 'type': 'home', 'client_id': 32917577},
                ],
                'additional_ids': [{'value': '99999', 'client_id': 32917577}],
            },
        },
    )
    assert (await response.json()) == {'status': 'ok, not replied'}


@pytest.mark.parametrize('action_type', [None, 'close', 'forward'])
@pytest.mark.parametrize('with_reply', [True, False])
async def test_intercom(
        web_app_client, mockserver, monkeypatch, action_type, with_reply,
):
    monkeypatch.setattr('hmac.compare_digest', lambda x, y: True)

    send_message_counter = 0

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):

        feature_dict = {
            feature['key']: feature['value']
            for feature in request.json['features']
        }

        if not with_reply:
            assert feature_dict['user_email'] == 'test@exmaple.com'
            assert feature_dict['user_some_custom'] == 'value'
        else:
            assert len(request.json['dialog']['messages']) == 2

        assert feature_dict['conversation_tags'] == 'tag1,tag2'

        data = {
            'reply': {
                'text': 'hello, how are you?[NEW]Your problem is solved!',
                'texts': ['hello, how are you?', 'Your problem is solved!'],
            },
            'tag': {'add': ['test']},
            'features': {
                'most_probable_topic': '',
                'probabilities': [],
                'features': [],
            },
        }

        if action_type == 'close':
            data['close'] = {}
        elif action_type == 'forward':
            data['forward'] = {'line': 'test'}

        return web.json_response(data=data)

    @mockserver.json_handler('/intercom/conversations/1234/reply')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1

        assert 'message_type' in request.json
        assert 'type' in request.json
        assert 'admin_id' in request.json
        assert 'body' in request.json

        assert request.json['admin_id'] == 'admin'

        return web.json_response(status=200)

    @mockserver.json_handler('/intercom/conversations/1234/tags')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1

        assert request.json['admin_id'] == 'admin'
        assert request.json['id'] == 'test'

        return web.json_response(status=200)

    @mockserver.json_handler('/intercom/conversations/1234/parts')
    async def _(request):
        nonlocal send_message_counter
        send_message_counter += 1

        assert request.json['admin_id'] == 'admin'
        assert (
            request.json['type'] == 'team'
            if action_type == 'forward'
            else 'admin'
        )
        assert (
            request.json['message_type'] == 'assignment'
            if action_type == 'forward'
            else 'close'
        )

        if action_type == 'forward':
            assert request.json['assignee_id'] == 'test'

        return web.json_response(status=200)

    @mockserver.json_handler('/intercom/contacts/user_id')
    async def _(request):
        return web.json_response(
            status=200,
            data={
                'type': 'contact',
                'id': 'user_id',
                'workspace_id': 'id',
                'external_id': '25',
                'role': 'user',
                'email': 'test@exmaple.com',
                'phone': '+1123456789',
                'name': 'Hoban Washburn',
                'browser': 'chrome',
                'browser_version': '77.0.3865.90',
                'browser_language': 'en',
                'os': 'OS X 10.14.6',
                'android_app_name': 'Test',
                'custom_attributes': {'some_custom': 'value'},
            },
        )

    request = {
        'type': 'notification_event',
        'topic': 'conversation.user.created',
        'id': 'notif_ccd8a4d0-f965-11e3-a367-c779cae3e1b3',
        'app_id': 'a86dr8yl',
        'created_at': 1392731331,
        'delivery_attempts': 1,
        'first_sent_at': 1392731392,
        'data': {
            'item': {
                'type': 'conversation',
                'id': '1234',
                'user': {'type': 'user', 'id': 'user_id'},
                'conversation_message': {
                    'type': 'conversation_message',
                    'id': '1354405662',
                    'subject': '',
                    'body': '<p>У меня есть оформленный заказ</p>',
                    'author': {'type': 'user', 'id': 'user_id'},
                    'attachments': [],
                },
                'conversation_parts': {
                    'conversation_parts': [],
                    'total_count': 1,
                    'type': 'conversation_part.list',
                },
                'tags': {
                    'type': 'tag.list',
                    'tags': [
                        {'type': 'tag', 'id': '1', 'name': 'tag1'},
                        {'type': 'tag', 'id': '2', 'name': 'tag2'},
                    ],
                },
            },
        },
    }

    if with_reply:
        request['data']['item']['conversation_parts'][
            'conversation_parts'
        ].append(
            {
                'assigned_to': None,
                'attachments': [],
                'author': {'id': '815309', 'type': 'bot'},
                'body': 'Hello',
                'created_at': 1539897200,
                'external_id': None,
                'id': '2202737122',
                'notified_at': 1539897200,
                'part_type': 'comment',
                'type': 'conversation_part',
                'updated_at': 1539897200,
                'redacted': False,
            },
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/intercom/conversation/kupibilet_dialog',
        headers={'X-Real-IP': '1.2.3.4', 'X-Hub-Signature': '12345'},
        json=request,
    )
    assert response.status == 200
    assert send_message_counter == 3 if action_type is None else 2


async def test_vk_api(web_app_client, mockserver):
    vk_request = {
        'group_id': 123,
        'type': 'message_new',
        'event_id': '86911221238048a510a582714e80b7c5a20073a6',
        'v': '5.131',
        'object': {
            'message': {
                'date': 1654190300,
                'from_id': 11111,
                'id': 495,
                'out': 0,
                'attachments': [],
                'conversation_message_id': 408,
                'fwd_messages': [],
                'important': False,
                'is_hidden': False,
                'peer_id': 61899449,
                'random_id': 0,
                'text': 'Бот, добрый вечер!',
            },
        },
    }

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def support_handler(request):
        assert request.query['project_id'] == 'some_vk_project'
        request_json = request.json
        assert request_json['chat_id'] == '61899449'
        assert request_json['dialog'] == {
            'messages': [
                {
                    'author': 'user',
                    'text': 'Бот, добрый вечер!',
                    'language': 'ru',
                },
            ],
        }
        request_features = {
            feature['key']: feature['value']
            for feature in request_json['features']
        }
        assert request_features == {
            'message_id': 495,
            'user_id': 11111,
            'peer_id': 61899449,
            'group_id': 123,
            'request_source': 'vk',
        }
        return web.json_response(
            data={'reply': {'text': 'Человек, добрый вечер!'}},
        )

    @mockserver.json_handler('/vk-api/method/messages.send')
    async def vk_handler(request):
        query_params = dict(request.query)
        assert query_params['access_token'] == 'access_token_for_group_123'
        assert query_params['user_id'] == '11111'
        assert 'random_id' in query_params
        assert query_params['peer_id'] == '61899449'
        assert query_params['message'] == 'Человек, добрый вечер!'
        return {}

    response = await web_app_client.post(
        '/supportai-api/v1/external/vk_api?project_id=some_vk_project',
        json=vk_request,
        headers={'X-Real-IP': '0.0.0.0'},
    )
    assert response.status == 200
    assert (await response.read()) == b'ok'
    assert support_handler.times_called == 1
    assert vk_handler.times_called == 1


async def test_vk_bot_confirmation(web_app_client, mockserver):
    vk_request = {'type': 'confirmation', 'group_id': 123}

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def support_handler(_):
        assert False

    @mockserver.json_handler('/vk-api/method/messages.send')
    async def vk_handler(_):
        assert False

    response = await web_app_client.post(
        '/supportai-api/v1/external/vk_api?project_id=some_vk_project',
        json=vk_request,
        headers={'X-Real-IP': '0.0.0.0'},
    )
    assert response.status == 200
    assert (await response.read()) == b'confirmation_code_for_group_123'
    assert support_handler.times_called == 0
    assert vk_handler.times_called == 0


async def test_vk_ignoring_invalid_jsons(web_app_client, mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def support_handler(_):
        assert False

    @mockserver.json_handler('/vk-api/method/messages.send')
    async def vk_handler(_):
        assert False

    good_json = {
        'group_id': 123,
        'type': 'message_new',
        'object': {
            'message': {
                'from_id': 11111,
                'peer_id': 61899449,
                'text': 'Бот, добрый вечер!',
            },
        },
    }

    async def check_response(req_json):
        response = await web_app_client.post(
            '/supportai-api/v1/external/vk_api?project_id=some_vk_project',
            json=req_json,
            headers={'X-Real-IP': '0.0.0.0'},
        )
        assert response.status == 200
        assert (await response.read()) == b'ok'
        assert support_handler.times_called == 0
        assert vk_handler.times_called == 0

    for key in good_json:
        bad_json = copy.deepcopy(good_json)
        bad_json.pop(key)
        await check_response(bad_json)

    for key in good_json['object']['message']:
        bad_json = copy.deepcopy(good_json)
        bad_json['object']['message'].pop(key)
        await check_response(bad_json)

    bad_json = copy.deepcopy(good_json)
    bad_json['type'] = 'unknown_type'
    await check_response(bad_json)


@pytest.mark.parametrize('vk_error_message', ['some error', None])
async def test_vk_sending_buttons(
        web_app_client, mockserver, caplog, vk_error_message,
):
    vk_request = {
        'group_id': 123,
        'type': 'message_new',
        'v': '5.131',
        'object': {
            'message': {
                'from_id': 11111,
                'id': 495,
                'peer_id': 61899449,
                'text': 'Добрый вечер, мистер Бот!',
            },
        },
    }

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def support_handler(_):
        return web.json_response(
            data={
                'reply': {'text': 'Добрый вечер, человек! Выбирай!'},
                'buttons_block': {
                    'buttons': [
                        {'text': 'первый стул'},
                        {'text': 'второй стул'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/vk-api/method/messages.send')
    async def vk_handler(request):
        query_params = dict(request.query)
        assert query_params['access_token'] == 'access_token_for_group_123'
        assert query_params['user_id'] == '11111'
        assert 'random_id' in query_params
        assert query_params['peer_id'] == '61899449'
        assert query_params['message'] == 'Добрый вечер, человек! Выбирай!'
        keyboard = query_params.get('keyboard')
        assert keyboard is not None
        keyboard_object = json.loads(keyboard)
        assert keyboard_object == {
            'one_time': True,
            'buttons': [
                [
                    {
                        'action': {'type': 'text', 'label': 'первый стул'},
                        'color': 'secondary',
                    },
                ],
                [
                    {
                        'action': {'type': 'text', 'label': 'второй стул'},
                        'color': 'secondary',
                    },
                ],
            ],
        }
        return (
            {'error': {'error_code': 5, 'error_msg': vk_error_message}}
            if vk_error_message
            else {}
        )

    response = await web_app_client.post(
        '/supportai-api/v1/external/vk_api?project_id=some_vk_project',
        json=vk_request,
        headers={'X-Real-IP': '0.0.0.0'},
    )
    assert response.status == 200
    assert (await response.read()) == b'ok'
    assert support_handler.times_called == 1
    assert vk_handler.times_called == 1

    error_log_messages = [
        record.getMessage()
        for record in caplog.records
        if record.levelname == 'ERROR'
    ]

    assert len(error_log_messages) == int(vk_error_message is not None)
    if error_log_messages:
        error_message = error_log_messages[0]
        preview, code = error_message.split('Code: ')
        code, message = code.split(', message: ')
        assert preview == 'An error occurred during sending the message. '
        assert code == '5'
        assert message == vk_error_message


async def test_ya_messenger_plain_text(web_app_client, mockserver):
    ya_messenger_request = {
        'message': {
            'from': {
                'is_bot': False,
                'login': 'jeen-jahn',
                'display_name': 'Gleb',
                'id': '63536ba',
            },
            'text': 'hello, bot!',
            'chat': {
                'username': 'should-not-be-used',
                'display_name': 'should-not-be-used',
                'type': 'private',
                'id': '502c9603',
            },
        },
    }

    for idx, project_id in enumerate(('ya_msgr_project', 'detmir_dialog')):

        @mockserver.json_handler('/supportai/supportai/v1/support')
        async def supportai_handler(request):
            if idx == 1:
                assert False
            features = {
                feature['key']: feature['value']
                for feature in request.json['features']
            }
            assert features == {
                'user_login': 'jeen-jahn',
                'user_display_name': 'Gleb',
                'chat_id': '502c9603',
            }
            assert request.query['project_id'] == 'ya_msgr_project'
            assert request.json['chat_id'] == '502c9603'
            assert (
                request.json['dialog']['messages'][0]['text'] == 'hello, bot!'
            )
            return web.json_response(
                data={'reply': {'text': 'good evening, my dear human!'}},
            )

        @mockserver.json_handler('/ya-messenger/bot/sendMessage')
        async def ya_msgr_handler(request):
            if idx == 1:
                assert False
            assert request.headers['Authorization'] == 'Oauth ya_msgr_token'
            assert request.json['chat_id'] == '502c9603'
            assert request.json['text'] == 'good evening, my dear human!'
            return {}

        response = await web_app_client.post(
            f'/supportai-api/v1/external/ya-messenger/webhook/{project_id}',
            json=ya_messenger_request,
            headers={'X-Real-IP': '0.0.0.0'},
        )
        assert response.status == 200

        assert supportai_handler.times_called == int(idx == 0)
        assert ya_msgr_handler.times_called == int(idx == 0)


async def test_ya_messenger_buttons(web_app_client, mockserver):
    ya_messenger_request = {
        'message': {
            'from': {},
            'text': 'hello, bot!',
            'chat': {'id': '502c9603'},
        },
    }

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def supportai_handler(_):
        return web.json_response(
            data={
                'reply': {'text': 'good evening, what are you looking for?'},
                'buttons_block': {
                    'buttons': [{'text': 'option 1'}, {'text': 'option 2'}],
                },
            },
        )

    @mockserver.json_handler('/ya-messenger/bot/sendMessage')
    async def ya_msgr_handler(request):
        assert (
            request.json['text'] == 'good evening, what are you looking for?'
        )
        assert request.json['reply_markup'] == {
            'inline_keyboard': [
                [{'text': 'option 1'}],
                [{'text': 'option 2'}],
            ],
        }
        return {}

    response = await web_app_client.post(
        '/supportai-api/v1/external/ya-messenger/webhook/ya_msgr_project',
        json=ya_messenger_request,
        headers={'X-Real-IP': '0.0.0.0'},
    )
    assert response.status == 200

    assert supportai_handler.times_called == 1
    assert ya_msgr_handler.times_called == 1


async def test_ya_messenger_error_response(web_app_client, mockserver, caplog):
    ya_messenger_request = {
        'message': {
            'from': {},
            'text': 'hello, bot!',
            'chat': {'id': '502c9603'},
        },
    }

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(_):
        return web.json_response(data={'reply': {'text': 'yeah'}})

    responses_cases = [
        #  HTTP code, error code, error message
        (200, None, None),
        (400, 'bad_request', 'The request is bad!'),
        (401, 'not_authorized', None),
        (403, None, None),
        (404, None, 'not found, my friend'),
        (414, None, None),
    ]

    for status, error_code, error in responses_cases:

        @mockserver.json_handler('/ya-messenger/bot/sendMessage')
        # pylint: disable=undefined-loop-variable
        async def _(_):
            response_body = {}
            if error_code:
                response_body['error_code'] = error_code
            if error:
                response_body['error'] = error
            return web.json_response(status=status, data=response_body)

        response = await web_app_client.post(
            '/supportai-api/v1/external/ya-messenger/webhook/ya_msgr_project',
            json=ya_messenger_request,
            headers={'X-Real-IP': '0.0.0.0'},
        )
        assert response.status == 200

    error_log_messages = [
        record.getMessage()
        for record in caplog.records
        if record.levelname == 'ERROR'
    ]
    assert len(error_log_messages) == 5

    for log_message, (status, error_code, error_message) in zip(
            error_log_messages, responses_cases[1:],
    ):
        expected_log_message = ''
        if error_code:
            expected_log_message += f'Error code: {error_code}. '
        if error_message:
            expected_log_message += f'Error message: {error_message}'
        if status == 414:
            expected_log_message = ''

        expected_log_message = (
            f'The request to Ya Messenger finished with status {status}. '
            f'{expected_log_message}'
        )
        assert log_message == expected_log_message
