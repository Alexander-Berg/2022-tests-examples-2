# pylint: disable=redefined-outer-name
import contextlib
import os.path
import shutil
from unittest import mock

import pytest

from taxi.scripts import db as scripts_db
from taxi.scripts import exceptions
from taxi.scripts import os as scripts_os
from taxi.scripts import utils
from tests.taxi import scripts


USER = 'taxi'
REPO = 'tools-py3'
REFERENCE = '081cb7c564540ddf61e65a3585ea847e3c404bed'
PROJECT = 'real-project'
SCRIPT_URL_TEMPLATE = (
    f'https://github.yandex-team.ru/{USER}/{REPO}/blob/'
    f'{REFERENCE}/{PROJECT}/{{}}'
)
DEFAULT_PATH_IN_PROJECT = 'script.py'
SCRIPT_URL = SCRIPT_URL_TEMPLATE.format(DEFAULT_PATH_IN_PROJECT)

TEST_SCRIPT_FILENAME = 'test_script.py'


def _get_script_with_path_in_project(path_in_project, **kwargs):
    path_in_project.lstrip('/')

    return scripts_db.Script(
        None,
        scripts.get_script_doc(
            dict(
                {
                    'url': SCRIPT_URL_TEMPLATE.format(path_in_project),
                    'local_relative_path': f'real-project/{path_in_project}',
                },
                **kwargs,
            ),
        ),
    )


def _create_script_src_dir(tmpdir, script, script_static_filename):
    working_area = tmpdir.mkdir('working_area')
    script_dir = (
        working_area.mkdir(script.primary_key)
        .mkdir('src')
        .mkdir('taxi-tools-py3')
        .mkdir(PROJECT)
    )

    shutil.copy(
        scripts.get_static_filepath(script_static_filename), script_dir,
    )
    return working_area


def test_parse_url():
    vcs_info = scripts_os.utils.parse_script_url(SCRIPT_URL)

    assert vcs_info.user == USER
    assert vcs_info.repo == REPO
    assert vcs_info.reference == REFERENCE
    assert vcs_info.script == f'{PROJECT}/{DEFAULT_PATH_IN_PROJECT}'


@pytest.mark.parametrize(
    'script_path', ['taxi-corp/script.py', 'taxi-exp/script.py', 'script.py'],
)
def remove_script_dir_if_exists(script_path, tmpdir):
    script = _get_script_with_path_in_project(script_path)
    working_area = _create_script_src_dir(tmpdir, script, script_path)

    with mock.patch('taxi.scripts.settings.WORKING_AREA_DIR', working_area):
        scripts_os.remove_script_dir_if_exists(script)


@pytest.mark.parametrize(
    'arg_set,expected_exit_code', [('fail', 1), ('success', 0)],
)
async def test_run_script_command(tmpdir, arg_set, expected_exit_code):
    with open(
            scripts.get_static_filepath(os.path.join(arg_set, 'args')), 'r',
    ) as args_file:
        script_args = args_file.read().split()

    script = _get_script_with_path_in_project(
        TEST_SCRIPT_FILENAME,
        status=scripts_db.ScriptStatus.RUNNING,
        arguments=script_args,
    )

    working_area = _create_script_src_dir(tmpdir, script, TEST_SCRIPT_FILENAME)

    with mock.patch('taxi.scripts.settings.WORKING_AREA_DIR', working_area):
        exit_code, _ = scripts_os.run_script_command(script)

    assert exit_code == expected_exit_code

    for log_filename in ('stderr_log', 'stdout_log'):
        with open(
                scripts.get_static_filepath(
                    os.path.join(arg_set, log_filename),
                ),
                'r',
        ) as expected_log_file:
            formated_logname = log_filename.replace('_', '.')
            primary_key = script.primary_key
            assert expected_log_file.read() == (
                working_area.join(primary_key).join(formated_logname).read()
            )


async def test_cant_create_subprocess(tmpdir):
    with contextlib.ExitStack() as stack:
        script = _get_script_with_path_in_project(TEST_SCRIPT_FILENAME)
        working_area = _create_script_src_dir(
            tmpdir, script, TEST_SCRIPT_FILENAME,
        )

        stack.enter_context(
            mock.patch(
                'taxi.scripts.os.subprocess.Popen', side_effect=OSError,
            ),
        )
        stack.enter_context(
            mock.patch(
                'taxi.scripts.os.settings.WORKING_AREA_DIR', working_area,
            ),
        )
        stack.enter_context(pytest.raises(exceptions.ExecutionError))

        scripts_os.run_script_command(script)


def test_read_or_empty(tmpdir):
    existing_path = tmpdir.join('existing.txt')
    non_existing_path = tmpdir.join('non_existing.txt')

    with open(existing_path, 'w') as existing_file:
        existing_file.write('A')

    assert scripts_os.read_or_empty(existing_path) == 'A'
    assert scripts_os.read_or_empty(non_existing_path) == ''


def test_environment_additions():
    script = scripts_db.Script(
        None,
        scripts.get_script_doc(
            {
                'executable': 'python2',
                'pythonpath_extension': ['/usr/lib/python2'],
                'path_extension': ['/usr/lib'],
                'environment_variables': {'A': 'b', 'PYTHONPATH': 'BAD_THING'},
            },
        ),
    )

    envs = scripts_os.get_env(script, 'some_cwd')
    assert envs['PYTHONPATH'] == 'BAD_THING:some_cwd'
    assert envs['PATH'].startswith('/usr/lib:')
    assert envs['A'] == 'b'

    cmd = scripts_os.get_cmd(script)
    assert cmd[0] == 'python2'


@pytest.mark.parametrize(
    'url',
    [
        pytest.param(
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            id='github url',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/schemas/schemas/postgresql/overlord_catalog/'
                'overlord_catalog/0000-basic.sql?'
                'rev=r9171278'
            ),
            id='arc url',
        ),
    ],
)
def test_get_checkouted_root(tmp_path, monkeypatch, url):
    monkeypatch.setattr(
        'taxi.scripts.settings.WORKING_AREA_DIR', str(tmp_path),
    )
    script = scripts_db.Script(None, scripts.get_script_doc({'url': url}))

    base_dir = os.path.join(str(tmp_path), script.primary_key)
    os.makedirs(base_dir)
    if 'git' in url:
        os.makedirs(os.path.join(base_dir, 'src', 'taxi-tools'))
    else:
        os.makedirs(os.path.join(base_dir, 'src'))

    path = scripts_os.get_checkouted_repo_root(
        script, utils.parse_script_url(script.url),
    )

    if 'git' in url:
        assert path == os.path.join(base_dir, 'src', 'taxi-tools')
    else:
        assert path == os.path.join(base_dir, 'src')
