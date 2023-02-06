# pylint: disable=unused-variable
# pylint: disable=too-many-lines
import pytest

import arc_api.components as arc_api

from clownductor.internal import related_services
from clownductor.internal import services as services_module
from clownductor.internal.utils import postgres


ARCADIA_URL = 'https://a.yandex-team.ru'
OK_REQUESTS = [
    (
        (
            f'{ARCADIA_URL}/arc/trunk/arcadia/taxi/frontend/services/'
            f'hiring-partners-app/service.yaml'
        ),
        'frontend.yaml',
        {
            'flavor': 's2.micro',
            'type': 'pgaas',
            'disk_size_gb': 4,
            'testing_disk_size_gb': 2,
            'db_version': '12',
        },
        {
            'db_name': 'partners_app',
            'db_flavor': 's2.micro',
            'db_type': 'pgaas',
            'db_disk_size_gb': 10,
            'db_testing_disk_size_gb': 10,
            'db_version': '12',
        },
    ),
    (
        (
            f'{ARCADIA_URL}/arc/trunk/arcadia/taxi/frontend/services/'
            f'hiring-partners-app/service.yaml'
        ),
        'frontend.yaml',
        {
            'flavor': 's2.micro',
            'type': 'mongo',
            'disk_size_gb': 4,
            'testing_disk_size_gb': 2,
            'db_version': '4.2',
        },
        {
            'db_name': 'partners_app',
            'db_flavor': 's2.micro',
            'db_type': 'mongo',
            'db_disk_size_gb': 10,
            'db_testing_disk_size_gb': 10,
            'db_version': '4.2',
        },
    ),
]


