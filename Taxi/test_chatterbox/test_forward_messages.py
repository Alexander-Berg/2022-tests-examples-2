# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals, no-member
import datetime
import http

import bson
import pytest

from taxi import discovery


@pytest.mark.now('2019-11-13T12:00:00+0')
@pytest.mark.parametrize(
    'task_id_str, data, params, expected_support_chat_data,'
    'support_chat_response_code, support_chat_response, expected_code,'
    'expected_data',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            409,
            '',
            409,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.messages_already_forwarded',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            404,
            '',
            404,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.chat_not_found',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            400,
            '{"error": {"reason_code": "forward_support_messages"}}',
            400,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.forward_support_messages',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            400,
            '{"error": {"reason_code": "unsupported_chat_type"}}',
            400,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.forward_unsupported_chat_type',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            400,
            '{"error": {"reason_code": "test_code"}}',
            400,
            {'status': 'error', 'code': 'error', 'message': ''},
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            400,
            '',
            400,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.forward_task_on_other_support',
            },
        ),
    ],
)
async def test_forward_messages_fails(
        cbox,
        task_id_str,
        data,
        params,
        expected_support_chat_data,
        support_chat_response_code,
        support_chat_response,
        expected_code,
        expected_data,
        patch_aiohttp_session,
        response_mock,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url)
    def support_chat_api(method, url, **kwargs):
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat/forward'
        assert kwargs['json'] == expected_support_chat_data
        return response_mock(
            text=support_chat_response, status=support_chat_response_code,
        )

    await cbox.post(
        '/v1/tasks/{}/forward_messages'.format(task_id_str),
        data=data,
        params=params,
    )
    assert cbox.status == support_chat_response_code
    assert cbox.body_data == expected_data


