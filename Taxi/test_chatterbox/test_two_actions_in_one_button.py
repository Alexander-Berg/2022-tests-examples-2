# pylint: disable=too-many-lines
# pylint: disable=no-member, unused-variable, protected-access
import datetime
import http

import bson
import pytest

from taxi import discovery

from chatterbox import stq_task
from test_chatterbox import plugins as conftest


NOW = datetime.datetime(2018, 6, 15, 12, 34)
SUPPORT_NAME = 'support_1'

# pylint: disable=invalid-name
pytestmark = pytest.mark.usefixtures('mock_uuid_fixture')


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
    },
    CHAT_LINE_TRANSITIONS={'first': ['second']},
)
@pytest.mark.now(NOW.isoformat())
async def test_forward(
        cbox,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    ticket_id = '5b2cae5cb2682a976914c2a1'

    await cbox.post(
        '/v1/tasks/{}/forward'.format(ticket_id),
        data={
            'themes': ['2'],
            'themes_tree': ['1'],
            'hidden_comment': 'text',
            'hidden_comment_metadata': {'encrypt_key': '123'},
        },
        params={'line': 'second', 'macro_id': 123},
        headers={'Accept-Language': 'ru'},
    )

    assert cbox.status == http.HTTPStatus.OK
    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(ticket_id)},
    )
    assert task['line'] == 'second'
    assert task['status'] == 'forwarded'

    assert task['history'] == [
        {
            'action_id': 'test_uid',
            'action': 'communicate',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'comment': 'button comment',
            'in_addition': False,
            'next_action_id': 'test_uid',
            'next_action_type': 'forward',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'macro_id',
                    'value': '123',
                },
                {
                    'change_type': 'set',
                    'field_name': 'currently_used_macro_ids',
                    'value': ['123'],
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': 'macro_tag1'},
                {'change_type': 'add', 'tag': 'macro_tag2'},
            ],
        },
        {
            'action_id': 'test_uid',
            'action': 'forward',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'new_line': 'second',
            'hidden_comment': 'text',
            'in_addition': False,
            'meta_changes': [
                {'change_type': 'set', 'field_name': 'themes', 'value': [2]},
                {
                    'change_type': 'set',
                    'field_name': 'theme_name',
                    'value': 'Theme',
                },
                {
                    'change_type': 'set',
                    'field_name': 'themes_tree',
                    'value': [1],
                },
            ],
            'query_params': {'line': 'second', 'macro_id': '123'},
            'tags_changes': [
                {'change_type': 'add', 'tag': '3'},
                {'change_type': 'add', 'tag': '4'},
            ],
        },
    ]
    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


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
            {
                'new_chat_type': 'client_support',
                'additional_tag': 'add_tag',
                'macro_id': 123,
            },
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
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': datetime.datetime(2019, 11, 13, 12, 0),
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'button comment',
                    'in_addition': False,
                    'next_action_id': 'test_uid',
                    'next_action_type': 'forward_messages',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['123'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'macro_tag1'},
                        {'change_type': 'add', 'tag': 'macro_tag2'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward_messages',
                    'created': datetime.datetime(2019, 11, 13, 12, 0),
                    'line': 'first',
                    'forwarded_messages': ['message_1', 'message_2'],
                    'login': 'superuser',
                    'in_addition': False,
                    'hidden_comment': 'test_comment',
                },
            ],
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
                'meta_info': {},
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
    ],
)
async def test_forward_messages(
        cbox,
        stq,
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
        mock_chat_get_history,
        mock_random_str_uuid,
        response_mock,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()

    @patch_aiohttp_session(discovery.find_service('support_chat').url)
    def support_chat_api(method, url, **kwargs):
        if url == 'http://support-chat.taxi.dev.yandex.net/v1/chat/forward':
            assert kwargs['json'] == expected_support_chat_data
            return response_mock(json=support_chat_forward_response)
        if (
                url
                == 'http://support-chat.taxi.dev.yandex.net/v1/chat/%s'
                % support_chat_forward_response['chat_id']
        ):
            return response_mock(json=support_chat_get_response)
        return response_mock(json={})

    await cbox.post(
        '/v1/tasks/{}/forward_messages'.format(task_id_str),
        data=data,
        params=params,
    )
    assert cbox.status == http.HTTPStatus.OK
    old_task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id_str)},
    )
    assert old_task['history'][-2:] == expected_history
    if expected_inner_comments:
        assert old_task['inner_comments'] == expected_inner_comments

    new_task_id = cbox.body_data['id']
    new_task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(new_task_id)},
    )
    if is_new_task:
        new_task.pop('_id')
    assert new_task == expected_task

    push_to_drive_stq_calls = [
        stq.support_chat_send_events_to_carsharing.next_call()
        for _ in range(stq.support_chat_send_events_to_carsharing.times_called)
    ]
    if params['new_chat_type'] == 'carsharing_support':
        assert push_to_drive_stq_calls[0]['eta'] == datetime.datetime(
            1970, 1, 1, 0, 0,
        )
        assert push_to_drive_stq_calls[0]['args'] == [
            {'$oid': str(new_task_id)},
            new_task['external_id'],
        ]
        push_to_drive_stq_calls[0]['kwargs'].pop('log_extra')
        assert push_to_drive_stq_calls[0]['kwargs'] == {
            'meta': new_task['meta_info'],
            'hidden_comment': 'test_comment',
        }
    else:
        assert not push_to_drive_stq_calls

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    'task_id_str, query, expected_history, expected_update_kwargs,'
    'expected_comment_kwargs, expected_transition_kwargs',
    [
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'chat closed',
                'comment_metadata': {'encrypt_key': '321'},
                'macro_id': '77',
                'themes': ['1', '2'],
                'tags': ['extra_tag'],
                'hidden_comment': 'hidden',
                'hidden_comment_metadata': {'encrypt_key': '123'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'button comment',
                    'in_addition': False,
                    'next_action_id': 'test_uid',
                    'next_action_type': 'closed',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['123'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'macro_tag1'},
                        {'change_type': 'add', 'tag': 'macro_tag2'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'hidden_comment': 'hidden',
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                        {'change_type': 'add', 'tag': 'extra_tag'},
                    ],
                    'query_params': {'macro_id': '123'},
                },
            ],
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {'encrypt_key': '321'},
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
            },
            None,
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_close(
        cbox,
        task_id_str,
        query,
        expected_history,
        expected_update_kwargs,
        expected_comment_kwargs,
        expected_transition_kwargs,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
        mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_st_get_comments([])
    mock_st_get_all_attachments()
    mock_st_update_ticket('close')
    mock_random_str_uuid()

    await cbox.post(
        '/v1/tasks/{}/close'.format(task_id_str),
        data=query,
        params={'macro_id': 123},
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == 'closed'
    assert task['history'] == expected_history

    add_update_calls = mock_chat_add_update.calls
    if expected_update_kwargs is not None:
        close_call = add_update_calls[1]
        assert close_call['args'] == (task['external_id'],)
        close_call['kwargs'].pop('log_extra')
        assert close_call['kwargs'] == expected_update_kwargs

    if expected_comment_kwargs is not None:
        create_comment_call = mock_st_create_comment.calls[0]
        assert create_comment_call['args'] == (task['external_id'],)
        create_comment_call['kwargs'].pop('log_extra')
        assert create_comment_call['kwargs'] == expected_comment_kwargs

    if expected_transition_kwargs is not None:
        execute_transition_call = mock_st_transition.calls[0]
        assert execute_transition_call['ticket'] == task['external_id']
        assert execute_transition_call['kwargs'] == expected_transition_kwargs

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            task_id_str,
        )
        assert len(result) == 1
        assert result[0]['count'] == 0

    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    'task_id_str, expected_update_kwargs, expected_transition_kwargs',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'message_text': None,
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
            },
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('chatterbox', files=['test_dismiss_pg.sql'])
async def test_dismiss(
        cbox,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_transition,
        mock_random_str_uuid,
        task_id_str,
        expected_update_kwargs,
        expected_transition_kwargs,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    await cbox.post(
        '/v1/tasks/{}/dismiss'.format(task_id_str),
        data={
            'tags': ['double tag', 'double tag'],
            'themes': ['1', '2'],
            'hidden_comment': 'text',
            'hidden_comment_metadata': {'encrypt_key': '123'},
        },
        params={
            'chatterbox_button': 'chatterbox_nto',
            'additional_tag': 'nto_tag',
            'macro_id': 123,
        },
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id_str)},
    )
    assert task['status'] == 'closed'
    expected_history = [
        {
            'action_id': 'test_uid',
            'action': 'communicate',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'comment': 'button comment',
            'in_addition': False,
            'next_action_id': 'test_uid',
            'next_action_type': 'dismiss',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'macro_id',
                    'value': '123',
                },
                {
                    'change_type': 'set',
                    'field_name': 'currently_used_macro_ids',
                    'value': ['123'],
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': 'macro_tag1'},
                {'change_type': 'add', 'tag': 'macro_tag2'},
            ],
        },
        {
            'action_id': 'test_uid',
            'action': 'dismiss',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'in_addition': False,
            'hidden_comment': 'text',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'chatterbox_button',
                    'value': 'chatterbox_nto',
                },
                {
                    'change_type': 'set',
                    'field_name': 'themes',
                    'value': [1, 2],
                },
            ],
            'query_params': {
                'chatterbox_button': 'chatterbox_nto',
                'additional_tag': 'nto_tag',
                'macro_id': '123',
            },
        },
    ]
    expected_tags = ['3', '4', 'double tag', 'macro_tag1', 'macro_tag2']
    expected_tags.extend(
        ['nto_tag', 'tag1', 'tag2', 'доп', 'доп_superuser_20180615'],
    )
    expected_history[1]['in_addition'] = True
    expected_history[1]['tags_changes'] = [
        {'change_type': 'add', 'tag': '3'},
        {'change_type': 'add', 'tag': '4'},
        {'change_type': 'add', 'tag': 'double tag'},
        {'change_type': 'add', 'tag': 'nto_tag'},
        {'change_type': 'add', 'tag': 'доп'},
        {'change_type': 'add', 'tag': 'доп_superuser_20180615'},
    ]
    assert task['history'] == expected_history
    assert task['tags'] == expected_tags
    assert task['meta_info']['chatterbox_button'] == 'chatterbox_nto'

    add_update_calls = mock_chat_add_update.calls
    if expected_update_kwargs is not None:
        add_update_call = add_update_calls[1]
        assert add_update_call['args'] == (task['external_id'],)
        add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == expected_update_kwargs

    if expected_transition_kwargs is not None:
        execute_transition_call = mock_st_transition.calls[0]
        assert execute_transition_call['ticket'] == task['external_id']
        assert execute_transition_call['kwargs'] == expected_transition_kwargs

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            task_id_str,
        )
        assert len(result) == 1
        assert result[0]['count'] == 0

    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    'locale, params, data, expected_code, expected_ticket_id, '
    'expected_history, expected_create_ticket_kwargs, expected_search_kwargs',
    [
        (
            None,
            {'macro_id': 123},
            {'request_id': 'some_request_id'},
            200,
            'YANDEXTAXI-1',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'button comment',
                    'in_addition': False,
                    'next_action_id': 'test_uid',
                    'next_action_type': 'create_extra_ticket',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['123'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'macro_tag1'},
                        {'change_type': 'add', 'tag': 'macro_tag2'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'create_extra_ticket',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'in_addition': False,
                    'extra_startrack_ticket': 'YANDEXTAXI-1',
                    'query_params': {'macro_id': '123'},
                    'meta_changes': [],
                },
            ],
            {
                'queue': 'YANDEXTAXI',
                'summary': (
                    'Дополнительный тикет для таска '
                    '5b2cae5cb2682a976914c2a1 в Крутилке'
                ),
                'description': (
                    'Линк на таск: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1'
                ),
                'tags': None,
                'custom_fields': {'chatterboxId': '5b2cae5cb2682a976914c2a1'},
                'unique': 'some_request_id',
            },
            None,
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'extra_ticket.summary': {'en': 'extra ticket for task {task_id}'},
        'extra_ticket.description': {
            'en': 'link: {supchat_url}/chat/{task_id}',
        },
    },
)
@pytest.mark.config(
    STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES=['YANDEXTAXI', 'CHATTERBOX'],
)
@pytest.mark.now(NOW.isoformat())
async def test_extra_ticket(
        cbox,
        mock_st_create_ticket,
        mock_st_search,
        mock_random_str_uuid,
        mock_chat_add_update,
        mock_chat_get_history,
        locale,
        params,
        data,
        expected_code,
        expected_ticket_id,
        expected_history,
        expected_create_ticket_kwargs,
        expected_search_kwargs,
        pgsql,
):
    mock_random_str_uuid()
    mock_chat_get_history({'messages': []})

    in_addition = False
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'UPDATE chatterbox.online_supporters os '
        'SET in_additional = %s '
        'WHERE os.supporter_login = %s',
        (in_addition, 'superuser'),
    )

    if locale is None:
        headers = None
    else:
        headers = {'Accept-Language': locale}
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/create_extra_ticket',
        params=params,
        data=data,
        headers=headers,
    )
    assert cbox.status == expected_code
    if expected_code != http.HTTPStatus.OK:
        return

    assert cbox.body_data == {
        'next_frontend_action': 'open_url',
        'url': 'https://tracker.yandex.ru/{}'.format(expected_ticket_id),
    }

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task['extra_startrack_tickets'] == [expected_ticket_id]

    if expected_history is not None:
        assert task['history'] == expected_history

    if expected_create_ticket_kwargs is not None:
        create_ticket_call = mock_st_create_ticket.calls[0]
        assert create_ticket_call['kwargs'] == expected_create_ticket_kwargs

    if expected_search_kwargs is not None:
        search_call = mock_st_search.calls[0]
        assert search_call['kwargs'] == expected_search_kwargs

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    (
        'profile',
        'summary_tanker_key',
        'description_tanker_key',
        'queue',
        'additional_tag',
        'expected_status',
        'expected_response',
        'expected_history',
    ),
    [
        (
            'yandex-team',
            'some_summary_key',
            'some_description_key',
            'TAXIBUGPOLICE',
            'не_в_крутилку',
            200,
            {
                'next_frontend_action': 'open_url',
                'url': (
                    'https://st.yandex-team.ru/createTicket?'
                    'summary=some%20summary%20at%202018-05-07&'
                    'description=some%20description%20'
                    'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                    'TAXIBUGPOLICE&tags=%D0%BD%D0%B5_%D0%B2_'
                    '%D0%BA%D1%80%D1%83%D1%82%D0%B8%D0%BB%D0%BA%D1%83'
                ),
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'button comment',
                    'in_addition': False,
                    'next_action_id': 'test_uid',
                    'next_action_type': 'generate_extra_ticket_link',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['123'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'macro_tag1'},
                        {'change_type': 'add', 'tag': 'macro_tag2'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'generate_extra_ticket_link',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'in_addition': False,
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'не_в_крутилку'},
                    ],
                    'url': (
                        'https://st.yandex-team.ru/createTicket?'
                        'summary=some%20summary%20at%202018-05-07&'
                        'description=some%20description%20'
                        'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                        'TAXIBUGPOLICE&tags=%D0%BD%D0%B5_%D0%B2_'
                        '%D0%BA%D1%80%D1%83%D1%82%D0%B8%D0%BB%D0%BA%D1%83'
                    ),
                    'query_params': {
                        'profile': 'yandex-team',
                        'queue': 'TAXIBUGPOLICE',
                        'summary_tanker_key': 'some_summary_key',
                        'description_tanker_key': 'some_description_key',
                        'additional_tag': 'не_в_крутилку',
                        'macro_id': '123',
                    },
                    'meta_changes': [],
                },
            ],
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'some_summary_key': {'ru': 'some summary at {date_created}'},
        'some_description_key': {'ru': 'some description of {task_id} {city}'},
        'extra_data_description_key': {
            'ru': 'some description with {extra_data}',
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_extra_ticket_link(
        cbox,
        mock_random_str_uuid,
        mock_chat_add_update,
        mock_chat_get_history,
        profile,
        summary_tanker_key,
        description_tanker_key,
        queue,
        additional_tag,
        expected_status,
        expected_response,
        expected_history,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    params = {
        'profile': profile,
        'queue': queue,
        'summary_tanker_key': summary_tanker_key,
        'description_tanker_key': description_tanker_key,
        'macro_id': '123',
    }
    if additional_tag:
        params['additional_tag'] = additional_tag

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/generate_extra_ticket_link',
        params=params,
        data={},
    )
    assert cbox.status == expected_status
    assert cbox.body_data == expected_response

    if expected_history is not None:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
        )
        assert task['history'] == expected_history

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    (
        'task_id_str',
        'inner_comments',
        'public_messages',
        'expected_import_ticket',
        'expected_import_comment',
        'expected_update_ticket',
        'expected_create_link',
        'expected_ticket_status',
    ),
    [
        (
            '5b2cae5cb2682a976914c2b9',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [{'id': 'first_client_attachment_id'}],
                    },
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {'id': 'second_client_attachment_id'},
                            {'id': 'third_client_attachment_id'},
                        ],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'summary': 'Копия тикета: 5b2cae5cb2682a976914c2b9',
                'tags': [
                    'macro_tag1',
                    'macro_tag2',
                    'one',
                    'three',
                    'two',
                    'additional_tag',
                ],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2b9 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-06-15T12:34:00',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': '123',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'False',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id_4',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Next client message',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 456,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
            ],
            {'tags': {'add': 'copy_from_chatterbox'}},
            None,
            'open',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_USER_ID=123,
    STARTRACK_CLIENT_USER_ID=456,
    MAX_STARTRACK_TAG_LENGTH=30,
    STARTRACK_SUPPORT_COPY_QUEUE='TESTQUEUE',
)
@pytest.mark.translations(
    chatterbox={'copy_to_tracker': {'ru': 'Копия тикета: {task_id}'}},
)
async def test_startrack_copy(
        cbox,
        mock_st_import_ticket,
        mock_st_get_ticket_with_status,
        mock_st_import_comment,
        mock_st_create_comment_old,
        mock_st_get_comments,
        mock_chat_get_history,
        mock_st_import_file,
        mock_st_create_link,
        mock_get_chat,
        mock_source_download_file,
        mock_st_update_ticket,
        mock_random_str_uuid,
        mock_chat_add_update,
        task_id_str,
        inner_comments,
        public_messages,
        expected_import_ticket,
        expected_import_comment,
        expected_update_ticket,
        expected_create_link,
        expected_ticket_status,
):
    mock_st_get_ticket_with_status('closed')
    st_comments = [
        {
            'id': 'some_comment_id',
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': 'some_id'},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': 'some_id'},
            'text': i['text'],
        }
        for i in public_messages
    ]
    mock_st_get_comments(st_comments)
    mock_chat_get_history({'messages': public_messages})
    mocked_update_ticket = mock_st_update_ticket('open')
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_random_str_uuid()

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mocked_import_ticket = mock_st_import_ticket(startrack_ticket)

    startrack_comment = {
        'id': 'some_imported_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mocked_import_comment = mock_st_import_comment(startrack_comment)

    finish_comment = {
        'id': 'some_finish_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mocked_finish_comment = mock_st_create_comment_old(finish_comment)

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    inner_comments.extend(
        await cbox.app.startrack_manager._prepare_hidden_comments_for_export(
            db_task,
        ),
    )

    await cbox.post(
        '/v1/tasks/{}/tracker_copy'.format(task_id),
        params={
            'additional_tag': 'additional_tag',
            'summary_tanker_key': 'copy_to_tracker',
            'queue': 'TESTQUEUE',
            'macro_id': '123',
        },
        data={},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 200
    assert cbox.body_data == {
        'next_frontend_action': 'open_url',
        'url': 'https://tracker.yandex.ru/TESTQUEUE-1',
    }

    del public_messages[0]

    cycle_range = len(public_messages) + len(inner_comments) + 1
    for _ in range(cycle_range):
        await stq_task.startrack_comment_import(
            cbox.app,
            task_id,
            startrack_ticket=startrack_ticket,
            inner_comments=inner_comments,
            public_messages=public_messages,
            action='copy',
        )

    import_ticket_calls = mocked_import_ticket.calls
    assert import_ticket_calls[0]['kwargs']['json'] == expected_import_ticket

    import_comment_calls = mocked_import_comment.calls
    if expected_import_comment is None:
        assert not import_comment_calls
    else:
        assert len(import_comment_calls) == len(expected_import_comment)
        for i, call in enumerate(import_comment_calls):
            assert call['ticket_id'] == 'TESTQUEUE-1'
            assert call['data'] == expected_import_comment[i]

    assert mocked_finish_comment.calls[0] == {
        'text': (
            'Ссылка на таск в chatterbox: '
            'https://supchat.taxi.dev.yandex-team.ru/chat/'
            '{} \n'.format(task_id)
        ),
        'ticket_id': 'TESTQUEUE-1',
    }

    create_link_calls = mock_st_create_link.calls
    if expected_create_link is None:
        assert not create_link_calls
    else:
        assert create_link_calls == expected_create_link

    if expected_update_ticket is not None:
        update_ticket_calls = mocked_update_ticket.calls
        assert update_ticket_calls[0]['ticket'] == 'TESTQUEUE-1'
        assert update_ticket_calls[0]['kwargs'] == expected_update_ticket

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert 'startrack_ticket' not in db_task
    assert 'startrack_ticket_status' not in db_task

    assert db_task['history'][-2:] == [
        {
            'action_id': 'test_uid',
            'action': 'communicate',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'comment': 'button comment',
            'in_addition': False,
            'next_action_id': 'test_uid',
            'next_action_type': 'tracker_copy',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'macro_id',
                    'value': '123',
                },
                {
                    'change_type': 'set',
                    'field_name': 'currently_used_macro_ids',
                    'value': ['123'],
                },
                {
                    'change_type': 'set',
                    'field_name': 'ml_suggestion_success',
                    'value': False,
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': 'macro_tag1'},
                {'change_type': 'add', 'tag': 'macro_tag2'},
            ],
            'first_answer': 3600,
            'first_answer_in_line': 3600,
            'full_resolve': 3600,
        },
        {
            'action_id': 'test_uid',
            'action': 'tracker_copy',
            'in_addition': False,
            'created': datetime.datetime(2018, 6, 15, 12, 34),
            'login': 'superuser',
            'line': 'first',
            'meta_changes': [],
        },
    ]

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    ('task_id', 'data', 'meta_info', 'history', 'status'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'field': 'queue',
                'new_value': 'some_queue',
                'chatterbox_button': 'some_button',
                'macro_id': '123',
            },
            {
                'city': 'Moscow',
                'queue': 'some_queue',
                'chatterbox_button': 'some_button',
                'macro_id': '123',
                'currently_used_macro_ids': ['123'],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'button comment',
                    'in_addition': False,
                    'next_action_id': 'test_uid',
                    'next_action_type': 'manual_update_meta',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['123'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'macro_tag1'},
                        {'change_type': 'add', 'tag': 'macro_tag2'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'chatterbox_button',
                            'value': 'some_button',
                        },
                    ],
                },
            ],
            200,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_meta(
        cbox: conftest.CboxWrap,
        task_id,
        data,
        meta_info,
        history,
        status,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
):
    mock_random_str_uuid()
    mock_chat_get_history({'messages': []})

    await cbox.post(
        'v1/tasks/%s/manual_update_meta' % task_id, params=data, data={},
    )
    assert cbox.status == status

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['meta_info'] == meta_info
    assert task['history'] == history

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }


