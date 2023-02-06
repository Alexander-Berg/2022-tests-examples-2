# pylint: disable=too-many-arguments, no-member, too-many-locals
# pylint: disable=too-many-lines
import datetime
import http

import pytest
import ticket_parser2.api.v1 as ticket_parser_api

from taxi.clients import messenger_chat_mirror
from taxi.clients import support_chat


NOW = datetime.datetime(2018, 6, 7, 12, 34, 56)


async def _dummy_add_update(*args, **kwargs):
    return 'dummy result'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_POST_UPDATE=True,
    CHATTERBOX_LINES={
        'online': {
            'name': '1 · DM РФ',
            'priority': 3,
            'mode': 'online',
            'projects': ['eats'],
        },
    },
    CHATTERBOX_DEFAULT_LINES={
        'client_support': 'first',
        'startrack': 'mail',
        'driver_support': 'driver_first',
        'sms_support': 'sms_first',
        'facebook_support': 'facebook',
        'eats_support': 'online',
        'carsharing_support': 'carsharing_first',
        'messenger': 'first',
        'samsara': 'samsara',
    },
    CHATTERBOX_SOURCE_TYPE_MAPPING={
        'facebook_support': 'client',
        'client_support': 'client',
        'startrack': 'startrack',
        'driver_support': 'driver',
        'sms_support': 'sms',
        'eats_support': 'client',
        'carsharing_support': 'carsharing',
        'messenger': 'messenger',
        'samsara': 'samsara',
    },
    CHATTERBOX_SAMSARA_PUSH_MESSAGE_DELAY=10,
)
@pytest.mark.parametrize(
    (
        'routing_percentage',
        'chat_id',
        'chat_open',
        'chat_visible',
        'last_message_from_user',
        'task_status',
        'chatterbox_id',
        'need_update_chat',
        'task_meta_info',
        'task_reopens',
        'chat_type',
        'hidden_comment',
        'expected_hidden_comments',
        'task_type',
        'expected_chat_type',
        'expected_tags',
        'expected_line',
        'put_online_chat_task',
        'supporter_tasks',
        'projects',
        'messages',
    ),
    [
        (
            0,
            'some_user_chat_message_id',
            True,
            True,
            True,
            'reopened',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            2,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'some_messenger_chat_message_id',
            True,
            True,
            True,
            'reopened',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            2,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'messenger',
            'messenger',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'some_online_user_chat_message_id',
            True,
            True,
            True,
            'in_progress',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            1,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'offered_online_user_chat_message_id',
            True,
            True,
            True,
            'offered',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            1,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'online',
            False,
            1,
            None,
            [],
        ),
        (
            0,
            'offered_online_user_chat_message_id',
            False,
            False,
            True,
            'ready_to_archive',
            None,
            True,
            {
                'some': 'value',
                'ask_csat': False,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
                'last_user_message_id': 'for_samsara_test_id',
            },
            1,
            '',
            'phone: phone\n' * 100,
            [
                'Task task_online_offered closed because source chat '
                'offered_online_user_chat_message_id is closed',
                'phone: phone\n' * 100,
            ],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
        ),
        (
            0,
            'user2_dismissed_task',
            False,
            False,
            True,
            'ready_to_archive',
            None,
            True,
            {
                'some': 'value',
                'ask_csat': False,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
                'last_user_message_id': 'for_samsara_test_id',
            },
            1,
            '',
            'phone: phone\n' * 100,
            [
                'Task dismissed_task closed because source chat '
                'user2_dismissed_task is closed',
                'phone: phone\n' * 100,
            ],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [],
        ),
        pytest.param(
            0,
            'user2_dismissed_task',
            False,
            False,
            True,
            'ready_to_archive',
            None,
            True,
            {
                'some': 'value',
                'ask_csat': False,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
                'last_user_message_id': 'for_samsara_test_id',
            },
            1,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {'__default__': True},
                    },
                ),
            ],
        ),
        (
            0,
            'accepted_online_user_chat_message_id',
            True,
            True,
            True,
            'accepted',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            1,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'closed_online_user_chat_message_id',
            True,
            True,
            True,
            'reopened',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            2,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'some_user_chat_message_id',
            True,
            True,
            False,
            'in_progress',
            None,
            True,
            {'some': 'value'},
            1,
            '',
            None,
            None,
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'some_user_chat_message_id',
            False,
            False,
            False,
            'ready_to_archive',
            'some_chatterbox_id',
            False,
            {
                'some': 'value',
                'ask_csat': False,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
            },
            1,
            '',
            None,
            None,
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'some_user_chat_message_id',
            False,
            True,
            False,
            'in_progress',
            'some_chatterbox_id',
            False,
            {'some': 'value'},
            1,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'new_user_chat_message_id',
            True,
            False,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'client_support',
            None,
            None,
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            ['taxi'],
            [],
        ),
        (
            0,
            'another_user_chat_message_id',
            True,
            True,
            True,
            'new',
            'another_chatterbox_id',
            False,
            {},
            0,
            '',
            None,
            None,
            'chat',
            'client',
            [],
            'second',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'new_user_chat_message_id',
            True,
            True,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'driver_support',
            None,
            None,
            'chat',
            'driver',
            [],
            'driver_first',
            False,
            0,
            ['taxi'],
            [],
        ),
        (
            0,
            'new_user_chat_message_id',
            True,
            True,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'sms_support',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'sms',
            [],
            'sms_first',
            False,
            0,
            ['taxi'],
            [],
        ),
        (
            0,
            'new_user_chat_message_id',
            True,
            True,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'carsharing_support',
            '',
            [''],
            'chat',
            'carsharing',
            [],
            'carsharing_first',
            False,
            0,
            ['taxi'],
            [],
        ),
        (
            0,
            'new_online_user_chat_message_id',
            True,
            True,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'eats_support',
            None,
            None,
            'chat',
            'client',
            [],
            'online',
            False,
            0,
            ['eats'],
            [],
        ),
        (
            0,
            'reopened_user_chat_message_id',
            True,
            True,
            True,
            'reopened',
            None,
            True,
            {},
            1,
            '',
            None,
            None,
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'reopened_user_chat_message_id',
            False,
            False,
            False,
            'ready_to_archive',
            'some_chatterbox_id',
            False,
            {
                'ask_csat': False,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
            },
            1,
            '',
            None,
            None,
            'chat',
            'client',
            [],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            100,
            'some_user_chat_message_id',
            True,
            True,
            True,
            'routing',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            2,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            ['use_post_update_ml_routing'],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            100,
            'closed_online_user_chat_message_id',
            True,
            True,
            True,
            'routing',
            None,
            True,
            {'some': 'value', 'last_user_message_id': 'for_samsara_test_id'},
            2,
            '',
            'phone: phone\n' * 100,
            ['phone: phone\n' * 100],
            'chat',
            'client',
            ['use_post_update_ml_routing'],
            'online',
            False,
            0,
            None,
            [],
        ),
        (
            100,
            'reopened_user_chat_message_id',
            True,
            True,
            True,
            'routing',
            None,
            True,
            {},
            1,
            '',
            None,
            None,
            'chat',
            'client',
            ['use_post_update_ml_routing'],
            'first',
            False,
            0,
            None,
            [],
        ),
        (
            100,
            'another_user_chat_message_id',
            True,
            True,
            True,
            'routing',
            None,
            True,
            {},
            0,
            '',
            None,
            None,
            'chat',
            'client',
            ['use_post_update_ml_routing'],
            'second',
            False,
            0,
            None,
            [],
        ),
        (
            0,
            'new_user_chat_message_id',
            True,
            True,
            True,
            'predispatch',
            None,
            True,
            {},
            0,
            'samsara',
            None,
            None,
            'chat',
            'samsara',
            [],
            'samsara',
            False,
            0,
            ['taxi'],
            [],
        ),
    ],
)
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_post_task(
        cbox,
        stq,
        mock_chat_get_history,
        routing_percentage,
        chat_id,
        chat_open,
        chat_visible,
        last_message_from_user,
        task_status,
        monkeypatch,
        chatterbox_id,
        need_update_chat,
        mock,
        task_meta_info,
        task_reopens,
        chat_type,
        hidden_comment,
        expected_hidden_comments,
        task_type,
        expected_chat_type,
        expected_tags,
        expected_line,
        put_online_chat_task,
        supporter_tasks,
        projects,
        messages,
        mock_chat_mark_processed,
):
    cbox.app.config.CHATTERBOX_POST_UPDATE_ROUTING_PERCENTAGE = (
        routing_percentage
    )
    mock_chat_get_history({'messages': messages})

    async def get_chat(*args, **kwargs):
        chat = {
            'id': chat_id,
            'status': {'is_open': chat_open, 'is_visible': chat_visible},
            'metadata': {
                'ask_csat': False,
                'last_message_from_user': last_message_from_user,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
            },
            'type': chat_type,
            'newest_message_id': 'for_samsara_test_id',
        }
        if chatterbox_id:
            chat['metadata']['chatterbox_id'] = chatterbox_id

        return chat

    @mock
    async def _dummy_chat_update(*args, **kwargs):
        return await _dummy_add_update(*args, **kwargs)

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_chat_update,
    )
    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'add_update',
        _dummy_chat_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )
    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'get_chat',
        get_chat,
    )

    data = {'type': task_type, 'external_id': chat_id}
    if hidden_comment is not None:
        data['hidden_comment'] = hidden_comment
        data['hidden_comment_metadata'] = {'encrypt_key': '123'}

    await cbox.post('/v1/tasks', data=data)
    assert cbox.status == http.HTTPStatus.OK

    assert mock_chat_mark_processed.calls

    task = await cbox.db.support_chatterbox.find_one(
        {'type': task_type, 'external_id': chat_id},
    )

    if hidden_comment is not None:
        assert [
            inner_comment['comment']
            for inner_comment in task['inner_comments']
        ] == expected_hidden_comments

    updated_chatterbox_id = None
    calls = _dummy_chat_update.calls
    if calls:
        updated_chatterbox_id = calls[0]['kwargs']['update_metadata'][
            'chatterbox_id'
        ]
    online_stq_calls = [
        stq.chatterbox_online_chat_processing.next_call()
        for _ in range(stq.chatterbox_online_chat_processing.times_called)
    ]
    post_update_stq_calls = [
        stq.chatterbox_post_update.next_call()
        for _ in range(stq.chatterbox_post_update.times_called)
    ]
    push_to_drive_stq_calls = [
        stq.support_chat_send_events_to_carsharing.next_call()
        for _ in range(stq.support_chat_send_events_to_carsharing.times_called)
    ]
    push_to_samsara_stq_calls = [
        stq.support_chat_send_messages_to_samsara.next_call()
        for _ in range(stq.support_chat_send_messages_to_samsara.times_called)
    ]
    assert task['tags'] == expected_tags
    assert task['status'] == task_status
    assert task['meta_info'] == task_meta_info
    if task_status == 'predispatch':
        assert task['external_id'] == chat_id
        assert not post_update_stq_calls
    else:
        assert post_update_stq_calls[0]['queue'] == 'chatterbox_post_update'
        assert post_update_stq_calls[0]['eta'] == datetime.datetime(
            1970, 1, 1, 0, 0,
        )
        assert post_update_stq_calls[0]['args'] == [str(task['_id'])]
    if put_online_chat_task:
        assert (
            online_stq_calls[0]['queue'] == 'chatterbox_online_chat_processing'
        )
        assert online_stq_calls[0]['eta'] == datetime.datetime(
            1970, 1, 1, 0, 0,
        )
        assert online_stq_calls[0]['args'] == [str(task['_id']), []]
    else:
        assert not online_stq_calls
    if chat_type == 'carsharing_support':
        assert (
            push_to_drive_stq_calls[0]['queue']
            == 'support_chat_send_events_to_carsharing'
        )
        assert push_to_drive_stq_calls[0]['eta'] == datetime.datetime(
            1970, 1, 1, 0, 0,
        )
        assert push_to_drive_stq_calls[0]['args'] == [
            {'$oid': str(task['_id'])},
            chat_id,
        ]
        push_to_drive_stq_calls[0]['kwargs'].pop('log_extra')
        assert push_to_drive_stq_calls[0]['kwargs'] == {
            'meta': task_meta_info,
            'hidden_comment': None,
        }
    else:
        assert not push_to_drive_stq_calls
    if expected_line == 'samsara':
        assert (
            push_to_samsara_stq_calls[0]['queue']
            == 'support_chat_send_messages_to_samsara'
        )
        assert push_to_samsara_stq_calls[0]['eta'] == datetime.datetime(
            2018, 6, 7, 12, 35, 6,
        )
        assert push_to_samsara_stq_calls[0]['args'] == [
            {'$oid': str(task['_id'])},
            chat_id,
        ]
        push_to_samsara_stq_calls[0]['kwargs'].pop('log_extra')
        assert push_to_samsara_stq_calls[0]['kwargs'] == {
            'meta': task_meta_info,
            'hidden_comment': None,
            'required_msg_id': 'for_samsara_test_id',
        }
    else:
        assert not push_to_samsara_stq_calls

    assert (not need_update_chat and not updated_chatterbox_id) or (
        updated_chatterbox_id == str(task['_id'])
    )
    if 'ask_csat' in task_meta_info:
        close_history_records = [
            record for record in task['history'] if record['action'] == 'close'
        ]
        assert close_history_records[0]['meta_changes'] == [
            {'change_type': 'set', 'field_name': 'ask_csat', 'value': False},
            {
                'change_type': 'set',
                'field_name': 'csat_value',
                'value': 'amazing',
            },
            {
                'change_type': 'set',
                'field_name': 'csat_reasons',
                'value': ['fast answer', 'thank you'],
            },
        ]
    if 'chat_type' in task:
        assert task['chat_type'] == expected_chat_type
        assert task['line'] == expected_line
    assert task.get('reopen_count', 0) == task_reopens
    if projects:
        assert task['projects'] == projects
    if task['status'] == 'ready_to_archive':
        has_dismiss = any(
            record['action'] == 'dismiss' for record in task['history']
        )
        assert task['history'][0].get('is_lost') or (
            not messages and has_dismiss
        )

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            ' FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task['_id']),
        )
        assert result[0]['count'] == supporter_tasks


