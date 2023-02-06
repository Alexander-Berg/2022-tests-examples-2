# pylint: disable=redefined-outer-name, protected-access
import datetime
import json

import pytest

from clownductor.internal.tasks import processor
from clownductor.internal.utils import postgres


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


@pytest.fixture
def get_current_task(get_job):
    async def _do_it(job_id):
        job = await get_job(job_id)
        job = job[0]
        return min(
            (x for x in job['tasks'] if x['status'] == 'in_progress'),
            key=lambda x: x['id'],
        )

    return _do_it


@pytest.mark.parametrize(
    'action, new_status, with_children',
    [
        ('cancel', 'canceled', False),
        ('cancel', 'canceled', True),
        ('finish', 'success', False),
        ('finish', 'success', True),
    ],
)
async def test_task_change_statuses(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        perform_action,
        action,
        new_status,
        with_children,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])
    task = jobs[0]['tasks'][0]

    response = await perform_action(task['id'], action, with_children)
    result = (await response.json())['updated_tasks']

    assert {x['job_id'] for x in result} == {task['job_id']}
    assert {x['old_status'] for x in result} == {'in_progress'}
    assert {x['new_status'] for x in result} == {new_status}

    if not with_children:
        assert len(result) == 1
    else:
        assert len(result) > 1

    jobs = await get_service_jobs(service['id'])
    task = jobs[0]['tasks'][0]
    assert task['status'] == new_status

    if not with_children:
        assert {
            x['status'] for x in jobs[0]['tasks'] if x['id'] != task['id']
        } == {'in_progress'}
    else:
        assert {
            x['status'] for x in jobs[0]['tasks'] if x['id'] >= task['id']
        } == {new_status}
        assert not [
            x['status']
            for x in jobs[0]['tasks']
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
async def test_task_change_statuses_not_from_start(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        perform_action,
        web_context,
        action,
        new_status,
        with_children,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])
    tasks = jobs[0]['tasks']
    ids_to_success = [x['id'] for x in tasks][:5]

    async with postgres.primary_connect(web_context) as conn:
        await conn.execute(
            """
            UPDATE task_manager.tasks
            SET status = 'success'
            WHERE id = ANY ($1::INTEGER[])
            """,
            ids_to_success,
        )

    await perform_action(tasks[5]['id'], action, with_children)

    jobs = await get_service_jobs(service['id'])
    tasks = jobs[0]['tasks']
    assert {x['status'] for x in tasks[:5]} == {'success'}
    if not with_children:
        assert {x['status'] for x in tasks[6:]} == {'in_progress'}
        assert tasks[5]['status'] == new_status
    else:
        assert {x['status'] for x in tasks[6:]} == {new_status}


@pytest.mark.parametrize(
    'expected_status, terminate_target, terminate_all_job',
    [(409, False, False), (200, True, False), (200, False, True)],
)
async def test_tasks_retry(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        perform_action,
        web_context,
        expected_status,
        terminate_target,
        terminate_all_job,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])
    task_id = jobs[0]['tasks'][5]['id']

    if terminate_target:
        async with postgres.primary_connect(web_context) as conn:
            await conn.execute(
                """
                UPDATE task_manager.tasks
                SET status = 'success'::JOB_STATUS
                WHERE id = $1::INTEGER;
                """,
                task_id,
            )
    if terminate_all_job:
        await perform_action(jobs[0]['tasks'][0]['id'], 'finish', True)
        async with postgres.primary_connect(web_context) as conn:
            await conn.execute(
                """
                UPDATE task_manager.jobs
                SET status = 'success'::JOB_STATUS
                WHERE id = $1::INTEGER;
                """,
                jobs[0]['job']['id'],
            )
        jobs = await get_service_jobs(service['id'])
        assert jobs[0]['job']['status'] == 'success'

    await perform_action(task_id, 'retry', expected_status=expected_status)
    jobs = await get_service_jobs(service['id'])
    assert jobs[0]['job']['status'] == 'in_progress'


