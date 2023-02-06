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
        'prestable',
        env='prestable',
        direct_link=f'{name}_prestable',
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


@pytest.mark.usefixtures('mock_internal_tp')
async def test_recipe_emergency_deploy_service(
        load_yaml,
        task_processor,
        run_job_with_meta,
        mockserver,
        load_json,
        login_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
):
    login_mockserver()
    staff_mockserver()

    await _setup_service(add_service, add_nanny_branch, add_related_service)

    task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployOneNannyService.yaml')['data'],
    )

    recipe = task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployService.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'service_id': 2,
            'branch_id': 3,
            'prestable_name': 'test_main_service',
            'prestable_aliases': [
                {
                    'service_id': 1,
                    'branch_id': 1,
                    'nanny_name': 'test_alias_service',
                    'image': 'alias_image',
                },
            ],
            'name': 'test_main_service',
            'aliases': [
                {
                    'service_id': 1,
                    'branch_id': 2,
                    'nanny_name': 'test_alias_service',
                    'image': 'alias_image',
                },
            ],
            'image': 'image_name',
            'sandbox_resources': None,
            'comment': 'SOS',
            'link_to_changelog': 'link_to_changelog',
            'lock_names': ['Deploy.taxi_test_service_stable'],
            'skip_pre': False,
        },
        initiator='clownductor',
        idempotency_token='clowny_token1',
    )
    await run_job_with_meta(job)
