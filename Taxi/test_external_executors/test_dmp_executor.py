import os.path
import subprocess

import pytest

import scripts.app

DMP_PROJECTS_PATH = '/usr/lib/yandex/taxi-dmp-{}'
BIN = 'python3.7'


def create_test_script(script_path):
    os.makedirs(os.path.dirname(script_path))

    with open(os.path.join(script_path), 'w') as fp:
        fp.write('import os; print(os.environ[\'PYTHONPATH\'])')


@pytest.mark.parametrize(
    'script_path, ext_args, expected_etl_service, expected_exit_code',
    [
        ('taxi_dmp_taxi_etl/core_etl/script.py', '', 'core-etl', 0),
        (
            'taxi/dmp/dwh-migrations/taxi_dmp_taxi_etl/core_etl/script.py',
            '',
            'core-etl',
            0,
        ),
        (
            'taxi_dmp_taxi_etl/migration/script.py',
            '--start_date=20190101 --end_date=20200101',
            'taxi-etl',
            0,
        ),
        (
            'taxi_dmp_eda_etl/migration/folder/script.py',
            '2010-01 abc',
            'eda-etl',
            0,
        ),
        (
            'taxi/dmp/dwh-migrations/taxi_dmp_eda_etl/migration/script.py',
            '2010-01 abc',
            'eda-etl',
            0,
        ),
        ('eda_etl/migration/folder/script.py', '2010-01 abc', None, 1),
    ],
)
async def test_dmp_executor(
        tmp_dir,
        script_path,
        ext_args,
        expected_etl_service,
        expected_exit_code,
):
    if expected_etl_service:
        expected = DMP_PROJECTS_PATH.format(expected_etl_service)
    else:
        expected = None

    executor_path = os.path.join(
        scripts.app.BASE_DIR,
        '..',
        'debian',
        'scripts-executors',
        'dmp_runner.py',
    )

    create_test_script(os.path.join(tmp_dir, script_path))

    cmd = [BIN, executor_path, script_path, *ext_args.split()]
    env = os.environ.copy()
    env['DMP_RUNNER_OS_USER'] = ''
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        cwd=tmp_dir,
        stderr=subprocess.PIPE,
        env=env,
    )
    process.wait()
    assert (
        process.returncode == expected_exit_code
    ), process.stderr.read().decode()
    if expected:
        result = process.stdout.read().decode()
        assert expected == result[: len(expected)]
