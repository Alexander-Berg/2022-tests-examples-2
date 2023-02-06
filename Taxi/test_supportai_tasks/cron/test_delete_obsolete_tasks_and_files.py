import datetime

import pytest

from supportai_tasks import models as db_models
from supportai_tasks.generated.cron import run_cron


@pytest.mark.config(
    SUPPORTAI_TASKS_STORE_TIMINGS={
        'default_tasks_and_files_store_time_in_days': 30,
        'tasks_chunk_size': 1000,
        'default_files_chunk_size': 200,
        'delay_between_chunks_ms': 0,
        'projects': [
            {
                'project_slug': 'project_with_specific_settings',
                'files_chunk_size': 100,
                'tasks_and_files_store_time_in_days': 1,
            },
            {
                'project_slug': 'no_such_project_anymore',
                'files_chunk_size': 100,
                'tasks_and_files_store_time_in_days': 1,
            },
        ],
    },
)
async def test_delete_obsolete_tasks_and_files(cron_context):
    now = datetime.datetime.now().astimezone()
    day = datetime.timedelta(days=1)
    projects = [
        # id, slug
        (1, 'project_with_specific_settings'),
        (2, 'some_project'),
        (3, 'some_another_project'),
    ]
    files = [
        # id, project_id, should_be_deleted
        (1, 1, True),
        (2, 1, False),
        (3, 2, False),
        (4, 2, True),
        (5, 2, True),
        (6, 1, True),
        (7, 2, True),
        (8, 3, False),
    ]
    tasks = [
        # id, project_id, file_id, created, should_be_deleted
        (1, 1, '1', now - 35 * day, True),
        (2, 1, '2', now - 2 * day, True),
        (3, 1, '2', now - 0.5 * day, False),
        (4, 1, None, now - 0.5 * day, False),
        (5, 2, '3', now - 2 * day, False),
        (6, 2, '4', now - 35 * day, True),
        (7, 2, '6', now - 25 * day, False),
        (8, 3, '7', now - 35 * day, True),
        (9, 2, '8', now - 25 * day, False),
    ]

    async with cron_context.pg.master_pool.acquire() as conn:
        for _, project_slug in projects:
            await db_models.Project.insert(
                cron_context, conn, project_slug, project_slug, False, None,
            )
        for _, project_id, _ in files:
            await db_models.File.insert(
                cron_context, conn, project_id, '', '', b'',
            )
        for _, project_id, file_id, created, _ in tasks:
            await db_models.Task.insert(
                context=cron_context,
                db_conn=conn,
                project_id=project_id,
                type_='outgoing_calls_init',
                created=created,
                status='created',
                file_id=file_id,
                name=None,
                params=None,
            )

    await run_cron.main(
        [
            'supportai_tasks.crontasks.delete_obsolete_tasks_and_files',
            '-t',
            '0',
        ],
    )

    tasks_left = []
    files_left = []
    async with cron_context.pg.slave_pool.acquire() as conn:
        for project_id, _ in projects:
            tasks_left += await db_models.Task.select_by_project(
                context=cron_context,
                db_conn=conn,
                project_id=project_id,
                types=None,
                ref_task_id=None,
                limit=1000,
                older_than=None,
            )
        for file_id in range(10):
            file = await db_models.File.select_by_id(
                cron_context, conn, file_id,
            )
            if file:
                files_left.append(file)

    expected_tasks_left = {
        id_ for id_, *_, should_be_deleted in tasks if not should_be_deleted
    }
    expected_files_left = {
        id_ for id_, _, should_be_deleted in files if not should_be_deleted
    }

    assert {task.id for task in tasks_left} == expected_tasks_left
    assert {file.id for file in files_left} == expected_files_left
