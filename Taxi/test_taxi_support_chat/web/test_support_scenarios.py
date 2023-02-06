import http
import json

import bson
import pytest

TRANSLATIONS = {
    'user_support_chat.support_name.dmitry': {'ru': 'Андрей'},
    'user_support_chat.support_name.yandex_support': {'ru': 'Саппорт яндекс'},
    'user_support_chat.support_name.uber_support': {'ru': 'Саппорт uber'},
    'user_support_chat.support_name.samir': {'ru': 'Самир'},
    'user_support_chat.support_name.dias': {'ru': 'Самир'},
    'user_support_chat.support_name.alihan': {'ru': 'Самир'},
    'user_support_chat.support_name.miras': {'ru': 'Самир'},
}

CURRENT_MESSAGES = [
    {
        'id': '5b4f5059779fb332fcc26152',
        'metadata': {'created': '2018-07-13T14:15:50+0000'},
        'sender': {'id': 'user', 'role': 'client', 'sender_type': 'client'},
        'text': 'text_3',
    },
]

SYSTEM_MESSAGE = {
    'id': 'c5400585d9fa40b28e1c88a6c5a27c82_question',
    'metadata': {'created': '2018-07-18T11:39:59+0000'},
    'sender': {
        'id': 'system',
        'role': 'system_scenarios',
        'sender_type': 'system_scenarios',
    },
    'text': 'bbb',
}
USER_MESSAGE = {
    'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
    'metadata': {'created': '2018-07-18T11:40:00+0000'},
    'sender': {
        'id': '5b4f5059779fb332fcc26152',
        'role': 'client',
        'sender_type': 'client',
    },
    'text': 'test',
}


@pytest.mark.now('2018-07-18T11:40:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
)
@pytest.mark.parametrize(
    [
        'data_override',
        'match_response_code',
        'match_response',
        'match_request',
        'display_response_code',
        'display_response',
        'expected_messages',
        'expected_action',
        'db_context',
    ],
    [
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': True},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, SYSTEM_MESSAGE, USER_MESSAGE],
            [],
            {'last_action_id': 'action_2'},
        ),
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.BAD_REQUEST,
            None,
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, SYSTEM_MESSAGE, USER_MESSAGE],
            [
                {
                    'type': 'call',
                    'id': 'action_3',
                    'view': {'title': 'Позвонить в 112'},
                    'params': {'number': '79099575227'},
                },
                {
                    'type': 'text',
                    'id': 'action_2',
                    'view': {'title': 'Написать 112'},
                    'params': {'text': '112'},
                },
            ],
            {'last_action_id': 'action_2'},
        ),
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'items': [],
                            'scenario_context': {
                                'last_action_id': 'action_1',
                                'anime': '=kaef',
                            },
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, USER_MESSAGE],
            [],
            {'last_action_id': 'action_2'},
        ),
        (
            {},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'show_message_input': False,
                            'items': [],
                            'scenario_context': {
                                'last_action_id': 'action_1',
                                'anime': '=kaef',
                            },
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': None},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, USER_MESSAGE],
            [],
            None,
        ),
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'message',
                        'id': 'action_1',
                        'content': {
                            'text': 'Ожидайте ответа саппорта',
                            'items': [],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': True},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [
                *CURRENT_MESSAGES,
                SYSTEM_MESSAGE,
                USER_MESSAGE,
                {
                    'id': 'c5400585d9fa40b28e1c88a6c5a27c82_action_1',
                    'metadata': {'created': '2018-07-18T11:40:01+0000'},
                    'sender': {
                        'id': 'system',
                        'role': 'system_scenarios',
                        'sender_type': 'system_scenarios',
                    },
                    'text': 'Ожидайте ответа саппорта',
                },
            ],
            [],
            None,
        ),
    ],
)
async def test_chatcreate_with_scenarios(
        web_app_client,
        web_context,
        dummy_tvm_check,
        patch_support_scenarios_matcher,
        patch_support_scenarios_display,
        data_override,
        match_response_code,
        match_response,
        match_request,
        display_response_code,
        display_response,
        expected_messages,
        expected_action,
        db_context,
):
    match_request = dict(match_request)

    patch_support_scenarios_matcher(
        response=match_response,
        status=match_response_code,
        expected_request=match_request,
    )
    patch_support_scenarios_display(
        response=display_response, status=display_response_code,
    )
    payload = {
        'include_history': True,
        'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
        'message': {
            'text': 'test',
            'sender': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
        },
        'metadata': {
            'user_id': 'test_user_id',
            'ask_csat': False,
            'user_locale': 'ru',
        },
        'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
    }
    payload['message'].update(data_override)
    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(payload),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status in [200, 201]
    result = await response.json()
    chat_id = result.pop('id')
    assert expected_messages == result['messages']

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    last_context = chat_doc['messages'][-1].get('scenario_context')
    assert db_context == last_context