async def test_post_task_tvm_missing(cbox, mock_chat_mark_processed):
    cbox.app.config.TVM_ENABLED = True
    await cbox.post(
        '/v1/tasks', data={'type': 'chat', 'external_id': 'some_external_id'},
    )
    assert cbox.status == http.HTTPStatus.FORBIDDEN


@pytest.mark.config(
    SERVICE_ROLES={'chatterbox': {'task_write': ['backend']}},
    TVM_ENABLED=True,
    TVM_SERVICES={'backend': 1, 'chatterbox': 2},
    FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True,
    TVM_RULES=[{'src': 'backend', 'dst': 'chatterbox'}],
)
async def test_post_task_tvm_ok_source(
        cbox, monkeypatch, mock_chat_mark_processed,
):
    async def get_chat(*args, **kwargs):
        return {
            'id': 'chat_id',
            'type': 'driver_support',
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': False},
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    class DummyServiceContext:
        class DummyTicket:
            src = 1

            def debug_info(self):
                pass

        def __init__(self, *args, **kwargs):
            pass

        def check(self, ticket_body):
            return self.DummyTicket()

    async def _dummy_get_keys(log_extra=None):
        return 'keys'

    monkeypatch.setattr(
        ticket_parser_api, 'ServiceContext', DummyServiceContext,
    )
    monkeypatch.setattr(cbox.app.tvm, 'get_keys', _dummy_get_keys)
    cbox.app.secdist['settings_override']['TVM_SERVICES'] = {
        'backend': {'secret': 'mysecret'},
        'chatterbox': {'secret': 'mysecret'},
    }
    await cbox.post(
        '/v1/tasks',
        data={'type': 'chat', 'external_id': 'some_external_id'},
        headers={'X-Ya-Service-Ticket': 'some_service_ticket'},
    )
    assert cbox.status == http.HTTPStatus.OK
    assert mock_chat_mark_processed.calls


@pytest.mark.config(
    SERVICE_ROLES={'chatterbox': {'task_write': ['backend']}},
    TVM_ENABLED=True,
    TVM_SERVICES={'backend': 1, 'chatterbox': 2},
    FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True,
    TVM_RULES=[],
)
async def test_post_task_tvm_bad_source(
        cbox, monkeypatch, mock_chat_mark_processed,
):
    async def get_chat(*args, **kwargs):
        return {
            'id': 'chat_id',
            'type': 'driver_support',
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': False},
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    class DummyServiceContext:
        class DummyTicket:
            src = 1

            def debug_info(self):
                pass

        def __init__(self, *args, **kwargs):
            pass

        def check(self, ticket_body):
            return self.DummyTicket()

    async def _dummy_get_keys(log_extra=None):
        return 'keys'

    monkeypatch.setattr(
        ticket_parser_api, 'ServiceContext', DummyServiceContext,
    )
    monkeypatch.setattr(cbox.app.tvm, 'get_keys', _dummy_get_keys)
    cbox.app.secdist['settings_override']['TVM_SERVICES'] = {
        'backend': {'secret': 'mysecret'},
        'chatterbox': {'secret': 'mysecret'},
    }
    await cbox.post(
        '/v1/tasks',
        data={'type': 'chat', 'external_id': 'some_external_id'},
        headers={'X-Ya-Service-Ticket': 'some_service_ticket'},
    )
    assert cbox.status == http.HTTPStatus.FORBIDDEN


@pytest.mark.config(CHATTERBOX_PREDISPATCH=True)
async def test_post_archived_task(cbox, monkeypatch, mock_chat_mark_processed):
    async def get_chat(*args, **kwargs):
        return {
            'id': 'chat_id',
            'type': 'client_support',
            'metadata': {'last_message_from_user': False},
            'status': {'is_open': True, 'is_visible': True},
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks',
        data={'type': 'chat', 'external_id': 'closed_chat_message_id'},
    )
    assert cbox.status == http.HTTPStatus.GONE


@pytest.mark.config(
    CHATTERBOX_DEFAULT_LINES={'messenger': 'messenger'},
    CHATTERBOX_SOURCE_TYPE_MAPPING={'messenger': 'messenger'},
)
async def test_post_messenger(
        cbox, monkeypatch, mock, mock_chat_mark_processed,
):
    @mock
    async def get_chat(*args, **kwargs):
        return {
            'id': '0/0/0e4b0158-0053-490e-a3ad-0ea0db62a81f',
            'type': 'messenger',
            'metadata': {'last_message_from_user': False},
            'status': {'is_open': True, 'is_visible': True},
        }

    @mock
    async def _dummy_chat_update(*args, **kwargs):
        return await _dummy_add_update(*args, **kwargs)

    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'get_chat',
        get_chat,
    )

    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'add_update',
        _dummy_chat_update,
    )

    data = {
        'type': 'messenger',
        'external_id': '0/0/0e4b0158-0053-490e-a3ad-0ea0db62a81f',
    }

    await cbox.post('/v1/tasks', data=data)
    assert cbox.status == http.HTTPStatus.OK


