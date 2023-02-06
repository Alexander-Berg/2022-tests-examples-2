# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import inspect
import json
import logging
import os
from typing import Optional

from aiohttp import web
import pytest

import clownductor.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from clownductor.internal import branches
from clownductor.internal import projects as projects_module
from clownductor.internal import related_services
from clownductor.internal import services as services_module
from clownductor.internal.tasks import cubes
from clownductor.internal.tasks import job_recipes
from clownductor.internal.utils import postgres

logger = logging.getLogger('clownductor')

pytest_plugins = [
    'clownductor.generated.service.pytest_plugins',
    'clownductor.generated.service.abc_nonofficial_api.pytest_plugin',
    'clownductor.generated.service.abk_configs.pytest_plugin',
    'clownductor.generated.service.conductor_api.pytest_plugin',
    'clownductor.generated.service.cookie_monster.pytest_plugin',
    'clownductor.generated.service.golovan.pytest_plugin',
    'clownductor.generated.service.grafana_api.pytest_plugin',
    'clownductor.generated.service.login_api.pytest_plugin',
    'clownductor.generated.service.mdb_api.pytest_plugin',
    'client_puncher.pytest_plugin',
    'clownductor.generated.service.pytest_plugins',
    'clownductor.generated.service.solomon_api.pytest_plugin',
    'clownductor.generated.service.yav_api.pytest_plugin',
]

from task_processor_lib import (  # noqa: E501,I100 pylint: disable=wrong-import-position
    types as tp_mock_types,
)


@pytest.fixture(autouse=True)
def taxi_config_default(taxi_config):
    clownductor_features = taxi_config.get('CLOWNDUCTOR_FEATURES')
    if clownductor_features.get('task_processor_enabled') is None:
        clownductor_features.update({'task_processor_enabled': False})
    taxi_config.set(CLOWNDUCTOR_FEATURES=clownductor_features)


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'NANNY_OAUTH': 'nanny_oauth',
            'SOLOMON_OAUTH': 'solomon_oauth',
            'STAFF_OAUTH': 'staff_oauth',
            'ABC_OAUTH': 'abc_oauth',
            'MDB_OAUTH': 'mdb_oauth',
            'CONDUCTOR_OAUTH': 'conductor_oauth',
            'ABC_DEFAULT_OWNER': 'robot-abc-owner',
            'LOGBROKER_OAUTH': 'logbroker-meoauth',
            'STARTRACK_API_PROFILES': {
                'robot-taxi-clown': {
                    'url': 'http://test-startrack-url/',
                    'org_id': 0,
                    'oauth_token': 'some_token',
                },
            },
        },
    )
    simple_secdist.update(
        {
            'deploy_tokens': {'lavka_token': 'lavka_special_token'},
            'TEAMCITY_AUTH_TOKEN': 'valid_teamcity_token',
            'STRONGBOX_API_TOKEN': 'sb_token',
            'ROBOT_CREDENTIALS': {
                'login': 'robot-taxi-clown',
                'password': 'qwerty',
            },
            'YAV_OAUTH': 'yav-oauth',
            'DISPENSER_OAUTH': 'DISPENSER_OAUTH',
            'AWACS_OAUTH': 'awacs-oauth',
            'L3MGR_OAUTH': 'l3mgr-oauth',
            'DNS_OAUTH': 'dns-oauth',
            'PUNCHER_OAUTH': 'puncher-oauth',
            'ABK_OAUTH': 'abk-oauth',
            'GRAFANA_TOKEN': 'grafana-oauth',
            'LENTA_API_KEY': 'lenta_api_key',
            'TSUM_OAUTH': 'tsum_api_key',
            'SANDBOX_OAUTH': 'sandbox_api_key',
        },
    )
    return simple_secdist


@pytest.fixture(name='get_namespace')
def _get_namespace(web_context):
    async def _wrapper(name):
        query, args = web_context.sqlt.namespaces_retrieve(name)
        async with postgres.primary_connect(web_context) as conn:
            return await conn.fetchrow(query, args)

    return _wrapper


