import pytest

from metrika.pylib.test_utils.mock_kazoo import get_zk

import metrika.pylib.zkconnect
from metrika.pylib.lock import ZLock


class LockTestError(Exception):
    pass


def test_init(monkeypatch):
    monkeypatch.setattr(metrika.pylib.zkconnect, 'get_zk', get_zk)
    with ZLock('/test/lock/path') as lock:
        assert isinstance(lock, ZLock)


def test_zk_start_called_in_enter(monkeypatch):
    def mock_start_zk(*args, **kwargs):
        raise LockTestError

    monkeypatch.setattr(metrika.pylib.zkconnect, 'get_zk', get_zk)
    lock = ZLock('/test/lock/path')

    monkeypatch.setattr(lock.zk, 'start', mock_start_zk)

    with pytest.raises(LockTestError):
        with lock:
            pass


def test_zk_stop_called_in_enter(monkeypatch):
    def mock_stop_zk(*args, **kwargs):
        raise LockTestError

    monkeypatch.setattr(metrika.pylib.zkconnect, 'get_zk', get_zk)
    lock = ZLock('/test/lock/path')

    monkeypatch.setattr(lock.zk, 'stop', mock_stop_zk)

    with pytest.raises(LockTestError):
        with lock:
            pass
