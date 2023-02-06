import json
import os.path
import subprocess
import sys

import pytest

import scripts.app


@pytest.fixture(name='secdist')
def _secdist(simple_secdist):
    simple_secdist['postgresql_settings']['databases'][
        'test-db'
    ] = simple_secdist['postgresql_settings']['databases']['test']
    return simple_secdist


def _git(directory, *args):
    exit_code = subprocess.call(['git', *args], shell=False, cwd=directory)
    assert exit_code == 0


def create_git_repo(repo_root, services_dir, service_name, migrations_path):
    os.makedirs(repo_root)
    _git(repo_root, 'init')
    _git(repo_root, 'config', 'user.email', 'ya@ya.ru')
    _git(repo_root, 'config', 'user.name', 'User User')

    _git(repo_root, 'checkout', '-b', 'develop')

    migrations_root = os.path.join(
        repo_root, services_dir, service_name, migrations_path,
    )
    os.makedirs(migrations_root)
    with open(os.path.join(migrations_root, 'V01__init.sql'), 'w') as fp:
        fp.write(
            """
        BEGIN;
        CREATE SCHEMA IF NOT EXISTS myschema;
        CREATE TABLE myschema.mytable (id INTEGER PRIMARY KEY);
        COMMIT;
        """,
        )
    _git(repo_root, 'add', os.path.join(migrations_root, 'V01__init.sql'))
    _git(repo_root, 'commit', '-m', 'initial')


@pytest.mark.parametrize(
    'executable',
    [
        pytest.param('python3.6', id='py3.6_compat'),
        pytest.param('python3.6', id='py3.7_compat'),
        pytest.param(sys.executable, id='current_host_compat'),
    ],
)
@pytest.mark.parametrize(
    'services_dir_in_args, services_dir_in_repo',
    [
        ('services', 'services'),
        ('', ''),
        (None, 'services'),
        ('my-services', 'my-services'),
    ],
)
async def test_pgmigrate_executor(
        monkeypatch,
        secdist,
        tmp_dir,
        executable,
        services_dir_in_args,
        services_dir_in_repo,
):
    executor_path = os.path.join(
        scripts.app.BASE_DIR,
        '..',
        'debian',
        'scripts-executors',
        'pgmigrate_request_script.py',
    )
    secdist_path = os.path.join(tmp_dir, 'secdist.json')
    with open(secdist_path, 'w') as fp:
        json.dump(secdist, fp)
    monkeypatch.setenv('TAXI_SECDIST_SETTINGS', secdist_path)

    repo_root = os.path.join(tmp_dir, 'repo')
    create_git_repo(
        repo_root=os.path.join(repo_root, 'test-repo'),
        services_dir=services_dir_in_repo,
        service_name='test-service',
        migrations_path='postgresql/test-db/migrations',
    )

    cmd = [
        executable,
        executor_path,
        '--db_name',
        'test-db',
        '--service_name',
        'test-service',
        '--repository',
        'test-repo',
    ]
    if services_dir_in_args is not None:
        cmd.extend(['--services_dir', services_dir_in_args])
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, 'GIT_HOST': repo_root, 'PYTHONPATH': os.getcwd()},
    )
    process.wait()
    assert process.returncode == 0