@pytest.mark.config(
    CHATTERBOX_LINES={
        'corp': {
            'name': 'Корп',
            'priority': 2,
            'sort_order': 1,
            'mode': 'online',
            'conditions': {'tags': {'#in': ['корп_пользователь']}},
        },
    },
    CHATTERBOX_POST_UPDATE=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    (
        'chat_id',
        'chat_type',
        'metadata',
        'task_status',
        'task_meta_info',
        'expected_post_update_calls',
        'expected_predispatch_calls',
    ),
    [
        (
            'some_user_chat_message_id',
            'client_support',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'some',
                        'value': 'value',
                    },
                ],
                'update_tags': [
                    {'tag': 'Корп_пользователь', 'change_type': 'add'},
                ],
            },
            'reopened',
            {'some': 'value'},
            [
                {
                    'queue': 'chatterbox_post_update',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'task_in_progress',
                    'args': ['task_in_progress'],
                    'kwargs': {},
                },
            ],
            [],
        ),
        (
            'some_messenger_chat_message_id',
            'messenger',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'some',
                        'value': 'value',
                    },
                ],
                'update_tags': [
                    {'tag': 'Корп_пользователь', 'change_type': 'add'},
                ],
            },
            'reopened',
            {'some': 'value'},
            [
                {
                    'queue': 'chatterbox_post_update',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'messenger_task_in_progress',
                    'args': ['messenger_task_in_progress'],
                    'kwargs': {},
                },
            ],
            [],
        ),
        (
            'some_user_chat_message_id',
            'client_support',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'another',
                        'value': 'value',
                    },
                ],
            },
            'reopened',
            {'some': 'value', 'another': 'value'},
            [
                {
                    'queue': 'chatterbox_post_update',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'task_in_progress',
                    'args': ['task_in_progress'],
                    'kwargs': {},
                },
            ],
            [],
        ),
        (
            'predispatch_user_chat_message_id',
            'client_support',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'some',
                        'value': 'value',
                    },
                ],
            },
            'predispatch',
            {'some': 'value'},
            [],
            [
                {
                    'queue': 'chatterbox_predispatch_queue',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'predispatch_task',
                    'args': ['predispatch_task'],
                    'kwargs': {},
                },
            ],
        ),
        (
            'predispatch_user_chat_message_id',
            'client_support',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79999999999',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_driver_license',
                    },
                ],
            },
            'predispatch',
            {
                'some': 'value',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
            },
            [],
            [
                {
                    'queue': 'chatterbox_predispatch_queue',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'predispatch_task',
                    'args': ['predispatch_task'],
                    'kwargs': {},
                },
            ],
        ),
        (
            'routing_user_chat_message_id',
            'client_support',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79999999999',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_driver_license',
                    },
                ],
            },
            'routing',
            {
                'some': 'value',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
            },
            [
                {
                    'queue': 'chatterbox_post_update',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': 'routing_task',
                    'args': ['routing_task'],
                    'kwargs': {},
                },
            ],
            [],
        ),
    ],
)
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_post_with_metadata(
        cbox,
        stq,
        chat_id,
        chat_type,
        monkeypatch,
        mock,
        mock_personal,
        metadata,
        task_status,
        task_meta_info,
        expected_post_update_calls,
        expected_predispatch_calls,
        mock_chat_mark_processed,
):
    async def get_chat(*args, **kwargs):
        return {
            'id': 'chat_id',
            'type': chat_type,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': True},
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )
    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'get_chat',
        get_chat,
    )

    @mock
    async def _dummy_chat_update(*args, **kwargs):
        return await _dummy_add_update(*args, **kwargs)

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_chat_update,
    )
    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'add_update',
        _dummy_chat_update,
    )

    await cbox.post(
        '/v1/tasks',
        data={'type': 'chat', 'external_id': chat_id, 'metadata': metadata},
    )
    assert cbox.status == http.HTTPStatus.OK
    assert mock_chat_mark_processed.calls

    task = await cbox.db.support_chatterbox.find_one({'external_id': chat_id})
    assert task['status'] == task_status
    assert task['meta_info'] == task_meta_info

    post_update_calls = [
        stq.chatterbox_post_update.next_call()
        for _ in range(stq.chatterbox_post_update.times_called)
    ]
    predispatch_calls = [
        stq.chatterbox_predispatch_queue.next_call()
        for _ in range(stq.chatterbox_predispatch_queue.times_called)
    ]
    for call in post_update_calls:
        del call['kwargs']['log_extra']
    for call in predispatch_calls:
        del call['kwargs']['log_extra']
    assert post_update_calls == expected_post_update_calls
    assert predispatch_calls == expected_predispatch_calls


