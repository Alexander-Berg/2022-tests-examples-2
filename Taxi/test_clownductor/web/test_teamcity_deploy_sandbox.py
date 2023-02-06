# pylint: disable=redefined-outer-name
import pytest


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


@pytest.mark.parametrize(
    ['data', 'exp_response'],
    [
        pytest.param(
            {
                'service_name': 'existing-service',
                'env': 'production',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
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
                'secdist': {
                    'I': 'am',
                    'completely': {'unstructured': 'really'},
                },
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'release_ticket': 'TAXIREL-1234',
            },
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services'
                    '/catalog/existing-service_stable/'
                ),
                'service_info_link': '/services/2/edit/2/deployments/9',
            },
            id='ok',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
@pytest.mark.features_on(
    'new_get_approvers',
    'cancel_old_deploys',
    'named_target_deploy',
    'diff_validation',
    'startrek_close_approval',
    'enable_simultaneous_sandbox_docker_deploy',
)
@pytest.mark.config(
    EXTERNAL_STARTRACK_DISABLE={'robot-taxi-clown': True},
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'abc', 'parameters': ['maintainers']},
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
)
async def test_teamcity_deploy_image_sandbox(
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_related_service,
        add_nanny_branch,
        add_conductor_branch,
        simple_secdist,
        data,
        exp_response,
        get_branch,
):  # pylint: disable=R0913
    login_mockserver()
    conductor_mockserver()
    staff_mockserver()

    branch_ids = {'stable': {}, 'unstable': {}}
    input_services = [
        ('existing-service', 'taxi'),
        ('e-service-1', 'taxi'),
        ('e-service-1', 'faketaxi'),
        ('e-service-2', 'taxi'),
    ]
    for name, project in input_services:
        nanny_service = await add_service(
            project,
            name,
            type_='nanny',
            direct_link=name,
            artifact_name='taxi/existing-service',
        )
        stable_branch_id = await add_nanny_branch(
            nanny_service['id'],
            'stable',
            env='stable',
            direct_link=f'{name}_stable',
        )
        branch_ids['stable'][name] = stable_branch_id

    conductor_service = await add_service(
        'taxi',
        'existing-conductor-service',
        type_='conductor',
        direct_link='existing-conductor-service',
    )
    await add_conductor_branch(
        conductor_service['id'], 'stable', direct_link='stable',
    )
    await add_related_service(input_services)
    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=data,
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert result.status == 200, await result.text()
    content = await result.json()
    assert content == exp_response
    branch = await get_branch(branch_ids['stable']['existing-service'])
    assert sorted(branch[0]['configs']) == sorted(data['configs'])
