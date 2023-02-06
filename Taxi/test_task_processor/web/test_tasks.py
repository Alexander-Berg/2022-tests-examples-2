# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def perform_action(web_app_client):
    async def _do_id(
            task_id, action, with_children=False, expected_status=200,
    ):
        response = await web_app_client.post(
            f'/v1/jobs/tasks/{action}/',
            json={'task_id': task_id, 'with_children': with_children},
            headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == expected_status
        return response

    return _do_id


@pytest.mark.parametrize(
    'expected_status, terminate_target, terminate_all_job',
    [(409, False, False), (200, True, False), (200, False, True)],
)
@pytest.mark.pgsql('task_processor', files=['test_tasks_retry.sql'])
@pytest.mark.xfail(reason='Flaps')
async def test_tasks_retry(
        perform_action,
        patch,
        get_job,
        pgsql,
        web_context,
        expected_status,
        terminate_target,
        terminate_all_job,
):
    job_id = await web_context.task_processor.create_job(
        provider_name='deoevgen',
        recipe_name='test_create_job',
        variables={
            'service_id': 1,
            'test': 'test321',
            'env': 'unstable',
            'new_service_ticket': 'test-1',
        },
        change_doc_id='test_change_doc_id',
        token=None,
    )
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        f'select id from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    task_id = tasks_rows[0][0]
    if terminate_target:
        async with web_context.pg.master_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    UPDATE task_processor.tasks
                    SET status = 'success'::JOB_STATUS
                    WHERE id = $1::INTEGER;
                    """,
                    task_id,
                )
    if terminate_all_job:
        await perform_action(task_id, 'finish', True)
        async with web_context.pg.master_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    UPDATE task_processor.jobs
                    SET status = 'success'::JOB_STATUS
                    WHERE id = $1::INTEGER;
                    """,
                    job_id,
                )
        job = await get_job(job_id)
        assert dict(job)['status'] == 'success'

    await perform_action(task_id, 'retry', expected_status=expected_status)
    job = await get_job(job_id)
    assert dict(job)['status'] == 'in_progress'


@pytest.mark.parametrize(
    'action, new_status, with_children',
    [
        ('cancel', 'canceled', False),
        ('cancel', 'canceled', True),
        ('finish', 'success', False),
        ('finish', 'success', True),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_task_change_statuses.sql'])
async def test_task_change_statuses(
        perform_action,
        patch,
        pgsql,
        web_context,
        action,
        new_status,
        with_children,
        mock_provider_client,
):
    @mock_provider_client('/task-processor/v1/cubes/')
    # pylint: disable=unused-variable
    def handler(request):
        return {'status': 'in_progress'}

    job_id = await web_context.task_processor.create_job(
        provider_name='deoevgen',
        recipe_name='test_create_job',
        variables={
            'service_id': 1,
            'test': 'test321',
            'env': 'unstable',
            'new_service_ticket': 'test-1',
        },
        change_doc_id='test_change_doc_id',
        token=None,
    )
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        f'select id, job_id from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    task = {'id': tasks_rows[0][0], 'job_id': tasks_rows[0][1]}

    response = await perform_action(task['id'], action, with_children)
    result = (await response.json())['updated_tasks']

    assert {x['job_id'] for x in result} == {task['job_id']}
    assert {x['old_status'] for x in result} == {'in_progress'}
    assert {x['new_status'] for x in result} == {new_status}

    if not with_children:
        assert len(result) == 1
    else:
        assert len(result) > 1

    cursor.execute(
        f'select id, job_id, status from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    tasks = []
    for task_row in tasks_rows:
        tasks.append(
            {'id': task_row[0], 'job_id': task_row[1], 'status': task_row[2]},
        )
    task = tasks[0]
    assert task['status'] == new_status

    if not with_children:
        assert {x['status'] for x in tasks if x['id'] != task['id']} == {
            'in_progress',
        }
    else:
        assert {x['status'] for x in tasks if x['id'] >= task['id']} == {
            new_status,
        }
        assert not [
            x['status']
            for x in tasks
            if x['id'] < task['id'] and x['status'] != 'in_progress'
        ]


@pytest.mark.parametrize(
    'action, new_status, with_children',
    [
        ('cancel', 'canceled', False),
        ('cancel', 'canceled', True),
        ('finish', 'success', False),
        ('finish', 'success', True),
    ],
)
@pytest.mark.pgsql(
    'task_processor', files=['test_task_change_statuses_not_from_start.sql'],
)
async def test_task_change_statuses_not_from_start(
        perform_action,
        patch,
        pgsql,
        web_context,
        action,
        new_status,
        with_children,
        mock_provider_client,
):
    @mock_provider_client('/task-processor/v1/cubes/')
    # pylint: disable=unused-variable
    def handler(request):
        return {'status': 'in_progress'}

    job_id = await web_context.task_processor.create_job(
        provider_name='deoevgen',
        recipe_name='test_create_job',
        variables={
            'service_id': 1,
            'test': 'test321',
            'env': 'unstable',
            'new_service_ticket': 'test-1',
        },
        change_doc_id='test_change_doc_id',
        token=None,
    )

    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        f'select id, job_id from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    ids_to_success = [x[0] for x in tasks_rows][:2]

    async with web_context.pg.master_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE task_processor.tasks
                SET status = 'success'
                WHERE id = ANY ($1::INTEGER[])
                """,
                ids_to_success,
            )

    await perform_action(tasks_rows[2][0], action, with_children)

    cursor.execute(
        f'select id, job_id, status from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    tasks = []
    for task_row in tasks_rows:
        tasks.append(
            {'id': task_row[0], 'job_id': task_row[1], 'status': task_row[2]},
        )

    assert {x['status'] for x in tasks[:2]} == {'success'}
    if not with_children:
        assert {x['status'] for x in tasks[3:]} == {'in_progress'}
        assert tasks[2]['status'] == new_status
    else:
        assert {x['status'] for x in tasks[3:]} == {new_status}
