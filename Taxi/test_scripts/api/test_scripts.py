# pylint: disable=unused-variable, invalid-name
import datetime
import io
import json
import zipfile

import freezegun
import pytest

from taxi.scripts import db as scripts_db
from testsuite.utils import matching

from scripts.api import scripts as api
from scripts.lib.vcs_utils import common

NOW = datetime.datetime(2019, 2, 28)


@pytest.mark.now(NOW.isoformat())
async def test_get_next_scripts_not_found(scripts_client):
    response = await scripts_client.post(
        '/scripts/next-script/', data=json.dumps({'service_name': 'test'}),
    )
    assert response.status == 200
    data = await response.json()
    assert not data


@pytest.mark.config(SCRIPTS_FEATURES={'pass_extra_script_info': True})
@pytest.mark.usefixtures('setup_many_scripts', 'load_schemas_mock')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'body,expected',
    [
        ({'service_name': 'test'}, {}),
        (
            {'service_name': 'approved-test'},
            {
                'arguments': ['--arg', 'arg'],
                'local_relative_path': 'fake-project/test.py',
                'python_path': 'FAKE_PYTHON_PATH',
                'url': 'fake-url',
                'executable': 'python3.7',
                'execute_type': 'python',
                'features': ['pass_extra_script_info'],
                'extra_info': {
                    'author': 'vlmazlov',
                    'execute_type': 'python',
                    'id': 'approved-test-id',
                    'local_relative_path': 'fake-project/test.py',
                    'organization': 'taxi',
                    'service': 'approved-test',
                    'ticket': 'TAXIBACKEND-1',
                    'url': 'fake-url',
                },
            },
        ),
        ({'service_name': 'approved-locked-test'}, {}),
        (
            {'service_name': 'test-using-executables'},
            {
                'arguments': ['--arg', 'arg'],
                'local_relative_path': 'fake-project/test.py',
                'python_path': 'FAKE_PYTHON_PATH',
                'url': 'fake-url',
                'executable': 'python2.7',
                'path_extension': ['/usr/bin'],
                'pythonpath_extension': ['/usr/lib/python2.7'],
                'environment_variables': {'A': 'b'},
                'execute_type': 'python',
                'features': ['pass_extra_script_info'],
                'extra_info': {
                    'author': 'vlmazlov',
                    'execute_type': 'python',
                    'id': matching.any_string,
                    'local_relative_path': 'fake-project/test.py',
                    'organization': 'taxi',
                    'service': 'test-using-executables',
                    'ticket': 'TAXIBACKEND-1',
                    'url': 'fake-url',
                },
            },
        ),
    ],
)
async def test_get_next_scripts(scripts_client, body, expected):
    response = await scripts_client.post(
        '/scripts/next-script/', data=json.dumps(body),
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    data.pop('id', None)
    assert data == expected


@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('setup_many_scripts')
async def test_get_script_twice(scripts_client):
    response = await scripts_client.post(
        '/scripts/next-script/',
        data=json.dumps(
            {'service_name': 'approved-test', 'fetch_lock_time': 120},
        ),
    )
    assert response.status == 200

    response = await scripts_client.post(
        '/scripts/next-script/',
        data=json.dumps(
            {'service_name': 'approved-test', 'fetch_lock_time': 120},
        ),
    )
    assert response.status == 200
    data = await response.json()
    assert not data


@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('setup_many_scripts')
async def test_scripts_marking(scripts_client, db):
    response = await scripts_client.post(
        '/scripts/next-script/',
        data=json.dumps(
            {'service_name': 'approved-test', 'fetch_lock_time': 120},
        ),
    )
    assert response.status == 200
    script = await response.json()
    _id = script['id']

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-running/'.format(id=_id),
        data=json.dumps({'fqdn': 'test-fqdn'}),
    )
    assert response.status == 200
    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.RUNNING
    assert script.server_name == 'test-fqdn'

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-succeeded/'.format(id=_id),
        data=json.dumps({'code': 0}),
    )
    assert response.status == 200
    script = await scripts_db.Script.get_script(db, _id)
    assert script.exit_code == 0

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-failed/'.format(id=_id),
        data=json.dumps({'reason': 'failing after success'}),
    )
    assert response.status == 409
    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.SUCCEEDED

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-failed/'.format(id=_id),
        data=json.dumps({'reason': 'failing after success', 'force': True}),
    )
    assert response.status == 409
    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.SUCCEEDED


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(USE_APPROVALS=True)
async def test_race_on_low_fetch_lock_use_approvals(patch, scripts_client):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def mock_get_drafts(*args, **kwargs):
        return [{'change_doc_id': 'hash_approved-test-id'}]

    await _test_race_marked_running(scripts_client)


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(USE_APPROVALS=False)
async def test_race_on_low_fetch_lock(patch, scripts_client):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def mock_get_drafts(*args, **kwargs):
        return [{'change_doc_id': 'hash_approved-test-id'}]

    await _test_race_marked_running(scripts_client)


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(USE_APPROVALS=True)
async def test_race_double_mark_running_use_app(patch, scripts_client):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def mock_get_drafts(*args, **kwargs):
        return [{'change_doc_id': 'hash_approved-test-id'}]

    await _test_race_double_mark_running(scripts_client)


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(USE_APPROVALS=False)
async def test_race_double_mark_running_not_use_app(patch, scripts_client):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def mock_get_drafts(*args, **kwargs):
        return [{'change_doc_id': 'hash_approved-test-id'}]

    await _test_race_double_mark_running(scripts_client)


