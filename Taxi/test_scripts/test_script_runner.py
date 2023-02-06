# pylint: disable=unused-variable, protected-access, redefined-outer-name
import asyncio
import os
import tempfile
import time

import pytest

from taxi.maintenance import log
from taxi.scripts import db as scripts_db

from scripts import scripts_runner
from . import helpers

ScriptFields = scripts_db.Script.Fields


@pytest.fixture(autouse=True)
def _setup_logging():
    log.init_loggers(ident='', debug=True, quiet=False)


@pytest.fixture
def _tmp_dirs(monkeypatch):
    with tempfile.TemporaryDirectory() as working_area:
        monkeypatch.setattr(
            'taxi.scripts.settings.WORKING_AREA_DIR', working_area,
        )
        yield working_area


@pytest.fixture
def scripts_client_mock(scripts_client, setup_scripts):
    class Client:
        next_command_called = 0
        next_command_responded_ok = 0
        apply_called = 0
        apply_tasks = []

        async def create_script(self, updates=None):
            if updates is None:
                updates = {}
            script_doc = helpers.get_script_doc(
                {
                    ScriptFields.url: (
                        'https://github.yandex-team.ru/taxi/tools/blob/'
                        '364c45deec5db8bd83e79d0cafc7feae6cd558f4/'
                        'test.py'
                    ),
                    ScriptFields.primary_key: '123',
                    ScriptFields.local_relative_path: 'test.py',
                    ScriptFields.created_by: 'd1mbas',
                    ScriptFields.status: 'running',
                    ScriptFields.features: [],
                    **updates,
                },
            )
            await setup_scripts([script_doc])
            return script_doc

        async def kill_script(self, _id):
            response = await scripts_client.post(
                f'/{_id}/kill/', headers={'X-Yandex-Login': 'd1mbas'},
            )
            assert response.status == 200, await response.text()
            return await response.json()

        async def get_next_command(self, script):
            self.next_command_called += 1
            response = await scripts_client.post(
                '/v1/scripts/commands/next/',
                json={'script_id': script.primary_key},
            )
            response.raise_for_status()
            self.next_command_responded_ok += 1
            return await response.json()

        async def apply_command(self, command_id, status):
            async def do_it():
                response = await scripts_client.post(
                    '/v1/scripts/commands/apply/',
                    json={'command_id': command_id, 'status': status},
                )
                self.apply_called += 1
                return response

            task = asyncio.create_task(do_it())
            self.apply_tasks.append(task)
            await task

    return Client()


@pytest.fixture
def dump_scripts_client():
    class Client:
        async def get_next_command(self, script):
            return {'sleep_for': 15}

    return Client()


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(NUM_MAX_RUNNING_SCRIPTS=1)
async def test_too_many_running(loop, patch, scripts_client):
    @patch('scripts.scripts_runner._do_stuff')
    async def _do_stuff_mock(*args, **kwargs):
        pass

    @patch('socket.getfqdn')
    def get_fqdn_mock():
        return 'test-dev'

    @patch('taxi.clients.scripts.ScriptsClient._request')
    async def get_current_running_count_mock(
            url,
            method='GET',
            data=None,
            json=None,
            params=None,
            log_extra=None,
            **kwargs,
    ):
        return await scripts_client.request(
            method=method,
            path=url,
            json=json,
            params=params,
            data=data,
            **kwargs,
        )

    await scripts_runner.do_stuff(loop=loop, service_name='test-running')

    assert _do_stuff_mock.call is None


@pytest.mark.usefixtures('load_schemas_mock')
@pytest.mark.usefixtures('setup_many_scripts')
async def test_executables_schema_usage(scripts_client):
    response = await scripts_client.request(
        'POST',
        '/scripts/next-script/',
        json={'service_name': 'test-using-executables'},
    )
    script = await response.json()

    assert script['path_extension'] == ['/usr/bin']
    assert script['pythonpath_extension'] == ['/usr/lib/python2.7']


