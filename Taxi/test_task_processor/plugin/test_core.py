# pylint: disable=import-only-modules, protected-access
import json

import pytest

from task_processor.generated.web.task_processor.plugin import InvalidStage
from task_processor.generated.web.task_processor.plugin import UnknownProvider
from task_processor.internal import core
from task_processor.internal.task_cube import TaskCube


@pytest.mark.parametrize(
    'job_name, initiator, exp_recipe_id, exp_jobs, exp_task_deps,'
    'exp_task_status, exp_job_status',
    [
        (
            'test_create_job',
            'deoevgen',
            1,
            [
                'CubeDeploy4',
                'CubeDeploy3',
                'CubeDeploy5',
                'CubeDeploy2',
                'CubeDeploy1',
            ],
            [(1, 2), (2, 3), (3, 4), (4, 5)],
            'success',
            'success',
        ),
        (
            'test_failed_job',
            'deoevgen',
            2,
            ['CubeDeployFailed'],
            [],
            'failed',
            'failed',
        ),
        (
            'test_failed_job',
            'initiator',
            2,
            ['CubeDeployFailed'],
            [],
            'failed',
            'failed',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_create_job.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=True)
async def test_create_job(
        web_context,
        pgsql,
        patch,
        make_iterations,
        job_name,
        initiator,
        exp_recipe_id,
        exp_jobs,
        exp_task_deps,
        exp_task_status,
        exp_job_status,
):
    try:
        job_id = await web_context.task_processor.create_job(
            provider_name=initiator,
            recipe_name=job_name,
            variables={
                'service_id': 1,
                'test': 'test321',
                'env': 'unstable',
                'new_service_ticket': 'test-1',
            },
            change_doc_id='test_change_doc_id',
            token=None,
        )
    except UnknownProvider as exp:
        assert exp.msg == f'Not found provider name: {initiator}'
        return

    assert job_id == 1
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        'SELECT id,recipe_id, name, initiator, status'
        '  from task_processor.jobs;',
    )
    rows = cursor.fetchall()

    assert rows == [(1, exp_recipe_id, job_name, initiator, 'in_progress')]

    # check tasks
    cursor.execute(
        'select name, status, input_mapping, output_mapping '
        'from task_processor.tasks where job_id = 1 order by id;',
    )
    tasks_rows = cursor.fetchall()
    exp_rows = []
    for exp_job in exp_jobs:
        if exp_job == 'CubeDeploy1':
            exp_rows.append(
                (
                    exp_job,
                    'in_progress',
                    '{"test_input_data": "service_id"}',
                    '{"ticket": "test_output"}',
                ),
            )
        else:
            exp_rows.append((exp_job, 'in_progress', '{}', '{}'))
    assert tasks_rows == exp_rows

    cursor.execute(
        'select prev_task_id, next_task_id from task_processor.task_deps;',
    )
    task_deps = cursor.fetchall()
    assert task_deps == exp_task_deps

    # pylint: disable=unused-variable
    @patch('task_processor.internal.task_cube.TaskCube')
    def need_to_test(context, data, variables, parents, provider, conn):
        # pylint: disable=abstract-method
        class MockTaskCube(TaskCube):
            async def _update(self, input_data):
                name = self.data['name']
                if self._data['retries'] > 3:
                    self.fail('test failed')
                if name == 'CubeDeployFailed':
                    raise Exception('test failed cube')
                payload = {'test_output': 'TESTTICKET-1'}
                self._data['payload'] = payload
                self.succeed()

            @classmethod
            def needed_parameters(cls):
                return []

            def sleep(self, duration, add_retry=False):
                if add_retry:
                    self._data['retries'] += 1

        return MockTaskCube(context, data, variables, parents, provider, conn)

    await make_iterations(job_id)

    cursor.execute(
        'select name, status from task_processor.tasks'
        ' where job_id = 1 order by id;',
    )
    rows = cursor.fetchall()
    exp_rows = []
    for exp_job in exp_jobs:
        exp_rows.append((exp_job, exp_task_status))
    assert rows == exp_rows

    cursor.execute('select status from task_processor.jobs where id=1;')
    rows = cursor.fetchall()
    assert rows[0][0] == exp_job_status


@pytest.mark.pgsql('task_processor', files=['test_invalid_status.sql'])
@pytest.mark.xfail(reason='Flaps')
async def test_invalid_job(web_context, get_job, get_tasks_by_job_id):
    job_id = 1
    job = await get_job(job_id)
    tasks = await get_tasks_by_job_id(job_id)
    assert job['status'] == 'in_progress'
    for task in tasks:
        assert task['status'] == 'in_progress'

    try:
        await web_context.task_processor.create_job(
            provider_name='deoevgen',
            recipe_name='test_invalid_job',
            variables={
                'service_id': 1,
                'test': 'test321',
                'env': 'unstable',
                'new_service_ticket': 'test-1',
            },
            change_doc_id='test_change_doc_id',
            token=None,
        )
    except InvalidStage as exp:
        msg = 'invalid cube InvalidCube, provider_id: 1, recipe_id 3'
        assert exp.msg == msg
        return

    job = await get_job(job_id)
    tasks = await get_tasks_by_job_id(job_id)
    assert job['status'] == 'failed'
    for task in tasks:
        assert task['status'] == 'failed'


@pytest.mark.parametrize(
    [
        'status',
        'payload',
        'sleep_duration',
        'error_message',
        'expected_job_status',
    ],
    [
        ('success', {'slug': 'slug', 'name': 'name'}, None, None, 'success'),
        (
            'failed',
            {},
            None,
            'Missing output parameter slug in payload {}',
            'failed',
        ),
        (
            'canceled',
            {'slug': 'slug', 'name': 'name'},
            None,
            'Cube is canceled',
            'failed',
        ),
        ('in_progress', {}, 3, None, 'in_progress'),
        ('in_progress', {}, None, None, 'in_progress'),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_task_cube_update.sql'])
@pytest.mark.xfail(reason='Flaps')
@pytest.mark.config(TASK_PROCESSOR_ENABLED=True)
async def test_task_cube_update(
        mock_provider_client,
        web_context,
        make_iterations,
        get_job,
        get_tasks_by_job_id,
        expected_job_status,
        status,
        payload,
        sleep_duration,
        error_message,
):
    @mock_provider_client(
        '/task-processor/v1/cubes/AbcCubeGenerateServiceName/',
    )
    # pylint: disable=unused-variable
    def handler(request):
        response = {'status': status}
        if payload:
            response['payload'] = payload
        if sleep_duration:
            response['sleep_duration'] = sleep_duration
        if error_message:
            response['error_message'] = error_message
        return response

    job_id = await web_context.task_processor.create_job(
        provider_name='clownductor',
        recipe_name='test_abc_cube',
        variables={
            'project': 'project_name',
            'service': 'test_service',
            'st_task': 'TAXIPLATFORM-1',
        },
        change_doc_id='test_change_doc_id',
        token=None,
    )
    assert job_id == 1

    await make_iterations(job_id)

    job = await get_job(job_id)
    tasks = await get_tasks_by_job_id(job_id)
    task = tasks[0]
    job = dict(job)
    assert job['status'] == expected_job_status
    assert task['status'] == status
    if task.get('payload'):
        assert json.loads(task['payload']) == payload
    if task.get('sleep_duration'):
        assert task['sleep_duration'] == sleep_duration
    if task.get('error_message'):
        assert task['error_message'] == error_message


@pytest.mark.parametrize(
    'result',
    [
        pytest.param([]),
        pytest.param(
            [1],
            marks=pytest.mark.pgsql(
                'task_processor', files=['base.sql', 'non_started_job.sql'],
            ),
        ),
        pytest.param(
            [2],
            marks=pytest.mark.pgsql(
                'task_processor', files=['base.sql', 'started_job.sql'],
            ),
        ),
        pytest.param(
            [1],
            marks=pytest.mark.pgsql(
                'task_processor', files=['base.sql', 'task_succeeded.sql'],
            ),
        ),
    ],
)
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_get_next_task_to_process(patch, web_context, result):
    tasks = []

    @patch('task_processor.internal.core._try_update_task')
    async def _try_update_task(context, conn, task_id):
        tasks.append(task_id)

    await core._update_tasks(web_context)

    assert tasks == result
