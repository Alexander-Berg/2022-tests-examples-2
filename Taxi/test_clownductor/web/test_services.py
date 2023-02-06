# pylint: disable=unused-variable
from aiohttp import web
import pytest

from task_processor_lib import types as mock_types

from clownductor.internal import services as services_module

PULL_REQUEST_CONTENT = (
    b"""
{
    "settings_override": {
        "TVM_SERVICES": {
            "service-with-tvm": {{ TVM_TAXI_SERVICE_WITH_TVM }}
        }
    }
}
""".lstrip()
)


@pytest.fixture(name='cube_caller')
def _cube_caller(cube_caller, mockserver, web_context):
    async def _wrapper(stage, cube, request_data):
        if cube.name == 'MockRecipe':
            return mockserver.make_response(
                json={
                    'status': 'success',
                    'payload': {
                        'tvm_id': '123456',
                        'tvm_secret_tmp_yav_id': 'sec-XXX',
                    },
                },
            )
        return await cube_caller(stage, cube, request_data)

    return _wrapper


@pytest.fixture(name='mock_abc_create_tvm_resource_recipe')
def _mock_abc_create_tvm_resource_recipe(cube_caller, task_processor):
    provider = task_processor.provider('clownductor')
    cube = task_processor.add_cube(
        'MockRecipe',
        needed_parameters=[],
        optional_parameters=[],
        output_parameters=['tvm_id', 'tvm_secret_tmp_yav_id'],
        check_input_mappings=True,
        check_output_mappings=True,
        provider=provider,
    )
    task_processor.add_recipe(
        'AbcCreateTvmResource',
        provider=provider,
        job_vars=[],
        stages=[
            mock_types.RecipeStage(
                provider=provider,
                cube=cube,
                input_mapping={},
                output_mapping={
                    'tvm_id': 'tvm_id',
                    'tvm_secret_tmp_yav_id': 'tvm_secret_tmp_yav_id',
                },
            ),
        ],
    )


@pytest.mark.usefixtures(
    'mock_internal_tp', 'mock_abc_create_tvm_resource_recipe',
)
@pytest.mark.features_on('service_config_tvm')
@pytest.mark.parametrize(['api_handler'], [('/api/services',)])
@pytest.mark.pgsql('clownductor')
async def test_services_add(
        task_processor,
        run_job_with_meta,
        get_service_jobs,
        patch,
        api_handler,
        web_app_client,
        login_mockserver,
        abc_mockserver,
        abc_nonofficial_mockserver,
        staff_mockserver,
        cookie_monster_mockserver,
        abk_configs_mockserver,
        yav_mockserver,
        add_project,
        get_service,
        mock_strongbox,
        tvm_info_mockserver,
):  # pylint: disable=R0913,R0914
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        pass

    login_mockserver()
    abc_mockserver(services=True)
    abc_nonofficial_mockserver()
    staff_mockserver()
    cookie_monster_mockserver()
    yav_mockserver()
    abk_configs_mockserver()
    tvm_info_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    @mock_strongbox('/v1/secrets/')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'name': 'SOME_NAME',
            },
        )

    response = await web_app_client.post(
        api_handler,
        params={'project_id': project_id},
        json={
            'name': 'service-with-tvm',
            'artifact_name': 'ubuntu',
            'cluster_type': services_module.ClusterType.NANNY.value,
            'st_task': 'TAXIADMIN-100500',
        },
        headers={
            'Authorization': 'OAuth valid_oauth',
            'X-Yandex-Login': 'ilyasov',
        },
    )
    assert response.status == 200
    added_service = await response.json()
    assert isinstance(added_service['id'], int)

    jobs = await get_service_jobs(added_service['id'])
    assert len(jobs) == 1
    job = task_processor.job(jobs[0]['job']['id'])
    await run_job_with_meta(job)

    service = await get_service(added_service['id'])

    assert service['tvm_testing_abc_service'] == 'taxiservicewithtvm'
    assert service['tvm_stable_abc_service'] == 'taxiservicewithtvm'