async def _test_race_marked_running(scripts_client):
    with freezegun.freeze_time(NOW.isoformat()):
        response = await scripts_client.post(
            '/scripts/next-script/',
            data=json.dumps(
                {'service_name': 'approved-test', 'fetch_lock_time': 1},
            ),
        )
        assert response.status == 200

        response = await scripts_client.post(
            '/scripts/{id}/mark-as-running/'.format(id='approved-test-id'),
            data=json.dumps({'fqdn': 'test-fqdn'}),
        )
        assert response.status == 200

    with freezegun.freeze_time(
            (NOW + datetime.timedelta(seconds=5)).isoformat(),
    ):
        response = await scripts_client.post(
            '/scripts/next-script/',
            data=json.dumps(
                {'service_name': 'approved-test', 'fetch_lock_time': 5},
            ),
        )
        assert response.status == 200
        script = await response.json()
        assert not script


async def _test_race_double_mark_running(scripts_client):
    with freezegun.freeze_time(NOW.isoformat()):
        response = await scripts_client.post(
            '/scripts/next-script/',
            data=json.dumps(
                {'service_name': 'approved-test', 'fetch_lock_time': 1},
            ),
        )
        assert response.status == 200

    with freezegun.freeze_time(
            (NOW + datetime.timedelta(seconds=5)).isoformat(),
    ):
        response = await scripts_client.post(
            '/scripts/next-script/',
            data=json.dumps(
                {'service_name': 'approved-test', 'fetch_lock_time': 5},
            ),
        )
        assert response.status == 200
        script = await response.json()
        assert script

    with freezegun.freeze_time(NOW.isoformat()):
        response = await scripts_client.post(
            '/scripts/{id}/mark-as-running/'.format(id='approved-test-id'),
            data=json.dumps({'fqdn': 'test-fqdn'}),
        )
        assert response.status == 200

    with freezegun.freeze_time(
            (NOW + datetime.timedelta(seconds=5)).isoformat(),
    ):
        response = await scripts_client.post(
            '/scripts/{id}/mark-as-running/'.format(id='approved-test-id'),
            data=json.dumps({'fqdn': 'test-fqdn'}),
        )
        assert response.status == 409


@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('setup_many_scripts')
async def test_mark_failed(scripts_client, db):
    response = await scripts_client.post(
        '/scripts/next-script/',
        data=json.dumps(
            {'service_name': 'approved-test', 'fetch_lock_time': 120},
        ),
    )
    assert response.status == 200
    script = await response.json()
    _id = script['id']

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-running/'.format(id=_id),
        data=json.dumps({'fqdn': 'test-fqdn'}),
    )
    assert response.status == 200
    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.RUNNING
    assert script.server_name == 'test-fqdn'

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-failed/'.format(id=_id),
        data=json.dumps({'reason': 'failing after success'}),
    )
    assert response.status == 200
    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.FAILED


