import pytest


@pytest.fixture
def internal_mock_vars():
    return {'status': 'in_progress'}


@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.features_on('cancel_old_deploys', 'locks_for_deploy')
@pytest.mark.dontfreeze
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_deploy_diff_types_in_middle_of_deploy(
        nanny_mockserver, task_processor, web_app_client, get_job,
):
    # start deploy sandbox resources
    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json={
            'aliases': ['test_service_2', 'test_service_3'],
            'service_name': 'test_service',
            'env': 'unstable',
            'sandbox_resources': [
                {
                    'local_path': 'road-graph',
                    'resource_id': '1656867606',
                    'resource_type': 'TAXI_GRAPH_ROAD_GRAPH_RESOURSE',
                    'task_id': '745057883',
                    'task_type': 'TAXI_GRAPH_DO_UPLOAD_TASK',
                },
            ],
        },
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '1',
        },
    )
    assert response.status == 200, await response.text()
    first_job_id = (await response.json())['job_id']
    first_job = task_processor.find_job(first_job_id)

    while not first_job.status.is_terminated:
        task, _ = await first_job.step()
        if task.cube.name == 'MetaStartDeployNannyServices':
            break
    nanny_deploy_job_ids = task.payload['job_ids']
    nanny_deploy_jobs = [
        task_processor.find_job(x) for x in nanny_deploy_job_ids
    ]
    for _job in nanny_deploy_jobs:
        while not _job.status.is_terminated:
            _task, _ = await _job.step()
            if _task.cube.name == 'NannyCubeDeploySnapshot':
                break

    # start code deploy for one of the services from aliases
    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json={
            'service_name': 'test_service_2',
            'env': 'unstable',
            'docker_image': 'taxi/test_service_2/unstable:0.0.1',
        },
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '1',
        },
    )
    assert response.status == 200, await response.text()
    second_job_id = (await response.json())['job_id']
    second_job = task_processor.find_job(second_job_id)
    _task, _ = await second_job.step()
    assert _task.status.is_in_progress
    assert all(x.status.is_in_progress for x in nanny_deploy_jobs)
    clown_jobs = [(await get_job(x))[0] for x in nanny_deploy_job_ids]
    assert all(x['job']['status'] == 'in_progress' for x in clown_jobs), [
        (x['job']['name'], x['job']['status']) for x in clown_jobs
    ]
