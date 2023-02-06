import datetime

import pytest

from hiring_telephony_oktell_callback.internal import constants
from hiring_telephony_oktell_callback.internal import dbops

QUERY_CHECK_ARCHIVATION = """SELECT *
FROM "hiring_telephony_oktell_callback"."tasks"
"""

QUERY_CHECK_DELETION = """SELECT *
FROM "hiring_telephony_oktell_callback"."archived_tasks"
"""

QUERY_CHECK_INTERVAL_DELETION = """SELECT *
FROM "hiring_telephony_oktell_callback"."call_intervals"
"""

QUERY_SET_TASK_STATE = """
UPDATE "hiring_telephony_oktell_callback"."tasks" AS "tasks"
SET "task_state" = '%s'
RETURNING "tasks"."task_id"
"""


@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_archivate_and_delete_tasks(
        create_tasks,
        load_json,
        cron_context,
        cron_runner,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
):
    # arrange
    tasks = load_json('request_create_tasks.json')
    prepare_tasks(tasks, days=-1)
    mock_salesforce_create_bulk_job({'id': 'test_job_id'})
    await create_tasks(tasks)
    await set_tasks_state(cron_context, 'pending')

    # act
    await cron_runner.archivate_tasks()
    await cron_runner.delete_tasks()

    # assert
    await _check_empty_table(QUERY_CHECK_DELETION, cron_context)


@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_archivate_tasks_pending(
        create_tasks,
        load_json,
        cron_context,
        cron_runner,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
        pgsql,
):
    # arrange
    tasks = load_json('request_create_tasks.json')
    prepare_tasks(tasks, days=-1)
    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )
    await create_tasks(tasks)
    await set_tasks_state(cron_context, 'pending')

    # act
    await cron_runner.archivate_tasks()

    # assert
    await _check_empty_table(QUERY_CHECK_ARCHIVATION, cron_context)
    await _check_empty_table(QUERY_CHECK_INTERVAL_DELETION, cron_context)
    await _check_non_empty_table(QUERY_CHECK_DELETION, cron_context)

    assert mock_salesforce_upload_data.times_called == 1
    request = mock_salesforce_upload_data.next_call()['request']
    assert (
        request.get_data().decode()
        == 'Id,Status\r\nID1,Expired\r\nID2,Expired\r\nID3,Expired\r\n'
    )

    assert sf_mock_create_bulk.has_calls
    request = sf_mock_create_bulk.next_call()['request']
    assert request.json == {
        'object': 'Task',
        'operation': 'update',
        'lineEnding': 'CRLF',
    }

    assert mock_salesforce_close_bulk_job.has_calls


@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_archivate_and_delete_tasks_cancelled(
        create_tasks,
        load_json,
        cron_context,
        cron_runner,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
):
    # arrange
    tasks = load_json('request_create_tasks.json')
    prepare_tasks(tasks, days=-1)
    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )
    await create_tasks(tasks)
    await set_tasks_state(cron_context, 'cancelled')

    # act
    await cron_runner.archivate_tasks()

    # assert
    await _check_empty_table(QUERY_CHECK_ARCHIVATION, cron_context)
    await _check_empty_table(QUERY_CHECK_INTERVAL_DELETION, cron_context)
    await _check_non_empty_table(QUERY_CHECK_DELETION, cron_context)

    assert mock_salesforce_upload_data.times_called == 0
    assert not sf_mock_create_bulk.has_calls
    assert not mock_salesforce_close_bulk_job.has_calls

    await cron_runner.delete_tasks()
    await _check_empty_table(QUERY_CHECK_DELETION, cron_context)


async def test_not_archivate_tasks(
        create_tasks,
        load_json,
        cron_context,
        cron_runner,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
):
    # arrange
    tasks = load_json('request_create_tasks.json')
    prepare_tasks(tasks, days=-1)
    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )
    await create_tasks(tasks)
    await set_tasks_state(cron_context, 'acquired')

    # act
    await cron_runner.archivate_tasks()

    # assert
    await _check_non_empty_table(QUERY_CHECK_ARCHIVATION, cron_context)
    await _check_non_empty_table(QUERY_CHECK_INTERVAL_DELETION, cron_context)
    await _check_empty_table(QUERY_CHECK_DELETION, cron_context)

    assert mock_salesforce_upload_data.times_called == 0
    assert not sf_mock_create_bulk.has_calls
    assert not mock_salesforce_close_bulk_job.has_calls


async def test_skipping_archivate_and_delete_tasks(
        create_tasks, load_json, cron_context, cron_runner,
):
    # arrange
    tasks = load_json('request_create_tasks.json')
    prepare_tasks(tasks, days=365 * 20)
    res = await create_tasks(tasks)
    archive_rows = await _execute_query(QUERY_CHECK_ARCHIVATION, cron_context)
    delete_rows = await _execute_query(QUERY_CHECK_DELETION, cron_context)

    # act
    await cron_runner.archivate_tasks()
    await cron_runner.delete_tasks()

    # assert
    assert res.status == 200
    assert archive_rows == await _execute_query(
        QUERY_CHECK_ARCHIVATION, cron_context,
    )
    assert delete_rows == await _execute_query(
        QUERY_CHECK_DELETION, cron_context,
    )


def prepare_tasks(tasks: dict, days: int):

    formatter = '%Y-%m-%dT%H:%M:%S.%f'

    archivate, delete = _generate_archivate_and_delete_dt(days)
    for task in tasks['tasks']:
        task['archived_at_dt'] = archivate.strftime(formatter)
        task['deleted_at_dt'] = delete.strftime(formatter)


async def set_tasks_state(cron_context, state, policy=constants.POLICY_MASTER):
    assert await _execute_query(
        QUERY_SET_TASK_STATE % state, cron_context, policy,
    )


async def _check_non_empty_table(
        query, cron_context, policy=constants.POLICY_FASTEST,
):
    assert await _execute_query(query, cron_context, policy)


async def _check_empty_table(
        query, cron_context, policy=constants.POLICY_FASTEST,
):
    assert not await _execute_query(query, cron_context, policy)


async def _execute_query(query, cron_context, policy=constants.POLICY_FASTEST):
    pool = dbops.choose_pool(cron_context, policy)
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return rows


def _generate_archivate_and_delete_dt(days=0):
    archivate = datetime.datetime.now() + datetime.timedelta(days=days)
    delete = archivate + datetime.timedelta(hours=3)
    return archivate, delete