@pytest.fixture(name='add_namespace')
def _add_namespace(web_context):
    async def _wrapper(name):
        query, args = web_context.sqlt.namespaces_add(name)
        async with postgres.primary_connect(web_context) as conn:
            return await conn.fetchrow(query, *args)

    return _wrapper


@pytest.fixture
def add_project(web_context, add_namespace, get_namespace):
    async def _wrapper(
            project_name,
            namespace_id=None,
            service_abc='someserviceabcslug',
            project_prefix='taxi',
    ):
        if not namespace_id:
            namespace = await get_namespace(project_name)
            if not namespace:
                namespace = await add_namespace(project_name)

        owners = {
            'logins': ['test_login1', 'test_login2'],
            'groups': ['test_group'],
        }
        approving_managers = {'logins': ['damsker'], 'cgroups': [123, 456]}
        approving_devs = {'logins': ['abcdefg'], 'cgroups': [246, 123]}
        env_params = {
            'stable': {
                'domain': 'taxi.pytest',
                'juggler_folder': '%s.prod' % project_name,
            },
            'testing': {
                'domain': 'taxi.tst.pytest',
                'juggler_folder': '%s.test' % project_name,
            },
            'unstable': {
                'domain': 'taxi.dev.pytest',
                'juggler_folder': '%s.unst' % project_name,
            },
            'general': {
                'project_prefix': project_prefix,
                'docker_image_tpl': ('%s/{{ service }}/$' % project_name),
            },
        }
        responsible_team = {
            'ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
            'developers': [],
            'managers': [],
            'superusers': ['isharov', 'nikslim'],
        }
        yt_topic = {
            'path': 'taxi/taxi-access-log',
            'permissions': ['WriteTopic'],
        }
        project_data = projects_module.ProjectWithoutId(
            name=project_name,
            network_testing='_TEST_NET_',
            network_stable='_STABLE_NET_',
            service_abc=service_abc,
            yp_quota_abc='slugwithqouta',
            tvm_root_abc='tvmtvmtvm',
            owners=owners,
            approving_managers=approving_managers,
            approving_devs=approving_devs,
            pgaas_root_abc='test_params_slug',
            env_params=env_params,
            responsible_team=responsible_team,
            yt_topic=yt_topic,
            namespace_id=namespace_id or namespace['id'],
        )
        return await web_context.service_manager.projects.add(project_data)

    return _wrapper


