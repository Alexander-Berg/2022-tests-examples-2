# pylint: disable=unused-variable,protected-access,too-many-locals
import os
import tempfile

import pytest

from taxi.clients import scripts
from taxi.scripts import db as scripts_db
from taxi.scripts import os as scripts_os

from scripts import scripts_runner

URL_TMPL = (
    'https://github.yandex-team.ru/taxi/tools-py3/blob/'
    'master/{}/m4326_debugging_script.py'
)


@pytest.fixture
def _tmp_dirs(monkeypatch):
    with tempfile.TemporaryDirectory() as working_area:
        monkeypatch.setattr(
            'taxi.scripts.settings.WORKING_AREA_DIR', working_area,
        )
        yield


@pytest.mark.usefixtures('_tmp_dirs')
@pytest.mark.parametrize(
    'create_data,project_name,exec_type,local_rel_path,args_only',
    [
        (
            {
                'url': (
                    'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                    '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                    'migrations/sql/00_init.sql'
                ),
                'ticket': 'TAXIBACKEND-1',
                'python_path': '/usr/lib/yandex/taxi-import',
                'arguments': [
                    '--service-name=test',
                    '--psql-options="--echo-all -A"',
                ],
                'comment': 'some comment',
                'request_id': '123',
                'execute_type': 'psql',
            },
            'migrations',
            'psql',
            'migrations/sql/00_init.sql',
            False,
        ),
        (
            {
                'url': (
                    'https://bb.yandex-team.ru/projects/EDA/repos/'
                    'infrastructure_admin_scripts/browse/eda_scripts/'
                    'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e'
                ),
                'ticket': 'TAXIBACKEND-1',
                'python_path': '/usr/lib/yandex/taxi-import',
                'arguments': [],
                'comment': 'some comment',
                'request_id': '1234',
                'execute_type': 'python',
                'expiration_age': 1,
            },
            'eda_scripts',
            'python',
            'eda_scripts/test.py',
            False,
        ),
        (
            {
                'ticket': 'TAXIBACKEND-1',
                'python_path': '/usr/lib/yandex/taxi-import',
                'arguments': ['help'],
                'comment': 'some comment',
                'request_id': '12345',
                'execute_type': 'eda-php-console',
                'cgroup': 'eda_scripts',
            },
            'eda_scripts',
            'eda-php-console',
            'eda-php-console',
            True,
        ),
    ],
)
@pytest.mark.config(USE_APPROVALS=True)
async def test_run_psql_script(
        patch,
        db,
        scripts_client,
        create_data,
        project_name,
        exec_type,
        local_rel_path,
        args_only,
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

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(*args, **kwargs):
        return [
            {
                'change_doc_id': f'scripts_{_id}',
                'created_by': 'd1mbas',
                'id': 1,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
        ]

    @patch('taxi.clients.approvals.ApprovalsApiClient.finish_draft')
    async def finish_draft_mock(*args, **kwargs):
        pass

    @patch('scripts.lib.vcs_utils.github_utils._check_py3_project')
    async def _check_py3_project(*args, **kwargs):
        pass

    @patch('taxi.scripts.async_os.run_script_command')
    async def run_script_command_mock(script, log_extra=None):
        assert script.id == _id

        version_control_info = (
            script.url and scripts_os.utils.parse_script_url(script.url)
        )

        args = scripts_os.get_cmd(script)
        cwd = scripts_os.get_checkouted_repo_root(script, version_control_info)

        assert args[0] == 'python3.7'
        assert args[2:] == [x.encode() for x in script.arguments]
        return 0, os.path.join(cwd, script.local_relative_path)

    @patch('taxi.clients.github.GithubClient.get_archive')
    async def get_archive_mock(*args, **kwargs):
        return b''

    @patch('taxi.clients.scripts.ScriptsClient.get_next_script')
    async def get_next_script_mock(*args, **kwargs):
        _response = await scripts_client.post(
            '/scripts/next-script/', json={'service_name': project_name},
        )
        data = await _response.json()
        assert _response.status == 200, data
        return data

    @patch('taxi.clients.scripts.ScriptsClient.download_script')
    async def download_script_mock(script, *args, **kwargs):
        if args_only:
            assert False, 'nothing to download for args_only scripts'

        src_dir_path = scripts_os.get_src_dir_path(script)
        os.mkdir(src_dir_path)
        os.makedirs(
            os.path.join(
                src_dir_path,
                'taxi-tools-py3',
                os.path.dirname(local_rel_path),
            ),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(
                src_dir_path,
                'eda-infrastructure_admin_scripts',
                os.path.dirname(local_rel_path),
            ),
            exist_ok=True,
        )

    @patch('taxi.clients.scripts.ScriptsClient.download_extra_runner')
    async def download_extra_runner_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.scripts.ScriptsClient.mark_as_running')
    async def mark_as_running_mock(*args, **kwargs):
        _response = await scripts_client.post(
            f'/scripts/{_id}/mark-as-running/', json={'fqdn': 'test'},
        )
        assert _response.status == 200
        return _response.status

    @patch('taxi.clients.scripts.ScriptsClient.mark_as_succeeded')
    async def mark_as_succeeded_mock(*args, **kwargs):
        _response = await scripts_client.post(
            f'/scripts/{_id}/mark-as-succeeded/', json={'code': 0},
        )
        assert _response.status == 200

    @patch('taxi.clients.scripts.ScriptsClient.upload_logs')
    async def upload_logs_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.scripts.ScriptsClient.upload_script')
    async def upload_script_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.scripts.ScriptsClient.finish_upload')
    async def finish_upload_mock(script, *args, **kwargs):
        return await scripts_client.post(f'/scripts/{_id}/logs/finish-upload/')

    response = await scripts_client.post(
        '/scripts/', json=create_data, headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']

    script = await scripts_db.Script.get_script(db, _id)
    assert script.project == project_name
    assert script.execute_type == exec_type
    assert script.local_relative_path == local_rel_path

    await scripts_runner._do_stuff(
        client=scripts.ScriptsClient('', None), service_name=project_name,
    )
    assert finish_upload_mock.calls


@pytest.mark.parametrize(
    'create_params, get_params, script_additions',
    [
        ({}, {'service_name': 'fake-project'}, {}),
        (
            {
                'for_prestable': True,
                'url': URL_TMPL.format('taxi_conductor_service'),
            },
            {'service_name': 'taxi_conductor_service'},
            {},
        ),
        (
            {
                'for_prestable': True,
                'url': URL_TMPL.format('taxi_clownductor-service'),
            },
            {'service_name': 'taxi_clownductor-service_stable'},
            {},
        ),
        (
            {
                'for_prestable': True,
                'url': URL_TMPL.format('taxi_conductor_service'),
            },
            {'service_name': 'taxi_prestable_conductor_service'},
            {
                'arguments': [],
                'executable': 'python3.7',
                'execute_type': 'python',
                'expiration_age': 172800,
                'features': [
                    'repo_user_check',
                    'github_check_py3_service_name',
                    'allowed_repo_check',
                    'user_organization_check',
                    'check_bitbucket_rootdir',
                ],
                'local_relative_path': (
                    'taxi_conductor_service/m4326_debugging_script.py'
                ),
                'python_path': '',
                'url': (
                    'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                    'taxi_conductor_service/m4326_debugging_script.py'
                ),
            },
        ),
        (
            {
                'for_prestable': True,
                'url': URL_TMPL.format('taxi_clownductor-service'),
            },
            {'service_name': 'taxi_clownductor-service_pre_stable'},
            {
                'arguments': [],
                'executable': 'python3.7',
                'execute_type': 'python',
                'expiration_age': 172800,
                'features': [
                    'repo_user_check',
                    'github_check_py3_service_name',
                    'allowed_repo_check',
                    'user_organization_check',
                    'check_bitbucket_rootdir',
                ],
                'local_relative_path': (
                    'taxi_clownductor-service/m4326_debugging_script.py'
                ),
                'python_path': '',
                'url': (
                    'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                    'taxi_clownductor-service/m4326_debugging_script.py'
                ),
            },
        ),
        pytest.param(
            {
                'for_prestable': True,
                'url': URL_TMPL.format('taxi_clownductor-service'),
            },
            {'service_name': 'taxi_clownductor-service_pre_stable'},
            {
                'arguments': [],
                'executable': 'python3.7',
                'execute_type': 'python',
                'expiration_age': 172800,
                'features': [
                    'repo_user_check',
                    'github_check_py3_service_name',
                    'allowed_repo_check',
                    'check_bitbucket_rootdir',
                ],
                'local_relative_path': (
                    'taxi_clownductor-service/m4326_debugging_script.py'
                ),
                'python_path': '',
                'url': (
                    'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                    'taxi_clownductor-service/m4326_debugging_script.py'
                ),
            },
            marks=pytest.mark.config(
                SCRIPTS_FEATURES={
                    'repo_user_check': True,
                    'github_check_py3_service_name': True,
                    'allowed_repo_check': True,
                    'user_organization_check': False,
                    'check_bitbucket_rootdir': True,
                    'convert_gh_to_bb': False,
                },
            ),
            id='disabled user_organization_check',
        ),
    ],
)
@pytest.mark.config(SCRIPTS_ALLOW_MASTER_BLOB=True, USE_APPROVALS=True)
async def test_create_and_get_to_run(
        patch, scripts_client, create_params, get_params, script_additions,
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

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': URL_TMPL.format('taxi_test'),
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
            **create_params,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, timeout=None, log_extra=None):
        return [
            {
                'change_doc_id': f'scripts_{_id}',
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

    response = await scripts_client.post(
        '/scripts/next-script/', json=get_params,
    )
    assert response.status == 200
    script = await response.json()
    if not script_additions:
        assert script == {}
    else:
        assert script == {'id': _id, **script_additions}