@pytest.mark.config(
    CHATTERBOX_LINES={
        'corp': {
            'name': 'Корп',
            'priority': 2,
            'sort_order': 1,
            'mode': 'online',
            'conditions': {
                'type': {'#in': ['client', None]},
                'fields/payment_type': 'способ_оплаты_корпоративный',
            },
        },
    },
    CHATTERBOX_POST_UPDATE=True,
)
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_change_closed_task_line(
        cbox, stq, monkeypatch, mock_chat_mark_processed,
):

    chat_id = 'closed_user_chat_message_id'

    async def get_chat(*args, **kwargs):
        chat = {
            'id': chat_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': True},
            'type': 'client',
        }

        return chat

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks',
        data={
            'type': 'chat',
            'external_id': chat_id,
            'metadata': {
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'способ_оплаты_корпоративный',
                    },
                ],
            },
        },
    )
    assert cbox.status == http.HTTPStatus.OK
    assert mock_chat_mark_processed.calls

    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': chat_id},
    )

    assert task['status'] == 'reopened'
    assert task['line'] == 'corp'
    assert stq.chatterbox_post_update.times_called == 1
    call = stq.chatterbox_post_update.next_call()
    assert call['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
    assert call['args'] == [str(task['_id'])]


@pytest.mark.config(
    CHATTERBOX_LINES={
        'driver_first': {
            'name': '1 · DM РФ',
            'priority': 3,
            'autoreply': True,
        },
    },
    CHATTERBOX_DRIVERS_MULTI_AUTOREPLY={
        'percentage': 100,
        'timedelta': 60,
        'statuses': ['new'],
    },
    CHATTERBOX_POST_UPDATE=True,
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'chat_id, expected_autoreply, expected_status',
    [
        ('multi_autoreply_user_chat_message_id_1', True, 'new'),
        ('multi_autoreply_user_chat_message_id_2', False, 'new'),
        ('multi_autoreply_user_chat_message_id_999', False, 'predispatch'),
        ('multi_autoreply_user_chat_message_id_3', False, 'reopened'),
    ],
)
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_driver_multi_autoreply_conditions(
        cbox,
        stq,
        monkeypatch,
        chat_id,
        expected_autoreply,
        expected_status,
        mock_chat_mark_processed,
):
    async def get_chat(*args, **kwargs):
        chat = {
            'id': chat_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': True},
            'type': 'driver_support',
        }

        return chat

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks',
        data={
            'type': 'chat',
            'external_id': chat_id,
            'metadata': {
                'update_tags': [{'change_type': 'add', 'tag': 'some_tag'}],
            },
        },
    )
    assert cbox.status == http.HTTPStatus.OK
    assert mock_chat_mark_processed.calls

    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': chat_id},
    )

    assert task['status'] == expected_status
    if expected_autoreply:
        assert task['line'] == 'driver_first'
        stq_call = stq.chatterbox_post_update.next_call()
        assert stq_call['args'] == [str(task['_id'])]