@pytest.mark.usefixtures(
    'mocks_for_project_creation', 'mocks_for_service_creation',
)
@pytest.mark.dontfreeze
@pytest.mark.parametrize(
    'delay_for, complete_job, task_completed',
    [(5, True, True), (15, False, False)],
)
async def test_delayed_tasks(
        task_processor,
        monkeypatch,
        add_project,
        add_service,
        get_service_jobs,
        get_job,
        get_task,
        web_context,
        web_app_client,
        get_current_task,
        delay_for,
        complete_job,
        task_completed,
):
    task_processor.add_recipe(
        'AbcCreateTvmResource',
        provider=task_processor.provider('clownductor'),
        job_vars=[],
        stages=[],
    )
    await web_context.task_processor.on_shutdown()
    await add_project('taxi')
    service = await add_service('taxi', 'service-with-tvm')
    jobs = await get_service_jobs(service['id'])
    assert len(jobs) == 1
    job_id = jobs[0]['job']['id']

    processed_task_ids = []
    _origin_try_update_task = processor._try_update_task

    async def _try_update_task_mock(context, conn, task_id):
        processed_task_ids.append(task_id)
        return await _origin_try_update_task(context, conn, task_id)

    monkeypatch.setattr(
        'clownductor.internal.tasks.processor._try_update_task',
        _try_update_task_mock,
    )
    smanager = web_context.service_manager

    async def _make_iterations(num=None):
        waited = 0
        while True:
            await processor._iteration(web_context)
            waited += 1

            job_info = await get_job(job_id)
            job_info = job_info[0]
            assert _good_status(job_info['job']['status'])
            for _task in job_info['tasks']:
                if _task['name'] == 'MetaCubeAbcWaitTvmResource':
                    if _task['status'] != 'success':
                        await smanager.tasks.try_update_task_statuses(
                            _task['id'], 'success',
                        )
                        # just force cube to success and skip,
                        # cause it works only with ext TP
                        # but this test is completely based on internal TP
                        # and they are not integrated easily in each other
                        # and we need to update job vars with some states,
                        # that this cube produces for it
                        job_info['job_variables'].update(
                            {
                                'stable_tvm_id': '123456',
                                'testing_tvm_id': '123456',
                            },
                        )
                        await web_context.pg.primary.fetch(
                            web_context.postgres_queries[
                                'job_variables_update.sql'
                            ],
                            job_info['job']['id'],
                            json.dumps(job_info['job_variables']),
                        )

                        continue
                assert _good_status(_task['status']), str(_task)

            if num is not None:
                if waited >= num:
                    break

            if job_info['job']['status'] == 'success':
                break
            assert waited < 50

    await _make_iterations(5)

    task = await get_current_task(job_id)
    continue_at = int(
        (
            datetime.datetime.now() + datetime.timedelta(seconds=delay_for)
        ).timestamp(),
    )
    response = await web_app_client.post(
        '/v1/jobs/tasks/delay/',
        json={'task_id': task['id'], 'skip_for': delay_for},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    updated_task = await get_task(job_id, task['id'])
    assert updated_task['created_at'] < updated_task['continue_at']
    assert updated_task['updated_at'] < updated_task['continue_at']

    assert continue_at <= updated_task['continue_at'] <= continue_at + 1

    if complete_job:
        await _make_iterations()  # until job completes
    else:
        await _make_iterations(2)

    updated_task = await get_task(job_id, task['id'])
    if task_completed:
        assert updated_task['status'] == 'success'
    else:
        assert updated_task['status'] == 'in_progress'

    if task_completed:
        job_info = await get_job(job_id)
        assert job_info[0]['job']['status'] == 'success'
        for _task in job_info[0]['tasks']:
            assert _task['status'] == 'success', _task


def _good_status(x):
    return x in ['success', 'in_progress']
