import json

import pytest

from clownductor.internal.db import db_types
from clownductor.internal.db import flavors
from clownductor.internal.presets import presets

CREATE_NANNY_BRANCH_URL = '/v2/create_nanny_branch/'
CREATE_NANNY_BRANCH_VALIDATE_URL = '/v2/create_nanny_branch/validate/'
CREATE_TANK_BRANCH_URL = '/v1/create_tank_branch/'
CREATE_TANK_BRANCH_VALIDATE_URL = '/v1/create_tank_branch/validate/'
CREATE_DEV_BRANCH_URL = '/v1/create_dev_branch/'
CREATE_DEV_BRANCH_VALIDATE_URL = '/v1/create_dev_branch/validate/'

CREATE_POSTGRES_BRANCH_URL = '/v2/create_postgres_branch/'
CREATE_POSTGRES_BRANCH_VALIDATE_URL = '/v2/create_postgres_branch/validate/'

CREATE_DB_BRANCH_URL = '/v2/create_db_branch/'
CREATE_DB_BRANCH_VALIDATE_URL = '/v2/create_db_branch/validate/'

NEW_BRANCH_ID = 6

NANNY_DEFAULT_BODY = {
    'name': 'custom_branch',
    'env': 'testing',
    'description': 'test_branch',
    'preset': 'x2nano',
    'disk_profile': 'default',
}
NANNY_DEFAULT_PARAMS = {'service_id': 1}

POSTGRES_DEFAULT_BODY = {
    'name': 'custom_branch',
    'env': 'testing',
    'description': 'test_branch',
    'direct_link': 'custom_branch_link',
    'flavor': 's2.nano',
    'disk_size': 10,
}
POSTGRES_DEFAULT_PARAMS = {'service_id': 3}

DEFAULT_HEADERS = {'X-Yandex-Login': 'karachevda'}
CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS = {
    'components': ['duty'],
    'description_template': {
        'create_sec_branch': (
            'В этом тикете робот будет описывать прогресс создания нового '
            'окружения.\nПараметры окружения:\n{params}'
        ),
    },
    'summary_template': {
        'create_sec_branch': (
            'Second RTC-database: {project_name}-{service_name} '
            'environment: {env}'
        ),
    },
}
CLOWNDUCTOR_AVAILABLE_DATACENTERS = {
    'projects': [{'datacenters': ['vla', 'sas'], 'name': '__default__'}],
}
EXPECTED_NANNY_JOB = {
    'allocation_abc': 'taxiquotaypdefault',
    'branch': 'custom_branch',
    'branch_id': NEW_BRANCH_ID,
    'comment': 'Initial release',
    'cpu': 1000,
    'description': 'test_branch',
    'env': 'testing',
    'instances': [1, 1],
    'is_uservices': False,
    'mem': 4096,
    'network': '_taxitestnets_',
    'new_service_ticket': None,
    'owner_groups': ['meow'],
    'owner_logins': ['project_login_11'],
    'project': 'test_project',
    'regions': ['vla', 'man'],
    'root_size': 10240,
    'network_bandwidth_guarantee_mb_per_sec': 8388608,
    'root_bandwidth_guarantee_mb_per_sec': 2,
    'root_bandwidth_limit_mb_per_sec': 4,
    'root_storage_class': 'hdd',
    'service': 'test-service',
    'service_abc': 'taxiquotaypdefault',
    'fqdn_suffix': None,
    'volumes': [
        {
            'path': '/cores',
            'size': 10240,
            'type': 'hdd',
            'bandwidth_guarantee_mb_per_sec': 1,
            'bandwidth_limit_mb_per_sec': 2,
        },
        {
            'path': '/logs',
            'size': 50000,
            'type': 'hdd',
            'bandwidth_guarantee_mb_per_sec': 1,
            'bandwidth_limit_mb_per_sec': 2,
        },
        {
            'path': '/var/cache/yandex',
            'size': 2048,
            'type': 'hdd',
            'bandwidth_guarantee_mb_per_sec': 1,
            'bandwidth_limit_mb_per_sec': 2,
        },
    ],
    'work_dir': 256,
}

