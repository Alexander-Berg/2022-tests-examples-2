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
    ['auth_token', 'artifact_name', 'data', 'retcode', 'exp_response'],
    [
        pytest.param(  # invalid token
            'invalid_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
            },
            403,
            None,
            id='invalid_token',
        ),
        pytest.param(  # valid token, but unprocessable parameters
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': None,
                'docker_image': None,
            },
            400,
            None,
            id='unprocessable_params',
        ),
        pytest.param(  # valid token, but unprocessable parameters
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': None,
            },
            400,
            None,
            id='unprocessable_params_2',
        ),
        pytest.param(  # not existing service
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'not-existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/something:0.0.1',
            },
            422,
            None,
            id='non_existing_service',
        ),
        pytest.param(  # wrong cluster_type
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-conductor-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/something:0.0.1',
            },
            422,
            None,
            id='bad_cluster_type',
        ),
        pytest.param(  # wrong docker image name
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/wrong-docker-image:0.0.1',
            },
            422,
            None,
            id='bad_docker_image',
        ),
        pytest.param(  # missing branch
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'testing',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
            },
            422,
            None,
            id='missing_branch',
        ),
        pytest.param(  # finally the good one
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
                'secdist': {
                    'I': 'am',
                    'completely': {'unstrctured': 'really'},
                },
                'configs': ['CONFIG_1', 'CONFIG_2'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services'
                    '/catalog/existing-service_unstable/'
                ),
                'service_info_link': '/services/2/edit/2/deployments/9',
            },
            id='ok',
        ),
        pytest.param(
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'test_service',
                'env': 'unstable',
                'branch_name': 'unstable_name',
                'conductor_ticket': 123,
                'docker_image': 'artifact_name/unstable:0.0.1',
                'secdist': {
                    'I': 'am',
                    'completely': {'unstrctured': 'really'},
                },
                'configs': ['CONFIG_1', 'CONFIG_2'],
            },
            400,
            'NOT_CREATED_YET',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'named_target_deploy': True,
                    'check_creation_finished': True,
                    'diff_validation': True,
                },
            ),
            id='deploy_with_check_creation',
        ),
        (  # the good one with approves
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'production',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
            },
            400,
            None,
        ),
        (
            'valid_teamcity_token',
            'artifact_name',
            {
                'service_name': 'test_service',
                'env': 'production',
                'conductor_ticket': 123,
                'docker_image': 'artifact_name/production:0.0.1',
                'release_ticket': 'TAXIREL-1111',
            },
            400,
            None,
        ),
        (  # the good one with variable artifact name
            'valid_teamcity_token',
            'taxi/existing-service/$',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service/unstable:0.0.1',
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services'
                    '/catalog/existing-service_unstable/'
                ),
                'service_info_link': '/services/2/edit/2/deployments/9',
            },
        ),
        (  # the bad one with variable artifact name
            'valid_teamcity_token',
            'taxi/existing-service/$',
            {
                'service_name': 'existing-service',
                'env': 'unstable',
                'conductor_ticket': 123,
                'docker_image': 'taxi/existing-service:0.0.1',
            },
            422,
            None,
        ),
        pytest.param(
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': ['e-service-1', 'e-service-2'],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/existing-service_stable/\n'
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/e-service-1_stable/'
                ),
                'service_info_link': '',
            },
            marks=pytest.mark.features_off(
                'forbidden_deploy_services_collision',
            ),
            id='collision_off',
        ),
        pytest.param(
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': ['e-service-1', 'e-service-2'],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            422,
            None,
            marks=pytest.mark.features_on(
                'forbidden_deploy_services_collision',
            ),
            id='collision_on.error#1',
        ),
        pytest.param(
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/existing-service_stable/\n'
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/e-service-1_stable/'
                ),
                'service_info_link': '',
            },
            marks=pytest.mark.features_on(
                'forbidden_deploy_services_collision',
            ),
            id='collision_on.status_ok',
        ),
        pytest.param(
            'valid_teamcity_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': ['e-service-1', 'e-service-2', 'meow'],
                'release_ticket': 'TAXIREL-1111',
            },
            422,
            None,
            id='invalid_teamcity_token',
        ),
        pytest.param(
            'teamcity_existing_service_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'unstable',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/existing-service_unstable/\n'
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/e-service-1_unstable/'
                ),
                'service_info_link': '',
            },
            marks=[
                pytest.mark.features_on(
                    'forbidden_deploy_services_collision', 'use_deploy_tokens',
                ),
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_TOKENS={
                        '__default__': 'TEAMCITY_AUTH_TOKEN',
                        'taxi': {
                            '__default__': 'TEAMCITY_TAXI_TOKEN',
                            'existing-service': (
                                'TEAMCITY_EXISTING_SERVICE_TOKEN'
                            ),
                            'e-service-1': 'TEAMCITY_EXISTING_SERVICE_TOKEN',
                            'e-service-2': 'TEAMCITY_EXISTING_SERVICE_TOKEN',
                        },
                    },
                ),
            ],
            id='valid_service_token_unstable',
        ),
        pytest.param(
            'teamcity_existing_service_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            403,
            None,
            marks=[
                pytest.mark.features_on(
                    'forbidden_deploy_services_collision', 'use_deploy_tokens',
                ),
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_TOKENS={
                        '__default__': 'TEAMCITY_AUTH_TOKEN',
                        'taxi': {
                            '__default__': 'TEAMCITY_TAXI_TOKEN',
                            'existing-service': (
                                'TEAMCITY_EXISTING_SERVICE_TOKEN'
                            ),
                            'e-service-1': 'TEAMCITY_EXISTING_SERVICE_TOKEN',
                            'e-service-2': 'TEAMCITY_EXISTING_SERVICE_TOKEN',
                        },
                    },
                ),
            ],
            id='valid_service_token_production',
        ),
        pytest.param(
            'teamcity_taxi_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/existing-service_stable/\n'
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/e-service-1_stable/'
                ),
                'service_info_link': '',
            },
            marks=[
                pytest.mark.features_on(
                    'forbidden_deploy_services_collision', 'use_deploy_tokens',
                ),
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_TOKENS={
                        '__default__': 'TEAMCITY_AUTH_TOKEN',
                        'taxi': {'__default__': 'TEAMCITY_TAXI_TOKEN'},
                    },
                ),
            ],
            id='valid_project_token',
        ),
        pytest.param(
            'teamcity_taxi_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            422,
            None,
            marks=[
                pytest.mark.features_on(
                    'forbidden_deploy_services_collision',
                    'use_deploy_tokens',
                    'only_full_multialias_deploy',
                ),
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_TOKENS={
                        '__default__': 'TEAMCITY_AUTH_TOKEN',
                        'taxi': {'__default__': 'TEAMCITY_TAXI_TOKEN'},
                        'faketaxi': {'__default__': 'TEAMCITY_TAXI_TOKEN'},
                    },
                ),
            ],
            id='valid_project_token_enabled_multi_check_not_all_aliases',
        ),
        pytest.param(
            'teamcity_taxi_token',
            'taxi/existing-service',
            {
                'service_name': 'existing-service',
                'project_name': 'taxi',
                'env': 'production',
                'docker_image': 'taxi/existing-service:0.0.1',
                'configs': ['CONFIG_1', 'CONFIG_2'],
                'aliases': [
                    {'service_name': 'e-service-1', 'project_name': 'taxi'},
                    {
                        'service_name': 'e-service-1',
                        'project_name': 'faketaxi',
                    },
                    {'service_name': 'e-service-2', 'project_name': 'taxi'},
                ],
                'release_ticket': 'TAXIREL-1111',
                'migration_tickets': ['TAXIREL-0', 'TAXIREL-1'],
            },
            200,
            {
                'job_id': 9,
                'deploy_link': (
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/existing-service_stable/\n'
                    'https://nanny.yandex-team.ru/ui/#/services/'
                    'catalog/e-service-1_stable/'
                ),
                'service_info_link': '',
            },
            marks=[
                pytest.mark.features_on(
                    'forbidden_deploy_services_collision',
                    'use_deploy_tokens',
                    'only_full_multialias_deploy',
                ),
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_TOKENS={
                        '__default__': 'TEAMCITY_AUTH_TOKEN',
                        'taxi': {'__default__': 'TEAMCITY_TAXI_TOKEN'},
                        'faketaxi': {'__default__': 'TEAMCITY_TAXI_TOKEN'},
                    },
                ),
            ],
            id='valid_project_token_enabled_multi_check_all_aliases',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'new_get_approvers': True,
        'tc_deploy_links': True,
        'cancel_old_deploys': True,
        'named_target_deploy': True,
        'diff_validation': True,
    },
    EXTERNAL_STARTRACK_DISABLE={'robot-taxi-clown': True},
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'abc', 'parameters': ['maintainers']},
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
)
@pytest.mark.features_on('startrek_close_approval')
async def test_teamcity_deploy(
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
        auth_token,
        artifact_name,
        data,
        retcode,
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
            artifact_name=artifact_name,
        )
        branch_id = await add_nanny_branch(
            nanny_service['id'],
            'unstable',
            env='unstable',
            direct_link=f'{name}_unstable',
        )
        stable_branch_id = await add_nanny_branch(
            nanny_service['id'],
            'stable',
            env='stable',
            direct_link=f'{name}_stable',
        )
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
    await add_related_service(input_services)
    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=data,
        headers={'X-YaTaxi-Api-Key': auth_token},
    )
    assert result.status == retcode, await result.text()
    if result.status == 200:
        content = await result.json()
        assert content == exp_response
        if data['env'] == 'production':
            source = branch_ids['stable']
        else:
            source = branch_ids['unstable']
        if 'configs' in data:
            branch = await get_branch(source['existing-service'])
            assert sorted(branch[0]['configs']) == sorted(data['configs'])

    elif exp_response:
        content = await result.json()
        assert content['code'] == exp_response
