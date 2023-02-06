from passport.backend.tools.metrics.flock_utils import get_lock_name
import pytest


def test_get_lock_name_1():
    config_name = 'foo/bar/zar.ext'
    lock_name = get_lock_name('/tmp', config_name)
    assert lock_name == '/tmp/zar.lock'


def test_get_lock_name_2():
    config_name = 'foo/bar/zar'
    lock_name = get_lock_name('/tmp', config_name)
    assert lock_name == '/tmp/zar.lock'
