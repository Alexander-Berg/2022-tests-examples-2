import pytest


async def _add_nanny_service(name, add_service, add_nanny_branch):
    nanny_service = await add_service(
        'taxi',
        name,
        type_='nanny',
        direct_link=name,
        artifact_name=f'taxi/{name}/$',
    )
    await add_nanny_branch(
        nanny_service['id'],
        'unstable',
        env='unstable',
        direct_link=f'{name}_unstable',
    )
    await add_nanny_branch(
        nanny_service['id'],
        'stable',
        env='stable',
        direct_link=f'{name}_stable',
    )
    return nanny_service


async def _setup_service(
        add_service, add_nanny_branch, web_app_client, add_related_service,
):
    await _add_nanny_service(
        'test_alias_service', add_service, add_nanny_branch,
    )
    nanny_service = await _add_nanny_service(
        'test_main_service', add_service, add_nanny_branch,
    )

    deploy_vars = {
        'service_name': 'test_main_service',
        'env': 'production',
        'conductor_ticket': 456,
        'docker_image': 'taxi/existing-service/production:0.0.1',
        'release_ticket': 'TAXIREL-2',
        'aliases': ['test_alias_service'],
    }
    await add_related_service(
        [('test_main_service', 'taxi'), ('test_alias_service', 'taxi')],
    )
    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json=deploy_vars,
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert response.status == 200, await response.text()

    return nanny_service['id']


async def _get_deployments(web_app_client, service_id):
    result = await web_app_client.get(
        f'/v1/service/deployments/?service_id={service_id}',
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    result_json = await result.json()
    deployments = result_json['deployments']
    return deployments


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.usefixtures('cube_job_get_information_update')
async def test_recipe_emergency_deploy_nanny_service(
        load_yaml,
        task_processor,
        run_job_common,
        mockserver,
        load_json,
        nanny_mockserver,
):
    one_recipe = load_json('info_one_recipe.json')
    two_recipes = load_json('info_two_recipes.json')

    recipes = [one_recipe, two_recipes, two_recipes, two_recipes, one_recipe]

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service/info_attrs/',
    )
    async def info_attrs_handler(request):
        if request.method == 'GET':
            return recipes.pop(0)
        data = request.json
        expected_recipe = recipes.pop(0)
        assert expected_recipe['content'] == data['content']

    @mockserver.json_handler('/client-nanny/v2/services/test_service/events/')
    async def events_handler(request):
        assert request.json

    recipe = task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployOneNannyService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_service',
            'image': 'image_name',
            'comment': 'SOS',
            'link_to_changelog': 'link_to_changelog',
            'sandbox_resources': None,
            'emergency_deploy': True,
            'lock_names': ['Deploy.taxi_test_service_stable'],
        },
        initiator='clownductor',
        idempotency_token='clowny_token1',
    )
    await run_job_common(job)
    assert info_attrs_handler.times_called == 5
    assert events_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_deployments, expected_tp_deployment',
    [
        (
            [
                {'deployment_id': 5, 'status': 'inited'},
                {'deployment_id': 3, 'status': 'canceled'},
            ],
            {'tp_job_id': 1, 'status': 'in_progress'},
        ),
    ],
)
@pytest.mark.features_on('locks_for_deploy')
async def test_emergency_deployment(
        task_processor,
        web_context,
        login_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
        web_app_client,
        check_many_locks,
        expected_deployments,
        expected_tp_deployment,
        mock_task_processor,
        run_job_common,
        load_yaml,
):
    login_mockserver()
    staff_mockserver()

    task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployService.yaml')['data'],
    )

    task_processor.load_recipe(
        load_yaml('recipes/EmergencyDeployOneNannyService.yaml')['data'],
    )

    service_id = await _setup_service(
        add_service, add_nanny_branch, web_app_client, add_related_service,
    )
    _deployments = await _get_deployments(web_app_client, service_id)
    assert len(_deployments) == 1
    _deploy_id = _deployments[0]['deployment_id']
    await check_many_locks(_deploy_id, 2)

    response = await web_app_client.post(
        f'/v1/service/deployment/emergency/',
        json={'deployment_id': _deploy_id},
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert response.status == 200, await response.text()

    job = task_processor.job(id_=expected_tp_deployment['tp_job_id'])
    assert job.status.value == expected_tp_deployment['status']
    await check_many_locks(expected_tp_deployment['tp_job_id'], 2)

    deployments = await _get_deployments(web_app_client, service_id)
    assert len(deployments) == 2
    for (exp_deployment, actual) in zip(expected_deployments, deployments):
        for key in exp_deployment:
            assert actual[key] == exp_deployment[key]