@pytest.mark.now('2018-07-18T11:40:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
)
@pytest.mark.parametrize(
    [
        'data_override',
        'match_response_code',
        'match_response',
        'match_request',
        'display_response_code',
        'display_response',
        'expected_messages',
        'expected_action',
        'db_context',
    ],
    [
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': True},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, SYSTEM_MESSAGE, USER_MESSAGE],
            [],
            {'last_action_id': 'action_2'},
        ),
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.BAD_REQUEST,
            None,
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, SYSTEM_MESSAGE, USER_MESSAGE],
            [
                {
                    'type': 'call',
                    'id': 'action_3',
                    'view': {'title': 'Позвонить в 112'},
                    'params': {'number': '79099575227'},
                },
                {
                    'type': 'text',
                    'id': 'action_2',
                    'view': {'title': 'Написать 112'},
                    'params': {'text': '112'},
                },
            ],
            {'last_action_id': 'action_2'},
        ),
        (
            {'scenario_context': {'last_action_id': 'action_2'}},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'items': [],
                            'scenario_context': {
                                'last_action_id': 'action_1',
                                'anime': '=kaef',
                            },
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'action_2'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, USER_MESSAGE],
            [],
            {'last_action_id': 'action_2'},
        ),
        (
            {},
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'aaa',
                            'show_message_input': False,
                            'items': [],
                            'scenario_context': {
                                'last_action_id': 'action_1',
                                'anime': '=kaef',
                            },
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-18T14:40:00+0300',
                        'text': 'test',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': None},
            },
            http.HTTPStatus.OK,
            {'text': 'bbb'},
            [*CURRENT_MESSAGES, USER_MESSAGE],
            [],
            None,
        ),
    ],
)
async def test_chatupdate_with_scenarios(
        web_app_client,
        web_context,
        dummy_tvm_check,
        patch_support_scenarios_matcher,
        patch_support_scenarios_display,
        data_override,
        match_response_code,
        match_response,
        match_request,
        display_response_code,
        display_response,
        expected_messages,
        expected_action,
        db_context,
):
    patch_support_scenarios_matcher(
        response=match_response,
        status=match_response_code,
        expected_request=match_request,
    )
    patch_support_scenarios_display(
        response=display_response, status=display_response_code,
    )
    payload = {
        'created_date': '2018-07-18T11:40:00+0000',
        'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
        'message': {
            'text': 'test',
            'sender': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
        },
        'include_chat': True,
    }
    payload['message'].update(data_override)
    response = await web_app_client.post(
        '/v1/chat/5b436ca8779fb3302cc784ba/add_update',
        data=json.dumps(payload),
    )
    assert response.status in [200, 201]
    result = await response.json()
    chat = result['chat']
    chat_id = chat.pop('id')
    assert chat['messages'] == expected_messages

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    last_context = chat_doc['messages'][-1].get('scenario_context')
    assert db_context == last_context


