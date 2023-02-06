# pylint: disable=protected-access,unused-variable,invalid-name,too-many-lines
import itertools
import uuid

import aiohttp
import pytest

from taxi import settings
from taxi.clients import approvals
from taxi.scripts import db as scripts_db


@pytest.mark.config(
    CHECK_ORGANIZATION=True,
    SCRIPTS_FEATURES={'check_override_organization_by_config': True},
    SCRIPTS_SERVICE_APPROVE_PERMISSIONS={
        'organizations_overrides': [
            {
                'new_organization': 'taxi-override',
                'white_list': ['taxi_clownductor/'],
                'black_list': ['taxi_clownductor/fix_job_variables.py'],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'script_path, organization,status',
    [
        ('taxi_clownductor/example_1.py', 'taxi', 400),
        ('taxi_clownductor/example_1.py', 'taxi-override', 200),
        ('taxi_clownductor/fix_job_variables.py', 'taxi-override', 400),
        ('taxi_clownductor/fix_job_variables.py', 'taxi', 200),
    ],
)
async def test_approve_script_with_override_org(
        patch, scripts_client, script_path, organization, status,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.approve_draft')
    async def approve_draft_mock(*args, **kwargs):
        pass

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taxi/tools-py3'
                '/blob/8ff701b0a37760e8d314700244e4ec0e64b765f0/'
                f'{script_path}'
            ),
            'ticket': 'TPD-69',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [
                '1416614::{"owner_groups": ["svc_vopstaxi", "svc_edaops"]}',
            ],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'elrusso'},
    )
    assert response.status == 200
    _id = (await response.json())['id']

    response = await scripts_client.put(
        f'/{_id}/approval/',
        params={'organization': organization},
        headers={'X-Yandex-Login': 'elrusso'},
    )
    assert response.status == status


async def test_approve_twice(patch, scripts_client):
    approved = False

    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.approve_draft')
    async def approve_draft_mock(*args, **kwargs):
        nonlocal approved
        if approved:
            raise approvals.ApprovalsApiError(code=406, msg='already approved')
        approved = True

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']

    response = await scripts_client.put(
        f'/{_id}/approval/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200

    response = await scripts_client.put(
        f'/{_id}/approval/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 406


async def test_taximeter_script_check_error(patch, scripts_client):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def taximeter_check_script_mock(*args, **kwargs):
        raise aiohttp.ClientResponseError(None, (None,), status=406)

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taximeter/taxi-cloud-yandex/'
                'blob/2d23e811d261ff8cf1d6a01fb3975df1499d0454'
                '/src/Yandex.Taximeter.ScriptRunner/Scripts/TestScript.cs'
            ),
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 406


@pytest.mark.usefixtures('setup_many_scripts')
async def test_can_by_deleted(scripts_client, patch):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_drafts_mock(*args, **kwargs):
        return {
            'created_by': 'test-login',
            'id': 123,
            'description': 'aaaaa',
            'approvals': [],
            'status': 'applying',
            'run_manually': False,
        }

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['can_be_deleted']

    response = await scripts_client.post(
        '/scripts/test-can-by-deleted/mark-as-running/', json={'fqdn': 'test'},
    )
    assert response.status == 200

    response = await scripts_client.delete(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 403

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    result = await response.json()
    assert not result['can_be_deleted']


@pytest.mark.usefixtures('setup_many_scripts')
async def test_script_after_approved_before_start_running(
        scripts_client, patch,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_drafts_mock(*args, **kwargs):
        return {
            'created_by': 'test-login',
            'id': 123,
            'description': 'aaaaa',
            'approvals': [],
            'status': 'applying',
            'run_manually': False,
        }

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['can_be_deleted']

    response = await scripts_client.delete(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 404


@pytest.mark.usefixtures('setup_many_scripts')
async def test_scripts_statuses(scripts_client, patch):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_drafts_mock(*args, **kwargs):
        return {
            'created_by': 'test-login',
            'id': 123,
            'description': 'aaaaa',
            'approvals': [],
            'status': 'applying',
            'run_manually': False,
        }

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['status'] == 'execute_wait'

    response = await scripts_client.post(
        '/scripts/test-can-by-deleted/mark-as-running/', json={'fqdn': 'test'},
    )
    assert response.status == 200

    response = await scripts_client.get(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['status'] == 'running'


@pytest.mark.usefixtures('setup_many_scripts')
async def test_organizations_field(scripts_client, patch):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_drafts_mock(*args, **kwargs):
        return {
            'created_by': 'test-login',
            'id': 123,
            'description': 'aaaaa',
            'approvals': [],
            'status': 'applying',
            'run_manually': False,
        }

    response = await scripts_client.get(
        '/approved-test-id/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    data = await response.json()
    assert data['organization'] == ''

    response = await scripts_client.get(
        '/with-org-filed-id/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200
    data = await response.json()
    assert data['organization'] == 'test-org'


@pytest.mark.config(CHECK_ORGANIZATION=True)
async def test_check_organization(scripts_client, patch, db):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.approve_draft')
    async def approve_draft(*args, **kwargs):
        return

    script_url = (
        'https://github.yandex-team.ru/taxi/tools/blob/'
        '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
        'migrations/m4326_debugging_script.py'
    )
    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': script_url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    result = await response.json()
    script_id = result['id']

    script = await db.scripts.find_one(script_id)
    assert script['organization'] == 'taxi'

    response = await scripts_client.put(
        f'/{script_id}/approval/',
        headers={'X-Yandex-Login': 'd1mbas'},
        params={'organization': 'taximeter'},
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'status': 'error',
        'message': 'Passed organization dont equal to scripts organization',
        'code': 'invalid_organization',
    }

    response = await scripts_client.put(
        f'/{script_id}/approval/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'status': 'error',
        'code': 'invalid_organization',
        'message': 'Scripts organization is empty',
    }

    response = await scripts_client.put(
        f'/{script_id}/approval/',
        headers={'X-Yandex-Login': 'd1mbas'},
        params={'organization': 'taxi'},
    )
    assert response.status == 200


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize(
    'env,is_superuser,expected_status',
    [
        (settings.TESTING, True, 200),
        (settings.UNSTABLE, True, 200),
        (settings.DEVELOPMENT, True, 200),
        (settings.PRODUCTION, True, 200),
        (settings.PRODUCTION, False, 403),
    ],
)
async def test_add_approve_self_created_script(
        monkeypatch, scripts_client, patch, env, is_superuser, expected_status,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', env)

    @patch('taxi.clients.approvals.ApprovalsApiClient.approve_draft')
    async def approve_draft_mock(*args, **kwargs):
        # expects, that approval service still not implemented this check
        if not is_superuser:
            raise approvals.ApprovalsApiError(msg='Forbidden', code=403)

    response = await scripts_client.put(
        '/test-approve-self-created/approval/',
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == expected_status


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize(
    'env,is_superuser,expected_status',
    [
        (settings.TESTING, True, 200),
        (settings.UNSTABLE, True, 200),
        (settings.DEVELOPMENT, True, 200),
        (settings.PRODUCTION, True, 200),
        (settings.PRODUCTION, False, 403),
    ],
)
async def test_delete_approve_self_created_script(
        monkeypatch, scripts_client, patch, env, is_superuser, expected_status,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', env)

    @patch('taxi.clients.approvals.ApprovalsApiClient.delete_draft_approve')
    async def approve_draft_mock(*args, **kwargs):
        # expects, that approval service still not implemented this check
        if not is_superuser:
            raise approvals.ApprovalsApiError(msg='Forbidden', code=403)

    response = await scripts_client.delete(
        '/test-approve-self-created/approval/',
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == expected_status


async def test_organizations_endpoint(scripts_client):
    response = await scripts_client.get('/organizations/')
    orgs = (await response.json())['organizations']
    expected = [
        {'name': 'taxi'},
        {'name': 'taximeter'},
        {'name': 'taxi-dwh'},
        {'name': 'eda'},
        {'name': 'hiring_billing_yql_scripts'},
        {'name': 'eda_billing_yql_scripts'},
        {'name': 'lavka'},
    ]
    assert sorted(orgs, key=lambda x: x['name']) == sorted(
        expected, key=lambda x: x['name'],
    )


@pytest.mark.parametrize(
    'show_args_only',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SCRIPTS_SHOW_ARGS_ONLY_TYPES=True),
            id='show_args_only_types',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SCRIPTS_SHOW_ARGS_ONLY_TYPES=False),
            id='do_not_show_args_only_types',
        ),
    ],
)
async def test_get_execute_types(scripts_client, show_args_only):
    response = await scripts_client.get('/execute-types/')
    assert response.status == 200
    data = await response.json()
    data = sorted(data['types'], key=lambda x: x['name'])
    expected = [
        {'name': 'python'},
        {
            'name': 'psql',
            'explicit_service_name': True,
            'default_arguments': [
                '--psql-options=--echo-all',
                '--database-name=',
            ],
        },
        {'name': 'php'},
        {'name': 'yql'},
        {'name': 'mysql'},
        {'name': 'dmp-runner'},
        {
            'cgroups': ['eda_mysql_galera'],
            'name': 'galera',
            'default_arguments': ['--database-name=', '--version='],
        },
        {'name': 'nodejs', 'explicit_service_name': True},
    ]
    if show_args_only:
        expected.extend(
            [
                {
                    'name': 'eda-php-console',
                    'args_only': True,
                    'cgroups': [
                        'eda_core',
                        'eda_core-jobs',
                        'eda_scripts',
                        'eda_backend-service-vendor',
                        'eda_backend-service-vendor-jobs',
                    ],
                },
                {
                    'name': 'pgmigrate',
                    'args_only': True,
                    'cgroups': [],
                    'default_arguments': [
                        '--service_name=',
                        '--db_name=',
                        '--repository=',
                    ],
                },
                {
                    'name': 'nodejs-cli',
                    'args_only': True,
                    'cgroups': [],
                    'default_arguments': [
                        '--cwd=',
                        '--filename=',
                        '--payload=',
                    ],
                },
            ],
        )
    expected = sorted(expected, key=lambda x: x['name'])
    assert data == expected


@pytest.mark.parametrize(
    'exec_type_on_create,exec_type_in_db',
    [(None, 'python'), ('python', 'python'), ('psql', 'psql')],
)
async def test_exec_type_save_on_create(
        patch, db, scripts_client, exec_type_on_create, exec_type_in_db,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_draft_mock(*args, **kwargs):
        return {
            'created_by': 'd1mbas',
            'id': 1,
            'description': '',
            'approvals': [],
            'run_manually': False,
            'status': 'need_approvals',
        }

    script_url = (
        'https://github.yandex-team.ru/taxi/tools/blob/'
        '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
        'migrations/m4326_debugging_script.py'
    )
    post_data = {
        'url': script_url,
        'ticket': 'TAXIBACKEND-1',
        'python_path': '/usr/lib/yandex/taxi-import',
        'arguments': [],
        'comment': 'some comment',
        'request_id': '123',
    }
    if exec_type_on_create is not None:
        post_data['execute_type'] = exec_type_on_create

    response = await scripts_client.post(
        '/scripts/', json=post_data, headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']
    script = await scripts_db.find_one_by_id(db, 'scripts', _id)
    assert script.execute_type == exec_type_in_db

    response = await scripts_client.get(
        f'/{_id}/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    script = await response.json()
    assert script['execute_type'] == exec_type_in_db


async def test_all_exec_types_acceptable(patch, db, scripts_client):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_draft_mock(*args, **kwargs):
        return {
            'created_by': 'd1mbas',
            'id': 1,
            'description': '',
            'approvals': [],
            'run_manually': False,
            'status': 'need_approvals',
        }

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def cgroup_exists_mock(*args, **kwargs):
        return True

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def ngroup_exists_mock(*args, **kwargs):
        return True

    async def _test(exec_type, expected_exec_type, exec_settings):
        script_url = (
            'https://github.yandex-team.ru/taxi/tools/blob/'
            '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
            'migrations/m4326_debugging_script.py'
        )
        post_data = {
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': uuid.uuid4().hex,
        }
        if exec_settings.get('args_only'):
            post_data['cgroup'] = exec_settings.get(
                'cgroups', [{'name': 'test_group'}],
            )[0]['name']
            if not exec_settings.get('required_arguments'):
                post_data['arguments'].append('some-command')
        else:
            post_data['url'] = script_url
        for arg in exec_settings.get('required_arguments', []):
            post_data['arguments'].extend((f'--{arg}', 'taxi/repo'))
        if exec_type is not None:
            post_data['execute_type'] = exec_type
        response = await scripts_client.post(
            '/scripts/', json=post_data, headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == 200, await response.text()
        _id = (await response.json())['id']
        script = await scripts_db.find_one_by_id(db, 'scripts', _id)
        assert script.execute_type == expected_exec_type

        response = await scripts_client.get(
            f'/{_id}/', headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == 200
        script = await response.json()
        assert script['execute_type'] == expected_exec_type

    await _test(None, 'python', {})
    executable_schemas = scripts_client.app.executable_schemas['__default__']
    for _type, _settings in executable_schemas.items():
        await _test(_type, _type, _settings)


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize(
    'search_param,expected_statuses,expected_count',
    [
        ('approved', {scripts_db.ScriptStatus.APPROVED}, 2),
        ('running', {scripts_db.ScriptStatus.RUNNING}, 1),
        ('execute_wait', {scripts_db.ScriptStatus.EXECUTE_WAIT}, 1),
        (
            'approved,running',
            {
                scripts_db.ScriptStatus.APPROVED,
                scripts_db.ScriptStatus.RUNNING,
            },
            3,
        ),
        (
            'running,execute_wait',
            {
                scripts_db.ScriptStatus.RUNNING,
                scripts_db.ScriptStatus.EXECUTE_WAIT,
            },
            2,
        ),
        (
            'approved,execute_wait',
            {
                scripts_db.ScriptStatus.APPROVED,
                scripts_db.ScriptStatus.EXECUTE_WAIT,
            },
            3,
        ),
        (
            'approved,running,execute_wait',
            {
                scripts_db.ScriptStatus.APPROVED,
                scripts_db.ScriptStatus.EXECUTE_WAIT,
                scripts_db.ScriptStatus.RUNNING,
            },
            4,
        ),
        (
            '',
            {
                scripts_db.ScriptStatus.NEED_APPROVAL,
                scripts_db.ScriptStatus.APPROVED,
                scripts_db.ScriptStatus.EXECUTE_WAIT,
                scripts_db.ScriptStatus.RUNNING,
            },
            5,
        ),
    ],
)
@pytest.mark.config(USE_APPROVALS=True)
async def test_new_waiting_statuses(
        patch, scripts_client, search_param, expected_statuses, expected_count,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra):
        approvals_data = [
            {
                'change_doc_id': (
                    'scripts_' 'test-filter-by-run-status-need-approvals'
                ),
                'created_by': 'd1mbas',
                'id': 3,
                'description': '',
                'approvals': [],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.NEED_APPROVAL,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-run-status-approved',
                'created_by': 'd1mbas',
                'id': 3,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPROVED,
            },
            {
                'change_doc_id': (
                    'scripts_test-filter-by-run-status-approved-manual'
                ),
                'created_by': 'd1mbas',
                'id': 3,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': True,
                'status': scripts_db.ScriptStatus.APPROVED,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-run-status-running',
                'created_by': 'd1mbas',
                'id': 1,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': (
                    'scripts_' 'test-filter-by-run-status-not-running'
                ),
                'created_by': 'd1mbas',
                'id': 2,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
        ]

        if 'statuses' in data:
            return [
                x for x in approvals_data if x['status'] in data['statuses']
            ]
        return approvals_data

    response = await scripts_client.get(
        '/scripts/',
        params={'status': search_param},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _data = await response.json()
    _data = _data['items']
    assert {x['status'] for x in _data} == expected_statuses
    assert len(_data) == expected_count


def _make_tests_params():
    skip_param_variants = [(x, f'skip_{x}') for x in [None, 0, 10, 10 ** 3]]
    limit_param_variants = [(x, f'limit_{x}') for x in [None, 0, 50, 100]]
    for skip_param, limit_param in itertools.product(
            skip_param_variants, limit_param_variants,
    ):
        yield pytest.param(
            skip_param[0],
            limit_param[0],
            id=f'{skip_param[1]}-{limit_param[1]}',
        )


@pytest.mark.usefixtures('setup_lots_random_scripts')
@pytest.mark.parametrize(
    'params',
    [
        {},
        {'organizations': 'taxi'},
        {'organizations': 'taxi,taximeter'},
        {'execute_type': 'python'},
        {'execute_type': 'psql'},
    ],
)
@pytest.mark.parametrize('skip_param,limit_param', _make_tests_params())
async def test_lots_of_scripts(
        patch, scripts_client, params, skip_param, limit_param,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra):
        return []

    if skip_param is not None:
        params['skip'] = skip_param
    if limit_param is not None:
        params['limit'] = limit_param
    response = await scripts_client.get(
        '/scripts/', headers={'X-Yandex-Login': 'd1mbas'}, params=params,
    )
    assert response.status == 200


@pytest.mark.usefixtures('setup_many_scripts')
async def test_delete_script(patch, scripts_client, find_script):
    @patch('taxi.clients.approvals.ApprovalsApiClient._request')
    async def _request(url, method=None, **kwargs):
        if method is None or method == 'GET':
            return {'id': 123, 'change_doc_id': 'scripts_test-can-by-deleted'}

    response = await scripts_client.delete(
        '/test-can-by-deleted/', headers={'X-Yandex-Login': 'test-login'},
    )
    assert response.status == 200, await response.json()
    assert not await find_script('test-can-by-deleted')

    assert len(_request.calls) == 2
