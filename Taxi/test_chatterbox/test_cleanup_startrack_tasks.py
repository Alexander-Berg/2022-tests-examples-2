import asyncio
import datetime

import bson
import pytest

from taxi.maintenance import run

from chatterbox.crontasks import cleanup_startrack_tasks
from test_chatterbox import plugins as conftest

NOW = datetime.datetime(2018, 1, 2, 4, 0)

TASK_IN_PROGRESS = bson.ObjectId('5b2cae5cb2682a976914c2a1')
TASK_RECENTLY_CLOSED = bson.ObjectId('5b2cae5cb2682a976914c2a2')
TASK_CLOSED = bson.ObjectId('5b2cae5cb2682a976914c2a3')
TASK_RECENTLY_WAITING = bson.ObjectId('5b2cae5cb2682a976914c2a4')
TASK_WAITING = bson.ObjectId('5b2cae5cb2682a976914c2a5')


@pytest.mark.config(
    CLEANUP_CLOSED_STARTRACK_TASKS_DELAY=6,
    CLEANUP_WAITING_STARTRACK_TASKS_DELAY=11,
)
@pytest.mark.now(NOW.isoformat())
async def test_cleanup_closed(
        cbox: conftest.CboxWrap,
        cbox_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_get_comments,
        mock_st_update_ticket,
        mock_st_transition,
):
    mock_st_get_all_attachments(empty=True)
    mock_st_get_ticket_with_status('closed')
    mock_st_get_comments([])
    mock_st_update_ticket('closed')

    await cleanup_startrack_tasks.do_stuff(cbox_context, loop)
    task_in_progress = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_IN_PROGRESS},
    )
    assert task_in_progress['status'] == 'in_progress'

    task_recently_closed = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_RECENTLY_CLOSED},
    )
    assert task_recently_closed['status'] == 'closed'

    task_closed = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_CLOSED},
    )
    assert task_closed['status'] == 'ready_to_archive'

    task_recently_waiting = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_RECENTLY_WAITING},
    )
    assert task_recently_waiting['status'] == 'waiting'

    task_waiting = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_WAITING},
    )
    assert task_waiting['status'] == 'ready_to_archive'

    transition_calls = mock_st_transition.calls
    assert transition_calls[0]['ticket'] == task_waiting['external_id']


@pytest.mark.config(CLEANUP_WAITING_STARTRACK_TASKS_DELAY=11)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(support_chatterbox='errors')
async def test_cleanup_errors(
        cbox: conftest.CboxWrap,
        cbox_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_get_comments,
        mock_st_update_ticket,
        mock_st_transition,
):
    mock_st_get_all_attachments(empty=True)
    mock_st_get_ticket_with_status('solved')
    mock_st_get_comments([])
    mock_st_update_ticket('solved')

    with pytest.raises(cleanup_startrack_tasks.CleanupTasksError):
        await cleanup_startrack_tasks.do_stuff(cbox_context, loop)

    task_with_error = await cbox.db.support_chatterbox.find_one(
        {'_id': TASK_WAITING},
    )
    assert task_with_error['status'] == 'waiting'

    transition_calls = mock_st_transition.calls
    assert transition_calls[0]['ticket'] == task_with_error['external_id']


@pytest.mark.filldb(support_chatterbox='tracker_reopen')
async def test_cleanup_closed_task_not_reopen_by_tracker(
        cbox: conftest.CboxWrap,
        cbox_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_get_comments,
        mock_st_update_ticket,
        mock_st_transition,
):
    mock_st_get_all_attachments(empty=True)
    mock_st_get_ticket_with_status('closed')
    mock_st_get_comments([])
    mock_st_update_ticket('closed')

    await cleanup_startrack_tasks.do_stuff(cbox_context, loop)

    transition_calls = mock_st_transition.calls

    task = await cbox.db.support_chatterbox.find_one(
        bson.ObjectId('5b2cae5cb2682a976914c2a4'),
    )
    assert task['status'] == 'ready_to_archive'
    assert transition_calls[0]['kwargs']['transition'] == 'close'

    task = await cbox.db.support_chatterbox.find_one(
        bson.ObjectId('5b2cae5cb2682a976914c2a3'),
    )
    assert task['status'] == 'ready_to_archive'
    assert transition_calls[1]['kwargs']['transition'] == 'close'
