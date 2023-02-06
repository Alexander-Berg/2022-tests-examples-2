# pylint: disable=redefined-outer-name
import asyncio

import pytest

from clownductor.internal.utils import postgres


@pytest.fixture
def wait_job(get_job, get_job_variables, check_lock):
    async def do_it(job_id, job_id_must_not_continues=None):
        iterations = 0
        while True:
            iterations += 1
            job = (await get_job(job_id))[0]
            job_vars = await get_job_variables(job_id)
            if job['job']['status'] != 'in_progress':
                await check_lock(job_id, exists=False)
                return job

            if job_id_must_not_continues:
                job = (await get_job(job_id_must_not_continues))[0]
                assert (
                    job['job']['status'] == 'in_progress'
                ), 'second job finished'
                assert (
                    job['tasks'][0]['status'] == 'in_progress'
                ), f'lock acquired for job {job["job"]["id"]}'

            await asyncio.sleep(2)
            assert iterations < 10, job_vars['variables']

    return do_it


@pytest.fixture
def check_lock(web_context):
    async def do_it(job_id, exists=True):
        job_ids = await web_context.service_manager.jobs.get_remote_ids_or_own(
            [job_id],
        )
        assert len(job_ids) == 1
        job_id = job_ids[0]['job_id']
        locks = await web_context.locks.find(job_id=job_id)
        if exists:
            assert locks, f'lock did not created for job {job_id}'
        else:
            assert (
                not locks
            ), f'lock exists but not expected for job {job_id}: {locks}'

    return do_it


@pytest.fixture
def check_many_locks(web_context):
    async def do_it(job_id, expected_count):
        async with postgres.get_connection(web_context) as conn:
            rows = await conn.fetch(
                'SELECT * FROM task_manager.locks WHERE job_id = $1', job_id,
            )
        assert (
            len(rows) == expected_count
        ), f'job {job_id}, locks {[x["name"] for x in rows]}'

    return do_it


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist.update(
        {
            'deploy_tokens': {
                'TEAMCITY_TAXI_TOKEN': 'teamcity_taxi_token',
                'TEAMCITY_EXISTING_SERVICE_TOKEN': (
                    'teamcity_existing_service_token'
                ),
            },
        },
    )
    return simple_secdist


@pytest.mark.dontfreeze
@pytest.mark.pgsql('clownductor', files=['test_deploy_job_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'locks_for_deploy': True,
        'cancel_old_deploys': True,
        'task_processor_enabled': True,
    },
)
async def test_deploy_twice(
        monkeypatch,
        nanny_mockserver,
        web_app_client,
        check_many_locks,
        wait_job,
):
    def _wait_for(*args, **kwargs):
        return 1

    monkeypatch.setattr(
        'clownductor.internal.tasks.cubes.cubes_meta.'
        'MetaCubeWaitForJobsCommon._wait_for',
        _wait_for,
    )
    monkeypatch.setattr(
        'clownductor.internal.tasks.cubes.cubes_internal_locks.'
        'InternalGetLock._wait_for',
        _wait_for,
    )

    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json={
            'changelog': 'test deploy',
            'docker_image': 'taxi/test_service/unstable:0.0.1unstable01',
            'env': 'unstable',
            'service_name': 'test_service',
            'aliases': ['test_service_2'],
        },
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '1',
        },
    )
    assert response.status == 200, await response.text()
    first_job_id = (await response.json())['job_id']
    await check_many_locks(first_job_id, 2)

    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json={
            'changelog': 'test deploy',
            'docker_image': 'taxi/test_service/unstable:0.0.1unstable02',
            'env': 'unstable',
            'service_name': 'test_service',
            'aliases': ['test_service_2'],
        },
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '2',
        },
    )
    assert response.status == 200, await response.text()
    second_job_id = (await response.json())['job_id']
    await check_many_locks(first_job_id, 0)
    await check_many_locks(second_job_id, 2)

    first_job = await wait_job(first_job_id)
    second_job = await wait_job(second_job_id)

    assert first_job['job']['status'] == 'canceled'
    assert second_job['job']['status'] == 'success'


@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
@pytest.mark.config(
    EXTERNAL_STARTRACK_DISABLE={'robot-taxi-clown': True},
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'abc', 'parameters': ['maintainers']},
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
)
@pytest.mark.features_on(
    'startrek_close_approval',
    'allow_auto_unstable_creation',
    'new_get_approvers',
    'cancel_old_deploys',
    'named_target_deploy',
    'diff_validation',
)
async def test_teamcity_deploy_on_uncreated_branch(
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        add_conductor_branch,
        simple_secdist,
):
    login_mockserver()
    conductor_mockserver()
    staff_mockserver()
    artifact_name = 'taxi/existing-service/$'
    services = []
    branch_ids = {'stable': {}, 'unstable': {}}
    for name, project in [
            ('existing-service', 'taxi'),
            ('e-service-1', 'taxi'),
            ('e-service-1', 'faketaxi'),
            ('e-service-2', 'taxi'),
    ]:
        nanny_service = await add_service(
            project,
            name,
            type_='nanny',
            direct_link=name,
            artifact_name=artifact_name,
        )
        branch_id = await add_nanny_branch(
            nanny_service['id'],
            'unstable',
            env='unstable',
            direct_link='unstable',
        )
        stable_branch_id = await add_nanny_branch(
            nanny_service['id'], 'stable', env='stable', direct_link='stable',
        )
        services.append(nanny_service)
        branch_ids['stable'][name] = stable_branch_id
        branch_ids['unstable'][name] = branch_id

    conductor_service = await add_service(
        'taxi',
        'existing-conductor-service',
        type_='conductor',
        direct_link='existing-conductor-service',
    )
    await add_conductor_branch(
        conductor_service['id'], 'unstable', direct_link='unstable',
    )
    await add_conductor_branch(
        conductor_service['id'], 'stable', direct_link='stable',
    )

    params = {'service_id': services[0]['id']}
    request_body = {
        'name': 'new-unstable-branch',
        'allocate_request': {
            'branch_name': 'unstable',
            'regions': ['man', 'vla'],
            'work_dir': 10000,
            'volumes': [{'path': '/asd/', 'size': 10000, 'type': 'ssd'}],
            'cpu': 1000,
            'ram': 10000,
            'root_size': 10000,
        },
        'env': 'unstable',
    }
    headers = {
        'X-Yandex-Login': 'vstimchenko',
        'X-YaTaxi-Api-Key': 'valid_teamcity_token',
    }
    response = await web_app_client.post(
        '/v1/create_dev_branch/',
        json=request_body,
        params=params,
        headers=headers,
    )
    assert response.status == 200
    response = await response.json()
    assert response['branch']['job_id']

    auth_token = 'valid_teamcity_token'
    data = {
        'service_name': 'existing-service',
        'env': 'unstable',
        'branch_name': 'dev-new-unstable-branch',
        'conductor_ticket': 123,
        'docker_image': 'taxi/existing-service/unstable:0.0.1',
    }
    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=data,
        headers={'X-YaTaxi-Api-Key': auth_token},
    )
    assert result.status == 400, await result.text()
    resp = await result.json()
    assert resp['code'] == 'BRANCH_NOT_CREATED_YET'
    assert (
        resp['message'] == 'The branch creation must be '
        'finished before it can be deployed to'
    )
