# pylint: disable=invalid-name
import json

import pytest

from clownductor.internal.db import db_types
from clownductor.internal.db import flavors


async def test_meta_database_400_with_empty_body(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    result = await web_app_client.post(
        f'/v1/requests/database/?project_id={project_id}', json={},
    )

    assert result.status == 400


@pytest.mark.config(
    CLOWNDUCTOR_BANNED_PROJECTS=[
        {'project_name': 'taxi', 'description_error': 'bad shared project'},
    ],
)
@pytest.mark.parametrize(
    'db_type, flavor, disk_size, expected_disk_size',
    [
        (db_types.DbType.Postgres, flavors.FlavorNames.s2_nano, 1, 10),
        (db_types.DbType.Mongo, flavors.FlavorNames.s2_nano, 20, 20),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_nano, 10, 16),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_nano, 20, 20),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_micro, 10, 24),
    ],
)
async def test_meta_database(
        web_app_client,
        add_project,
        login_mockserver,
        get_job_variables,
        db_type,
        flavor,
        disk_size,
        expected_disk_size,
):
    login_mockserver()
    project = await add_project('taxi-infra')
    project_id = project['id']

    result = await web_app_client.post(
        f'/v1/requests/database/',
        json={
            'project_id': project_id,
            'db_name': 'taxi_admin_data',
            'db_type': db_type.value,
            'flavor': flavor.value,
            'disk_size_gb': disk_size,
            'testing_disk_size_gb': disk_size,
            'needs_unstable': False,
            'wiki_path': 'https://wiki.yandex-team.ru/taxi/backend/architecture/taxi-admin-data/',  # noqa: E501 pylint: disable=C0301
            'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
            'db_version': '12',
        },
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200

    data = await result.json()
    job_vars = await get_job_variables(data['job_id'])
    variables = json.loads(job_vars['variables'])
    assert variables['disk_size_gb'] == expected_disk_size
    assert variables['testing_disk_size_gb'] == expected_disk_size


@pytest.mark.config(
    CLOWNDUCTOR_BANNED_PROJECTS=[
        {'project_name': 'taxi', 'description_error': 'bad shared project'},
    ],
)
@pytest.mark.parametrize(
    'db_type, flavor',
    [
        (db_types.DbType.Postgres, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Mongo, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_nano),
    ],
)
@pytest.mark.parametrize(
    'project_name, status', [('taxi', 400), ('taxi-infra', 200)],
)
async def test_meta_database_validation(
        web_app_client,
        add_project,
        login_mockserver,
        db_type,
        flavor,
        project_name,
        status,
):
    login_mockserver()
    project = await add_project(project_name)
    project_id = project['id']
    body = {
        'project_id': project_id,
        'db_name': 'taxi_admin_data',
        'db_type': db_type.value,
        'flavor': flavor.value,
        'disk_size_gb': 10,
        'testing_disk_size_gb': 10,
        'needs_unstable': False,
        'wiki_path': 'https://wiki.yandex-team.ru/taxi/backend/architecture/taxi-admin-data/',  # noqa: E501 pylint: disable=C0301
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'db_version': '12',
    }

    result = await web_app_client.post(
        f'/v1/requests/database/validate/',
        json=body,
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == status
    if status != 200:
        return

    result_json = await result.json()
    handler_data = result_json['data']
    meta = handler_data.pop('meta_data')
    assert meta == {'project_name': project_name}
    assert handler_data.get('db_version')
    assert handler_data == body


@pytest.mark.parametrize(
    'db_type, flavor',
    [
        (db_types.DbType.Postgres, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Mongo, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_nano),
    ],
)
@pytest.mark.parametrize('use_design_review', [True, False])
async def test_validate_and_apply(
        web_app_client,
        add_project,
        login_mockserver,
        use_design_review,
        db_type,
        flavor,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    body = {
        'project_id': project_id,
        'db_name': 'taxi_admin_data',
        'db_type': db_type.value,
        'flavor': flavor.value,
        'disk_size_gb': 10,
        'testing_disk_size_gb': 10,
        'needs_unstable': False,
        'wiki_path': (
            'https://wiki.yandex-team.ru/'
            'taxi/backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
    }
    if use_design_review:
        body['design_review_ticket'] = 'TAXIMEOW-1'

    result = await web_app_client.post(
        f'/v1/requests/database/validate/',
        json=body,
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    data = await result.json()

    result = await web_app_client.post(
        f'/v1/requests/database/',
        json=data['data'],
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200


@pytest.mark.config(
    CLOWNDUCTOR_MAP_PROJECTS_BY_QOUTA_PARAMS={
        '__default__': {'use_single_abc_on_db': True},
    },
)
@pytest.mark.parametrize(
    'abc_service, slug, response',
    [
        (
            'https://abc.yandex-team.ru/services/cargocargo-finance/',
            'cargocargo-finance',
            200,
        ),
        (
            ' https://abc.yandex-team.ru/services/cargocargo-finance/',
            'cargocargo-finance',
            200,
        ),
        (
            'https://abc.yandex-team.ru/services/cargocargo-finance/ ',
            'cargocargo-finance',
            200,
        ),
        (
            ' https://abc.yandex-team.ru/services/cargocargo-finance/ ',
            'cargocargo-finance',
            200,
        ),
        (
            'https://abc.yandex-team.ru/services/cargocargo-finance',
            'cargocargo-finance',
            200,
        ),
        (
            ' https://abc.yandex-team.ru/services/cargocargo-finance',
            'cargocargo-finance',
            200,
        ),
        (
            'https://abc.yandex-team.ru/services/cargocargo-finance ',
            'cargocargo-finance',
            200,
        ),
        (
            ' https://abc.yandex-team.ru/services/cargocargo-finance ',
            'cargocargo-finance',
            200,
        ),
        ('cargocargofinance', 'cargocargofinance', 200),
        (' cargocargofinance', 'cargocargofinance', 200),
        ('cargocargofinance ', 'cargocargofinance', 200),
        (' cargocargofinance ', 'cargocargofinance', 200),
        ('https://abc.yandex-team.ru/services/', '', 400),
        ('https://abc.yandex-team.ru/services//', '', 400),
        (
            'some-messhttps://abc.yandex-team.ru/services/cargo-finance/',
            '',
            404,
        ),
        (
            'https://abc.yandex-team.ru/services/cargofinance/some-mess/',
            '',
            400,
        ),
    ],
)
async def test_database_slug(
        web_app_client,
        add_project,
        login_mockserver,
        get_job_variables,
        get_service,
        abc_service,
        slug,
        response,
        mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    @mockserver.json_handler('/client-abc/v3/services/')
    def _abc_get_service(request):
        if not slug:
            return {'results': []}
        assert request.query['slug'] == slug
        return {'results': [{'id': 1}]}

    result = await web_app_client.post(
        f'/v1/requests/database/',
        json={
            'project_id': project_id,
            'db_name': 'taxi_admin_data',
            'db_type': db_types.DbType.Postgres.value,
            'flavor': flavors.FlavorNames.s2_nano.value,
            'disk_size_gb': 1,
            'testing_disk_size_gb': 1,
            'needs_unstable': False,
            'wiki_path': (
                'https://wiki.yandex-team.ru/taxi/'
                'backend/architecture/taxi-admin-data/'
            ),
            'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
            'abc_service': abc_service,
        },
        headers={'X-Yandex-Login': 'azhuchkov'},
    )

    assert result.status == response
    if response != 400:
        assert _abc_get_service.times_called == 1

    if response == 200:
        data = await result.json()
        job_vars = await get_job_variables(data['job_id'])
        variables = json.loads(job_vars['variables'])
        service = await get_service(variables['service_id'])
        assert service['abc_service'] == slug
