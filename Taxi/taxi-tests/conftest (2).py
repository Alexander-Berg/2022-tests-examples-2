import os
import pytest
import subprocess
import sys


@pytest.fixture
def black_format():
    def run(data: bytes) -> bytes:
        proc = subprocess.run(
            [sys.executable, '-m', 'black', '--line-length=79', '-'],
            check=True,
            stdout=subprocess.PIPE,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env={},
            input=data,
        )
        return proc.stdout

    return run
