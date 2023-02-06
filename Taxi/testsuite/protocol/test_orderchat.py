import json

import pytest


chat_id = '8c83b49edb274ce0992f337061047370'


@pytest.mark.parametrize(
    'upd_request, history_request, history_response, expected_response',
    [
        (
            {'newest_message_id': '2'},
            None,
            {
                'updates': [
                    {
                        'created_date': 'cd',
                        'message': {
                            'id': '21',
                            'text': 'history message',
                            'sender': {'id': 'sender_id', 'role': 'client'},
                            'language': 'ru',
                            'translations': [
                                {'language': 'en', 'text': 'en text'},
                            ],
                        },
                        'newest_message_id': 'newest_id',
                    },
                ],
                'participants': [
                    {
                        'id': 'sender_id',
                        'role': 'client',
                        'active': True,
                        'metadata': {
                            'translation_settings': {
                                'to': 'ru',
                                'do_not_translate': [],
                            },
                        },
                    },
                    {
                        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                        'role': 'client',
                        'active': True,
                        'metadata': {
                            'translation_settings': {
                                'to': 'en',
                                'do_not_translate': [],
                            },
                        },
                    },
                ],
                'metadata': {'can_translate': True},
                'newest_message_id': '22',
                'total': 1,
                'all_languages': ['ru', 'en'],
                'can_translate': True,
            },
            {
                'newest_message_id': '22',
                'messages': [
                    {
                        'id': '21',
                        'created_date': 'cd',
                        'text': 'history message',
                        'sender': {'nickname': 'sender_id', 'role': 'client'},
                        'language': 'ru',
                        'translation': {'language': 'en', 'text': 'en text'},
                    },
                ],
                'translation_settings': {'to': 'en', 'do_not_translate': []},
                'all_languages': ['ru', 'en'],
                'can_translate': True,
            },
        ),
        (
            {'newest_message_id': '2'},
            None,
            {
                'updates': [
                    {
                        'created_date': 'cd',
                        'message': {
                            'id': '21',
                            'text': 'history message',
                            'sender': {'id': 'sender_id', 'role': 'client'},
                            'language': 'ru',
                            'translations': [
                                {'language': 'en', 'text': 'en text'},
                            ],
                        },
                        'newest_message_id': 'newest_id',
                    },
                ],
                'participants': [
                    {'id': 'sender_id', 'role': 'client', 'active': True},
                    {
                        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                        'role': 'client',
                        'active': True,
                        'metadata': {},
                    },
                ],
                'metadata': {'can_translate': True},
                'newest_message_id': '22',
                'total': 1,
                'all_languages': ['ru', 'en'],
                'can_translate': True,
            },
            {
                'newest_message_id': '22',
                'messages': [
                    {
                        'id': '21',
                        'created_date': 'cd',
                        'text': 'history message',
                        'sender': {'nickname': 'sender_id', 'role': 'client'},
                        'language': 'ru',
                        'translation': {'language': 'en', 'text': 'en text'},
                    },
                ],
                'all_languages': ['ru', 'en'],
                'can_translate': True,
            },
        ),
        (
            {},
            None,
            {
                'updates': [
                    {
                        'created_date': 'cd1',
                        'message': {
                            'id': '1',
                            'sender': {'id': 'system', 'role': 'system'},
                        },
                        'newest_message_id': '0',
                    },
                ],
                'participants': [],
                'newest_message_id': '1',
                'total': 0,
            },
            {'messages': []},
        ),
        (
            {},
            None,
            {
                'metadata': {'created_date': 'cd', 'comment': 'comment'},
                'updates': [],
                'participants': [],
                'newest_message_id': '0',
                'total': 0,
            },
            {
                'messages': [
                    {
                        'created_date': 'cd',
                        'id': 'comment_id',
                        'text': 'comment',
                        'sender': {'nickname': 'system', 'role': 'system'},
                    },
                ],
                'newest_message_id': 'comment_id',
            },
        ),
        (
            {},
            None,
            {
                'metadata': {
                    'created_date': 'cd',
                    'comment': 'comment',
                    'user_id': 'some_user_id',
                },
                'participants': [],
                'updates': [],
                'newest_message_id': '0',
                'total': 0,
            },
            {
                'messages': [
                    {
                        'created_date': 'cd',
                        'id': 'comment_id',
                        'text': 'comment',
                        'sender': {
                            'nickname': 'some_user_id',
                            'role': 'client',
                        },
                    },
                ],
                'newest_message_id': 'comment_id',
            },
        ),
        (
            {'newest_message_id': 'comment_id'},
            {
                'include_metadata': True,
                'include_participants': True,
                'on_behalf_of': {
                    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                    'role': 'client',
                },
            },
            {
                'updates': [],
                'participants': [],
                'newest_message_id': '0',
                'total': 0,
            },
            {'messages': [], 'newest_message_id': 'comment_id'},
        ),
        (
            {},
            None,
            {
                'updates': [
                    {
                        'created_date': 'cd2',
                        'message': {
                            'id': '2',
                            'text': 'history message 2',
                            'sender': {'id': 'sender_id', 'role': 'client'},
                        },
                        'newest_message_id': '1',
                    },
                    {
                        'created_date': 'cd1',
                        'message': {
                            'id': '1',
                            'sender': {'id': 'system', 'role': 'system'},
                        },
                        'newest_message_id': '0',
                    },
                ],
                'participants': [],
                'newest_message_id': '2',
                'total': 2,
            },
            {
                'newest_message_id': '2',
                'messages': [
                    {
                        'id': '2',
                        'created_date': 'cd2',
                        'text': 'history message 2',
                        'sender': {'nickname': 'sender_id', 'role': 'client'},
                    },
                ],
            },
        ),
    ],
)
def test_get_history(
        upd_request,
        history_request,
        history_response,
        expected_response,
        taxi_protocol,
        blackbox_service,
        mockserver,
):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    @mockserver.json_handler('/chat/1.0/chat/%s/history' % chat_id)
    def mock_history(request):
        if history_request:
            data = json.loads(request.get_data())
            assert data == history_request
        return mockserver.make_response(json.dumps(history_response), 200)

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'order_id': '8c83b49edb274ce0992f337061047375',
    }
    request.update(upd_request)

    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 200

    data = response.json()
    assert data == expected_response


