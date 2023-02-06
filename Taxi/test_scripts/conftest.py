# pylint: disable=redefined-outer-name, unused-variable
import datetime
import logging
import pathlib
import random
import subprocess

import pytest

from taxi.clients import bitbucket
from taxi.clients import github
from taxi.pytest_plugins import service
from taxi.util import client_session

from scripts import app
from scripts import cron_run
from scripts.lib import db_utils as scripts_db
from scripts.lib import executable_schemas
from . import helpers

logger = logging.getLogger(__name__)

Fields = scripts_db.Script.Fields

# Install service fixtures based on service.yaml file
service.install_service_local_fixtures(__name__)

pytest_plugins = ['test_scripts.pytest_plugins.async_checks_queue']


@pytest.fixture(autouse=True)
def _patch_arc_init(patch):
    @patch('scripts.lib.vcs_utils.arc.Arc.init')
    async def init():
        pass


@pytest.fixture
def simple_secdist(simple_secdist, mockserver):
    simple_secdist['settings_override']['S3MDS_TAXI_SCRIPTS_ARCHIVE'] = {
        'url': f'{mockserver.host}:{mockserver.port}/archive-s3',
        'bucket': 'scripts-archive',
        'access_key_id': 'access_key_id',
        'secret_key': 'secret_key',
        'config': {'retries': {'max_attempts': 0}},
    }
    simple_secdist['settings_override']['ARC_TOKEN'] = 'ARC_TOKEN'
    return simple_secdist


@pytest.fixture
async def scripts_app(loop, db, simple_secdist):
    _app = app.create_app(loop=loop, db=db)
    yield _app
    await _app.close_sessions()
    await _app.stop_background_tasks()


@pytest.fixture
def scripts_client(aiohttp_client, scripts_app, loop):
    return loop.run_until_complete(aiohttp_client(scripts_app))


@pytest.yield_fixture
async def scripts_tasks_app(loop, db, simple_secdist):
    _app = cron_run.TaxiScriptsCronApplication(loop=loop, db=db)
    for method in _app.on_startup:
        await method(_app)

    yield _app

    for method in _app.on_shutdown:
        await method(_app)


@pytest.fixture(autouse=True)
def get_last_commit_fixture(patch):
    @patch('taxi.clients.github.GithubClient.get_commit_sha')
    async def get_commit_sha_github(*args, **kwargs):
        return ''

    @patch('taxi.clients.bitbucket.BitBucketClient.get_commit_sha')
    async def get_commit_sha_bitbucket(*args, **kwargs):
        return ''


