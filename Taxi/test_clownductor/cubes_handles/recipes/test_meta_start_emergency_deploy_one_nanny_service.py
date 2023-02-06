import pytest


async def _add_nanny_service(name, add_service, add_nanny_branch):
    nanny_service = await add_service(
        'taxi',
        name,
        type_='nanny',
        direct_link=name,
        artifact_name=f'taxi/{name}/$',
    )
    unstable_branch = await add_nanny_branch(
        nanny_service['id'],
        'unstable',
        env='unstable',
        direct_link=f'{name}_unstable',
    )
    stable_branch = await add_nanny_branch(
        nanny_service['id'],
        'stable',
        env='stable',
        direct_link=f'{name}_stable',
    )
    return nanny_service, stable_branch, unstable_branch


async def _setup_service(add_service, add_nanny_branch, add_related_service):
    await _add_nanny_service(
        'test_alias_service', add_service, add_nanny_branch,
    )

    nanny_service, _, _ = await _add_nanny_service(
        'test_main_service', add_service, add_nanny_branch,
    )

    await add_related_service(
        [('test_main_service', 'taxi'), ('test_alias_service', 'taxi')],
    )

    return nanny_service['id']


@pytest.mark.parametrize(
    'expected_tp_deployments, skip, nanny_name, content_expected',
    [
        (
            [
                {'tp_job_id': 1, 'status': 'in_progress'},
                {'tp_job_id': 2, 'status': 'in_progress'},
            ],
            False,
            'test_main_service',
            {'payload': {'job_ids': [3, 4]}, 'status': 'success'},
        ),
        (
            [],
            True,
            'test_main_service',
            {'payload': {'job_ids': []}, 'status': 'success'},
        ),
        ([], False, None, {'payload': {'job_ids': []}, 'status': 'success'}),
    ],
)
async def test_start_emergency_deployment(
        task_processor,
        login_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
        expected_tp_deployments,
        skip,
        nanny_name,
        content_expected,
        load_yaml,
        call_cube_handle,
):
    login_mockserver()
    staff_mockserver()
    task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployOneNannyService.yaml')['data'],
    )

    await _setup_service(add_service, add_nanny_branch, add_related_service)

    response = await call_cube_handle(
        'MetaStartEmergencyDeployOneNannyService',
        {
            'content_expected': content_expected,
            'data_request': {
                'input_data': {
                    'service_id': 2,
                    'branch_id': 5,
                    'nanny_name': nanny_name,
                    'aliases': [
                        {
                            'service_id': 1,
                            'branch_id': 3,
                            'nanny_name': 'test_alias_service',
                            'image': 'alias_image',
                        },
                    ],
                    'comment': 'SOS',
                    'image': 'main_service_image',
                    'changelog': 'changelog',
                    'skip': skip,
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert response.status == 200, await response.text()

    for deployment in expected_tp_deployments:
        job = task_processor.job(deployment['tp_job_id'])
        assert job.status.value == deployment['status']