@pytest.mark.config(CLIENTDRIVER_CHAT_PROTOCOL_ENABLED=False)
def test_disable_chat(taxi_protocol, blackbox_service, mockserver):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'order_id': '8c83b49edb274ce0992f337061047375',
        'newest_message_id': '2',
    }

    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 404


def test_post_message(taxi_protocol, blackbox_service, mockserver):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    posted_msg_id = '8c83b49edb274ce0992f337061047369'
    wrong_last_id = '2'

    @mockserver.json_handler('/chat/1.0/chat/%s/add_update' % chat_id)
    def mock_add_update(request):
        data = json.loads(request.get_data())
        if data['newest_message_id'] == wrong_last_id:
            return mockserver.make_response(json.dumps({}), 409)
        assert data['message']['metadata']['action'] == 'some_action'
        assert data['message']['metadata']['language_hint'] == {
            'keyboard_languages': ['ru'],
            'app_language': 'en',
            'system_languages': ['en', 'de'],
        }
        return mockserver.make_response(
            json.dumps({'message_id': posted_msg_id, 'need_refresh': True}),
            201,
        )

    @mockserver.json_handler('/chat/1.0/chat/%s/history' % chat_id)
    def mock_history(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'updates': [
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': '21',
                                'text': 'history message',
                                'metadata': {'action': 'some_action'},
                                'sender': {
                                    'id': 'sender_id',
                                    'role': 'client',
                                },
                                'location': [12, 14],
                            },
                            'update_participants': {
                                'action': 'add',
                                'id': 'senderid',
                                'role': 'client',
                            },
                            'newest_message_id': 'newest_id',
                        },
                    ],
                    'participants': [],
                    'newest_message_id': '22',
                    'total': 1,
                },
            ),
            200,
        )

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'order_id': '8c83b49edb274ce0992f337061047375',
        'newest_message_id': wrong_last_id,
        'post_message': {
            'suggestion_alias': 'some_action',
            'text': 'message text',
            'location': [12, 12],
            'language_hint': {
                'keyboard_languages': ['ru'],
                'app_language': 'en',
                'system_languages': ['en', 'de'],
            },
        },
    }

    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 409

    request['newest_message_id'] = 'valid_newest_id'
    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 200
    data = response.json()
    assert data['newest_message_id'] == '22'
    assert data['need_refresh'] is True
    assert data['messages'][0] == {
        'created_date': 'cd',
        'id': '21',
        'location': [12, 14],
        'text': 'history message',
        'action': 'some_action',
        'sender': {'nickname': 'sender_id', 'role': 'client'},
    }


