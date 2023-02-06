import pytest

from clownductor.internal.utils import postgres


@pytest.mark.pgsql('clownductor', ['add_test_data.sql'])
@pytest.mark.parametrize(
    'params, job_ids',
    [
        ({'service_id': 1}, [2, 1]),
        ({'service_id': 1, 'limit': 1}, [2]),
        ({'service_id': 1, 'limit': 1, 'offset': 1}, [1]),
        ({'service_id': 1, 'limit': 1, 'offset': 2}, []),
        ({'service_id': 2}, [3]),
        ({'service_id': 3}, []),
        ({'branch_id': 1}, [1]),
        ({'branch_id': 1, 'limit': 1, 'offset': 1}, []),
        ({'job_id': 3}, [3]),
        ({'job_id': 4}, []),
    ],
)
async def test_get_jobs(web_app_client, params, job_ids):
    response = await web_app_client.get(
        f'/v1/jobs/', params=params, headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    result = await response.json()
    assert [job['job']['id'] for job in result] == job_ids


@pytest.mark.parametrize(
    'action, new_status',
    [
        ('cancel', 'canceled'),
        ('cancel', 'canceled'),
        ('finish', 'success'),
        ('finish', 'success'),
    ],
)
async def test_job_terminate(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        web_context,
        web_app_client,
        get_job,
        action,
        new_status,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])
    ids_to_success = [x['id'] for x in jobs[0]['tasks']][:2]
    await _update_tasks_status('success', ids_to_success, web_context)

    jobs = await get_service_jobs(service['id'])
    job = jobs[0]
    job_id = job['job']['id']

    response = await web_app_client.post(
        f'/v1/jobs/{action}/',
        json={'job_id': job_id},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    result = (await response.json())['updated_tasks']

    assert {x['job_id'] for x in result} == {job_id}
    assert {x['old_status'] for x in result} == {'in_progress'}
    assert {x['new_status'] for x in result} == {new_status}
    assert len(result) == len(job['tasks']) - len(ids_to_success)

    job_info = await get_job(job_id)
    job_info = job_info[0]
    assert job_info['job']['status'] == new_status


@pytest.mark.parametrize(
    'action, expected_code, expected_status',
    [
        ('cancel', 'INCORRECT_JOB', 400),
        ('cancel', 'JOB_NOT_FOUND', 404),
        ('cancel', 'WRONG_STATUS', 409),
        ('finish', 'JOB_NOT_FOUND', 404),
        ('finish', 'WRONG_STATUS', 409),
    ],
)
async def test_job_terminate_errors(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        add_nanny_branch,
        get_service_jobs,
        web_app_client,
        web_context,
        action,
        expected_code,
        expected_status,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service(
        'project-1', 'service-1', artifact_name='taxi/existing-service/$',
    )
    jobs = await get_service_jobs(service['id'])

    job_id = jobs[0]['job']['id']
    if expected_status == 400:
        await add_nanny_branch(
            service['id'],
            'testing',
            env='testing',
            direct_link=f'testing_name',
        )
        result = await web_app_client.post(
            '/api/teamcity_deploy',
            json={
                'service_name': 'service-1',
                'env': 'testing',
                'conductor_ticket': 456,
                'docker_image': 'taxi/existing-service/testing:0.0.1',
            },
            headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
        )
        assert result.status == 200
        row = await result.json()
        job_id = row['job_id']

    if expected_status == 404:
        job_id = -1
    if expected_status == 409:
        await _update_job_status('success', job_id, web_context)
    response = await web_app_client.post(
        f'/v1/jobs/{action}/',
        json={'job_id': job_id},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert expected_code == content['code'], f'Content: {content}'


@pytest.mark.parametrize('retry_from', [1, 2])
async def test_tasks_retry(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        web_app_client,
        web_context,
        retry_from,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])
    job_id = jobs[0]['job']['id']
    ids_to_success = [x['id'] for x in jobs[0]['tasks']][:2]
    await _update_tasks_status('success', ids_to_success, web_context)
    await _update_job_status('success', job_id, web_context)

    response = await web_app_client.post(
        f'/v1/jobs/retry/',
        json={'job_id': job_id, 'retry_from': retry_from},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    jobs = await get_service_jobs(service['id'])
    assert jobs[0]['job']['status'] == 'in_progress'

    result = (await response.json())['updated_tasks']

    assert {x['job_id'] for x in result} == {job_id}
    assert {x['old_status'] for x in result} == {'success'}
    assert {x['new_status'] for x in result} == {'in_progress'}
    assert len(result) == len([x for x in ids_to_success if x >= retry_from])

    jobs = await get_service_jobs(service['id'])
    for task in jobs[0]['tasks']:
        if task['id'] >= retry_from:
            assert task['status'] == 'in_progress'
        else:
            assert task['status'] == 'success'


@pytest.mark.parametrize(
    'expected_code, expected_status, error',
    [
        ('JOB_NOT_FOUND', 404, 'job_not_found'),
        ('WRONG_STATUS', 409, 'job_wrong_status'),
        ('TASK_NOT_FOUND', 404, 'task_not_found'),
        ('WRONG_STATUS', 409, 'task_wrong_status'),
        ('WRONG_TASK', 422, 'task_wrong_job'),
    ],
)
async def test_tasks_retry_errors(
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        web_app_client,
        web_context,
        expected_code,
        expected_status,
        error,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    jobs = await get_service_jobs(service['id'])

    job_id = jobs[0]['job']['id']
    if error == 'job_not_found':
        job_id = -1

    retry_from = jobs[0]['tasks'][1]['id']
    if error == 'task_not_found':
        retry_from = -1

    if error != 'task_wrong_status':
        ids_to_success = [x['id'] for x in jobs[0]['tasks']][:2]
        await _update_tasks_status('success', ids_to_success, web_context)

    if error != 'job_wrong_status':
        await _update_job_status('success', job_id, web_context)

    if error == 'task_wrong_job':
        row = await _insert_job(web_context)
        job_id = row['id']

    response = await web_app_client.post(
        f'/v1/jobs/retry/',
        json={'job_id': job_id, 'retry_from': retry_from},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert expected_code == content['code'], f'Content: {content}'


@pytest.mark.parametrize(
    'recipe_name,expected_status,expected_code',
    [
        ('WaitMainDeployNannyServiceNoApprove', 200, None),
        ('Not exist', 404, 'RECIPE_NOT_FOUND'),
    ],
)
@pytest.mark.pgsql('clownductor')
async def test_job_start(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_service_jobs,
        recipe_name,
        expected_status,
        expected_code,
):
    login_mockserver()
    staff_mockserver()

    await add_service('taxi', 'service_1')

    response = await web_app_client.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': recipe_name,
            'job_vars': {'job_id': 2},
            'service_id': 1,
        },
    )

    assert response.status == expected_status
    content = await response.json()

    if expected_status == 200:
        job = await get_service_jobs(1)
        assert job[0]['job']['id'] == content['job_id']
    else:
        assert content['code'] == expected_code


@pytest.mark.pgsql('clownductor')
async def test_job_start_custom_recipe(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_service_jobs,
):
    login_mockserver()
    staff_mockserver()

    await add_service('taxi', 'service_1')

    response = await web_app_client.post(
        f'/v1/jobs/start/custom_recipe/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': 'CreateBalancerAlias',
            'recipe': {
                'CreateBalancerAlias': {
                    'job_vars': [
                        'service_id',
                        'fqdn',
                        'env',
                        'new_service_ticket',
                    ],
                    'stages': [
                        {
                            'task': 'InternalCubeInitBalancerAlias',
                            'input': {
                                'service_id': 'service_id',
                                'env': 'env',
                            },
                            'output': {'host': 'host'},
                        },
                        {
                            'task': 'DNSCreateAlias',
                            'input': {
                                'alias': 'fqdn',
                                'canonical_name': 'host',
                            },
                            'output': {'job_id': 'job_id'},
                        },
                        {
                            'task': 'DNSWaitForJob',
                            'input': {'job_id': 'job_id'},
                        },
                    ],
                },
            },
            'job_vars': {
                'fqdn': 'foo.bar.blah.yandex.net',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'service_id': 1,
        },
    )

    job_id = await response.json()
    job = await get_service_jobs(1)

    assert job[0]['job']['id'] == job_id['job_id']


async def _update_tasks_status(status, ids, web_context):
    async with postgres.primary_connect(web_context) as conn:
        await conn.execute(
            """
            update task_manager.tasks
            set status = $2::JOB_STATUS
            where id = any($1::integer[]);
            """,
            ids,
            status,
        )


async def _update_job_status(status, job_id, web_context):
    async with postgres.primary_connect(web_context) as conn:
        await conn.execute(
            """
            update task_manager.jobs
            set status = $2::JOB_STATUS
            where id = $1::integer;
            """,
            job_id,
            status,
        )


async def _insert_job(web_context):
    async with postgres.primary_connect(web_context) as conn:
        return await conn.fetchrow(
            """
            insert into task_manager.jobs
            (service_id, branch_id, name, initiator, status)
            select service_id, branch_id, name, initiator, status
            from task_manager.jobs
            returning id;
            """,
        )


@pytest.mark.parametrize(
    'service_id, service_yaml_in_arcadia',
    [
        pytest.param(1, False, id='service_yaml_in_github'),
        pytest.param(3, True, id='service_yaml_in_arcadia'),
    ],
)
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_change_custom_parameters_job(
        task_processor,
        run_job_common,
        web_context,
        load,
        login_mockserver,
        staff_mockserver,
        patch_arc_read_file,
        patch_github_single_file,
        diff_proposal_mock,
        service_id,
        service_yaml_in_arcadia,
):
    login_mockserver()
    staff_mockserver()
    st_ticket = 'TAXIREL-123'
    reviewers = ['spolischouck']
    expected_service_yaml = load('expected_service.yaml')
    changes = [
        {
            'filepath': 'service.yaml',
            'state': 'created_or_updated',
            'data': expected_service_yaml,
        },
    ]
    if service_yaml_in_arcadia:
        df_mock, _ = diff_proposal_mock(
            user='arcadia',
            base='trunk',
            repo='taxi/backend-py3/services/clownductor',
            title='feat test_service_in_arcadia: change service.yaml',
            comment='Update service.yaml during job#1',
            changes=changes,
        )
        read_file_mock = patch_arc_read_file(
            'taxi/backend-py3/services/clownductor/service.yaml',
            'service.yaml',
        )
    else:
        df_mock, _ = diff_proposal_mock(
            user='taxi',
            base='develop',
            repo='backend-py3',
            title='feat test_service: change service.yaml',
            comment='Update service.yaml during job#1',
            changes=changes,
        )
        read_file_mock = patch_github_single_file(
            'services/clownductor/service.yaml', 'service.yaml',
        )

    expected_job_vars = {
        'service_id': service_id,
        'ticket': st_ticket,
        'responsibles': reviewers,
        'comment_props': {'summonees': reviewers},
        'content_service_yaml': expected_service_yaml,
        'diff_proposal': df_mock.serialize(),
        'merge_diff_job_id': 2,
    }

    job_id = await web_context.task_processor.create_job(
        'login',
        'ChangeCustomParameters',
        {
            'service_id': service_id,
            'ticket': st_ticket,
            'responsibles': reviewers,
            'comment_props': {'summonees': reviewers},
        },
        service_id,
    )
    job = task_processor.job(job_id)
    await run_job_common(job)

    assert job.job_vars == expected_job_vars
    assert len(read_file_mock.calls) == 1