@pytest.mark.config(USE_APPROVALS=True)
async def test_psql_env_ext(patch, db, scripts_client):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('scripts.internal.scripts_manager.check_script')
    async def check_script_mock(*args, **kwargs):
        return (
            common.VersionControlInfo(
                user='taxi',
                repo='tools-py3',
                reference='30665de7552ade50fd29b7d059c339e1fc1f93f0',
                script='migrations/m4326_debugging_script.py',
            ),
            (
                'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
        )

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

    @patch('scripts.api.scripts.read_external_executable')
    def read_external_executable_mock(*args, **kwargs):
        return ''

    script_url = (
        'https://github.yandex-team.ru/taxi/tools-py3/blob/'
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
        'execute_type': 'psql',
    }
    response = await scripts_client.post(
        '/scripts/', json=post_data, headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']
    script = await scripts_db.Script.get_script(db, _id)
    assert script.project == 'migrations'
    assert script.execute_type == 'psql'

    response = await scripts_client.post(
        '/scripts/next-script/',
        json={'service_name': 'migrations', 'fetch_lock_time': 120},
    )
    assert response.status == 200

    response = await scripts_client.get(
        f'/scripts/{_id}/download-external-runner/', params={'type': 'psql'},
    )
    assert response.status == 200


@pytest.mark.usefixtures('load_schemas_mock')
async def test_external_schemas_redefine(schemas):
    await schemas.load()
    executable = api.get_executable_settings(
        schemas, 'test-using-executables', 'psql',
    )['downloadable_executable']
    assert executable == 'test-executable.py'


async def test_external_schemas_wo_redefine(schemas):
    await schemas.load()
    executable = api.get_executable_settings(schemas, 'taxi', 'psql')[
        'downloadable_executable'
    ]
    assert executable == 'psql_request_script.py'


@pytest.mark.usefixtures('setup_many_scripts')
async def test_unknown_external_executor(scripts_client):
    response = await scripts_client.get(
        '/scripts/test-running-state/download-external-runner/',
        params={'type': 'some-unknown-type'},
    )
    assert response.status == 400
    _data = await response.json()
    assert _data == {
        'message': 'Unknown download type "some-unknown-type"',
        'code': 'unknown_download_type',
        'status': 'error',
    }


@pytest.fixture(name='mock_arc')
def _mock_arc(patch_method):
    calls = {'mount': 0, 'unmount': 0, 'mk_archive': 0, '_checkout': 0}

    @patch_method('scripts.lib.vcs_utils.arc.Arc.mount')
    async def _mount(self):
        calls['mount'] += 1

    @patch_method('scripts.lib.vcs_utils.arc.Arc.unmount')
    async def _unmount(self):
        calls['unmount'] += 1

    @patch_method('scripts.lib.vcs_utils.arc.Arc.mk_archive')
    async def _mk_archive(self):
        calls['mk_archive'] += 1

    @patch_method('scripts.lib.vcs_utils.arc_utils.ArcClient._checkout')
    async def _checkout(self, reference):
        calls['_checkout'] += 1

    return calls


@pytest.mark.config(
    SCRIPTS_FEATURES_BY_PROJECT={
        'download-script-from-s3': {'use_async_archive_creation': True},
        '__default__': {},
    },
)
@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize(
    'script_id',
    [
        'test-eda',
        'test-taxi-gh',
        'arc-script',
        'arc-test-script',
        'arc-test-taximeter',
        'arc-test-archive-not-ready',
    ],
)
async def test_download_script(patch, db, scripts_client, mock_arc, script_id):
    await db.queue_archives_from_arcadia.insert(
        {
            '_id': 'abc',
            'vcs': 'arc',
            'user': 'user',
            'repo': 'repo',
            'path': '',
            'ref': 'not-ready-ref',
            'status': 'pending',
            'created': 'created',
            'updated': 'updated',
        },
    )

    zip_data = b'some archive data'
    f_name = 'test.txt'

    data = io.BytesIO()
    _zip = zipfile.ZipFile(data, mode='w')
    _zip.writestr(f_name, data=zip_data)
    _zip.close()
    data.seek(0)

    @patch('taxi.clients.github.GithubClient.get_archive')
    async def _github_get_archive(*args, **kwargs):
        return data.read()

    @patch('taxi.clients.bitbucket.BitBucketClient.get_archive')
    async def _bitbucket_get_archive(*args, **kwargs):
        return data.read()

    @patch('scripts.lib.utils.os.read_file')
    async def _read_file(path, mode='rb'):
        return data.read()

    response = await scripts_client.get(f'/scripts/{script_id}/download/')
    if script_id == 'arc-test-archive-not-ready':
        assert response.status == 500
        assert (await response.json()) == {
            'code': 'ARCHIVE_NOT_READY',
            'message': 'archive still not ready, need to wait a little',
        }
        return

    assert response.status == 200
    response_data = io.BytesIO(await response.read())
    response_zip = zipfile.ZipFile(response_data)
    assert response_zip.namelist() == [f_name]
    assert response_zip.read(f_name) == zip_data
    calls = (
        _github_get_archive.calls
        + _bitbucket_get_archive.calls
        + _read_file.calls
    )
    assert len(calls) == 1

    if script_id in ('arc-script', 'arc-test-script', 'arc-test-taximeter'):
        for mock_name, mock_calls in mock_arc.items():
            assert mock_calls, f'{mock_name} has not called'


@pytest.mark.config(
    SCRIPTS_FEATURES_BY_PROJECT={
        'download-script-from-s3': {'use_async_archive_creation': True},
        '__default__': {},
    },
)
@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize('script_id', ['arc-test-archive-ready'])
async def test_download_archive_from_s3(
        mockserver, db, scripts_client, script_id,
):
    await db.queue_archives_from_arcadia.insert(
        {
            '_id': 'abcd',
            'vcs': 'arc',
            'user': 'user',
            'repo': 'repo',
            'path': '',
            'ref': 'ready-ref',
            'status': 'success',
            'created': 'created',
            'updated': 'updated',
        },
    )

    zip_data = b'some archive data'
    f_name = 'test.txt'

    data = io.BytesIO()
    _zip = zipfile.ZipFile(data, mode='w')
    _zip.writestr(f_name, data=zip_data)
    _zip.close()
    data.seek(0)

    @mockserver.handler('/archive-s3/scripts-archive/arc-repo--ready-ref')
    def _s3_handler(request):
        return mockserver.make_response(
            response=data.read(),
            headers={'ETag': '123', 'Key': 'arc-repo--ready-ref'},
        )

    response = await scripts_client.get(f'/scripts/{script_id}/download/')
    assert response.status == 200
    response_data = io.BytesIO(await response.read())
    response_zip = zipfile.ZipFile(response_data)
    assert response_zip.namelist() == [f_name]
    assert response_zip.read(f_name) == zip_data