@pytest.fixture
def get_project(web_app_client):
    async def _wrapper(project_name):
        response = await web_app_client.get(
            '/api/projects',
            params={'name': project_name},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()

        return data[0] if data else None

    return _wrapper


@pytest.fixture
def add_service(web_context, web_app_client, add_project, get_project):
    async def _wrapper(
            project_name,
            service_name,
            namespace_id=None,
            type_=services_module.ClusterType.NANNY.value,
            direct_link=None,
            artifact_name='ubuntu',
            design_review_ticket=None,
            abc_service=None,
            is_deleted=False,
    ):
        project = await get_project(project_name)
        if project is None:
            project = await add_project(project_name, namespace_id)
        project_id = project['id']
        data = {
            'name': service_name,
            'artifact_name': artifact_name,
            'cluster_type': type_,
            'st_task': 'TAXIADMIN-100500',
            'direct_link': direct_link,
            'abc_service': abc_service,
        }
        if design_review_ticket:
            data['design_review_ticket'] = design_review_ticket

        response = await web_app_client.post(
            f'/api/services',
            params={'project_id': project_id},
            json=data,
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        if is_deleted:
            await web_context.service_manager.services.set_deleted(data['id'])
        return data

    return _wrapper


@pytest.fixture
def add_related_service(web_context):
    async def _wrapper(data):
        manager = web_context.service_manager.related_services
        relation_type = related_services.ServiceRelationType.ALIAS_MAIN_SERVICE
        async with postgres.get_connection(
                web_context, transaction=True,
        ) as conn:
            services = []
            for (service_name, project_name) in data:
                service_data = (
                    await web_context.service_manager.services.get_by_name(
                        project_name=project_name,
                        cluster_type=services_module.ClusterType.NANNY,
                        name=service_name,
                        conn=conn,
                    )
                )
                services.append(service_data)
            related_data = []
            for alias in services[1:]:
                related_data.append(
                    related_services.ServiceRelation(
                        service_id=alias['id'],
                        related_service_id=services[0]['id'],
                        relation_type=relation_type,
                    ),
                )
            return await manager.add_many(
                related_data, is_autogenerated=True, conn=conn,
            )

    return _wrapper


@pytest.fixture
def get_service(web_app_client):
    async def _wrapper(service_id):
        response = await web_app_client.get(
            f'/api/services',
            params={'service_id': service_id},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data[0]

    return _wrapper


@pytest.fixture
def get_service_by_name(web_app_client):
    async def _wrapper(service_name, cluster_type, project_id):
        response = await web_app_client.get(
            f'/api/services',
            params={
                'name': service_name,
                'cluster_type': cluster_type,
                'project_id': project_id,
            },
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data[0]

    return _wrapper


@pytest.fixture
def get_services(web_app_client):
    async def _wrapper():
        response = await web_app_client.get(
            f'/v1/services/search',
            params={'name': ''},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data

    return _wrapper


@pytest.fixture
def add_branch(web_context):
    async def _wrapper(data):
        return await web_context.service_manager.branches.add(data)

    return _wrapper


@pytest.fixture
def get_branches(web_app_client):
    async def _wrapper(service_id):
        response = await web_app_client.get(
            f'/v1/branches/', params={'service_id': service_id},
        )
        assert response.status == 200
        data = await response.json()
        return data

    return _wrapper


@pytest.fixture
def add_nanny_branch_by_api(mock_strongbox, web_app_client):
    @mock_strongbox('/v1/groups/')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'service_name': 'some-service',
                'env': 'unstable',
            },
        )

    async def _wrapper(
            *,
            service_id: int,
            branch_name: str,
            env: str = 'unstable',
            preset: str = 'x2pico',
            disk_profile: str = 'default',
    ) -> int:
        response = await web_app_client.post(
            f'/v2/create_nanny_branch/',
            params={'service_id': service_id},
            json={
                'name': branch_name,
                'env': env,
                'preset': preset,
                'disk_profile': disk_profile,
            },
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        body = await response.json()
        return body['branch']['id']

    return _wrapper


@pytest.fixture
def add_nanny_branch(web_context):
    async def _wrapper(
            service_id,
            branch_name,
            env=branches.Env.UNSTABLE.value,
            direct_link=None,
    ):
        if branch_name in ('stable', 'testing', 'unstable'):
            env = branch_name
        branch = await web_context.service_manager.branches.add(
            {
                'service_id': service_id,
                'name': branch_name,
                'env': env,
                'direct_link': direct_link,
                'endpointsets': [
                    {'id': 'rtc_id', 'regions': ['MAN', 'SAS', 'VLA']},
                ],
            },
        )
        if env is branches.Env.STABLE.value:
            await web_context.service_manager.branches.add(
                {
                    'service_id': service_id,
                    'name': 'pre_stable',
                    'env': branches.Env.PRESTABLE.value,
                    'direct_link': direct_link,
                    'endpointsets': [
                        {
                            'id': 'rtc_id_pre_stable',
                            'regions': ['MAN', 'SAS', 'VLA'],
                        },
                    ],
                },
            )
        return branch['id']

    return _wrapper


@pytest.fixture
def add_postgres_branch(web_app_client):
    async def _wrapper(service_id, name, env, flavor, disk_size) -> int:
        response = await web_app_client.post(
            f'/v2/create_postgres_branch/',
            params={'service_id': service_id},
            json={
                'name': name,
                'env': env,
                'flavor': flavor,
                'disk_size': disk_size,
            },
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data['branch']['id']

    return _wrapper


@pytest.fixture
def add_db_branch(web_app_client):
    async def _wrapper(service_id, name, env, flavor, disk_size, db_type: str):
        response = await web_app_client.post(
            f'/v2/create_db_branch/',
            params={'service_id': service_id},
            json={
                'name': name,
                'env': env,
                'flavor': flavor,
                'disk_size': disk_size,
                'db_type': db_type,
            },
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data['branch']['id']

    return _wrapper


@pytest.fixture
def add_conductor_branch(web_context):
    async def _wrapper(service_id, env, direct_link=None):
        branch = await web_context.service_manager.branches.add(
            {
                'service_id': service_id,
                'name': env,
                'env': env,
                'direct_link': direct_link,
                'endpointsets': '[]',
            },
        )
        return branch['id']

    return _wrapper


@pytest.fixture
def get_branch(web_app_client):
    async def _wrapper(branch_id):
        response = await web_app_client.get(
            f'/api/branches',
            params={'branch_id': branch_id},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data

    return _wrapper


@pytest.fixture
def get_service_jobs(web_app_client):
    async def _wrapper(service_id):
        response = await web_app_client.get(
            '/api/jobs',
            params={'service_id': service_id},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        return await response.json()

    return _wrapper


@pytest.fixture
def get_branch_jobs(web_app_client):
    async def _wrapper(branch_id):
        response = await web_app_client.get(
            f'/api/jobs',
            params={'branch_id': branch_id},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data

    return _wrapper


@pytest.fixture
def get_job(web_app_client):
    async def _wrapper(job_id):
        response = await web_app_client.get(
            '/v1/jobs',
            params={'job_id': job_id},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        data = await response.json()
        return data

    return _wrapper


@pytest.fixture
def get_job_variables(web_context):
    async def _wrapper(job_id):
        query, args = web_context.sqlt.job_variables_get_job_ids(job_id)
        async with postgres.primary_connect(web_context) as conn:
            result = await conn.fetchrow(query, args)
            return dict(result) if result else None

    return _wrapper


@pytest.fixture
def get_task(get_job):
    async def _wrapper(job_id, task_id):
        job = await get_job(job_id)
        job = job[0]
        return [x for x in job['tasks'] if x['id'] == task_id][0]

    return _wrapper


@pytest.fixture
def relative_load_plaintext():
    """
    Load text from `./static/filename`.
    Raises `ValueError` if file not found or.
    """

    def _wrapper(filename, mode='r'):
        caller_filename = inspect.stack()[1][1]
        caller_dir = os.path.dirname(os.path.abspath(caller_filename))
        full_path = os.path.join(caller_dir, 'static', filename)
        try:
            with open(full_path, mode=mode) as fileobj:
                return fileobj.read()
        except FileNotFoundError as exc:
            raise ValueError('cannot load json from %s: %s' % (full_path, exc))

    return _wrapper


@pytest.fixture
def mocks_for_project_creation(login_mockserver):
    login_mockserver()


@pytest.fixture
@pytest.mark.usefixtures('patch_github')
def mocks_for_service_creation(
        abc_mockserver,
        abc_nonofficial_mockserver,
        abk_configs_mockserver,
        add_project,
        cookie_monster_mockserver,
        login_mockserver,
        mock_strongbox,
        staff_mockserver,
        yav_mockserver,
        tvm_info_mockserver,
        patch_github,
):
    login_mockserver()
    abc_mockserver(services=True)
    abc_nonofficial_mockserver()
    cookie_monster_mockserver()
    yav_mockserver()
    abk_configs_mockserver()
    staff_mockserver()
    tvm_info_mockserver()
    patch_github()

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


@pytest.fixture(name='mock_random_regions')
def _mock_random_regions(patch):
    @patch('clownductor.internal.presets.presets.random_region')
    def _random_region(context, count=1, project=None):
        assert context
        assert project
        return ['vla', 'man', 'sas'][0:count]

    return _random_region


@pytest.fixture(name='random_region')
async def _random_region(patch):
    @patch('clownductor.internal.presets.presets.random_region')
    async def _random_region(context, count=1, project=None):
        return ['vla', 'man', 'sas'][0:count]

    return _random_region


@pytest.fixture
def task_data():
    def _do_it(name, *, input_mapping=None, output_mapping=None, **updates):
        if input_mapping is None:
            input_mapping = {}
        if output_mapping is None:
            output_mapping = {}
        return {
            'id': 123,
            'job_id': 456,
            'name': name,
            'sleep_until': 0,
            'input_mapping': input_mapping,
            'output_mapping': output_mapping,
            'payload': {},
            'retries': 0,
            'status': 'in_progress',
            'error_message': None,
            'created_at': 0,
            'updated_at': 0,
            **updates,
        }

    return _do_it


@pytest.fixture
def patch_method(monkeypatch):
    def dec_generator(full_func_path):
        def dec(func):
            monkeypatch.setattr(full_func_path, func)
            return func

        return dec

    return dec_generator


@pytest.fixture
def cube_caller(mockserver, web_context):
    async def do_it(stage, cube, request_data):
        async with postgres.get_connection(web_context) as conn:
            cube = cubes.CUBES[cube.name](
                context=web_context,
                data={
                    'id': request_data['task_id'],
                    'job_id': request_data['job_id'],
                    'name': cube.name,
                    'status': request_data['status'],
                    'retries': request_data['retries'],
                    'input_mapping': stage.input_mapping,
                    'output_mapping': stage.output_mapping,
                    'payload': request_data['payload'],
                },
                variables=request_data['input_data'],
                parents=[],
                conn=conn,
            )
            # pylint: disable=protected-access
            await cube._update(request_data['input_data'])
            response_data = {'status': cube.status}
            if cube.has_payload:
                response_data['payload'] = cube.payload
            if cube.sleep_duration:
                response_data['sleep_duration'] = cube.sleep_duration
            return mockserver.make_response(json=response_data)

    return do_it


@pytest.fixture(name='external_call_cube')
def _external_call_cube(web_app_client):
    async def do_it(stage, cube, request_data):
        return await web_app_client.post(
            f'/task-processor/v1/cubes/{cube.name}/', json=request_data,
        )

    return do_it


_MIGRATED_RECIPES = {
    'CreateFullNannyService',
    'RelocateServiceToNanny',
    'CreateNannyService',
    'PrepareRelocationService',
    'CreateNannyBranch',
    'CreateFullNannyBranch',
    'CreatePostgresService',
    'CreatePostgresBranch',
    'CreateDBBranch',
    'CreateDBService',
    'ChangeAbcSubsystem',
    'ChangeProjectForService',
    'ResolveServiceDiff',
    'SyncServiceRemoteParameters',
    'DeployNannyServiceNoApprove',
    'DeployOneNannyService',
    'WaitMainDeployNannyServiceNoApprove',
    'DeployNannyServiceWithApprove',
    'WaitMainDeployNannyServiceWithApprove',
    'ChangeCustomParameters',
    'ChangeDcOnPrestable',
    'RemoveClownductorNannyService',
}


@pytest.fixture
async def _default_tp_init_params(
        cube_caller, external_call_cube, _external_raw_recipes,
):
    clown = tp_mock_types.Provider(
        name='clownductor', id=1, cube_caller=cube_caller,
    )
    clowny_balancer = tp_mock_types.Provider(
        name='clowny-balancer', id=2, cube_caller=external_call_cube,
    )
    clowny_roles = tp_mock_types.Provider(
        name='clowny-roles', id=3, cube_caller=external_call_cube,
    )
    taxi_strongbox = tp_mock_types.Provider(
        name='taxi-strongbox', id=4, cube_caller=external_call_cube,
    )
    clowny_perforator = tp_mock_types.Provider(
        name='clowny-perforator', id=35, cube_caller=external_call_cube,
    )

    return {
        'providers': [
            clown,
            clowny_balancer,
            clowny_roles,
            taxi_strongbox,
            clowny_perforator,
        ],
        'cubes': [
            tp_mock_types.Cube(
                provider=clown,
                name=name,
                needed_parameters=cube.needed_parameters(),
                optional_parameters=(
                    cube.optional_parameters()
                    if hasattr(cube, 'optional_parameters')
                    else []
                ),
                output_parameters=(
                    cube.output_parameters()
                    if hasattr(cube, 'output_parameters')
                    else []
                ),
                check_input_mappings=cube.check_input_mappings(),
                check_output_mappings=cube.check_output_mappings(),
            )
            for name, cube in cubes.CUBES.items()
        ],
        'recipes': [],
        'raw_recipes': [
            {
                'name': name,
                'provider_name': clown.name,
                'job_vars': recipe['job_vars'],
                'stages': [
                    {
                        'name': stage['task'],
                        'input_mapping': stage.get('input', {}),
                        'output_mapping': stage.get('output', {}),
                    }
                    for stage in recipe['stages']
                ],
            }
            for name, recipe in job_recipes.JOB_RECIPES.items()
            if name in _MIGRATED_RECIPES
        ] + _external_raw_recipes,
    }


@pytest.fixture(name='internal_mock_vars')
def _internal_mock_vars():
    return {}


@pytest.fixture
def mock_internal_tp(patch, task_processor, internal_mock_vars):
    @patch('clownductor.internal.utils.task_processor.use_task_processor')
    def _use_task_processor(job_name):
        return True

    @patch('clownductor.internal.tasks.manager.create_job')
    async def _create_job(
            context,
            initiator: str,
            recipe_name: str,
            variables: dict,
            service: int,
            recipe_json: Optional[dict] = None,
            branch: Optional[int] = None,
            token: Optional[str] = None,
            db_conn: Optional = None,
            change_doc_id: Optional[str] = None,
            remote_job_id: Optional[int] = None,
            **kwargs,
    ):
        if remote_job_id is None:
            remote_job = await task_processor.start_job(
                name=recipe_name,
                job_vars=variables,
                initiator=initiator,
                change_doc_id=change_doc_id,
                idempotency_token=token,
            )
            remote_job_id = remote_job.id

        job_query, job_args = context.sqlt.jobs_add(
            service_id=service,
            branch_id=branch,
            recipe_name=recipe_name,
            initiator=initiator,
            status=internal_mock_vars.get('status', 'inited'),
            change_doc_id=change_doc_id,
            remote_job_id=remote_job_id,
        )
        async with postgres.get_connection(context, db_conn) as conn:
            job_id = await conn.fetchval(job_query, *job_args)
            job_variables_query, job_variables_args = (
                context.sqlt.job_variables_add(
                    job_id=job_id, job_variables=json.dumps(variables),
                )
            )
            await conn.execute(job_variables_query, *job_variables_args)
        task_processor.internal_job_ids[job_id] = remote_job_id
        logger.info(
            'Job %s with id %s (external %s) saved',
            recipe_name,
            job_id,
            remote_job_id,
        )

        return job_id


@pytest.fixture
def get_job_from_internal(task_processor, get_job):
    async def do_it(job_id) -> tp_mock_types.Job:
        internal = (await get_job(job_id))[0]
        return task_processor.job(internal['job']['remote_job_id'])

    return do_it


@pytest.fixture
def check_many_locks(web_context):
    async def do_it(job_id, expected_count):
        query, args = web_context.sqlt.locks_find(job_id, None, None)
        async with postgres.primary_connect(web_context) as conn:
            rows = await conn.fetch(query, *args)
        assert (
            len(rows) == expected_count
        ), f'job {job_id}, locks {[x["name"] for x in rows]}'

    return do_it
