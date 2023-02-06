# pylint: disable=unused-variable, redefined-outer-name
import pytest


FIRST_DEPLOY = {
    'service_name': 'existing-service',
    'env': 'production',
    'conductor_ticket': 456,
    'docker_image': 'taxi/existing-service/production:0.0.1',
    'release_ticket': 'TAXIREL-2',
}

SECOND_DEPLOY = {
    'service_name': 'existing-service',
    'env': 'production',
    'conductor_ticket': 456,
    'docker_image': 'taxi/existing-service/production:0.0.2',
    'release_ticket': 'TAXIREL-2',
}

IMAGE_SANDBOX_DEPLOY = {
    'service_name': 'existing-service',
    'env': 'production',
    'conductor_ticket': 456,
    'docker_image': 'taxi/existing-service/production:0.0.1',
    'sandbox_resources': [
        {
            'is_dynamic': False,
            'local_path': 'road-graph',
            'resource_id': '1656867606',
            'resource_type': 'TAXI_GRAPH_ROAD_GRAPH_RESOURSE',
            'task_id': '745057883',
            'task_type': 'TAXI_GRAPH_DO_UPLOAD_TASK',
        },
    ],
    'release_ticket': 'TAXIREL-2',
}


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
        add_service,
        add_nanny_branch,
        web_app_client,
        deploy_params,
        add_related_service=None,
        with_alias=False,
):
    nanny_service = await _add_nanny_service(
        'existing-service', add_service, add_nanny_branch,
    )

    deploy = deploy_params.copy()
    if with_alias:
        deploy['aliases'] = ['test_service']
        await add_related_service(
            [('existing-service', 'taxi'), ('test_service', 'taxi')],
        )
    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json=deploy,
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert response.status == 200, await response.text()

    return nanny_service['id']