@pytest.mark.parametrize(
    'handler', ['forward_messages', 'forward_messages_with_tvm'],
)
@pytest.mark.now('2019-11-13T12:00:00+0')
@pytest.mark.config(
    CHATTERBOX_DEFAULT_LINES={
        'client_support': 'first',
        'eats_support': 'online',
        'carsharing_support': 'carsharing_first',
    },
    CHATTERBOX_SOURCE_TYPE_MAPPING={
        'client_support': 'client',
        'eats_support': 'client',
        'carsharing_support': 'carsharing',
    },
)
@pytest.mark.translations(
    chatterbox={
        'forward.hidden_comment': {
            'ru': (
                'Сообщения {forwarded_messages_id!s} перенаправлены '
                'саппортом {login!s}'
            ),
            'en': (
                'Messages {forwarded_messages_id!s} forwarded by '
                'support {login!s}'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'task_id_str, data, params, expected_support_chat_data,'
    'support_chat_forward_response, support_chat_get_response,'
    'expected_history, expected_inner_comments, is_new_task, expected_task',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'selected_messages_id': ['message_1', 'message_2'],
                'hidden_comment': 'test_comment',
            },
            {'new_chat_type': 'client_support', 'additional_tag': 'add_tag'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            {'chat_id': 'user_chat_id_1'},
            {
                'id': 'user_chat_id_1',
                'type': 'client_support',
                'status': {'is_open': True, 'is_visible': True},
                'metadata': {
                    'ask_csat': False,
                    'last_message_from_user': True,
                },
            },
            {
                'action': 'forward_messages',
                'created': datetime.datetime(2019, 11, 13, 12, 0),
                'line': 'first',
                'forwarded_messages': ['message_1', 'message_2'],
                'login': 'superuser',
                'in_addition': False,
                'hidden_comment': 'test_comment',
            },
            [
                {
                    'created': datetime.datetime(2019, 11, 13, 12, 0),
                    'login': 'superuser',
                    'comment': 'test_comment',
                },
            ],
            True,
            {
                'chat_type': 'client',
                'created': datetime.datetime(2019, 11, 13, 12, 0),
                'updated': datetime.datetime(2019, 11, 13, 12, 0),
                'external_id': 'user_chat_id_1',
                'user_chat_message_id': 'user_chat_id_1',
                'line': 'first',
                'tags': ['add_tag', 'forwarded_chat_tag'],
                'meta_info': {
                    'user_id': 'test_user_id',
                    'user_phone': '+7925',
                },
                'projects': ['taxi'],
                'status': 'predispatch',
                'inner_comments': [
                    {
                        'comment': (
                            'Сообщения [\'message_1\','
                            ' \'message_2\'] перенаправлены '
                            'саппортом superuser'
                        ),
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'login': 'superuser',
                    },
                    {
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'login': 'superuser',
                        'comment': 'test_comment',
                    },
                ],
                'type': 'chat',
                'history': [
                    {
                        'action': 'create',
                        'login': 'superuser',
                        'line': 'first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                    },
                    {
                        'action': 'update_meta',
                        'login': 'superuser',
                        'line': 'first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'tags_changes': [
                            {'change_type': 'add', 'tag': 'add_tag'},
                            {
                                'change_type': 'add',
                                'tag': 'forwarded_chat_tag',
                            },
                        ],
                        'meta_changes': [
                            {
                                'change_type': 'set',
                                'field_name': 'user_id',
                                'value': 'test_user_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+7925',
                            },
                        ],
                    },
                    {
                        'action': 'forward_task',
                        'login': 'superuser',
                        'hidden_comment': (
                            'Сообщения [\'message_1\','
                            ' \'message_2\'] перенаправлены '
                            'саппортом superuser'
                        ),
                        'in_addition': False,
                        'line': 'first',
                        'forwarded_messages': ['message_1', 'message_2'],
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                    },
                    {
                        'action': 'hidden_comment',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'line': 'first',
                        'login': 'superuser',
                        'in_addition': False,
                        'hidden_comment': 'test_comment',
                    },
                ],
                'profile': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c2a4',
            {
                'selected_messages_id': ['message_1', 'message_2'],
                'hidden_comment': 'test_comment',
            },
            {
                'new_chat_type': 'carsharing_support',
                'additional_tag': 'add_tag',
            },
            {
                'chat_id': 'some_user_chat_message_id_4',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'carsharing_support',
            },
            {'chat_id': 'user_chat_id_1'},
            {
                'id': 'user_chat_id_1',
                'type': 'carsharing_support',
                'status': {'is_open': True, 'is_visible': True},
                'metadata': {
                    'ask_csat': False,
                    'last_message_from_user': True,
                },
            },
            {
                'action': 'forward_messages',
                'created': datetime.datetime(2019, 11, 13, 12, 0),
                'line': 'first',
                'forwarded_messages': ['message_1', 'message_2'],
                'login': 'superuser',
                'in_addition': False,
                'hidden_comment': 'test_comment',
            },
            [
                {
                    'created': datetime.datetime(2019, 11, 13, 12, 0),
                    'login': 'superuser',
                    'comment': 'test_comment',
                },
            ],
            True,
            {
                'chat_type': 'carsharing',
                'created': datetime.datetime(2019, 11, 13, 12, 0),
                'updated': datetime.datetime(2019, 11, 13, 12, 0),
                'external_id': 'user_chat_id_1',
                'user_chat_message_id': 'user_chat_id_1',
                'line': 'carsharing_first',
                'tags': ['add_tag', 'forwarded_chat_tag'],
                'meta_info': {'phone_type': 'yandex'},
                'projects': ['taxi'],
                'status': 'predispatch',
                'inner_comments': [
                    {
                        'comment': (
                            'Сообщения [\'message_1\','
                            ' \'message_2\'] перенаправлены '
                            'саппортом superuser'
                        ),
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'login': 'superuser',
                    },
                    {
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'login': 'superuser',
                        'comment': 'test_comment',
                    },
                ],
                'type': 'chat',
                'history': [
                    {
                        'action': 'create',
                        'login': 'superuser',
                        'line': 'carsharing_first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                    },
                    {
                        'action': 'update_meta',
                        'login': 'superuser',
                        'line': 'carsharing_first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'tags_changes': [
                            {'change_type': 'add', 'tag': 'add_tag'},
                            {
                                'change_type': 'add',
                                'tag': 'forwarded_chat_tag',
                            },
                        ],
                        'meta_changes': [
                            {
                                'change_type': 'set',
                                'field_name': 'phone_type',
                                'value': 'yandex',
                            },
                        ],
                    },
                    {
                        'action': 'forward_task',
                        'login': 'superuser',
                        'hidden_comment': (
                            'Сообщения [\'message_1\','
                            ' \'message_2\'] перенаправлены '
                            'саппортом superuser'
                        ),
                        'in_addition': False,
                        'line': 'carsharing_first',
                        'forwarded_messages': ['message_1', 'message_2'],
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                    },
                    {
                        'action': 'hidden_comment',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'line': 'carsharing_first',
                        'login': 'superuser',
                        'in_addition': False,
                        'hidden_comment': 'test_comment',
                    },
                ],
                'profile': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'selected_messages_id': ['message_3', 'message_4']},
            {'new_chat_type': 'client_support'},
            {
                'chat_id': 'some_user_chat_message_id',
                'forwarded_messages_id': ['message_3', 'message_4'],
                'new_chat_type': 'client_support',
            },
            {'chat_id': 'some_user_chat_message_id_2'},
            {
                'id': 'some_user_chat_message_id_2',
                'type': 'client_support',
                'status': {'is_open': True, 'is_visible': True},
                'metadata': {
                    'ask_csat': False,
                    'last_message_from_user': True,
                },
            },
            {
                'action': 'forward_messages',
                'created': datetime.datetime(2019, 11, 13, 12, 0),
                'line': 'first',
                'forwarded_messages': ['message_3', 'message_4'],
                'login': 'superuser',
                'in_addition': False,
            },
            [],
            False,
            {
                '_id': bson.ObjectId('5b2cae5cb2682a976914c2a2'),
                'created': datetime.datetime(2018, 6, 15, 12, 32, 59),
                'updated': datetime.datetime(2019, 11, 13, 12, 0),
                'external_id': 'some_user_chat_message_id_2',
                'line': 'first',
                'tags': ['tag1', 'tag2', 'forwarded_chat_tag'],
                'meta_info': {'phone_type': 'yandex'},
                'status': 'reopened',
                'chat_type': 'client',
                'type': 'chat',
                'support_admin': 'superuser',
                'reopen_count': 1,
                'inner_comments': [
                    {
                        'comment': (
                            'Сообщения [\'message_3\','
                            ' \'message_4\'] перенаправлены '
                            'саппортом superuser'
                        ),
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'login': 'superuser',
                    },
                ],
                'history': [
                    {
                        'action': 'reopen',
                        'login': 'superuser',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'line': 'first',
                    },
                    {
                        'action': 'update_meta',
                        'login': 'superuser',
                        'line': 'first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'tags_changes': [
                            {
                                'change_type': 'add',
                                'tag': 'forwarded_chat_tag',
                            },
                        ],
                    },
                    {
                        'action': 'forward_task',
                        'login': 'superuser',
                        'in_addition': False,
                        'line': 'first',
                        'created': datetime.datetime(2019, 11, 13, 12, 0),
                        'forwarded_messages': ['message_3', 'message_4'],
                        'hidden_comment': (
                            'Сообщения [\'message_3\','
                            ' \'message_4\'] перенаправлены '
                            'саппортом superuser'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_forward_messages(
        cbox,
        stq,
        handler,
        task_id_str,
        data,
        params,
        expected_support_chat_data,
        support_chat_forward_response,
        support_chat_get_response,
        expected_history,
        expected_inner_comments,
        is_new_task,
        expected_task,
        patch_aiohttp_session,
        mock_chat_add_update,
        response_mock,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url)
    def support_chat_api(method, url, **kwargs):
        if method == 'post':
            assert (
                url == 'http://support-chat.taxi.dev.yandex.net/v1/'
                'chat/forward'
            )
            assert kwargs['json'] == expected_support_chat_data
            return response_mock(json=support_chat_forward_response)

        assert (
            url == 'http://support-chat.taxi.dev.yandex.net/v1/'
            'chat/%s' % support_chat_forward_response['chat_id']
        )
        return response_mock(json=support_chat_get_response)

    await cbox.post(
        '/v1/tasks/{}/{}'.format(task_id_str, handler),
        data=data,
        params=params,
    )
    assert cbox.status == http.HTTPStatus.OK
    old_task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id_str)},
    )
    assert old_task['history'][-1] == expected_history
    if expected_inner_comments:
        assert old_task['inner_comments'] == expected_inner_comments

    new_task_id = cbox.body_data['id']
    new_task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(new_task_id)},
    )
    if is_new_task:
        new_task.pop('_id')
    assert new_task == expected_task

    if params['new_chat_type'] == 'carsharing_support':
        stq_call = stq.support_chat_send_events_to_carsharing.next_call()
        assert stq_call['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
        assert stq_call['args'] == [
            {'$oid': new_task_id},
            new_task['external_id'],
        ]
        stq_call['kwargs'].pop('log_extra')
        assert stq_call['kwargs'] == {
            'meta': new_task['meta_info'],
            'hidden_comment': 'test_comment',
        }
    assert not stq.support_chat_send_events_to_carsharing.has_calls


@pytest.mark.now('2019-11-13T12:00:00+0')
@pytest.mark.parametrize(
    'task_id_str, data, params, expected_code, expected_data',
    [
        (
            '5b2cae5cb2682a976914c2a5',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            400,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.forward_task_on_other_support',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            {'selected_messages_id': ['message_1', 'message_2']},
            {'new_chat_type': 'client_support'},
            400,
            {
                'status': 'error',
                'code': 'error',
                'message': 'errors.forward_task_on_other_support',
            },
        ),
    ],
)
async def test_forward_messages_with_tvm_fails(
        cbox, task_id_str, data, params, expected_code, expected_data,
):
    await cbox.post(
        '/v1/tasks/{}/forward_messages_with_tvm'.format(task_id_str),
        data=data,
        params=params,
    )
    assert cbox.status == expected_code
    assert cbox.body_data == expected_data