@pytest.mark.parametrize(
    'task_id, expected_status, expected_task_status, '
    'expected_status_before_assign, expected_skipped_by_list',
    [
        (
            '5b2cae5cb2682a976914c2a4',
            200,
            'new',
            None,
            ['support_10', 'support_15', SUPPORT_NAME],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_skip_simple(
        cbox,
        patch_auth,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_random_str_uuid,
        task_id,
        expected_status,
        expected_task_status,
        expected_status_before_assign,
        expected_skipped_by_list,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()

    async def _assign_task(cbox, login, task_id):
        async with cbox.app.pg_master_pool.acquire() as conn:
            result = await conn.execute(
                'INSERT INTO chatterbox.supporter_tasks '
                '(supporter_login, task_id) VALUES ($1, $2)',
                login,
                task_id,
            )
        return bool(result)

    async def _check_tasks_assigned(cbox, login):
        async with cbox.app.pg_master_pool.acquire() as conn:
            result = await conn.fetch(
                'SELECT * FROM chatterbox.supporter_tasks '
                'WHERE supporter_login = $1',
                login,
            )
        return bool(result)

    patch_auth(login=SUPPORT_NAME, superuser=True)
    await _assign_task(cbox, SUPPORT_NAME, task_id)
    await cbox.post(
        '/v1/tasks/{0}/skip'.format(task_id),
        data={},
        params={'macro_id': '123'},
    )
    assert cbox.status == expected_status

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )
    assert task['updated'] == NOW
    expected_history = [
        {
            'action_id': 'test_uid',
            'action': 'communicate',
            'created': NOW,
            'login': 'support_1',
            'line': 'corp',
            'comment': 'button comment',
            'in_addition': False,
            'next_action_id': 'test_uid',
            'next_action_type': 'skip',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'macro_id',
                    'value': '123',
                },
                {
                    'change_type': 'set',
                    'field_name': 'currently_used_macro_ids',
                    'value': ['123'],
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': 'macro_tag1'},
                {'change_type': 'add', 'tag': 'macro_tag2'},
            ],
            'latency': 26,
        },
        {
            'action_id': 'test_uid',
            'action': 'skip',
            'created': NOW,
            'login': SUPPORT_NAME,
        },
    ]
    assert task['history'] == expected_history
    assert task['support_admin'] == 'superuser'
    assert task['skipped_by'] == expected_skipped_by_list
    assert (
        task['meta_info'].get('status_before_assign')
        == expected_status_before_assign
    )
    assert not await _check_tasks_assigned(cbox, SUPPORT_NAME)

    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls[0]['kwargs']['message_text'] == 'button comment'
    assert add_update_calls[0]['kwargs']['update_metadata'] == {
        'ticket_status': 'open',
    }
