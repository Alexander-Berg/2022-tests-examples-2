import pytest

from chatterbox.crontasks import close_idle_waiting_tasks


CLOSE_WAITING_TASK_MACRO_IDS = ['1001', '1002']
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
    assert kwargs['close_task']
    assert not kwargs['communicate']
    assert kwargs['macro_id'] == CLOSE_WAITING_TASK_MACRO_IDS[0]

    if 'chat_type' not in task:
        raise Exception(f'Chat type not in task')


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_CLOSE_WAITING_TASK_MACRO_IDS=CLOSE_WAITING_TASK_MACRO_IDS,
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

    await close_idle_waiting_tasks.do_stuff(cbox_context, loop)

    successful_count = 0
    error_count = 0
    for message in caplog.messages:
        if 'close successful' in message:
            successful_count += 1
        else:
            error_count += 1
    assert not error_count
    assert successful_count == 2
    assert len(_apply.calls) == 2


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_CLOSE_WAITING_TASK_MACRO_IDS=CLOSE_WAITING_TASK_MACRO_IDS,
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

    await close_idle_waiting_tasks.do_stuff(cbox_context, loop)

    successful_count = 0
    error_count = 0
    for message in caplog.messages:
        if 'close successful' in message:
            successful_count += 1
        else:
            error_count += 1
    assert error_count == 1
    assert successful_count == 1
    assert len(_apply.calls) == 2


@pytest.mark.now(NOW)
@pytest.mark.config(
    CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE=CHATTERBOX_MAX_IDLE_MINUTES_FOR_LINE,
    CHATTERBOX_CLOSE_WAITING_TASK_MACRO_IDS=CLOSE_WAITING_TASK_MACRO_IDS,
)
@pytest.mark.filldb(support_chatterbox='skip_tasks')
async def test_skip_tasks(cbox_context, loop, patch):
    @patch(
        'chatterbox.internal.tasks_manager._common.' 'TasksManager.autoreply',
    )
    async def _apply(*args, **kwargs):

        await check_apply_params(cbox_context, *args, **kwargs)

    @patch('random.choice')
    def _choice(lst):
        return lst[0]

    await close_idle_waiting_tasks.do_stuff(cbox_context, loop)

    assert not _apply.calls