@pytest.yield_fixture
async def setup_many_scripts(db):
    await db.scripts.insert_many(
        [
            helpers.get_script_doc(
                {
                    'project': 'approved-test',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    '_id': 'approved-test-id',
                    'organization': None,
                },
            ),
            helpers.get_script_doc(
                {
                    'project': 'approved-locked-test',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'fetch_lock_expires_at': (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(weeks=1)
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-running-state',
                    'project': 'test-running',
                    'status': scripts_db.ScriptStatus.RUNNING,
                    'server_name': 'test-dev',
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-approved-state',
                    'project': 'test-running',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'server_name': 'test-dev',
                },
            ),
            helpers.get_script_doc(
                {'_id': 'test-can-by-deleted', 'created_by': 'test-login'},
            ),
            helpers.get_script_doc({'project': 'test-using-executables'}),
            helpers.get_script_doc(
                {'_id': 'test-get-script', 'created_by': 'test-login'},
            ),
            helpers.get_script_doc(
                {'_id': 'with-org-filed-id', 'organization': 'test-org'},
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-approve-self-created',
                    'created_by': 'd1mbas',
                    'status': scripts_db.ScriptStatus.NEED_APPROVAL,
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-filter-by-org',
                    'organization': 'taximeter',
                    'ticket': 'TAXIBACKEND-TEST',
                    'created_by': 'd1mbas',
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-send-stats-1',
                    'status': 'running',
                    'created': datetime.datetime(2019, 5, 30, 13, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-send-stats-2',
                    'status': 'failed',
                    'created': datetime.datetime(2019, 5, 30, 13, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-send-stats-3',
                    'status': 'need_approval',
                    'created': datetime.datetime(2019, 5, 30, 13, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-send-stats-4',
                    'status': 'succeeded',
                    'created': datetime.datetime(2019, 5, 30, 13, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-created-by-cgroup',
                    'project': 'taxi_scripts',
                    'created': datetime.datetime(2019, 5, 30, 19, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-created-by-project-name',
                    'project': 'billing-replication',
                    'created': datetime.datetime(2019, 5, 30, 19, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-created-in-taxi',
                    'project': 'taxi',
                    'created': datetime.datetime(2019, 5, 30, 19, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    '_id': 'test-created-in-taximeter',
                    'project': 'taximeter',
                    'organization': 'taximeter',
                    'created': datetime.datetime(2019, 5, 30, 19, 59),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.failed_reason: 'expired',
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.FAILED
                    ),
                    scripts_db.Script.Fields.created: datetime.datetime(
                        2019, 5, 29,
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.failed_reason: 'some fail',
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.FAILED
                    ),
                    scripts_db.Script.Fields.created: datetime.datetime(
                        2019, 5, 29,
                    ),
                },
            ),
            # api.test_admin.test_new_waiting_statuses
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-run-status-approved'
                    ),
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.NEED_APPROVAL
                    ),
                    scripts_db.Script.Fields.run_manually: False,
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-run-status-approved-manual'
                    ),
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.NEED_APPROVAL
                    ),
                    scripts_db.Script.Fields.run_manually: True,
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-run-status-running'
                    ),
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.RUNNING
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-run-status-not-running'
                    ),
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.NEED_APPROVAL
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-run-status-need-approvals'
                    ),
                    scripts_db.Script.Fields.status: (
                        scripts_db.ScriptStatus.NEED_APPROVAL
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-exec-type-psql'
                    ),
                    scripts_db.Script.Fields.execute_type: 'psql',
                    scripts_db.Script.Fields.created_by: 'd1mbas',
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: 'test-eda',
                    scripts_db.Script.Fields.url: (
                        'https://bb.yandex-team.ru/projects/EDA/repos/'
                        'infrastructure_admin_scripts/browse/eda_scripts/'
                        'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e'
                    ),
                    scripts_db.Script.Fields.organization: 'eda',
                    scripts_db.Script.Fields.project: 'eda_scripts',
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: 'test-taxi-gh',
                    scripts_db.Script.Fields.url: (
                        'https://github.yandex-team.ru/taxi/tools/blob/'
                        '364c45deec5db8bd83e79d0cafc7feae6cd558f4/'
                        'testing/test_big_log.py'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'arc-script',
                    Fields.url: (
                        'https://a.yandex-team.ru/arc_vcs/'
                        'taxi/schemas/schemas/postgresql/overlord_catalog/'
                        'overlord_catalog/0000-basic.sql?'
                        'rev=r9171278'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'arc-test-script',
                    Fields.url: (
                        'https://a.yandex-team.ru/arc_vcs/'
                        'taxi/infra/tools-py3/clownductor/test_script.py'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'arc-test-taximeter',
                    Fields.url: (
                        'https://a.yandex-team.ru/arc_vcs/'
                        'taxi/github/taximeter/taxi-cloud-yandex/src/'
                        'Yandex.Taximeter.ScriptRunner/Scripts/TestScript.cs'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-comment-1'
                    ),
                    scripts_db.Script.Fields.comment: 'Comment',
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-comment-2'
                    ),
                    scripts_db.Script.Fields.comment: 'xcom ',
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-ticket'
                    ),
                    scripts_db.Script.Fields.ticket: 'TICKET-TEST',
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-script-1'
                    ),
                    scripts_db.Script.Fields.local_relative_path: (
                        'src/Yandex.Taximeter.JobRunner/Job/'
                        'SyncParkRobotSettings.cs'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-script-2'
                    ),
                    scripts_db.Script.Fields.local_relative_path: (
                        'taxi-corp/drive_descriptions.py'
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    scripts_db.Script.Fields.primary_key: (
                        'test-filter-by-arguments'
                    ),
                    scripts_db.Script.Fields.arguments: """--repository=a-andriyanov/uservices
--branch=features/add_author_and_id_in_rules_get_EFFICIENCYDEV-3802""",
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'test-filter-by-started-from',
                    Fields.started_running_at: datetime.datetime(
                        2020, 5, 6, 12, 1,
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'arc-test-archive-not-ready',
                    Fields.project: 'download-script-from-s3',
                    Fields.url: (
                        'https://a.yandex-team.ru/arc_vcs/'
                        'taxi/infra/tools-py3/clownductor/test_script.py?'
                        'rev=ref'
                    ),
                    Fields.vci: (
                        'user',
                        'repo',
                        'not-ready-ref',
                        'taxi/infra/tools-py3/clownductor/test_script.py',
                    ),
                },
            ),
            helpers.get_script_doc(
                {
                    Fields.primary_key: 'arc-test-archive-ready',
                    Fields.project: 'download-script-from-s3',
                    Fields.url: (
                        'https://a.yandex-team.ru/arc_vcs/'
                        'taxi/infra/tools-py3/clownductor/test_script.py?'
                        'rev=ref'
                    ),
                    Fields.vci: (
                        'user',
                        'repo',
                        'ready-ref',
                        'taxi/infra/tools-py3/clownductor/test_script.py',
                    ),
                },
            ),
        ],
    )

    yield

    await db.scripts.drop()


