# pylint: disable=protected-access
import asyncio
import contextlib
import os
import sys
from unittest import mock

import pytest

from taxi.scripts import async_os
from taxi.scripts import db as scripts_db
from taxi.scripts import exceptions
from tests.taxi import scripts

from . import test_os


async def test_async_subprocess():
    proc = await asyncio.create_subprocess_exec(
        *[sys.executable, '-c', '1/0'],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        env={},
    )
    await proc.wait()
    assert proc.returncode
    stdout = await proc.stdout.read()
    stderr = await proc.stderr.read()

    assert stdout == b''
    assert stderr == (
        b'Traceback (most recent call last):\n  '
        b'File "<string>", line 1, in <module>\n'
        b'ZeroDivisionError: division by zero\n'
    )


@pytest.mark.parametrize(
    'arg_set, expected_exit_code', [('fail', 1), ('success', 0)],
)
async def test_run_script_command(
        tmpdir, arg_set, expected_exit_code, dump_scripts_client,
):
    with open(
            scripts.get_static_filepath(os.path.join(arg_set, 'args')), 'r',
    ) as args_file:
        script_args = args_file.read().split()

    script = test_os._get_script_with_path_in_project(
        test_os.TEST_SCRIPT_FILENAME,
        status=scripts_db.ScriptStatus.RUNNING,
        arguments=script_args,
    )

    working_area = test_os._create_script_src_dir(
        tmpdir, script, test_os.TEST_SCRIPT_FILENAME,
    )

    with mock.patch('taxi.scripts.settings.WORKING_AREA_DIR', working_area):
        exit_code, _ = await async_os.run_script_command(
            script, dump_scripts_client,
        )

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


async def test_cant_create_async_subprocess(tmpdir, dump_scripts_client):
    with contextlib.ExitStack() as stack:
        script = test_os._get_script_with_path_in_project(
            test_os.TEST_SCRIPT_FILENAME,
        )
        working_area = test_os._create_script_src_dir(
            tmpdir, script, test_os.TEST_SCRIPT_FILENAME,
        )

        stack.enter_context(
            mock.patch(
                'taxi.scripts.async_os.asyncio.subprocess.Process',
                side_effect=OSError,
            ),
        )
        stack.enter_context(
            mock.patch(
                'taxi.scripts.os.settings.WORKING_AREA_DIR', working_area,
            ),
        )
        stack.enter_context(pytest.raises(exceptions.ExecutionError))

        await async_os.run_script_command(script, dump_scripts_client)