@pytest.mark.parametrize(
    'service_yaml_link, service_yaml, database, expected_db_params',
    OK_REQUESTS,
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
async def test_request_service_from_yaml_with_token(
        web_app_client,
        login_mockserver,
        patch,
        load,
        service_yaml_link,
        service_yaml,
        load_yaml,
        task_processor,
        database,
        get_job,
        expected_db_params,
):
    @patch('arc_api.components.ArcClient.read_file')
    async def read_file(*args, **kwargs):
        try:
            yaml_data = load(service_yaml)
        except FileNotFoundError:
            raise arc_api.ArcClientBaseError()
        return arc_api.ReadFileResponse(header=None, content=yaml_data)

    task_processor.load_recipe(
        load_yaml('recipes/WaitingToCreateServices.yaml')['data'],
    )

    login_mockserver()
    for i in range(2):
        response = await web_app_client.post(
            '/v1/requests/service_from_yaml/',
            json={
                'service_yaml_link': service_yaml_link,
                'database': database,
            },
            headers={
                'X-Yandex-Login': 'deoevgen',
                'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
                'X-YaTaxi-Draft-Id': 'TAXIADMIN-1234',
            },
        )
        data = await response.json()
        if i == 0:
            assert response.status == 200, data
            jobs = await get_job(data['job_id'])
            job = jobs[0]
            job_variables = job['job_variables']
            assert job_variables
            assert job_variables['database'] == expected_db_params
        else:
            # TODO: TAXIPLATFORM-5401 need change to 200
            assert response.status == 400, data


@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.features_on('enable_check_unit_for_create_alias_service')
@pytest.mark.parametrize('with_database', [True, False])
@pytest.mark.parametrize(
    'service_yaml, service_yaml_link, is_200',
    [
        pytest.param(
            'service_py3',
            f'{ARCADIA_URL}/arc/trunk/arcadia/ololo/backend-py3/'
            'services/my-new-service/service.yaml',
            True,
            id='arcadia_svn_url-backend_py3',
        ),
        pytest.param(
            'service_py3',
            f'{ARCADIA_URL}/arc_vcs/backend-py3/'
            'services/my-new-service/service.yaml',
            True,
            id='arcadia_arc_url-backend_py3',
        ),
        pytest.param(
            'uservice',
            f'{ARCADIA_URL}/arc/trunk/arcadia/lavka/kavka/uservices/'
            'services/my-new-service/service.yaml',
            True,
            id='arcadia_svn_url-uservices',
        ),
        pytest.param(
            'uservice',
            f'{ARCADIA_URL}/arc_vcs/uservices/'
            'services/my-new-service/service.yaml',
            True,
            id='arcadia_arc_url-uservices',
        ),
        pytest.param(
            'common',
            f'{ARCADIA_URL}/arc_vcs/folder/my-new-service/service.yaml',
            True,
            id='arcadia_arc_random_folder_url-common',
        ),
        pytest.param(
            'common',
            f'{ARCADIA_URL}/arc_vcs/my-new-service/service.yaml',
            True,
            id='arcadia_arc_non_folder_url-common',
        ),
        pytest.param(
            'common',
            (
                f'{ARCADIA_URL}/arc_vcs/services/'
                'services/my-new-service/service.yaml'
            ),
            True,
            id='arcadia_arc_twice_services_url-common',
        ),
        pytest.param(
            'common',
            f'{ARCADIA_URL}/arc/trunk/arcadia/folder/my-service/service.yaml',
            True,
            id='arcadia_svn_random_folder_url-common',
        ),
        pytest.param(
            'common',
            f'{ARCADIA_URL}/arc/trunk/arcadia/my-new-service/service.yaml',
            True,
            id='arcadia_svn_non_folder_url-common',
        ),
        pytest.param(
            'common',
            (
                f'{ARCADIA_URL}/arc/trunk/arcadia/services/services/'
                f'my-new-service/service.yaml'
            ),
            True,
            id='arcadia_svn_twice_services_url-common',
        ),
        pytest.param(
            'stq_service_without_one_unit',
            (
                f'{ARCADIA_URL}/arc/trunk/arcadia/services/services/'
                f'my-new-service/service.yaml'
            ),
            False,
            id='arcadia_svn_stq_with_alias_without_init',
        ),
        pytest.param(
            'service_frontend',
            (
                f'{ARCADIA_URL}/arc/trunk/arcadia/taxi/frontend/services/'
                f'hiring-partners-app/service.yaml'
            ),
            False,
            id='arcadia_frontend_yaml_with_wrong_name',
        ),
        pytest.param(
            'frontend',
            (
                f'{ARCADIA_URL}/arc/trunk/arcadia/taxi/frontend/services/'
                f'hiring-partners-app/service.yaml'
            ),
            True,
            id='arcadia_frontend_yaml_ok',
        ),
    ],
)
async def test_validate_and_apply(
        service_yaml,
        service_yaml_link,
        load,
        patch,
        login_mockserver,
        web_app_client,
        with_database,
        is_200,
        task_processor,
        load_yaml,
):
    @patch('arc_api.components.ArcClient.read_file')
    async def read_file(*args, **kwargs):
        try:
            yaml_data = load(f'{service_yaml}.yaml')
        except FileNotFoundError:
            raise arc_api.ArcClientBaseError()
        return arc_api.ReadFileResponse(header=None, content=yaml_data)

    login_mockserver()
    task_processor.load_recipe(
        load_yaml('recipes/WaitingToCreateServices.yaml')['data'],
    )
    request = {'service_yaml_link': service_yaml_link}
    if with_database:
        request['database'] = {
            'flavor': 's2.micro',
            'type': 'pgaas',
            'disk_size_gb': 40,
            'testing_disk_size_gb': 20,
        }

    response = await web_app_client.post(
        '/v1/requests/service_from_yaml/validate/',
        json=request,
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    data = await response.json()
    if is_200:
        assert response.status == 200, data

        response = await web_app_client.post(
            '/v1/requests/service_from_yaml/',
            json=data['data'],
            headers={'X-Yandex-Login': 'deoevgen'},
        )
        data = await response.json()
        assert response.status == 200, data
    else:
        assert response.status == 400, data
        if service_yaml == 'stq_service_without_one_unit':
            assert data['code'] == 'YAML_VALIDATION_ERROR'
        else:
            assert data['code'] == 'INVALID_NAME'


@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
async def test_409_request_service_from_yaml(
        web_app_client,
        patch,
        load,
        task_processor,
        load_yaml,
        mock_task_processor,
        mockserver,
):
    @patch('arc_api.components.ArcClient.read_file')
    async def read_file(*args, **kwargs):
        try:
            yaml_data = load('common.yaml')
        except FileNotFoundError:
            raise arc_api.ArcClientBaseError()
        return arc_api.ReadFileResponse(header=None, content=yaml_data)

    task_processor.load_recipe(
        load_yaml('recipes/WaitingToCreateServices.yaml')['data'],
    )

    @mock_task_processor('/v1/jobs/start/')
    async def _start_job(request):
        return mockserver.make_response(
            status=409,
            json={
                'code': 'code',
                'message': 'external_tp_message',
                'details': {
                    'job': {
                        'change_doc_id': 'change_doc_id',
                        'idempotency_token': 'idempotency_token',
                        'name': 'name',
                        'provider_name': 'provider_name',
                        'id': 2,
                    },
                },
            },
        )

    link = (
        f'{ARCADIA_URL}/arc/trunk/arcadia/services/services/'
        f'my-new-service/service.yaml'
    )
    handle = '/v1/requests/service_from_yaml/'
    body = {'service_yaml_link': link}

    response = await web_app_client.post(
        handle,
        json=body,
        headers={
            'X-Yandex-Login': 'deoevgen',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )
    content = await response.json()
    assert response.status == 400, content
    assert content == {
        'code': 'RACE_CONDITION',
        'message': 'Job already exists, extTP error: external_tp_message',
    }


@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.parametrize(
    'service_yaml, service_yaml_link, service_names',
    [
        pytest.param(
            'multi_alias',
            f'{ARCADIA_URL}/arc_vcs/folder/common-service/service.yaml',
            [
                'common-service',
                'common-service-critical',
                'common-service-eda',
            ],
            id='multi_alias',
        ),
    ],
)
async def test_main_alias_service_relation(
        web_context,
        service_yaml,
        service_yaml_link,
        service_names,
        load,
        patch,
        login_mockserver,
        web_app_client,
        task_processor,
        load_yaml,
):
    @patch('arc_api.components.ArcClient.read_file')
    async def read_file(*args, **kwargs):
        try:
            yaml_data = load(f'{service_yaml}.yaml')
        except FileNotFoundError:
            raise arc_api.ArcClientBaseError()
        return arc_api.ReadFileResponse(header=None, content=yaml_data)

    task_processor.load_recipe(
        load_yaml('recipes/WaitingToCreateServices.yaml')['data'],
    )

    login_mockserver()

    request = {'service_yaml_link': service_yaml_link}
    response = await web_app_client.post(
        '/v1/requests/service_from_yaml/',
        json=request,
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    content = await response.json()
    assert response.status == 200, content

    service_ids = []
    relation_type = related_services.ServiceRelationType.ALIAS_MAIN_SERVICE
    async with postgres.get_connection(web_context, transaction=False) as conn:
        related_services_table = (
            await web_context.service_manager.related_services.get_all(
                conn=conn,
            )
        )

        main_service = await web_context.service_manager.services.get_by_name(
            project_name='taxi',
            cluster_type=services_module.ClusterType.NANNY,
            name=service_names[0],
            conn=conn,
        )
        for service_name in service_names[1:]:
            service = await web_context.service_manager.services.get_by_name(
                project_name='taxi',
                cluster_type=services_module.ClusterType.NANNY,
                name=service_name,
                conn=conn,
            )
            service_ids.append(
                related_services.ServiceRelation(
                    service_id=service['id'],
                    related_service_id=main_service['id'],
                    relation_type=relation_type,
                ),
            )
    assert related_services_table == service_ids