async def _check_status(web_app_client, dep_id, status):
    result = await web_app_client.get(
        f'/v1/service/deployment/?deployment_id={dep_id}',
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    result_json = await result.json()
    assert result_json['status'] == status


async def _get_deployments(web_app_client, service_id):
    result = await web_app_client.get(
        f'/v1/service/deployments/?service_id={service_id}',
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    result_json = await result.json()
    deployments = result_json['deployments']
    return deployments


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[pytest.mark.features_on('locks_for_deploy')],
            id='locks_for_deploy_ON',
        ),
        pytest.param(
            marks=[pytest.mark.features_off('locks_for_deploy')],
            id='locks_for_deploy_OFF',
        ),
    ],
)
@pytest.mark.features_on('cancel_old_deploys')
@pytest.mark.pgsql('clownductor')
async def test_deployments(
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        patch,
):  # pylint: disable=R0913
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        if ticket == 'TAXIREL-2':
            return {'status': {'key': 'open'}}
        return {'status': {'key': 'closed'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        if ticket in ['TAXIREL-2']:
            assert 'Deployment was' in text
        else:
            assert False

    login_mockserver()
    conductor_mockserver()
    staff_mockserver()

    service_id = await _setup_service(
        add_service, add_nanny_branch, web_app_client, FIRST_DEPLOY,
    )

    # get deployments for service
    deployments = await _get_deployments(web_app_client, service_id)
    assert len(deployments) == 1
    first_deployment = deployments[0]
    first_dep_id = first_deployment['deployment_id']

    # get deployment info
    result = await web_app_client.get(
        f'/v1/service/deployment/?deployment_id={first_dep_id}',
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    result_json = await result.json()
    assert result_json == first_deployment

    # deploy second version
    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=SECOND_DEPLOY,
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert result.status == 200
    result_json = await result.json()
    second_dep_id = result_json['job_id']
    deployments = await _get_deployments(web_app_client, service_id)
    assert len(deployments) == 2
    assert any(map(lambda x: x['deployment_id'] == first_dep_id, deployments))
    assert any(map(lambda x: x['deployment_id'] == second_dep_id, deployments))
    await _check_status(web_app_client, first_dep_id, 'canceled')
    await _check_status(web_app_client, second_dep_id, 'in_progress')

    # test retry second task with invalid ticket
    result = await web_app_client.post(
        f'/v1/service/deployment/retry',
        json={'deployment_id': first_dep_id, 'taxirel_ticket': 'TAXIREL-3'},
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 400

    # test retry second task
    result = await web_app_client.post(
        f'/v1/service/deployment/retry',
        json={'deployment_id': second_dep_id, 'taxirel_ticket': 'TAXIREL-2'},
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    result_json = await result.json()
    redeploy_id = result_json['deployment_id']
    assert redeploy_id is not None

    deployments = await _get_deployments(web_app_client, service_id)
    assert len(deployments) == 3
    assert any(map(lambda x: x['deployment_id'] == first_dep_id, deployments))
    assert any(map(lambda x: x['deployment_id'] == second_dep_id, deployments))
    assert any(map(lambda x: x['deployment_id'] == redeploy_id, deployments))
    await _check_status(web_app_client, first_dep_id, 'canceled')
    await _check_status(web_app_client, second_dep_id, 'canceled')
    await _check_status(web_app_client, redeploy_id, 'in_progress')

    # cancel re-deployment
    result = await web_app_client.post(
        f'/v1/service/deployment/cancel/?deployment_id={redeploy_id}',
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    await _check_status(web_app_client, redeploy_id, 'canceled')

    # check comments
    assert len(create_comment.calls) == 3


@pytest.mark.config(
    CLOWNDUCTOR_RELEASE_TICKET_PROPERTIES={'TAXIREL': 'deployed'},
)
@pytest.mark.features_on('use_startrack_queue_check')
@pytest.mark.parametrize(
    'job_id, ticket, exp_status, code',
    [
        (1, 'TAXIREL-2', 200, ''),
        (1, 'TAXIREL-3', 200, ''),
        (2, 'TAXIREL-2', 200, ''),
        (2, 'TAXIREL-3', 200, ''),
        (3, 'TAXIREL-2', 200, ''),
        (3, 'TAXIREL-3', 400, 'INVALID_TICKET_STATUS'),
        (3, 'INVALIDREL-1', 400, 'INVALID_TICKET_QUEUE'),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'locks_for_deploy': True},
            ),
            id='locks_for_deploy_ON',
        ),
        pytest.param(
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'locks_for_deploy': False},
            ),
            id='locks_for_deploy_OFF',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
async def test_retry_deployment(
        web_app_client, patch, job_id, ticket, exp_status, code,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        if ticket in ['TAXIREL-2', 'INVALIDREL-1']:
            return {'status': {'key': 'open'}}
        return {'status': {'key': 'closed'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        if ticket == 'TAXIREL-2':
            assert 'Deployment was' in text
        else:
            assert False

    result = await web_app_client.post(
        f'/v1/service/deployment/retry',
        json={'deployment_id': job_id, 'taxirel_ticket': ticket},
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    assert result.status == exp_status
    if result.status == 400:
        content = await result.json()
        assert content['code'] == code


@pytest.mark.parametrize(
    ['deploy_params'],
    [
        pytest.param(
            FIRST_DEPLOY,
            id='code deploy',
            marks=[pytest.mark.features_on('locks_for_deploy')],
        ),
        pytest.param(
            IMAGE_SANDBOX_DEPLOY,
            id='code and sandbox deploy',
            marks=[
                pytest.mark.features_on(
                    'locks_for_deploy',
                    'enable_simultaneous_sandbox_docker_deploy',
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clownductor')
async def test_canceling_and_retrying(
        patch,
        login_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
        web_app_client,
        check_many_locks,
        deploy_params,
):
    login_mockserver()
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        if ticket == 'TAXIREL-2':
            return {'status': {'key': 'open'}}
        return {'status': {'key': 'closed'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        if ticket == 'TAXIREL-2':
            assert 'Deployment was' in text
        else:
            assert False

    await _add_nanny_service('test_service', add_service, add_nanny_branch)
    service_id = await _setup_service(
        add_service,
        add_nanny_branch,
        web_app_client,
        deploy_params,
        add_related_service,
        with_alias=True,
    )
    _deployments = await _get_deployments(web_app_client, service_id)
    _deploy_id = _deployments[0]['deployment_id']
    await check_many_locks(_deploy_id, 2)

    response = await web_app_client.post(
        f'/v1/service/deployment/cancel/',
        headers={'X-Yandex-Login': 'ilyasov'},
        params={'deployment_id': _deploy_id},
    )
    assert response.status == 200, await response.text()
    await check_many_locks(_deploy_id, 0)

    response = await web_app_client.post(
        f'/v1/service/deployment/retry/',
        json={'deployment_id': _deploy_id, 'taxirel_ticket': 'TAXIREL-2'},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200, await response.text()

    await check_many_locks((await response.json())['deployment_id'], 2)


@pytest.mark.parametrize(
    ['deploy_params'],
    [
        pytest.param(
            FIRST_DEPLOY,
            id='code deploy',
            marks=[pytest.mark.features_on('locks_for_deploy')],
        ),
        pytest.param(
            IMAGE_SANDBOX_DEPLOY,
            id='code and sandbox deploy',
            marks=[
                pytest.mark.features_on(
                    'locks_for_deploy',
                    'enable_simultaneous_sandbox_docker_deploy',
                ),
            ],
        ),
    ],
)
async def test_revert(
        patch,
        login_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
        web_app_client,
        check_many_locks,
        deploy_params,
):
    login_mockserver()
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        return {'status': {'key': 'open'}}

    await _add_nanny_service('test_service', add_service, add_nanny_branch)
    service_id = await _setup_service(
        add_service,
        add_nanny_branch,
        web_app_client,
        deploy_params,
        add_related_service,
        with_alias=True,
    )
    _deployments = await _get_deployments(web_app_client, service_id)
    assert len(_deployments) == 1
    _deploy_id = _deployments[0]['deployment_id']
    await check_many_locks(_deploy_id, 2)

    response = await web_app_client.post(
        f'/v1/service/deployment/cancel/',
        headers={'X-Yandex-Login': 'ilyasov'},
        params={'deployment_id': _deploy_id},
    )
    assert response.status == 200, await response.text()
    await check_many_locks(_deploy_id, 0)

    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json={'release_ticket': 'TAXIREL-3', **deploy_params},
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert response.status == 200, await response.text()
    _new_deploy = (await response.json())['job_id']
    await check_many_locks(_new_deploy, 1)

    response = await web_app_client.post(
        f'/v1/service/deployment/retry/',
        json={'deployment_id': _deploy_id, 'taxirel_ticket': 'TAXIREL-3'},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200, await response.text()
    await check_many_locks(_new_deploy, 0)
    await check_many_locks((await response.json())['deployment_id'], 2)

    deployments = await _get_deployments(web_app_client, service_id)
    assert len(deployments) == 3
    latest_deployment = deployments[0]
    assert latest_deployment.get('sandbox_resources') == deploy_params.get(
        'sandbox_resources',
    )
    assert latest_deployment.get('image') == deploy_params.get('docker_image')