@pytest.mark.config(
    CLOWNDUCTOR_BANNED_PROJECTS=[
        {'project_name': 'taxi', 'description_error': 'bad shared project'},
    ],
)
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.parametrize(['api_handler'], [('/api/services',)])
@pytest.mark.parametrize(
    'cluster_type, slug',
    [
        pytest.param(
            services_module.ClusterType.POSTGRES.value,
            'taxipgaasdbservice',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_MAP_PROJECTS_BY_QOUTA_PARAMS={
                        'taxi': {'use_single_abc_on_db': True},
                        '__default__': {'use_single_abc_on_db': False},
                    },
                ),
            ],
        ),
        pytest.param(
            services_module.ClusterType.POSTGRES.value,
            'taxipgaasdbservice',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_MAP_PROJECTS_BY_QOUTA_PARAMS={
                        'taxi': {'use_single_abc_on_db': False},
                        '__default__': {'use_single_abc_on_db': False},
                    },
                ),
            ],
        ),
        pytest.param(
            services_module.ClusterType.MONGO_MDB.value,
            'taximongoaasdbservice',
        ),
        pytest.param(
            services_module.ClusterType.REDIS_MDB.value,
            'taxiredisdbservice',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_MAP_PROJECTS_BY_QOUTA_PARAMS={
                        'taxi': {'use_single_abc_on_db': True},
                        '__default__': {'use_single_abc_on_db': False},
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clownductor')
async def test_services_db_add(
        task_processor,
        run_job_common,
        get_service_jobs,
        api_handler,
        web_app_client,
        login_mockserver,
        abc_mockserver,
        mdb_mockserver,
        abc_nonofficial_mockserver,
        staff_mockserver,
        cookie_monster_mockserver,
        yav_mockserver,
        add_project,
        get_service,
        mock_dispenser,
        cluster_type,
        slug,
):  # pylint: disable=R0913,R0914
    login_mockserver()
    abc_mockserver(services=True)
    mdb_mockserver(slug=slug)
    abc_nonofficial_mockserver()
    staff_mockserver()
    cookie_monster_mockserver()
    yav_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    @mock_dispenser('/common/api/v1/projects')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'result': [
                    {
                        'key': 'taxistoragepgaas',
                        'name': 'taxistoragedbaas',
                        'description': '',
                        'abcServiceId': 2219,
                        'responsibles': {'persons': [], 'yandexGroups': {}},
                        'members': {'persons': [], 'yandexGroups': {}},
                        'parentProjectKey': 'taxistorage',
                        'subprojectKeys': [
                            'taxipgaasbillingmaintenance',
                            slug,
                        ],
                        'person': None,
                    },
                ],
            },
        )

    data = {
        'name': 'db-service',
        'cluster_type': cluster_type,
        'st_task': 'TAXIADMIN-100500',
        'abc_service': slug,
    }
    if 'api' in api_handler:
        data.update({'artifact_name': 'ubuntu'})  # HACKITY HACK

    response = await web_app_client.post(
        api_handler,
        params={'project_id': project_id},
        json=data,
        headers={
            'Authorization': 'OAuth valid_oauth',
            'X-Yandex-Login': 'ilyasov',
        },
    )
    assert response.status == 200
    added_service = await response.json()
    assert isinstance(added_service['id'], int)

    jobs = await get_service_jobs(added_service['id'])
    assert len(jobs) == 1
    job = task_processor.job(jobs[0]['job']['id'])
    await run_job_common(job)

    service = await get_service(added_service['id'])
    assert service is not None