@pytest.fixture
async def setup_scripts(db):
    async def _setup(script_docs):
        if script_docs:
            await db.scripts.insert_many(
                [helpers.get_script_doc(x) for x in script_docs],
            )

    yield _setup

    await db.scripts.drop()


@pytest.fixture
def find_script(db):
    async def _do_id(_id):
        return await db.scripts.find_one({'_id': _id})

    return _do_id


@pytest.fixture
def load_schemas_mock(monkeypatch, load_yaml):
    _orig_load_executables_schema = executable_schemas.Schemas.load

    async def load_schemas_mock(self, app=None):
        await _orig_load_executables_schema(self, app=app)
        self['test-using-executables'] = load_yaml(
            'test-using-executables.yaml',
        )

    monkeypatch.setattr(
        'scripts.lib.executable_schemas.Schemas.load', load_schemas_mock,
    )


@pytest.fixture
def schemas(scripts_app):
    return scripts_app.executable_schemas


@pytest.fixture
async def setup_lots_random_scripts(db):
    organizations = ['taxi']
    exec_types = ['python', 'psql']
    creators = [
        'ilyasov',
        'dvasiliev89',
        'nevladov',
        'oboroth',
        'mazgutov',
        'd1mbas',
        'victorshch',
    ]
    statuses = list(scripts_db.ScriptStatus.ALL)
    docs = [
        helpers.get_script_doc(
            {
                'organization': random.choice(organizations),
                'execute_type': random.choice(exec_types),
                'created_by': random.choice(creators),
                'status': random.choice(statuses),
                '_id': f'random-script-{x}',
            },
        )
        for x in range(10)
    ]
    await db.scripts.insert_many(docs)
    yield
    await db.scripts.drop()


@pytest.fixture
async def bitbucket_client(simple_secdist):
    async with client_session.get_client_session() as session:
        return bitbucket.BitBucketClient(
            session=session, secdist=simple_secdist,
        )