def test_post_message_with_empty_id(
        taxi_protocol, blackbox_service, mockserver,
):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    first_message_id = 'first_message_id'

    @mockserver.json_handler('/chat/1.0/chat/%s/add_update' % chat_id)
    def mock_add_update(request):
        data = json.loads(request.get_data())
        assert data['newest_message_id'] == ''
        assert data['message']['metadata']['action'] == 'some_action'
        return mockserver.make_response(
            json.dumps({'message_id': first_message_id}), 201,
        )

    @mockserver.json_handler('/chat/1.0/chat/%s/history' % chat_id)
    def mock_history(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'updates': [
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': first_message_id,
                                'text': 'history message',
                                'metadata': {'action': 'some_action'},
                                'sender': {
                                    'id': 'sender_id',
                                    'role': 'client',
                                },
                                'location': [12, 14],
                            },
                            'newest_message_id': '',
                        },
                    ],
                    'participants': [],
                    'newest_message_id': first_message_id,
                    'total': 1,
                },
            ),
            200,
        )

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'order_id': '8c83b49edb274ce0992f337061047375',
        'newest_message_id': '',
        'post_message': {
            'suggestion_alias': 'some_action',
            'text': 'message text',
        },
    }

    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'newest_message_id': first_message_id,
        'messages': [
            {
                'created_date': 'cd',
                'id': first_message_id,
                'text': 'history message',
                'action': 'some_action',
                'location': [12, 14],
                'sender': {'nickname': 'sender_id', 'role': 'client'},
            },
        ],
    }


