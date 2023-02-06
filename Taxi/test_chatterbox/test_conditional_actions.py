# pylint: disable=no-self-use,redefined-outer-name, no-member
import datetime

import pytest

from chatterbox.crontasks import check_conditional_actions
from chatterbox.internal import autoexport

NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_ACTIONS=[
        {
            'action_tag': 'dismiss_test_tag',
            'enabled': True,
            'conditions': {'line': 'wanna_dismiss'},
            'action': 'dismiss',
        },
        {
            'action_tag': 'test_Tag',
            'enabled': True,
            'conditions': {
                'created': {'#gt': 'since:3d'},
                'meta_info/city': 'Moscow',
            },
            'action': 'export',
        },
        {
            'action_tag': 'other_test_tag',
            'enabled': True,
            'conditions': {'line': 'next'},
            'action': 'close',
            'macro_id': 3,
        },
        {
            'action_tag': 'communicate_tag',
            'enabled': True,
            'conditions': {'line': 'comm'},
            'action': 'communicate',
            'macro_id': 3,
        },
        {
            'action_tag': 'communicate_tag',
            'enabled': True,
            'conditions': {'line': 'comm', 'chat_type': 'bank'},
            'action': 'communicate_forbidden',
            'macro_id': 3,
        },
        {
            'action_tag': 'communicate_tag_w',
            'enabled': True,
            'conditions': {'line': 'comm_w'},
            'action': 'communicate',
            'macro_id': 3,
        },
        {
            'action_tag': 'next_test_tag',
            'enabled': True,
            'conditions': {'line': 'first'},
            'action': 'forward',
            'line': 'second',
        },
        {
            'action_tag': 'next_test_tag',
            'enabled': True,
            'conditions': {'line': 'first', 'status': {'$nin': ['forwarded']}},
            'action': 'forward',
            'line': 'second',
        },
        {
            'action': 'restart_routing',
            'action_tag': 'restart_routing_tag',
            'enabled': True,
            'conditions': {'external_id': 'restart_routing_external_id'},
        },
        {
            'action': 'defer',
            'action_tag': 'defer_tag',
            'enabled': True,
            'conditions': {'external_id': 'defer_external_id'},
            'defer_sec': 86400,
            'macro_id': 3,
        },
    ],
    CHATTERBOX_LINES={
        'first': {'types': ['client'], 'priority': 1, 'tags': ['chat_driver']},
        'second': {'types': ['client'], 'priority': 2},
    },
    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
        'bank': {'__default__': False, 'conditional_actions': True},
    },
)
async def test_conditional_actions(
        cbox_context, loop, mock_chat_add_update, mock_chat_get_history,
):
    cbox_context.data.secdist['settings_override'][
        'ADMIN_ROBOT_LOGIN_BY_TOKEN'
    ] = {'some_token': 'robot-chatterbox'}
    mock_chat_get_history({'messages': []})

    await check_conditional_actions.do_stuff(cbox_context, loop)

    tasks = cbox_context.data.db.support_chatterbox.find()
    async for task in tasks:
        if task['_id'] == 'must_be_exported':
            assert task['status'] == 'export_enqueued'
            assert 'test_tag' in task['tags']
        elif task['_id'] == 'must_be_closed':
            assert task['status'] == 'closed'
            assert 'other_test_tag' in task['tags']
        elif task['_id'] == 'must_be_forwarded':
            assert task['status'] == 'reopened'
            assert 'next_test_tag' in task['tags']
            assert task['line'] == 'second'
        elif task['_id'] == 'already_exported':
            assert task['status'] == 'exported'
        elif task['_id'] == 'is_still_exporting':
            assert task['status'] == 'export_enqueued'
        elif task['_id'] == 'already_archived':
            assert task['status'] == 'archived'
        elif task['_id'] == 'is_still_archiving':
            assert task['status'] == 'archive_in_progress'
        elif task['_id'] == 'communicate':
            assert task['status'] == 'new'
            assert 'communicate_tag' in task['tags']
        elif task['_id'] == 'communicate_forbidden':
            assert task['status'] == 'new'
            assert 'communicate_tag' not in task['tags']
        elif task['_id'] == 'communicate_waiting':
            assert task['status'] == 'waiting'
            assert 'communicate_tag_w' in task['tags']
        elif task['_id'] == 'must_be_dismissed':
            assert task['status'] == 'closed'
        elif task['_id'] == 'must_be_restart_routing':
            assert task['line'] == 'first'
        elif task['_id'] == 'must_be_deferred':
            assert task['status'] == 'deferred'
            assert task['reopen_at'] > datetime.datetime.utcnow()
        assert 'ar_reply' not in task.get('tags', [])


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'conditions,expected_length',
    [
        ({'meta_info/city': 'Moscow'}, 1),
        ({'created': {'#gt': 'since:3d'}}, 3),
        ({'created': {'#gt': 'since:1d'}}, 0),
        ({'created': {'#gt': 'timestring:2018-05-04T00:00:00+0300'}}, 3),
        ({'created': {'#gt': 'timestring:2018-05-06T00:00:00+0300'}}, 0),
    ],
)
async def test_conditions(cbox, conditions, expected_length):
    tasks = cbox.app.tasks_manager.iterate_active_tasks(
        extra_rule={'export_tag': 'test_tag', 'conditions': conditions},
    )
    assert len([_ async for _ in tasks]) == expected_length


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_ACTIONS=[
        {
            'action': 'export',
            'action_tag': 'test_limit_tag',
            'enabled': True,
            'conditions': {'line': 'second'},
        },
        {
            'action': 'export',
            'action_tag': 'test_limit_tag',
            'enabled': True,
            'conditions': {'line': 'second'},
        },
    ],
    ZENDESK_EXPORT_RULES_LIMIT=1,
)
async def test_conditional_export_limit(cbox_context, loop):
    for expected_cnt in range(1, 2):
        await check_conditional_actions.do_stuff(cbox_context, loop)

        cnt = await cbox_context.data.db.support_chatterbox.find(
            {'tags': 'test_limit_tag'},
        ).count()

        assert cnt == expected_cnt


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_ACTIONS=[
        {
            'action': 'export',
            'action_tag': 'test_limit_tag',
            'enabled': True,
            'conditions': {'line': 'second'},
        },
        {
            'action_tag': 'other_test_tag',
            'enabled': True,
            'conditions': {'line': 'next'},
            'action': 'close',
            'macro_id': 3,
        },
    ],
)
async def test_autoexport_error(
        cbox_context, loop, mock_chat_add_update, mock_chat_get_history,
):
    cbox_context.data.secdist['settings_override'][
        'ADMIN_ROBOT_LOGIN_BY_TOKEN'
    ] = {'some_token': 'robot-chatterbox'}
    mock_chat_get_history({'messages': []})

    with pytest.raises(autoexport.MassActionRuntimeError):
        await check_conditional_actions.do_stuff(cbox_context, loop)

    task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': 'must_be_closed'},
    )

    assert task['status'] == 'closed'
    assert 'other_test_tag' in task['tags']


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_ACTIONS=[
        {
            'action_tag': 'other_test_tag',
            'enabled': True,
            'conditions': {'line': 'next'},
            'action': 'close',
            'macro_id': 3,
        },
    ],
    CHATTERBOX_TAGS_SERVICE_CONDITIONS=[
        {
            'condition_tags': ['tag', 'other_test_tag'],
            'tag_to_add': 'close_tag',
            'entity_type': 'phone_id',
            'tag_lifetime': 3600,
        },
    ],
)
async def test_conditional_actions_tagging(
        cbox_context, loop, mock_chat_add_update, mock_chat_get_history, stq,
):
    cbox_context.data.secdist['settings_override'][
        'ADMIN_ROBOT_LOGIN_BY_TOKEN'
    ] = {'some_token': 'robot-chatterbox'}
    mock_chat_get_history({'messages': []})

    await check_conditional_actions.do_stuff(cbox_context, loop)

    tasks = cbox_context.data.db.support_chatterbox.find()
    async for task in tasks:
        if task['_id'] == 'must_be_closed':
            assert task['status'] == 'closed'
            assert 'other_test_tag' in task['tags']
            assert 'tags_macro_3' in task['tags']
    assert stq.chatterbox_add_tag_to_tags_service.times_called == 1
    call = stq.chatterbox_add_tag_to_tags_service.next_call()
    assert call['args'] == ['must_be_closed', 'close_tag', 'phone_id', 3600]
