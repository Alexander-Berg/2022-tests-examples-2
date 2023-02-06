from __future__ import absolute_import

import os
import time

import pytest

from sandbox.client import system


def test__privileged_subprocess():
    x = 0
    ppid = os.getpid()
    with system.PrivilegedSubprocess("child"):
        x += 1
        pid = os.getpid()
        assert ppid != pid
        with system.PrivilegedSubprocess("grandchild"):
            assert pid == os.getpid()
            with system.PrivilegedSubprocess(("child", "of", "grandchild")):
                assert pid == os.getpid()
    assert not x

    now = time.time()
    with pytest.raises(RuntimeError):
        with system.PrivilegedSubprocess("child"):
            time.sleep(1)
            raise RuntimeError("Check it!")
    assert time.time() - now >= 1