@pytest.mark.now('2017-12-28T13:05:05+0000')
def test_autoresolve_conflict(taxi_protocol, blackbox_service, mockserver):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    def request_response_gen(items):
        for i in items:
            resp, code = i[1]
            response = mockserver.make_response(json.dumps(resp), code)
            yield i[0], response
        assert False, 'all out of mocks'

    update_mock_info = request_response_gen(
        [
            (
                {
                    'newest_message_id': '',
                    'created_date': '2017-12-28T13:05:05+0000',
                    'message': {
                        'id': '',
                        'metadata': {},
                        'sender': {
                            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                            'role': 'client',
                        },
                        'text': 'message text',
                    },
                },
                ({}, 409),
            ),
            (
                {
                    'newest_message_id': '1',
                    'created_date': '2017-12-28T13:05:05+0000',
                    'message': {
                        'id': '',
                        'metadata': {},
                        'sender': {
                            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                            'role': 'client',
                        },
                        'text': 'message text',
                    },
                },
                ({}, 409),
            ),
            (
                {
                    'newest_message_id': '5',
                    'created_date': '2017-12-28T13:05:05+0000',
                    'message': {
                        'id': '',
                        'metadata': {},
                        'sender': {
                            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                            'role': 'client',
                        },
                        'text': 'message text',
                    },
                },
                ({'message_id': '6'}, 201),
            ),
        ],
    )

    history_mock_info = request_response_gen(
        [
            (
                {
                    'include_participants': False,
                    'on_behalf_of': {
                        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                        'role': 'client',
                    },
                },
                (
                    {
                        'updates': [
                            {
                                'created_date': 'cd',
                                'message': {
                                    'id': '1',
                                    'text': '',
                                    'sender': {
                                        'id': 'system',
                                        'role': 'system',
                                    },
                                },
                                'update_participants': {
                                    'action': 'add',
                                    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                                    'role': 'client',
                                },
                                'newest_message_id': '',
                            },
                        ],
                        'newest_message_id': '1',
                        'total': 1,
                    },
                    200,
                ),
            ),
            (
                {
                    'include_participants': False,
                    'on_behalf_of': {
                        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                        'role': 'client',
                    },
                    'range': {'message_ids': {'newer_than': '1'}},
                },
                (
                    {
                        'updates': [
                            {
                                'created_date': 'cd',
                                'message': {
                                    'id': '5',
                                    'text': 'history message',
                                    'sender': {
                                        'id': 'sender_id',
                                        'role': 'client',
                                    },
                                },
                                'newest_message_id': '',
                            },
                        ],
                        'newest_message_id': '5',
                        'total': 2,
                    },
                    200,
                ),
            ),
            (
                {
                    'include_participants': True,
                    'include_metadata': True,
                    'on_behalf_of': {
                        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                        'role': 'client',
                    },
                },
                (
                    {
                        'updates': [
                            {
                                'newest_message_id': '5',
                                'created_date': '2017-12-28T13:05:05+0000',
                                'message': {
                                    'id': '6',
                                    'metadata': {},
                                    'sender': {
                                        'id': (
                                            'b300bda7d41b4bae8d58dfa93221ef16'
                                        ),
                                        'role': 'client',
                                    },
                                    'text': 'message text',
                                },
                            },
                            {
                                'created_date': 'cd',
                                'message': {
                                    'id': '5',
                                    'text': 'history message',
                                    'sender': {
                                        'id': 'sender_id',
                                        'role': 'client',
                                    },
                                },
                                'newest_message_id': '',
                            },
                        ],
                        'participants': [],
                        'newest_message_id': '6',
                        'total': 2,
                    },
                    200,
                ),
            ),
        ],
    )

    @mockserver.json_handler('/chat/1.0/chat/%s/add_update' % chat_id)
    def mock_add_update(request):
        data = json.loads(request.get_data())
        expected_request, response = next(update_mock_info)
        assert expected_request == data
        return response

    @mockserver.json_handler('/chat/1.0/chat/%s/history' % chat_id)
    def mock_history(request):
        data = json.loads(request.get_data())
        expected_request, response = next(history_mock_info)
        assert expected_request == data
        return response

    response = taxi_protocol.post(
        '3.0/orderchat',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
            'newest_message_id': '',
            'post_message': {'text': 'message text'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'newest_message_id': '6',
        'messages': [
            {
                'created_date': '2017-12-28T13:05:05+0000',
                'id': '6',
                'text': 'message text',
                'sender': {
                    'nickname': 'b300bda7d41b4bae8d58dfa93221ef16',
                    'role': 'client',
                },
            },
            {
                'created_date': 'cd',
                'id': '5',
                'text': 'history message',
                'sender': {'nickname': 'sender_id', 'role': 'client'},
            },
        ],
    }


@pytest.mark.config(CLIENTDRIVER_CHAT_AUTOTRANSLATE_SYSTEM_MESSAGES=True)
@pytest.mark.parametrize(
    'text,tanker_locale,translations,can_translate,' ',expected_text',
    [
        (
            'original text',
            'en',
            [{'language': 'ru', 'text': 'Перевод оригинала'}],
            True,
            'Перевод оригинала',
        ),
        (
            'original text',
            None,
            [{'language': 'ru', 'text': 'Перевод оригинала'}],
            True,
            'Перевод оригинала',
        ),
        (
            'original text',
            'en',
            [{'language': 'ru', 'text': 'Перевод оригинала'}],
            False,
            'original text',
        ),
        ('original text', 'en', None, True, 'original text'),
        (
            'original text',
            'de',
            [
                {'language': 'ru', 'text': 'Перевод оригинала'},
                {'language': 'en', 'text': 'translation'},
            ],
            True,
            'original text',
        ),
    ],
)
def test_autotranslate_system_message(
        text,
        tanker_locale,
        translations,
        can_translate,
        expected_text,
        taxi_protocol,
        blackbox_service,
        mockserver,
):
    blackbox_service.set_token_info('test_token', uid='4003514353')

    @mockserver.json_handler('/chat/1.0/chat/%s/history' % chat_id)
    def mock_history(request):
        response = {
            'updates': [
                {
                    'created_date': 'cd2',
                    'message': {
                        'id': '2',
                        'text': text,
                        'sender': {'id': 'system', 'role': 'system'},
                        'metadata': {},
                    },
                    'newest_message_id': '1',
                },
            ],
            'metadata': {'can_translate': can_translate},
            'can_translate': True,
            'participants': [],
            'newest_message_id': '2',
            'total': 2,
        }
        message = response['updates'][0]['message']
        if translations:
            message['translations'] = translations
        if tanker_locale:
            message['metadata']['tanker_locale'] = tanker_locale
        return mockserver.make_response(json.dumps(response), 200)

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'order_id': '8c83b49edb274ce0992f337061047375',
    }

    response = taxi_protocol.post('3.0/orderchat', request)
    assert response.status_code == 200

    data = response.json()
    expected = {
        'messages': [
            {
                'text': expected_text,
                'sender': {'role': 'system', 'nickname': 'system'},
                'id': '2',
                'created_date': 'cd2',
            },
        ],
        'newest_message_id': '2',
    }
    if can_translate:
        expected['can_translate'] = True
    assert data == expected
