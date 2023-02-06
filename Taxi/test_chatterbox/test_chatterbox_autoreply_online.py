# pylint: disable=no-member

import bson
import pytest

from chatterbox import stq_task


PREDISPATCH_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a5')
UPDATE_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a6')
FAILED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a7')
CLOSED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a8')
MANUAL_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a9')
CHAT_HISTORY = {
    'messages': [
        {
            'sender': {'id': 'some_login', 'role': 'client'},
            'id': 'some_id',
            'text': 'hello',
            'metadata': {'created': '2018-05-05T15:34:56'},
        },
    ],
    'new_message_count': 1,
}
CHAT_HISTORY_SUPPORT = {
    'messages': [
        {
            'sender': {'id': 'some_login', 'role': 'client'},
            'id': 'some_id',
            'text': 'hello',
            'metadata': {'created': '2018-05-05T15:34:56'},
        },
        {
            'sender': {'id': 'support_login', 'role': 'support'},
            'id': 'other_id',
            'text': 'goodbye',
            'metadata': {'created': '2018-05-05T15:34:57'},
        },
    ],
    'new_message_count': 1,
}


@pytest.mark.now('2021-05-13T17:53:00')
@pytest.mark.usefixtures('mock_get_user_phone', 'mock_chat_add_update')
@pytest.mark.parametrize(
    (
        'task_id',
        'history',
        'autoreply_response',
        'expected_stq_queue',
        'expected',
        'stq_queue',
    ),
    [
        (
            PREDISPATCH_TASK_ID,
            CHAT_HISTORY,
            'ok',
            'chatterbox_common_autoreply_queue',
            'autoreply_ok',
            'predispatch',
        ),
        (
            PREDISPATCH_TASK_ID,
            CHAT_HISTORY,
            'nope',
            'chatterbox_online_chat_processing',
            'autoreply_nope',
            'predispatch',
        ),
        (
            PREDISPATCH_TASK_ID,
            CHAT_HISTORY,
            'not_reply',
            'chatterbox_common_autoreply_queue',
            'autoreply_nto',
            'predispatch',
        ),
        (
            PREDISPATCH_TASK_ID,
            CHAT_HISTORY,
            'waiting',
            'chatterbox_common_autoreply_queue',
            'autoreply_waiting',
            'predispatch',
        ),
        (
            PREDISPATCH_TASK_ID,
            CHAT_HISTORY,
            'error',
            'chatterbox_online_chat_processing',
            'autoreply_error',
            'predispatch',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY,
            'ok',
            'chatterbox_common_autoreply_queue',
            'update_ok',
            'post_update',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY,
            'nope',
            None,
            'update_nope',
            'post_update',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY,
            'not_reply',
            'chatterbox_common_autoreply_queue',
            'update_nto',
            'post_update',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY,
            'waiting',
            'chatterbox_common_autoreply_queue',
            'update_waiting',
            'post_update',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY,
            'error',
            None,
            'update_error',
            'post_update',
        ),
        (
            UPDATE_TASK_ID,
            CHAT_HISTORY_SUPPORT,
            'ok',
            None,
            'update_ok',
            'post_update',
        ),
        (
            FAILED_TASK_ID,
            CHAT_HISTORY,
            'ok',
            None,
            'update_fail',
            'post_update',
        ),
        (
            CLOSED_TASK_ID,
            CHAT_HISTORY,
            'ok',
            None,
            'closed_not_add_tag',
            'post_update',
        ),
        (
            MANUAL_TASK_ID,
            CHAT_HISTORY_SUPPORT,
            'ok',
            'chatterbox_online_chat_processing',
            'update_manual',
            'post_update',
        ),
    ],
)
async def test_online_autoreply(
        cbox,
        stq,
        task_id,
        history,
        autoreply_response,
        expected_stq_queue,
        expected,
        stq_queue,
        load_json,
        mock_translate,
        mock_chat_get_history,
        mock_autoreply,
        mock_uuid_uuid4,
):
    mock_translate('ru')
    mock_chat_get_history(history)
    mock_autoreply(autoreply_response)

    if stq_queue == 'predispatch':
        await stq_task.chatterbox_predispatch(cbox.app, task_id)
    elif stq_queue == 'post_update':
        await stq_task.post_update(cbox.app, task_id)

    if expected_stq_queue is not None:
        assert getattr(stq, expected_stq_queue).times_called == 1

    task = await cbox.db.support_chatterbox.find_one(task_id)
    expected_task = load_json('expected_tasks.json')[expected]
    assert set(task['tags']) == set(expected_task['tags'])
    assert task['meta_info'] == expected_task['meta_info']
    assert task['status'] == expected_task['status']