@pytest.mark.parametrize(
    'external_id, newest_message_id, update_meta, expected_status,'
    'expected_meta_info',
    [
        (
            'chat_task_to_reopen',
            'id_newest_message',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'new',
                        'value': 'value',
                    },
                ],
            },
            'reopened',
            {
                'new': 'value',
                'old': 'value',
                'last_user_message_id': 'id_newest_message',
            },
        ),
        (
            'chat_task_to_reopen',
            'id_newest_message',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'old',
                        'value': 'value',
                    },
                ],
            },
            'closed',
            {'old': 'value', 'last_user_message_id': 'id_newest_message'},
        ),
        (
            'chat_task_to_reopen',
            'new_id_newest_message',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'new',
                        'value': 'value',
                    },
                ],
            },
            'reopened',
            {
                'new': 'value',
                'old': 'value',
                'last_user_message_id': 'new_id_newest_message',
            },
        ),
        (
            'chat_task_to_reopen',
            'new_id_newest_message',
            {'update_meta': []},
            'reopened',
            {'old': 'value', 'last_user_message_id': 'new_id_newest_message'},
        ),
        ('new_chat_task', 'new_id_newest_message', {}, 'predispatch', {}),
        (
            'new_chat_task',
            'new_id_newest_message',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'new',
                        'value': 'value',
                    },
                ],
            },
            'predispatch',
            {'new': 'value'},
        ),
        ('chat_task_empty', 'new_id_newest_message', {}, 'reopened', {}),
    ],
)
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_reopen_when_new_message(
        cbox,
        monkeypatch,
        external_id,
        newest_message_id,
        update_meta,
        expected_status,
        expected_meta_info,
        mock_chat_mark_processed,
):
    async def get_chat(*args, **kwargs):
        chat = {
            'id': external_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': True},
            'type': 'driver_support',
            'newest_message_id': newest_message_id,
        }

        return chat

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks',
        data={
            'type': 'chat',
            'external_id': external_id,
            'metadata': update_meta,
        },
    )
    assert cbox.status == http.HTTPStatus.OK
    assert mock_chat_mark_processed.calls

    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': external_id},
    )

    assert task['status'] == expected_status
    assert task['meta_info'] == expected_meta_info


