# pylint: disable=redefined-outer-name
import os
import uuid

import pytest

from taxi import settings
from taxi.scripts import db as scripts_db

from scripts import settings as scripts_settings


@pytest.fixture
def patch_path(monkeypatch):
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(scripts_settings.__file__),
            '../debian/scripts-executors/',
        ),
    )
    monkeypatch.setattr(
        scripts_settings, 'EXTERNAL_EXECUTOR_SCRIPTS_DIR', path,
    )


@pytest.fixture(name='arc_mock')
def _arc_mock(patch_method):
    @patch_method('scripts.lib.vcs_utils.arc.Arc._run_shell')
    async def _run_shell(self, *cmd, with_cwd=True):
        if cmd[0] == 'checkout':
            if self._ref_name != 'trunk':
                raise self.ShellOperationError(
                    f'error: path \'{self._ref_name}\' '
                    f'did not match any file(s) known to arc.',
                )


def _case(post, expected_code, response_message=None, env=None):
    return post, expected_code, response_message, env


@pytest.mark.usefixtures('patch_path', 'arc_mock')
@pytest.mark.config(
    SCRIPTS_CHECK_SERVICE_NAME_SETTINGS={
        'enabled': True,
        'specific_names': [],
    },
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'service': '__ANY__', 'execute_type': '__ANY__', 'value': True},
    ],
)
@pytest.mark.parametrize(
    'post, expected_code, response_message, env',
    [
        _case({}, 400),
        _case(
            {
                'url': (
                    'https://github.yandex-team.ru/taxi/tools/blob/'
                    '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                    'migrations/m4326_debugging_script.py'
                ),
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [],
                'comment': 'comment',
                'request_id': '123',
            },
            200,
        ),
        _case(
            {
                'url': (
                    'https://github.yandex-team.ru/taxi/tools/blob/'
                    '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                    'migrations/m4326_debugging_script.py'
                ),
                'ticket': 'TAXIBACKEND-7',
                'arguments': [],
                'comment': 'comment',
                'request_id': '123',
            },
            200,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': ['some-command'],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'eda-php-console',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': ['some-command'],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'eda-php-console',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': ['some-command'],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'eda-php-console',
                'cgroup': 'eda_scripts',
            },
            200,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': ['some-command'],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'eda-php-console',
                'cgroup': 'some_strange_group',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'taxi/some',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'some_existing_group',
            },
            200,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'some_existing_group',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'taxi/some',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'non_existing_group',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'unknown_org/some_repo',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'non_existing_group',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'unknown_org/some_repo',
                    'some-unknown-arg',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'some_existing_group',
            },
            406,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'taxi/uservices',
                    '--forked_by',
                    'users/d1mbas/some/feature',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'some_existing_group',
            },
            406,
            response_message={
                'code': 'ILLEGAL_ARGUMENTS',
                'message': 'forked_by is prohibited for production',
                'status': 'error',
            },
            env=settings.PRODUCTION,
        ),
        _case(
            {
                'ticket': 'TAXIBACKEND-7',
                'python_path': 'fake-path',
                'arguments': [
                    '--service_name',
                    'some_service',
                    '--db_name',
                    'some_db',
                    '--repository',
                    'taxi/uservices',
                    '--branch',
                    'some-bad-branch',
                ],
                'comment': 'comment',
                'request_id': uuid.uuid4().hex,
                'execute_type': 'pgmigrate',
                'cgroup': 'some_existing_group',
            },
            406,
            response_message={
                'code': 'BAD_BRANCH',
                'message': (
                    'cannot fetch branch None, '
                    'branch/commit \'some-bad-branch\''
                ),
                'status': 'error',
            },
        ),
    ],
)
async def test_create_script(
        monkeypatch,
        patch,
        scripts_client,
        post,
        expected_code,
        response_message,
        env,
):
    if env:
        monkeypatch.setattr('taxi.settings.ENVIRONMENT', env)

    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def _check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        return {}

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def _cgroup_exists_mock(group, *args, **kwargs):
        return group in {'some_existing_group'}

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def _ngroup_exists_mock(*args, **kwargs):
        return False

    response = await scripts_client.post(
        '/scripts/', json=post, headers={'X-Yandex-Login': 'd1mbas'},
    )
    result = await response.json()
    if response_message is not None:
        assert result == response_message
    else:
        assert result['status'] == (
            'ok' if expected_code == 200 else 'error'
        ), result
    assert response.status == expected_code, result
    if expected_code == 200 and post.get('execute_type') == 'eda-php-console':
        response = await scripts_client.get(
            f'/scripts/{result["id"]}/download-external-runner/',
            params={'type': post['execute_type']},
        )
        assert response.status == 200, await response.text()
        assert (
            'CONSOLE_PATH = \'/var/www/bin/console\'' in await response.text()
        )


@pytest.mark.config(
    CHECK_ORGANIZATION=True,
    SCRIPTS_FEATURES={'try_get_real_organization': True},
)
async def test_args_only_script_creation(patch, db, scripts_client):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def _check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def _get_draft_mock(*args, **kwargs):
        return {
            'created_by': 'd1mbas',
            'id': 1,
            'change_doc_id': f'scripts_{_id}',
            'description': '',
            'approvals': [],
            'run_manually': False,
            'status': 'need_approvals',
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.approve_draft')
    async def _add_approve(*args, **kwargs):
        return

    @patch('scripts.lib.clients.conductor.Client.find_project_name')
    async def _conductor_find_project_name(group):
        assert group == 'eda_scripts'

    @patch('scripts.lib.clients.clownductor.Client.find_project_info')
    async def _clownductor_find_project_info(group):
        assert group == 'eda_scripts'
        return None

    response = await scripts_client.post(
        '/scripts/',
        json={
            'ticket': 'TAXIBACKEND-7',
            'python_path': 'fake-path',
            'arguments': ['some-command'],
            'comment': 'comment',
            'request_id': uuid.uuid4().hex,
            'execute_type': 'eda-php-console',
            'cgroup': 'eda_scripts',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    _id = (await response.json())['id']

    script = await scripts_db.find_one_by_id(db, 'scripts', _id)
    assert script.url == ''
    assert script.execute_type == 'eda-php-console'
    assert script.project == 'eda_scripts'
    assert script.organization == 'eda'

    response = await scripts_client.get(
        f'/{_id}/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    script = await response.json()
    assert script['url'] == ''
    assert script['cgroup'] == 'eda_scripts'
    assert script['organization'] == 'eda'

    response = await scripts_client.put(
        f'/{_id}/approval/',
        params={'organization': 'taxi'},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 400

    response = await scripts_client.put(
        f'/{_id}/approval/',
        params={'organization': 'eda'},
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