@pytest.fixture
async def github_client():
    async with client_session.get_client_session() as session:
        return github.GithubClient(session=session)


@pytest.fixture
def create_scripts_common(patch):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def script_check_taximeter_mock(*args, **kwargs):
        pass

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def check_cgroup_exists(group, log_extra=None):
        return False

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def check_ngroup_exists(group, log_extra=None):
        return True


@pytest.fixture
def patch_method(monkeypatch):
    def dec_generator(full_func_path):
        def dec(func):
            monkeypatch.setattr(full_func_path, func)
            return func

        return dec

    return dec_generator


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'enable_raw_arc_client: enables to use arc with out patches',
    )


@pytest.fixture(autouse=True)
def _disable_arc(request, patch_method):
    if request.node.get_closest_marker('enable_raw_arc_client') is not None:
        return

    @patch_method('scripts.lib.vcs_utils.arc.Arc._run_shell')
    async def _run_shell(self, *args, **kwargs):
        raise RuntimeError('arc client not mocked')


@pytest.fixture(name='mock_executor_schemas')
def _mock_executor_schemas(monkeypatch, schemas):
    def _wrapper(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setitem(schemas, key, value)

    return _wrapper


class _ArcMock:
    def __init__(self, root_dir: pathlib.Path):
        self._root_dir = root_dir

        logger.debug('create arc dir %s', self.arc_dir)
        self._root_dir.mkdir(parents=True, exist_ok=True)
        self.arc_dir.mkdir(parents=True, exist_ok=True)

        logger.debug('create bare dir %s', self.arc_dir / 'bare')
        (self.arc_dir / 'bare').mkdir(parents=True, exist_ok=True)

        logger.debug('init bare repo')
        self.__run_arc_shell('init', '--bare', cwd=self.arc_dir / 'bare')

        logger.debug('more bare dir into .arc')
        (self.arc_dir / 'bare').rename(self.arc_dir / '.arc')

        assert (self.arc_dir / '.arc').is_dir()

        logger.debug('initial changes and commits')
        self.__run_arc_shell('add', '.')
        self.__run_arc_shell('commit', '-m', 'init', '--force')

    def write_file(self, path: str, content: str):
        (self.arc_dir / path).write_text(content)
        self.__run_arc_shell('add', path)
        self.commit(f'upsert {path!r} file')

    def mk_dir(self, path: str) -> pathlib.Path:
        result = self.arc_dir / path
        result.mkdir(parents=True, exist_ok=True)
        return result

    def commit(self, msg: str):
        self.__run_arc_shell('commit', '-m', msg, '--force')

    def make_branch(self, name: str):
        self.__run_arc_shell('checkout', '-b', name)

    def checkout(self, ref_name: str = 'trunk'):
        self.__run_arc_shell('checkout', ref_name)

    @property
    def root_dir(self) -> pathlib.Path:
        return self._root_dir

    @property
    def arc_dir(self) -> pathlib.Path:
        return self.root_dir / 'arcadia'

    def __run_arc_shell(self, *cmd, cwd=None) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ['arc', *cmd], cwd=cwd or self.arc_dir, capture_output=True,
        )
        streams = ['stdout', 'stderr']
        for stream_name in streams:
            stream: bytes = getattr(proc, stream_name)
            for line in stream.splitlines():
                logger.debug(
                    '%s: %s', stream_name.upper(), line.strip().decode(),
                )
        assert not proc.returncode
        return proc


@pytest.fixture(name='arc_mock')
def _arc_mock(patch):
    @patch('scripts.lib.vcs_utils.arc.Arc.mount')
    async def _arc_mount(*args, **kwargs):
        pass

    @patch('scripts.lib.vcs_utils.arc.Arc.unmount')
    async def _arc_unmount(*args, **kwargs):
        pass

    def _wrapper(root_dir: pathlib.Path):
        return _ArcMock(pathlib.Path(root_dir))

    return _wrapper
