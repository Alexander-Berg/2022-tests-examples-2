import bson
import pytest

from chatterbox.crontasks import move_idle_task_to_waiting
from chatterbox.internal import tasks_manager

CHATTERBOX_HOLD_MACRO_TAGS = ['HOLD_MACRO']
CHATTERBOX_WAITING_MACRO_IDS = ['999', '1000']
CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE = {
    'first': {'in_progress': 4, 'waiting': 4},
    'second': {'in_progress': 5, 'waiting': 5},
}


NOW = '11.11.2021T13:00:00'


async def check_apply_params(cbox_context, *args, **kwargs):
    task = kwargs['task']
    task_in_database = (
        await cbox_context.data.db.secondary.support_chatterbox.find_one(
            {'_id': task['_id']},
        )
    )
    assert task == task_in_database
    assert task['support_admin'] == tasks_manager.LOGIN_SUPERUSER
    assert (
        task['history'][-1]['action']
        == tasks_manager.ACTION_RESET_SUPPORT_ADMIN
    )
    assert not kwargs['close_task']
    assert not kwargs['communicate']
    assert kwargs['macro_id'] == CHATTERBOX_WAITING_MACRO_IDS[0]

    if 'chat_type' not in task:
        raise Exception(f'Chat type not in task')


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_HOLD_MACRO_TAGS=CHATTERBOX_HOLD_MACRO_TAGS,
    CHATTERBOX_WAITING_MACRO_IDS=CHATTERBOX_WAITING_MACRO_IDS,
)
async def test_all_green(cbox_context, loop, patch, caplog):
    @patch(
        'chatterbox.internal.tasks_manager._common.' 'TasksManager.autoreply',
    )
    async def _apply(*args, **kwargs):

        await check_apply_params(cbox_context, *args, **kwargs)

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    successful_count = 0
    error_count = 0
    for message in caplog.messages:
        if 'waiting successful' in message:
            successful_count += 1
        elif 'failed' in message:
            error_count += 1
    assert not error_count
    assert successful_count == 5
    assert len(_apply.calls) == 5


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_HOLD_MACRO_TAGS=CHATTERBOX_HOLD_MACRO_TAGS,
    CHATTERBOX_WAITING_MACRO_IDS=[],
)
@pytest.mark.filldb(support_chatterbox='green_empty_waiting_macro_ids')
async def test_green_empty_waiting_macro_ids(
        cbox_context, loop, patch, caplog,
):
    task_id = '5b2cae5cb2682a976914c2a1'

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    task = await cbox_context.db.secondary.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['status'] == tasks_manager.STATUS_WAITING
    assert task['history'][-1]['action'] == 'comment'
    assert 'comment' not in task['history'][-1]
    assert 'macro_ids' not in task['history'][-1]


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_HOLD_MACRO_TAGS=CHATTERBOX_HOLD_MACRO_TAGS,
    CHATTERBOX_WAITING_MACRO_IDS=CHATTERBOX_WAITING_MACRO_IDS,
)
@pytest.mark.filldb(support_chatterbox='green_red_autoreply')
async def test_green_red_autoreply(cbox_context, loop, patch, caplog):
    @patch(
        'chatterbox.internal.tasks_manager._common.' 'TasksManager.autoreply',
    )
    async def _apply(*args, **kwargs):
        await check_apply_params(cbox_context, *args, **kwargs)

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    successful_count = 0
    error_count = 0
    for message in caplog.messages:
        if 'waiting failed' in message:
            error_count += 1
        if 'waiting successful' in message:
            successful_count += 1
    assert error_count == 1
    assert successful_count == 1
    assert len(_apply.calls) == 2


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_HOLD_MACRO_TAGS=CHATTERBOX_HOLD_MACRO_TAGS,
    CHATTERBOX_WAITING_MACRO_IDS=CHATTERBOX_WAITING_MACRO_IDS,
)
@pytest.mark.filldb(support_chatterbox='green_red_change')
async def test_green_red_change(cbox_context, loop, patch, caplog):
    @patch(
        'chatterbox.internal.tasks_manager._common.' 'TasksManager.autoreply',
    )
    async def _apply(*args, **kwargs):
        await check_apply_params(cbox_context, *args, **kwargs)

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    successful_count = 0
    error_count = 0
    for message in caplog.messages:
        if 'support admin failed' in message:
            error_count += 1
        if 'waiting successful' in message:
            successful_count += 1
    assert error_count == 1
    assert successful_count == 1
    assert len(_apply.calls) == 1


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_HOLD_MACRO_TAGS=CHATTERBOX_HOLD_MACRO_TAGS,
    CHATTERBOX_WAITING_MACRO_IDS=CHATTERBOX_WAITING_MACRO_IDS,
)
@pytest.mark.filldb(support_chatterbox='skip_tasks')
async def test_skip_tasks(cbox_context, loop, patch, caplog):
    @patch(
        'chatterbox.internal.tasks_manager._common.' 'TasksManager.autoreply',
    )
    async def _apply(*args, **kwargs):
        await check_apply_params(cbox_context, *args, **kwargs)

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    assert not caplog.messages
    assert not _apply.calls


@pytest.mark.now(NOW)
@pytest.mark.config(CHATTERBOX_HOLD_MACRO_TAGS='UNEXPECTED_HOLD_TAG')
async def test_empty_hold_macro_ids(cbox_context, loop, caplog):
    await move_idle_task_to_waiting.do_stuff(cbox_context, loop)
    logs = caplog.messages
    assert len(logs) == 1
    assert 'Hold macro not found' in logs[0]