@pytest.mark.pgsql('clownductor')
async def test_services_get_by_id(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_project,
):
    login_mockserver()
    staff_mockserver()
    service_name = 'service_1'
    service = await add_service('taxi', service_name)
    service_id = service['id']

    project = await get_project('taxi')

    response = await web_app_client.get(
        f'/api/services',
        params={'service_id': service_id},
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    data = await response.json()
    data = data[0]

    assert data['id'] == service_id
    assert data['project_id'] == project['id']
    assert data['name'] == service_name


@pytest.mark.pgsql('clownductor')
async def test_services_get_by_project_id(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_project,
):
    login_mockserver()
    staff_mockserver()
    services = ['service_1', 'service_2']
    for service in services:
        await add_service('taxi', service)
    other_services = ['blah', 'foo']
    for other_service in other_services:
        await add_service('taximeter', other_service)

    project = await get_project('taxi')
    project_id = project['id']

    response = await web_app_client.get(
        f'/api/services',
        params={'project_id': project_id},
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    data = await response.json()

    assert isinstance(data, list)
    assert len(data) == len(services)
    for service in data:
        assert service['name'] in services


@pytest.mark.pgsql('clownductor')
async def test_services_get_by_namespace(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        add_namespace,
        get_namespace,
):
    login_mockserver()
    staff_mockserver()
    services = ['service_1', 'service_2']
    namespace = await add_namespace('taxi')
    for service in services:
        await add_service(
            project_name='taxi',
            service_name=service,
            namespace_id=namespace['id'],
        )
    other_services = ['blah', 'foo']
    other_namespace = await add_namespace('lavka')
    for other_service in other_services:
        await add_service(
            'lavka-frontend',
            other_service,
            namespace_id=other_namespace['id'],
        )

    assert namespace == await get_namespace('taxi')
    assert other_namespace == await get_namespace('lavka')
    namespace_name = namespace['name']

    response = await web_app_client.get(
        '/v1/services/',
        params={'tplatform_namespace': namespace_name},
        headers={
            'Authorization': 'OAuth valid_oauth',
            'X-Yandex-Login': 'username',
        },
    )
    assert response.status == 200
    data = await response.json()
    assert isinstance(data, list)
    assert len(data) == len(services)
    for service in data:
        assert service['name'] in services


@pytest.mark.pgsql('clownductor', files=['projects.sql', 'services.sql'])
@pytest.mark.parametrize(
    'params, response_data',
    [
        pytest.param(
            {'name': 'service_1', 'namespace': 'eda'},
            [
                {
                    'project_id': 2,
                    'project_name': 'eda',
                    'services': [
                        {
                            'id': 5,
                            'name': 'eda_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                        },
                    ],
                },
            ],
        ),
        pytest.param(
            {'name': 'service_1'},
            [
                {
                    'project_id': 2,
                    'project_name': 'eda',
                    'services': [
                        {
                            'id': 5,
                            'name': 'eda_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                        },
                    ],
                },
                {
                    'project_id': 1,
                    'project_name': 'taxi',
                    'services': [
                        {
                            'id': 1,
                            'name': 'taxi_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                        },
                    ],
                },
            ],
        ),
        pytest.param(
            {'name': ''},
            [
                {
                    'project_id': 2,
                    'project_name': 'eda',
                    'services': [
                        {
                            'id': 5,
                            'name': 'eda_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                        },
                        {
                            'id': 6,
                            'name': 'eda_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                        },
                        {
                            'id': 7,
                            'name': 'eda_service_5_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                        },
                    ],
                },
                {
                    'project_id': 3,
                    'project_name': 'lavka_empty',
                    'services': [],
                },
                {
                    'project_id': 5,
                    'project_name': 'market',
                    'services': [
                        {
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'market_service',
                            'id': 9,
                            'name': 'market_service',
                            'production_ready': False,
                            'project_id': 5,
                            'requester': 'unit_test',
                        },
                    ],
                },
                {
                    'project_id': 6,
                    'project_name': 'new_market_project',
                    'services': [
                        {
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'market_service',
                            'id': 10,
                            'name': 'new_market_service',
                            'production_ready': False,
                            'project_id': 6,
                            'requester': 'unit_test',
                        },
                    ],
                },
                {
                    'project_id': 4,
                    'project_name': 'project_with_deleted_services',
                    'services': [],
                },
                {
                    'project_id': 1,
                    'project_name': 'taxi',
                    'services': [
                        {
                            'id': 1,
                            'name': 'taxi_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                        },
                        {
                            'id': 2,
                            'name': 'taxi_service_2_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                        },
                        {
                            'id': 3,
                            'name': 'taxi_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                        },
                        {
                            'id': 4,
                            'name': 'taxi_service_4_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                        },
                    ],
                },
            ],
        ),
        pytest.param(
            {'name': 'market'},
            [
                {
                    'project_id': 5,
                    'project_name': 'market',
                    'services': [
                        {
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'market_service',
                            'id': 9,
                            'name': 'market_service',
                            'production_ready': False,
                            'project_id': 5,
                            'requester': 'unit_test',
                        },
                    ],
                },
                {
                    'project_id': 6,
                    'project_name': 'new_market_project',
                    'services': [
                        {
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'market_service',
                            'id': 10,
                            'name': 'new_market_service',
                            'production_ready': False,
                            'project_id': 6,
                            'requester': 'unit_test',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_services_search(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        params,
        response_data,
):
    login_mockserver()
    staff_mockserver()

    response = await web_app_client.get(
        f'/v1/services/search/',
        params=params,
        headers={
            'Authorization': 'OAuth valid_oauth',
            'X-Yandex-Login': 'username',
        },
    )
    assert response.status == 200
    data = await response.json()
    data = data['projects']
    assert data == response_data


@pytest.mark.pgsql('clownductor')
async def test_services_update(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_service,
        get_project,
):
    login_mockserver()
    staff_mockserver()
    service_name = 'service_1'
    service = await add_service('taxi', service_name)
    service_id = service['id']

    project = await get_project('taxi')

    response = await web_app_client.put(
        f'/api/services',
        params={'service_id': service_id},
        headers={'Authorization': 'OAuth valid_oauth'},
        json={'production_ready': True, 'artifact_name': 'something-funny'},
    )
    assert response.status == 200

    service = await get_service(service_id)

    assert service['id'] == service_id
    assert service['project_id'] == project['id']
    assert service['name'] == service_name
    assert service['artifact_name'] == 'something-funny'
    assert service['production_ready'] is True


@pytest.mark.pgsql('clownductor')
async def test_services_update_missing(web_app_client, login_mockserver):
    login_mockserver()

    response = await web_app_client.put(
        f'/api/services',
        params={'service_id': 100500},
        headers={'Authorization': 'OAuth valid_oauth'},
        json={'production_ready': True, 'artifact_name': 'something-funny'},
    )
    assert response.status == 404


async def test_create_service_with_db(
        login_mockserver, staff_mockserver, add_service,
):
    login_mockserver()
    staff_mockserver()
    await add_service('taxi', 'service')
    await add_service(
        'taxi', 'service', type_=services_module.ClusterType.POSTGRES.value,
    )


@pytest.mark.parametrize('project_id, service_id', [(1, None), (None, 2)])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'get_chief_services': True})
async def test_get_services(
        web_app_client,
        staff_mockserver,
        login_mockserver,
        add_project,
        add_service,
        project_id,
        service_id,
):
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    await add_project('infra')
    await add_service('taxi', 'service')
    await add_service('taxi', 'test_duo')

    params = {}
    if service_id:
        params['service_id'] = service_id
    elif project_id:
        params['project_id'] = project_id
    response = await web_app_client.get(
        'v1/services/',
        params=params,
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200, await response.json()


@pytest.mark.parametrize(
    'project_name, service_name, cluster_type',
    [
        ('taxi-devops', 'test-service', 'nanny'),
        ('lavka', 'test-service', 'nanny'),
    ],
)
async def test_get_services_by_name(
        web_app_client,
        staff_mockserver,
        login_mockserver,
        add_project,
        add_service,
        project_name,
        service_name,
        cluster_type,
):
    login_mockserver()
    staff_mockserver()
    await add_project(project_name)
    await add_service(project_name, service_name)

    params = {
        'project_name': project_name,
        'name': service_name,
        'cluster_type': cluster_type,
    }
    response = await web_app_client.get(
        'v1/services/',
        params=params,
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    rows = await response.json()
    assert len(rows) == 1
    service = rows.pop()
    assert service['project_name'] == project_name
    assert service['name'] == service_name
    assert service['cluster_type'] == cluster_type


async def test_get_cluster_types(web_app_client, login_mockserver):
    login_mockserver()

    response = await web_app_client.get('/v1/cluster_types')
    assert response.status == 200
    data = await response.json()
    expected_types = services_module.ClusterType.get_cluster_types()

    assert 'types' in data
    content = data['types']
    assert isinstance(content, list)
    assert len(content) == len(expected_types)
    assert set(content) == set(expected_types)
