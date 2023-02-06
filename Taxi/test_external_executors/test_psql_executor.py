import json
import os
import subprocess
import sys
from typing import List
from typing import Optional

import pytest

import scripts.app


PSQL_SCRIPT_CONTENT = """
SELECT 1 AS res;
"""

HELP_HEADER = """
usage: psql_request_script.py [-h] [--service-name SERVICE_NAME]
                              [--database-name DATABASE_NAME]
                              [--shards-ids SHARDS_IDS]
                              [--shard-ids SHARD_IDS [SHARD_IDS ...]]
                              [--psql-options PSQL_OPTIONS]
                              filename
"""
BAD_PSQL_ARG_MESSAGE_TMPL = (
    HELP_HEADER + 'psql_request_script.py: error: argument --psql-options: '
    'Illegal or invalid psql param or flag "{}". '
    'Allowed flags: [\'-a\', \'--echo-all\', \'-A\', \'--no-align\', \'-e\', '
    '\'--echo-queries\', \'-E\', \'--echo-hidden\', \'-l\', \'--list\', '
    '\'-n\', \'--no-readline\', \'-q\', \'--quiet\', \'-t\', '
    '\'--tuples-only\', \'-V\', \'--version\', \'-X\', \'--no-psqlrc\', '
    '\'-z\', \'--field-separator-zero\', \'-1\', '
    '\'--single-transaction\'], Allowed params: [\'-v\']'
)


@pytest.fixture(name='secdist')
def _secdist(simple_secdist):
    db_conn = simple_secdist['postgresql_settings']['databases']['test'][0]
    simple_secdist['postgresql_settings']['databases']['test'].append(
        {**db_conn, 'shard_number': 1},
    )
    return simple_secdist


@pytest.mark.parametrize(
    'executable',
    [
        pytest.param('python2.7', id='py2_compat'),
        pytest.param('python3.6', id='py3.6_compat'),
        pytest.param('python3.6', id='py3.7_compat'),
        pytest.param(sys.executable, id='current_host_compat'),
    ],
)
@pytest.mark.parametrize(
    'cmd_ext,return_code,expected_stderr,non_empty_stdout',
    [
        pytest.param([], 0, '', True, id='empty_cmd'),
        pytest.param(['--shards-ids=1'], 0, '', True, id='one_shards_ids'),
        pytest.param(['--shards-ids=0,1'], 0, '', True, id='two_shards_ids'),
        pytest.param(
            ['--shards-ids=0,1,2'],
            0,
            'WARN: Specified non existing shards',
            True,
            id='extra_shards_ids',
        ),
        pytest.param(
            ['--shards-ids', '0,1', '--shard-ids', '0', '1'],
            1,
            (
                'FATAL: Conflicting arguments "--shard-ids" '
                'and "--shards-ids". '
                'Use only "--shards-ids" instead.'
            ),
            False,
            id='conflicting_shards_arguments',
        ),
        pytest.param(
            ['--shard-ids', '0', '1'],
            0,
            (
                'WARN: "--shard-ids" argument is deprecated. '
                'Use "--shards-ids" instead.'
            ),
            True,
            id='deprecation_warning',
        ),
        pytest.param(
            ['--psql-options=--echo-all -A'],
            0,
            '',
            True,
            id='psql_options_check',
        ),
        pytest.param(
            ['--psql-options=-v some_arg=\'some_val\''],
            0,
            '',
            True,
            id='psql_param_"-v"_check',
        ),
        pytest.param(
            ['--psql-options=-v'],
            2,
            BAD_PSQL_ARG_MESSAGE_TMPL.format('-v').strip(),
            False,
            id='psql_invalid_param_check',
        ),
        pytest.param(
            ['--psql-options=-v some_arg='],
            0,
            '',
            True,
            id='psql_param_"-v"_unset_var',
        ),
    ],
)
async def test_psql_executor(
        monkeypatch,
        tmp_dir,
        secdist,
        executable,
        cmd_ext,
        return_code,
        expected_stderr,
        non_empty_stdout,
):
    executor_path = os.path.join(
        scripts.app.BASE_DIR,
        '..',
        'debian',
        'scripts-executors',
        'psql_request_script.py',
    )
    secdist_path = os.path.join(tmp_dir, 'secdist.json')
    with open(secdist_path, 'w') as fp:
        json.dump(secdist, fp)
    monkeypatch.setenv('TAXI_SECDIST_SETTINGS', secdist_path)

    psql_script_path = os.path.join(tmp_dir, 'script.sql')
    with open(psql_script_path, 'w') as fp:
        fp.write(PSQL_SCRIPT_CONTENT)

    cmd = [
        executable,
        executor_path,
        psql_script_path,
        '--database-name',
        'test',
        *cmd_ext,
    ]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    process.wait()

    assert process.stderr.read().decode().strip() == expected_stderr
    if non_empty_stdout:
        assert process.stdout.read()
    else:
        assert not process.stdout.read()
    assert process.returncode == return_code