EXPECTED_FULL_NANNY_JOB = {
    'branch_name': 'custom_branch',
    'description': 'test_branch',
    'env': 'testing',
    'is_uservices': False,
    'needs_balancers': False,
    'nested': False,
    'branch_params': {
        'cpu': 1000,
        'ram': 4096,
        'root_size': 10240,
        'network': '_taxitestnets_',
        'instances': [1, 1],
        'regions': ['vla', 'man'],
        'root_bandwidth_guarantee_mb_per_sec': 2,
        'root_bandwidth_limit_mb_per_sec': 4,
        'work_dir': 256,
        'root_storage_class': 'hdd',
        'network_bandwidth_guarantee_mb_per_sec': 8388608,
        'volumes': [
            {
                'path': '/cores',
                'size': 10240,
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 1,
                'bandwidth_limit_mb_per_sec': 2,
            },
            {
                'path': '/logs',
                'size': 50000,
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 1,
                'bandwidth_limit_mb_per_sec': 2,
            },
            {
                'path': '/var/cache/yandex',
                'size': 2048,
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 1,
                'bandwidth_limit_mb_per_sec': 2,
            },
        ],
    },
    'branch_id': NEW_BRANCH_ID,
    'project_id': 1,
    'fqdn_suffix': None,
    'service_id': 1,
    'st_ticket': None,
    'user': 'automation',
    'create_unstable_entrypoint': False,
    'protocol': 'http',
    'pre_deploy_job_id': None,
}


@pytest.fixture
def _check_job(get_job, get_job_variables):
    async def _wrapper(job_id, name, expected_variables):
        job = await get_job(job_id)
        assert job[0]['job']['name'] == name
        variables = await get_job_variables(job_id)
        assert json.loads(variables['variables']) == expected_variables

    return _wrapper


@pytest.fixture
def _nanny_post(web_app_client):
    async def _wrapper(preset=None):
        url = CREATE_NANNY_BRANCH_URL
        body = NANNY_DEFAULT_BODY

        if preset is not None:
            body['preset'] = preset
        response = await web_app_client.post(
            url,
            json=body,
            params=NANNY_DEFAULT_PARAMS,
            headers=DEFAULT_HEADERS,
        )
        return response

    return _wrapper


