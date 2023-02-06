# -*- coding: utf-8 -*-
import shutil
import subprocess
import tempfile

import yatest.common as yc


def assert_dirs_equal(actual_dir, expected_dir):
    proc = subprocess.Popen(
        [
            'diff',
            actual_dir,
            expected_dir,
            '-u',
            '--ignore-trailing-space',
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    assert stdout == b'', stdout.decode()
    assert stderr == b'', stderr.decode()


def test_ok():
    expected_dir = yc.source_path('passport/backend/oauth/sql/expected')
    work_dir = tempfile.mkdtemp()
    yc.execute(
        [
            yc.binary_path('passport/backend/oauth/sql/bin/generate-sql'),
            work_dir,
        ],
        check_exit_code=True,
    )
    assert_dirs_equal(
        work_dir,
        expected_dir,
    )
    shutil.rmtree(work_dir)
