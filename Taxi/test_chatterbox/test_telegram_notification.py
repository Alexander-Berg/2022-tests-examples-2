# pylint: disable=protected-access,unused-variable, no-member
import datetime
import http

import bson
import pytest

from taxi.clients import support_chat

from chatterbox import stq_task

NOW = datetime.datetime(2019, 12, 5, 12, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(CHATTERBOX_TELEGRAM_NOTIFY_CHATS={'1': 'telegram_id1'})
@pytest.mark.parametrize(
    ['expires', 'must_send_message'],
    [
        (None, True),
        (datetime.datetime(2019, 12, 5, 13, 15, 0), True),
        (datetime.datetime(2019, 12, 5, 11, 15, 0), False),
    ],
)
@pytest.mark.parametrize(
    ('task_id', 'rule_message'),
    [
        (bson.ObjectId('5b2cae5cb2682a976914c2a1'), 'message'),
        (bson.ObjectId('5b2cae5cb2682a976914c2a2'), None),
    ],
)
async def test_telegram_notification(
        cbox_stq,
        mock,
        patch,
        expires,
        must_send_message,
        task_id,
        rule_message,
):
    @mock
    @patch('telegram.Bot.send_message')
    def send_message(*args, **kwargs):
        message = args[1]
        if not rule_message:
            assert message == (
                'Task %s updated.'
                ' Check task https://supchat.taxi.dev.yandex-team.ru/chat/%s'
            ) % (task_id, task_id)
        else:
            assert message == rule_message

    await stq_task.chatterbox_telegram_notify(
        cbox_stq, task_id, None, message=rule_message, expires=expires,
    )
    assert bool(send_message.calls) == must_send_message


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    chatterbox={
        'tlg_tanker_1': {'ru': 'Text {meta_info[meta_field]} {status}'},
        'tlg_tanker_2': {'ru': 'Text {meta_info[not_exist_field]} {status}'},
    },
)
@pytest.mark.config(
    CHATTERBOX_TELEGRAM_NOTIFY={
        'first': {
            'conditions': {'line': 'first'},
            'chat_id': 'telegram_id1',
            'enabled': True,
        },
        'second': {
            'conditions': {'line': 'second'},
            'chat_id': 'telegram_id2',
            'enabled': True,
        },
        'check_enabled': {
            'conditions': {'line': 'second'},
            'chat_id': 'telegram_id3',
            'enabled': False,
        },
        'check_conditions': {
            'conditions': {
                'tags': {'#in': ['tlg_tag']},
                'status': 'reopened',
                'fields/meta_field': '123',
            },
            'chat_id': 'telegram_id4',
            'enabled': True,
        },
        'check_message': {
            'conditions': {'line': 'fourth'},
            'chat_id': 'telegram_id5',
            'message_tanker': 'tlg_tanker_1',
            'enabled': True,
        },
        'check_message_error': {
            'conditions': {'line': 'fourth'},
            'chat_id': 'telegram_id9',
            'message_tanker': 'tlg_tanker_2',
            'enabled': True,
        },
        'in_time_range': {
            'conditions': {'line': 'firth'},
            'chat_id': 'telegram_id6',
            'time_from': '23:00',
            'time_to': '13:00',
            'enabled': True,
        },
        'in_time_range_2': {
            'conditions': {'line': 'firth'},
            'chat_id': 'telegram_id7',
            'time_from': '09:00',
            'time_to': '12:15',
            'enabled': True,
        },
        'not_in_time_range': {
            'conditions': {'line': 'firth'},
            'chat_id': 'telegram_id8',
            'time_from': '09:00',
            'time_to': '11:00',
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize('enable_ttl', [False, True])
@pytest.mark.parametrize(
    ('chat_id', 'telegram_chat_ids', 'notify_count', 'message'),
    [
        ('chat_line_first', ['telegram_id1'], 1, None),
        pytest.param(
            'chat_line_first',
            ['telegram_id1'],
            0,
            None,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {'__default__': False, 'telegram': True},
                    },
                ),
            ],
        ),
        ('chat_line_second', ['telegram_id2'], 1, None),
        ('chat_line_third', [], 0, None),
        ('chat_telegram_check', ['telegram_id1', 'telegram_id4'], 2, None),
        (
            'chat_telegram_check_2',
            ['telegram_id5', 'telegram_id9'],
            2,
            ['Text 123 reopened', None],
        ),
        ('chat_telegram_check_3', ['telegram_id6', 'telegram_id7'], 2, None),
    ],
)
async def test_post_task_notify(
        cbox,
        stq,
        enable_ttl,
        chat_id,
        telegram_chat_ids,
        notify_count,
        message,
        monkeypatch,
        mock_chat_get_history,
        mock_chat_mark_processed,
):
    cbox.app.config.CHATTERBOX_TELEGRAM_NOTIFY_ENABLE_TTL = enable_ttl
    mock_chat_get_history({'messages': []})

    async def get_chat(*args, **kwargs):
        chat = {
            'id': chat_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {
                'ask_csat': False,
                'last_message_from_user': True,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
            },
            'type': 'client_support',
        }

        return chat

    async def _dummy_chat_update(*args, **kwargs):
        return 'test'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_chat_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    data = {'type': 'chat', 'external_id': chat_id}
    await cbox.post('/v1/tasks', data=data)
    assert cbox.status == http.HTTPStatus.OK
    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': chat_id},
    )
    notify_stq_calls = [
        stq.chatterbox_telegram_notify.next_call()
        for _ in range(stq.chatterbox_telegram_notify.times_called)
    ]
    if notify_count:
        assert len(notify_stq_calls) == notify_count
        for notify in range(notify_count):
            assert notify_stq_calls[notify]['args'] == [
                task['_id'],
                telegram_chat_ids[notify],
            ]
            if message:
                assert (
                    notify_stq_calls[notify]['kwargs']['message']
                    == message[notify]
                )
            if enable_ttl:
                assert notify_stq_calls[notify]['kwargs']['expires'] == {
                    '$date': 1575551700000,
                }
    else:
        assert not notify_stq_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_TELEGRAM_NOTIFY={
        'first': {
            'conditions': {'line': 'first'},
            'chat_id': 'telegram_id1',
            'enabled': True,
        },
        'corp': {
            'conditions': {'line': 'corp'},
            'chat_id': 'telegram_id2',
            'enabled': True,
        },
    },
    CHAT_LINE_TRANSITIONS={'corp': ['urgent'], 'second': ['first']},
    CHATTERBOX_LINES={
        'urgent': {
            'name': 'Urgent',
            'priority': 1,
            'conditions': {'tags': 'elite'},
            'types': ['client'],
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'types': ['client']},
        'corp': {
            'name': 'Corp',
            'priority': 2,
            'conditions': {'tags': 'online'},
        },
        'second': {'types': ['client']},
    },
)
@pytest.mark.parametrize('enable_ttl', [False, True])
@pytest.mark.parametrize(
    'task_id, line, telegram_chat_id, notify',
    [
        ('5c222085779fb31c8c6b8f0a', 'urgent', None, False),
        ('5c222124779fb31c8c6b8f0b', 'first', 'telegram_id1', True),
    ],
)
async def test_forward_task_notify(
        cbox, stq, enable_ttl, task_id, line, telegram_chat_id, notify,
):
    cbox.app.config.CHATTERBOX_TELEGRAM_NOTIFY_ENABLE_TTL = enable_ttl
    await cbox.post(
        '/v1/tasks/%s/forward' % task_id, params={'line': line}, data={},
    )
    assert cbox.status == http.HTTPStatus.OK

    if notify:
        stq_put_call = stq.chatterbox_telegram_notify.next_call()
        assert stq_put_call['args'] == [{'$oid': task_id}, telegram_chat_id]
        if enable_ttl:
            assert stq_put_call['kwargs']['expires'] == {
                '$date': 1575551700000,
            }
    else:
        assert not stq.chatterbox_telegram_notify.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_TELEGRAM_NOTIFY={
        'first': {
            'conditions': {'line': 'first'},
            'chat_id': 'telegram_id1',
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize('enable_ttl', [False, True])
@pytest.mark.parametrize(
    'chat_id, telegram_chat_id, notify',
    [('chat_line_first_predispatch', 'telegram_id1', True)],
)
async def test_predispatch_task_notify(
        cbox,
        stq,
        enable_ttl,
        chat_id,
        telegram_chat_id,
        notify,
        monkeypatch,
        mock_chat_get_history,
        mock_get_chat_order_meta,
):
    cbox.app.config.CHATTERBOX_TELEGRAM_NOTIFY_ENABLE_TTL = enable_ttl
    mock_chat_get_history({'messages': []})

    async def get_chat(*args, **kwargs):
        chat = {
            'id': chat_id,
            'status': {'is_open': True, 'is_visible': True},
            'metadata': {
                'ask_csat': False,
                'last_message_from_user': True,
                'csat_value': 'amazing',
                'csat_reasons': ['fast answer', 'thank you'],
            },
            'type': 'client_support',
        }

        return chat

    async def _dummy_chat_update(*args, **kwargs):
        return 'test'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_chat_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    task = await cbox.db.support_chatterbox.find_one(
        {'type': 'chat', 'external_id': chat_id},
    )
    await stq_task.chatterbox_predispatch(cbox.app, task['_id'])

    notify_stq_calls = [
        stq.chatterbox_telegram_notify.next_call()
        for _ in range(stq.chatterbox_telegram_notify.times_called)
    ]
    if notify:
        assert notify_stq_calls[0]['args'] == [task['_id'], telegram_chat_id]
        if enable_ttl:
            assert notify_stq_calls[0]['kwargs']['expires'] == {
                '$date': 1575551700000,
            }
    else:
        assert not notify_stq_calls