@pytest.mark.features_on(
    'use_network_guarantee_config_create_branch', 'disk_profiles',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_full_nanny_branch(
        _nanny_post, _check_job, mock_random_regions,
):
    response = await _nanny_post()
    assert response.status == 200
    data = await response.json()
    assert data == {'branch': {'id': NEW_BRANCH_ID, 'job_id': 1}}
    await _check_job(1, 'CreateFullNannyBranch', EXPECTED_FULL_NANNY_JOB)
    assert len(mock_random_regions.calls) == 1


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'disk_profiles': True,
        'nanny_branch_draft_ticket': True,
    },
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_nanny_branch_validate(web_app_client, load_json):
    response = await web_app_client.post(
        CREATE_NANNY_BRANCH_VALIDATE_URL,
        json=NANNY_DEFAULT_BODY,
        params=NANNY_DEFAULT_PARAMS,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    data = await response.json()
    expected = load_json('expected_response_nanny_validate.json')
    assert data == expected


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'disk_profiles': True})
@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'status, code, body_override, service_id',
    [
        (404, 'SERVICE_NOT_FOUND', {}, 40),
        (404, 'DISK_PROFILE_NOT_FOUND', {'disk_profile': 'not-found'}, 1),
        (400, 'WRONG_SERVICE_TYPE', {}, 2),
        (409, 'BRANCH_ALREADY_EXISTS', {'name': 'testing_branch'}, 1),
        (
            400,
            'REQUEST_VALIDATION_ERROR',
            {'name': 'tcustom', 'env': 'stable'},
            1,
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_nanny_branch_errors(
        web_app_client, is_validate, status, code, body_override, service_id,
):
    await _test_branch_create_errors(
        web_app_client,
        is_validate,
        status,
        code,
        body_override,
        service_id,
        is_nanny=True,
    )


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_postgres_branch(web_app_client):
    response = await web_app_client.post(
        CREATE_POSTGRES_BRANCH_URL,
        json=POSTGRES_DEFAULT_BODY,
        params=POSTGRES_DEFAULT_PARAMS,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data == {'branch': {'id': NEW_BRANCH_ID}}


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'pg_branch_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_postgres_branch_validate(web_app_client, load_json):
    response = await web_app_client.post(
        CREATE_POSTGRES_BRANCH_VALIDATE_URL,
        json=POSTGRES_DEFAULT_BODY,
        params=POSTGRES_DEFAULT_PARAMS,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    data = await response.json()
    expected = load_json('expected_response_pg_validate.json')
    assert data == expected


@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'status, code, body_override, service_id',
    [
        (404, 'SERVICE_NOT_FOUND', {}, 40),
        (400, 'FLAVOR_ERROR', {'flavor': 'meow'}, 3),
        (400, 'WRONG_SERVICE_TYPE', {}, 2),
        (409, 'BRANCH_ALREADY_EXISTS', {'name': 'db-branch'}, 3),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_postgres_branch_errors(
        web_app_client, is_validate, status, code, body_override, service_id,
):
    await _test_branch_create_errors(
        web_app_client,
        is_validate,
        status,
        code,
        body_override,
        service_id,
        is_nanny=False,
    )


@pytest.mark.parametrize(
    'db_type, service_id, flavor',
    [
        (db_types.DbType.Postgres, 3, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Mongo, 4, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Redis, 5, flavors.FlavorNames.m2_nano),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_db_branch(web_app_client, db_type, service_id, flavor):
    body = POSTGRES_DEFAULT_BODY.copy()
    body.update({'db_type': db_type.value})
    body.update({'flavor': flavor.value})
    response = await web_app_client.post(
        CREATE_DB_BRANCH_URL,
        json=body,
        params=_make_request_params(service_id),
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data == {'branch': {'id': NEW_BRANCH_ID}}


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'db_branch_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.parametrize(
    'db_type, service_id, flavor, db_version',
    [
        (db_types.DbType.Postgres, 3, flavors.FlavorNames.s2_nano, '14'),
        (db_types.DbType.Mongo, 4, flavors.FlavorNames.s2_nano, '4.4'),
        (db_types.DbType.Redis, 5, flavors.FlavorNames.m2_nano, '6.0'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_db_branch_validate(
        web_app_client, load_json, db_type, service_id, flavor, db_version,
):
    body = POSTGRES_DEFAULT_BODY.copy()
    body.update({'db_type': db_type.value})
    body.update({'flavor': flavor.value})
    body.update({'db_version': db_version})
    response = await web_app_client.post(
        CREATE_DB_BRANCH_VALIDATE_URL,
        json=body,
        params=_make_request_params(service_id),
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    data = await response.json()
    filename = f'expected_response_{db_type.value}_validate.json'
    expected = load_json(filename)
    assert data == expected


@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'status, code, body_override, service_id',
    [
        (404, 'SERVICE_NOT_FOUND', {}, 40),
        (400, 'FLAVOR_ERROR', {'flavor': 'meow'}, None),
        (400, 'WRONG_SERVICE_TYPE', {}, 2),
        (409, 'BRANCH_ALREADY_EXISTS', {'name': 'db-branch'}, None),
    ],
)
@pytest.mark.parametrize(
    'db_type, service_id_override, flavor',
    [
        (db_types.DbType.Postgres, 3, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Mongo, 4, flavors.FlavorNames.s2_nano),
        (db_types.DbType.Redis, 5, flavors.FlavorNames.m2_nano),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_db_branch_errors(
        web_app_client,
        is_validate,
        status,
        code,
        body_override,
        service_id,
        db_type,
        service_id_override,
        flavor,
):
    await _test_branch_create_errors(
        web_app_client,
        is_validate,
        status,
        code,
        body_override,
        service_id or service_id_override,
        is_nanny=False,
        db_type=db_type,
        flavor=flavor,
    )


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize('preset', presets.PRESETS.keys())
async def test_branch_presets(_nanny_post, preset):
    response = await _nanny_post(preset)
    assert response.status == 200, await response.text()


async def _test_branch_create_errors(
        web_app_client,
        is_validate,
        status,
        code,
        body_override,
        service_id,
        is_nanny,
        db_type=None,
        flavor=None,
):
    body, url = _define_branch_errors_args(
        is_nanny, is_validate, db_type, flavor,
    )
    body.update(body_override)
    response = await web_app_client.post(
        url,
        json=body,
        params=_make_request_params(service_id),
        headers=DEFAULT_HEADERS,
    )
    data = await response.json()
    assert response.status == status, data
    assert data['code'] == code


def _define_branch_errors_args(is_nanny, is_validate, db_type, flavor):
    if is_nanny:
        body = NANNY_DEFAULT_BODY.copy()
        url = CREATE_NANNY_BRANCH_VALIDATE_URL
        if not is_validate:
            url = CREATE_NANNY_BRANCH_URL
    elif db_type is None:
        body = POSTGRES_DEFAULT_BODY.copy()
        url = CREATE_POSTGRES_BRANCH_VALIDATE_URL
        if not is_validate:
            url = CREATE_POSTGRES_BRANCH_URL
    else:
        body = POSTGRES_DEFAULT_BODY.copy()
        body.update({'db_type': db_type.value})
        body.update({'flavor': flavor.value})
        url = (
            CREATE_DB_BRANCH_VALIDATE_URL
            if is_validate
            else CREATE_DB_BRANCH_URL
        )
    return body, url


def _make_request_params(service_id: int):
    return {'service_id': service_id}


@pytest.mark.config(
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.parametrize(
    'request_body, expected_validate_file, expected_file',
    [
        (
            {
                'allocate_request': {
                    'branch_name': 'stable_branch',
                    'regions': ['man', 'vla'],
                },
            },
            'expected_response_tank_validate.json',
            'expected_tank_create.json',
        ),
        (
            {
                'allocate_request': {
                    'branch_name': 'stable_branch',
                    'cpu': 2000,
                    'volumes': [
                        {
                            'path': '/cores',
                            'size': 1234,
                            'type': 'ssd',
                            'bandwidth_guarantee_mb_per_sec': 7,
                            'bandwidth_limit_mb_per_sec': 7,
                        },
                    ],
                    'regions': ['man', 'vla'],
                },
            },
            'expected_response_tank_validate_overrides.json',
            'expected_tank_create_overrides.json',
        ),
    ],
)
@pytest.mark.features_on(
    'use_network_guarantee_config_create_branch',
    'disk_profiles',
    'nanny_branch_draft_ticket',
)
@pytest.mark.parametrize('validate', [True, False])
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_tank_branch(
        web_app_client,
        load_json,
        request_body,
        validate,
        expected_validate_file,
        expected_file,
        _check_job,
):
    params = {'service_id': 1}
    url = CREATE_TANK_BRANCH_URL
    if validate:
        url = CREATE_TANK_BRANCH_VALIDATE_URL
    response = await web_app_client.post(
        url, json=request_body, params=params, headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    data = await response.json()
    if validate:
        expected = load_json(expected_validate_file)
        assert data == expected
    else:
        expected = load_json(expected_file)
        assert data == expected['response']
        expected['job']['pre_deploy_job_id'] = None
        await _check_job(1, 'CreateFullNannyBranch', expected['job'])


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'disk_profiles': True,
        'nanny_branch_draft_ticket': True,
    },
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.parametrize(
    'request_body, expected_code, status',
    [
        (
            {
                'allocate_request': {
                    'cpu': 2000,
                    'ram': 1234,
                    'regions': ['man', 'vla'],
                },
            },
            'BAD_PARAMETERS',
            400,
        ),
    ],
)
@pytest.mark.parametrize('validate', [True, False])
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_tank_branch_errors(
        web_app_client, request_body, validate, expected_code, status,
):
    params = {'service_id': 1}
    url = CREATE_TANK_BRANCH_URL
    if validate:
        url = CREATE_TANK_BRANCH_VALIDATE_URL
    response = await web_app_client.post(
        url, json=request_body, params=params, headers=DEFAULT_HEADERS,
    )
    assert response.status == status
    data = await response.json()
    assert data['code'] == expected_code


@pytest.mark.config(
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
)
@pytest.mark.parametrize(
    'request_body, expected_validate_file, expected_file',
    [
        (
            {
                'allocate_request': {
                    'branch_name': 'stable_branch',
                    'regions': ['man', 'vla'],
                },
                'env': 'unstable',
            },
            'expected_response_dev_validate.json',
            'expected_dev_create.json',
        ),
        (
            {
                'allocate_request': {
                    'branch_name': 'stable_branch',
                    'regions': ['man', 'vla'],
                },
                'env': 'unstable',
                'fqdn_suffix': 'lavka.dev.yandex.ru',
            },
            'expected_response_dev_validate_with_fqdn.json',
            'expected_dev_create_with_fqdn.json',
        ),
        (
            {
                'allocate_request': {
                    'branch_name': 'stable_branch',
                    'cpu': 2000,
                    'volumes': [
                        {
                            'path': '/cores',
                            'size': 1234,
                            'type': 'ssd',
                            'bandwidth_guarantee_mb_per_sec': 7,
                            'bandwidth_limit_mb_per_sec': 7,
                        },
                    ],
                    'regions': ['man', 'vla'],
                },
                'env': 'unstable',
            },
            'expected_response_dev_validate_overrides.json',
            'expected_dev_create_overrides.json',
        ),
    ],
)
@pytest.mark.parametrize('validate', [True, False])
@pytest.mark.features_on(
    'disk_profiles',
    'nanny_branch_draft_ticket',
    'allow_auto_unstable_creation',
    'use_network_guarantee_config_create_branch',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_dev_branch(
        web_app_client,
        load_json,
        request_body,
        validate,
        expected_validate_file,
        expected_file,
        _check_job,
):
    params = {'service_id': 1}
    url = CREATE_DEV_BRANCH_URL
    headers = dict(
        DEFAULT_HEADERS, **{'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    if validate:
        url = CREATE_DEV_BRANCH_VALIDATE_URL
    response = await web_app_client.post(
        url, json=request_body, params=params, headers=headers,
    )
    assert response.status == 200
    data = await response.json()
    if validate:
        expected = load_json(expected_validate_file)
        assert data == expected
    else:
        expected = load_json(expected_file)
        assert data == expected['response']
        expected['job']['pre_deploy_job_id'] = None
        await _check_job(1, 'CreateFullNannyBranch', expected['job'])


@pytest.mark.config(
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS=CLOWNDUCTOR_AVAILABLE_DATACENTERS,
    CLOWNDUCTOR_DEPLOY_TOKENS={
        '__default__': '',
        'test_project': {'__default__': 'lavka_token'},
    },
)
@pytest.mark.parametrize(
    'request_body, expected_code, status',
    [
        (
            {
                'allocate_request': {
                    'cpu': 2000,
                    'ram': 1234,
                    'regions': ['man', 'vla'],
                    'env': 'unstable',
                },
                'env': 'unstable',
            },
            'BAD_PARAMETERS',
            400,
        ),
    ],
)
@pytest.mark.parametrize('validate', [True, False])
@pytest.mark.parametrize(
    'token', ['valid_teamcity_token', 'lavka_special_token'],
)
@pytest.mark.features_on(
    'disk_profiles',
    'nanny_branch_draft_ticket',
    'allow_auto_unstable_creation',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_dev_branch_errors(
        web_app_client, request_body, validate, expected_code, status, token,
):
    headers = dict(DEFAULT_HEADERS, **{'X-YaTaxi-Api-Key': token})
    params = {'service_id': 1}
    url = CREATE_DEV_BRANCH_URL
    if validate:
        url = CREATE_DEV_BRANCH_VALIDATE_URL
    response = await web_app_client.post(
        url, json=request_body, params=params, headers=headers,
    )
    assert response.status == status
    data = await response.json()
    assert data['code'] == expected_code


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize(
    'preset', ['x2pico', 'x2nano', 'x2micro', 'x3pico', 'x3nano', 'x3micro'],
)
async def test_draft_on_create_branch(web_app_client, preset):
    response = await web_app_client.post(
        CREATE_NANNY_BRANCH_VALIDATE_URL,
        json={
            'name': 'test-branch',
            'env': 'unstable',
            'preset': preset,
            'disk_profile': 'default',
        },
        params={'service_id': 1},
        headers={'X-Yandex-Login': 'd1masb'},
    )
    assert response.status == 200, await response.text()

    response = await web_app_client.post(
        CREATE_NANNY_BRANCH_URL,
        json=(await response.json())['data'],
        params={'service_id': 1},
        headers={'X-Yandex-Login': 'd1masb'},
    )
    assert response.status == 200, await response.text()