@pytest.mark.now('2018-07-18T11:40:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
)
@pytest.mark.parametrize(
    [
        'match_response_code',
        'match_response',
        'match_request',
        'owner_id',
        'expected_actions',
        'expected_view',
    ],
    [
        (
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'сдох',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-13T17:15:50+0300',
                        'text': 'text_3',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'anime'},
            },
            '5b4f5059779fb332fcc26152',
            [
                {
                    'type': 'questionary',
                    'id': 'action_1',
                    'content': {
                        'items': [
                            {
                                'params': {'number': '79099575227'},
                                'id': 'action_3',
                                'view': {'title': 'Позвонить в 112'},
                                'type': 'call',
                            },
                            {
                                'params': {'text': '112'},
                                'id': 'action_2',
                                'view': {'title': 'Написать 112'},
                                'type': 'text',
                            },
                        ],
                        'text': 'сдох',
                    },
                },
            ],
            {'show_message_input': False},
        ),
        (
            http.HTTPStatus.OK,
            {
                'actions': [
                    {
                        'type': 'message',
                        'id': 'action_1',
                        'content': {
                            'text': 'сдох',
                            'items': [],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            {
                'messages': [
                    {
                        'message_timestamp': '2018-07-13T17:15:50+0300',
                        'text': 'text_3',
                    },
                ],
                'chat_data': {
                    'locale': 'ru',
                    'chat_type': 'client_support',
                    'country': None,
                },
                'scenario_context': {'last_action_id': 'anime'},
            },
            '5b4f5059779fb332fcc26152',
            [],
            {'show_message_input': False},
        ),
    ],
)
async def test_search_with_scenarios(
        web_app_client,
        web_context,
        dummy_tvm_check,
        patch_support_scenarios_matcher,
        match_response_code,
        match_response,
        match_request,
        owner_id,
        expected_actions,
        expected_view,
):
    patch_support_scenarios_matcher(
        response=match_response,
        status=match_response_code,
        expected_request=match_request,
    )
    payload = {
        'owner': {'id': owner_id, 'role': 'client'},
        'type': 'visible',
        'include_actions': True,
    }
    chat_doc_before_search = (
        await web_context.mongo.user_chat_messages.find_one(
            {'owner_id': owner_id},
        )
    )
    response = await web_app_client.post(
        '/v1/chat/search/', data=json.dumps(payload),
    )
    assert response.status == 200
    result = await response.json()
    actions = result['chats'][0]['actions']
    view = result['chats'][0]['view']
    assert expected_actions == actions
    assert expected_view == view

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'owner_id': owner_id},
    )
    assert chat_doc == chat_doc_before_search


@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
)
async def test_search_with_support_message(web_app_client):
    # Not mocking support-scenarios. It mustn't make any requests
    # Because of support message already in the chat
    response = await web_app_client.post(
        '/v1/chat/search/',
        data=json.dumps(
            {
                'owner': {'id': '5b2cae5cb2682a976914c2a3', 'role': 'client'},
                'type': 'visible',
                'include_actions': True,
            },
        ),
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'include_actions, chat_id, match_request_key, match_status, '
    'match_response_key, support_chat_response_key',
    [
        (
            'true',
            '5b436ca8779fb3302cc784ba',
            'include_actions_ok',
            200,
            'response_with_actions',
            'chat_with_actions',
        ),
        (
            'true',
            '5b436ca8779fb3302cc784ba',
            'include_actions_ok',
            400,
            'empty_response',
            'chat_without_actions',
        ),
        (
            'true',
            '5b2cae5cb2682a976914c2a3',
            'include_actions_ok',
            200,
            'response_with_actions',
            'chat_without_actions_due_to_user_messages',
        ),
        (
            'false',
            '5b436ca8779fb3302cc784ba',
            'include_actions_ok',
            None,
            None,
            'chat_without_actions',
        ),
        (
            'false',
            '5b2cae5cb2682a976914c2a3',
            'include_actions_ok',
            None,
            None,
            'chat_without_actions_due_to_user_messages',
        ),
    ],
)
@pytest.mark.config(USER_CHAT_MESSAGES_USE_ARCHIVE_API=True)
async def test_chat_with_scenarios(
        web_app_client,
        patch_support_scenarios_matcher,
        dummy_tvm_check,
        load_json,
        include_actions,
        chat_id,
        match_request_key,
        match_status,
        match_response_key,
        support_chat_response_key,
):
    match_response = load_json('match_responses.json').get(match_response_key)
    expected_match_request = load_json('expected_match_requests.json').get(
        match_request_key,
    )
    expected_result = load_json('expected_support_chat_responses.json').get(
        support_chat_response_key,
    )
    patch_support_scenarios_matcher(
        response=match_response,
        status=match_status,
        expected_request=expected_match_request,
    )
    response = await web_app_client.get(
        '/v1/chat/%s' % chat_id, params={'include_actions': include_actions},
    )
    assert response.status == http.HTTPStatus.OK
    response_body = await response.json()
    assert response_body == expected_result