def case(
        sql_content: str,
        cmd_ext: Optional[List[str]] = None,
        expected_stdout: Optional[str] = None,
        expected_stderr: Optional[str] = None,
        res_code: int = 0,
        id_=None,
):
    return pytest.param(
        sql_content,
        cmd_ext or [],
        expected_stdout or '',
        expected_stderr or '',
        res_code,
        id=id_,
    )


@pytest.mark.parametrize(
    'executable',
    [
        pytest.param('python2.7', id='py2_compat'),
        pytest.param('python3.6', id='py3.6_compat'),
        pytest.param('python3.7', id='py3.7_compat'),
        pytest.param(sys.executable, id='current_host_compat'),
    ],
)
@pytest.mark.parametrize(
    'sql_content, cmd_ext, expected_stdout, expected_stderr, res_code',
    [
        case(
            PSQL_SCRIPT_CONTENT,
            ['--psql-options', '--echo-all -A'],
            """
SELECT 1 AS res;
res
1
(1 row)
INFO: Running command ['psql', '-f', '{tmp_dir}/script.sql', '--echo-all', '-A', '--set=ON_ERROR_STOP=on', '<DSN>'] for shard 0 of database test
""".lstrip(),  # noqa: E501 (line too long)
            id_='psql_options_through_separate_key-value_check',
        ),
        case(
            PSQL_SCRIPT_CONTENT,
            ['--psql-options', '--echo-all -A', '--shards-ids', '0,1'],
            """
SELECT 1 AS res;
res
1
(1 row)
SELECT 1 AS res;
res
1
(1 row)
INFO: Running command ['psql', '-f', '{tmp_dir}/script.sql', '--echo-all', '-A', '--set=ON_ERROR_STOP=on', '<DSN>'] for shard 0 of database test
INFO: Running command ['psql', '-f', '{tmp_dir}/script.sql', '--echo-all', '-A', '--set=ON_ERROR_STOP=on', '<DSN>'] for shard 1 of database test
""".lstrip(),  # noqa: E501 (line too long)
            id_='psql_options_through_separate_key-value_check',
        ),
        case(
            'SELECT N;',
            expected_stdout="""
INFO: Running command ['psql', '-f', '{tmp_dir}/script.sql', '--set=ON_ERROR_STOP=on', '<DSN>'] for shard 0 of database test
""".lstrip(),  # noqa: E501 (line too long)
            expected_stderr="""
psql:{tmp_dir}/script.sql:1: ERROR:  column "n" does not exist
LINE 1: SELECT N;
               ^
FATAL: Command returned exit code 3
""".lstrip(),
            res_code=3,
            id_='bad sql syntax',
        ),
        case(
            'SET statement_timeout=1; SELECT pg_sleep(2);',
            expected_stdout="""
SET
INFO: Running command ['psql', '-f', '{tmp_dir}/script.sql', '--set=ON_ERROR_STOP=on', '<DSN>'] for shard 0 of database test
""".lstrip(),  # noqa: E501 (line too long)
            expected_stderr="""
psql:{tmp_dir}/script.sql:1: ERROR:  canceling statement due to statement timeout
FATAL: Command returned exit code 3
""".lstrip(),  # noqa: E501 (line too long)
            res_code=3,
            id_='statement timeout',
        ),
    ],
)
async def test_psql_executor_for_new_args(
        monkeypatch,
        tmp_dir,
        secdist,
        executable,
        sql_content,
        cmd_ext,
        expected_stdout,
        expected_stderr,
        res_code,
):
    executor_path = os.path.join(
        scripts.app.BASE_DIR,
        '..',
        'debian',
        'scripts-executors',
        'psql_request_script.py',
    )
    secdist_path = os.path.join(tmp_dir, 'secdist.json')
    with open(secdist_path, 'w') as fp:
        json.dump(secdist, fp)
    monkeypatch.setenv('TAXI_SECDIST_SETTINGS', secdist_path)

    psql_script_path = os.path.join(tmp_dir, 'script.sql')
    with open(psql_script_path, 'w') as fp:
        fp.write(sql_content)

    cmd = [
        executable,
        executor_path,
        psql_script_path,
        '--database-name',
        'test',
        *cmd_ext,
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        text=True,
    )

    stdout, stderr = process.communicate()
    assert process.returncode == res_code

    assert stdout == expected_stdout.format(tmp_dir=tmp_dir)
    assert stderr == expected_stderr.format(tmp_dir=tmp_dir)