async def test_run_script(
        monkeypatch, patch, load, _tmp_dirs, dump_scripts_client,
):
    monkeypatch.setenv('PYTHONPATH', '')
    tmp_dir = os.path.join(_tmp_dirs, '123', 'src')
    os.makedirs(tmp_dir, exist_ok=True)
    with open(os.path.join(tmp_dir, 'test.py'), 'w') as fp:
        fp.write(load('test.py'))

    @patch('taxi.scripts.os.get_checkouted_repo_root')
    def _foo(*args, **kwargs):
        return tmp_dir

    script = scripts_db.Script(
        None,
        helpers.get_script_doc(
            {
                ScriptFields.url: (
                    'https://github.yandex-team.ru/taxi/tools/blob/'
                    '364c45deec5db8bd83e79d0cafc7feae6cd558f4/'
                    'test.py'
                ),
                ScriptFields.primary_key: '123',
                ScriptFields.local_relative_path: 'test.py',
                ScriptFields.features: [],
            },
        ),
    )
    exit_code, script_path = await scripts_runner.async_os.run_script_command(
        script, dump_scripts_client,
    )
    assert not exit_code
    with open(os.path.join(tmp_dir, '..', 'stderr.log')) as fp:
        stderr = fp.read()
    assert stderr == ''

    with open(os.path.join(tmp_dir, '..', 'stdout.log')) as fp:
        stdout = fp.read()
    assert stdout == '[\'test.py\', \'--arg\', \'arg\']\n'


@pytest.mark.dontfreeze
@pytest.mark.config(SCRIPTS_COMMANDS_POLL_SETTINGS={'delay': 1})
async def test_run_script_and_kill_it(
        monkeypatch, patch, load, _tmp_dirs, scripts_client_mock,
):
    monkeypatch.setenv('PYTHONPATH', '')
    tmp_dir = os.path.join(_tmp_dirs, '123', 'src')
    os.makedirs(tmp_dir, exist_ok=True)
    with open(os.path.join(tmp_dir, 'test.py'), 'w') as fp:
        fp.write(load('long_running_script.py'))

    @patch('taxi.scripts.os.get_checkouted_repo_root')
    def _foo(*args, **kwargs):
        return tmp_dir

    script_doc = await scripts_client_mock.create_script()
    await scripts_client_mock.kill_script(script_doc['_id'])

    script = scripts_db.Script(None, script_doc)

    start = time.monotonic()
    exit_code, _ = await scripts_runner.async_os.run_script_command(
        script, scripts_client_mock,
    )
    assert 0 < time.monotonic() - start < 2
    assert exit_code == -9
    assert len(scripts_client_mock.apply_tasks) == 1
    if not scripts_client_mock.apply_tasks[0].done():
        await scripts_client_mock.apply_tasks[0]
    assert scripts_client_mock.apply_called == 1
    assert (
        scripts_client_mock.next_command_called
        == scripts_client_mock.next_command_responded_ok
    )


@pytest.mark.dontfreeze
async def test_run_scripts_and_timeout(
        monkeypatch, patch, load, _tmp_dirs, scripts_client_mock,
):
    monkeypatch.setenv('PYTHONPATH', '')
    tmp_dir = os.path.join(_tmp_dirs, '123', 'src')
    os.makedirs(tmp_dir, exist_ok=True)
    with open(os.path.join(tmp_dir, 'test.py'), 'w') as fp:
        fp.write(load('long_running_script.py'))

    @patch('taxi.scripts.os.get_checkouted_repo_root')
    def _foo(*args, **kwargs):
        return tmp_dir

    script_doc = await scripts_client_mock.create_script({'expiration_age': 1})
    script = scripts_db.Script(None, script_doc)

    start = time.monotonic()
    exit_code, _ = await scripts_runner.async_os.run_script_command(
        script, scripts_client_mock,
    )
    assert 0 < time.monotonic() - start < 2
    assert exit_code == -9