@pytest.mark.parametrize(
    'external_id, newest_message_id, update_meta, expected_status,'
    'expected_meta_info',
    [
        (
            'chat_task_to_reopen',
            'id_newest_message',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'call_guid',
                        'value': '000000000',
                    },
                ],
            },
            'reopened',
            {
                'call_guid': '000000000',
                'old': 'value',
                'last_user_message_id': 'id_newest_message',
            },
        ),
    ],
)
@pytest.mark.config(CHATTERBOX_CALLCENTER_QA_DISABLED_DELAY=10)
async def test_callcenter_qa_csat(
        cbox,
        stq,
        monkeypatch,
        external_id,
        newest_message_id,
        update_meta,
        expected_status,
        expected_meta_info,
):
    async def get_chat(*args, **kwargs):
        chat = {
            'id': external_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {'last_message_from_user': True},
            'type': 'driver_support',
            'newest_message_id': newest_message_id,
        }

        return chat

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks',
        data={
            'type': 'chat',
            'external_id': external_id,
            'metadata': update_meta,
        },
    )

    assert cbox.status == http.HTTPStatus.OK
    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': external_id},
    )

    assert task['status'] == expected_status
    assert task['meta_info'] == expected_meta_info

    expected_eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)

    stq_call = stq.chatterbox_check_callcenter_csat.next_call()
    assert stq_call['eta'] == expected_eta
    assert stq_call['args'] == [
        str(task['_id']),
        task['meta_info']['call_guid'],
        0,
    ]
