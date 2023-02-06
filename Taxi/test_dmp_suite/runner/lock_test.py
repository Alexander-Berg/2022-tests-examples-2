# coding: utf-8
import errno
import fcntl
import functools
import os
import subprocess
import sys
import threading

import pytest
from mock import MagicMock

from dmp_suite.lock.base import LocalLock, ComposeLock, AbstractLock, \
    ProlongableComposeLock, ProlongableLocalLock, Autoprolong, \
    ProlongableBatchLock, BatchLock
from dmp_suite.runner import NotAcquiredLockError
from test_dmp_suite.runner.runner_test import temp_dir


def _get_lock_file_name(temp_dir, path):
    return os.path.join(
        temp_dir,
        path.replace('/', '_') + '.lck'
    )


def script_is_lock(temp_dir, script):
    it_was_locked = False
    with open(_get_lock_file_name(temp_dir, script), 'a+') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK:
                it_was_locked = True
        finally:
            if not it_was_locked:
                fcntl.flock(f, fcntl.LOCK_UN)
    return it_was_locked


@pytest.fixture
def lock_provider(temp_dir):
    return functools.partial(
        BatchLock,
        functools.partial(LocalLock, temp_dir)
    )


class TestBatchLock(object):
    batch_lock_args = dict()
    wait_lock_args = dict(wait_limit_sec=0.1, sleep_limit_sec=0.1)

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock(self, temp_dir, lock_provider, lock_args):
        with lock_provider('path1', **lock_args):
            assert script_is_lock(temp_dir, 'path1') is True

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_raise_interface(self, temp_dir, lock_provider, lock_args):
        assert script_is_lock(temp_dir, 'path1') is False
        with lock_provider('path1', **lock_args):
            assert script_is_lock(temp_dir, 'path1') is True
            with pytest.raises(NotAcquiredLockError):
                with lock_provider('path1', **lock_args):
                    assert True is False  # it must not execute
            assert script_is_lock(temp_dir, 'path1') is True
        assert script_is_lock(temp_dir, 'path1') is False

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_each_script(self, temp_dir, lock_provider, lock_args):
        with lock_provider(*('path1', 'path2'), **lock_args):
            assert script_is_lock(temp_dir, 'path1') is True
            assert script_is_lock(temp_dir, 'path2') is True

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_none_first(self, temp_dir, lock_provider, lock_args):
        with lock_provider(*(None, 'path2'), **lock_args):
            assert script_is_lock(temp_dir, 'path2') is True

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_none_last(self, temp_dir, lock_provider, lock_args):
        with lock_provider(*('path2', None), **lock_args):
            assert script_is_lock(temp_dir, 'path2') is True

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_partial_realise(self, temp_dir, lock_provider, lock_args):
        locker = lock_provider(*('path1', 'path2'), **lock_args)
        with locker:
            locker.release_keys('path1')
            assert script_is_lock(temp_dir, 'path1') is False
            assert script_is_lock(temp_dir, 'path2') is True

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_lock_not_realised_script_if_exists_another(self, temp_dir, lock_provider, lock_args):
        locker = lock_provider(*('path1', 'path2', 'path1'), **lock_args)
        with locker:
            locker.release_keys('path1')
            assert script_is_lock(temp_dir, 'path1') is True
            assert script_is_lock(temp_dir, 'path2') is True


    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_full_realise_if_has_been_lock(self, temp_dir, lock_provider, lock_args):
        with lock_provider('path2', **lock_args):
            assert script_is_lock(temp_dir, 'path1') is False
            with pytest.raises(NotAcquiredLockError):
                with lock_provider(*('path1', 'path2'), **lock_args):
                    assert False is True
            assert script_is_lock(temp_dir, 'path1') is False
            assert script_is_lock(temp_dir, 'path2') is True
        assert script_is_lock(temp_dir, 'path2') is False


    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_full_realise_if_raise(self, temp_dir, lock_provider, lock_args):
        locker = lock_provider(*('path2', 'path1', 'path2'), **lock_args)
        with pytest.raises(ValueError):
            with locker:
                raise ValueError()
        assert script_is_lock(temp_dir, 'path2') is False
        assert script_is_lock(temp_dir, 'path1') is False

    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_has_locks(self, temp_dir, lock_provider, lock_args):
        locker = lock_provider(*('path1', 'path2', 'path1'), **lock_args)
        assert not locker.has_locks()
        with locker:
            assert locker.has_locks()
            locker.release_keys('path1')
            assert locker.has_locks()
            locker.release_keys('path2')
            assert locker.has_locks()
            locker.release_keys('path1')
            assert not locker.has_locks()
        assert not locker.has_locks()

    @pytest.mark.skipif(
        condition='linux' not in sys.platform.lower(),
        reason='OS is not supported'
    )
    @pytest.mark.parametrize('lock_args', [batch_lock_args, wait_lock_args])
    def test_flock_compatibility(self, temp_dir, lock_provider, lock_args):
        lock_file = os.path.join(temp_dir, 'success.lck')
        with lock_provider('success', **lock_args):
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.check_call([
                    'flock', '-w', '0', lock_file, 'sleep', '0.01'
                ])

    @pytest.mark.skip(reason='не удалось выяснить почему ингода тест падает,'
                             'при необходимости запустить руками')
    def test_lock_timeout(self, temp_dir, lock_provider):
        wait_args = dict(wait_limit_sec=0.2, sleep_limit_sec=0.01)

        with lock_provider('path1', **wait_args) as locker:
            assert script_is_lock(temp_dir, 'path1') is True
            threading.Timer(0.05, lambda: locker.release_keys('path1')).start()

            with lock_provider(*('path1', 'path2'), **wait_args):
                assert script_is_lock(temp_dir, 'path2') is True
                assert script_is_lock(temp_dir, 'path1') is True


class HelpLock(AbstractLock):
    def __init__(self, raise_exc=False):
        self._lock = threading.Lock()
        self.raise_exc=raise_exc

    def get_lock_description(self):
        return 'help lock'

    def acquire(self):
        if self.raise_exc:
             raise ValueError('test')
        else:
            return self._lock.acquire(False)

    def release(self):
        if self.raise_exc:
             raise ValueError('test')
        else:
            return self._lock.release()

    def locked(self):
        return self._lock.locked()


class HelpProlonableLock(HelpLock):
    timeout = 1
    prolong_frequency = 5

    def __init__(self, raise_exc=False, prolong_res=True):
        super(HelpProlonableLock, self).__init__(raise_exc)
        self.prolong_res = prolong_res

    def prolong(self):
        if self.raise_exc:
            raise ValueError('test')
        else:
            return self.prolong_res


class TestProlongableBatchLock(object):
    def test_prolong(self):
        def lock_provider(key, timeout, frequency):
            return HelpProlonableLock()

        lock = ProlongableBatchLock(lock_provider, 'key1', 'key2', 'key1')
        assert not lock.prolong()

        with lock:
            assert lock.prolong()
            lock.release_keys('key1')
            assert lock.prolong()
            lock.release_keys('key2')
            assert lock.prolong()

        assert not lock.prolong()

    def test_prolong(self):

        def lock_provider(key, timeout, frequency):
            return HelpProlonableLock(prolong_res=key != 'key2')

        lock = ProlongableBatchLock(lock_provider, 'key1', 'key2', 'key1')
        assert not lock.prolong()

        with lock:
            assert not lock.prolong()
            lock.release_keys('key1')
            assert not lock.prolong()
            lock.release_keys('key2')
            assert lock.prolong()

        assert not lock.prolong()


class TestComposeLock(object):
    help_lock_class = HelpLock
    compose_lock_class = ComposeLock

    def test_acquire_all(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)

        assert lock.acquire()
        assert primary_lock.locked()
        assert secondary_lock.locked()
        lock.release()
        assert not primary_lock.locked()
        assert not secondary_lock.locked()

    def test_acquire_context_manager(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()

        with self.compose_lock_class(primary_lock, secondary_lock):
            assert primary_lock.locked()
            assert secondary_lock.locked()
        assert not primary_lock.locked()
        assert not secondary_lock.locked()

    def test_no_primary_lock(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)

        assert primary_lock.acquire()
        assert not lock.acquire()
        assert not secondary_lock.locked()
        primary_lock.release()
        assert not primary_lock.locked()
        assert not secondary_lock.locked()

    def test_no_secondary_lock(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)

        assert secondary_lock.acquire()
        assert lock.acquire()
        assert primary_lock.locked()
        secondary_lock.release()
        lock.release()
        assert not primary_lock.locked()
        assert not secondary_lock.locked()

    def test_secondary_lock_raise(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class(raise_exc=True)
        lock = self.compose_lock_class(primary_lock, secondary_lock)

        assert lock.acquire()
        assert primary_lock.locked()
        assert not secondary_lock.locked()
        lock.release()
        assert not primary_lock.locked()
        assert not secondary_lock.locked()

    def test_repr(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        assert ComposeLock.__name__ in repr(lock)


class TestProlongableComposeLock(TestComposeLock):
    help_lock_class = HelpProlonableLock
    compose_lock_class = ProlongableComposeLock

    def test_incompatible_timeout(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        secondary_lock.timeout = 3

        with pytest.raises(ValueError):
            self.compose_lock_class(primary_lock, secondary_lock)

    def test_incompatible_prolong_frequency(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        secondary_lock.prolong_frequency = 3

        with pytest.raises(ValueError):
            self.compose_lock_class(primary_lock, secondary_lock)

    def test_timeout_args(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)

        assert lock.timeout == primary_lock.timeout
        assert lock.prolong_frequency == primary_lock.prolong_frequency
        assert lock.timeout == secondary_lock.timeout
        assert lock.prolong_frequency == secondary_lock.prolong_frequency

    def test_prolong(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        assert lock.prolong()

    def test_no_prolong_secondary(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        secondary_lock.prolong = MagicMock(return_value=False)
        assert lock.prolong()
        secondary_lock.prolong.assert_called_once()

    def test_raise_prolong_secondary(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class(raise_exc=True)
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        assert lock.prolong()

    def test_no_prolong_primary(self):
        primary_lock = self.help_lock_class()
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        primary_lock.prolong = MagicMock(return_value=False)
        secondary_lock.prolong = MagicMock()

        assert not lock.prolong()
        secondary_lock.prolong.assert_not_called()

    def test_raise_prolong_primary(self):
        primary_lock = self.help_lock_class(raise_exc=True)
        secondary_lock = self.help_lock_class()
        lock = self.compose_lock_class(primary_lock, secondary_lock)
        secondary_lock.prolong = MagicMock()

        with pytest.raises(ValueError):
            lock.prolong()
        secondary_lock.prolong.assert_not_called()


class TestProlongableLocalLock(object):
    def test_repr(self, temp_dir):
        lock = ProlongableLocalLock(temp_dir, 'test_key', 1, 1)
        assert ProlongableLocalLock.__name__ in repr(lock)

    @pytest.mark.parametrize('timeout, prolong_frequency, exc', [
        (1, 1, False), (0, 1, True), (None, 1, True), (-1, 1, True),
        (1, None, True), (1, 0, True), (1, -1, True)
    ])
    def test_init(self, temp_dir, timeout, prolong_frequency, exc):
        if exc:
            with pytest.raises(ValueError):
                ProlongableLocalLock(
                    lock_dir=temp_dir, key='test_key',
                    timeout=timeout, prolong_frequency=prolong_frequency
                )
        else:
            lock = ProlongableLocalLock(
                    lock_dir=temp_dir, key='test_key',
                    timeout=timeout, prolong_frequency=prolong_frequency
                )

            assert lock.timeout
            assert lock.prolong_frequency

    def test_prolong(self, temp_dir):
        lock = ProlongableLocalLock(
            lock_dir=temp_dir, key='test_key', timeout=1, prolong_frequency=5
        )
        assert not lock.prolong()

        with lock:
            assert lock.prolong()

        assert not lock.prolong()


class TestAutoprolong(object):

    def test_success_prolong(self):
        ev = threading.Event()
        context_ = type('', (), {})()
        context_.state = None

        def prolong_callback():
            context_.state = True
            ev.set()
            return True

        def fail_callback():
            context_.state = False

        with Autoprolong(
            timeout=0.05, frequency=5,
            prolong_callback=prolong_callback,
            fail_callback=fail_callback) as autoprolog:
            assert not autoprolog.is_stopped()
            assert ev.wait(0.03)
        assert context_.state
        assert autoprolog.is_stopped()

    def test_error_prolong(self):
        ev = threading.Event()
        context_ = type('', (), {})()
        context_.state = None

        def fail_prolong_callback():
            raise RuntimeError()

        def fail_callback():
            context_.state = False

        with Autoprolong(
                timeout=0.05, frequency=5,
                prolong_callback=fail_prolong_callback,
                fail_callback=fail_callback):
            assert not ev.wait(0.03)
        assert context_.state is False

    def test_error_limit_prolong(self):
        ev = threading.Event()
        context_ = type('', (), {})()
        context_.state = None

        def fail_prolong_callback():
            raise RuntimeError()

        def fail_callback():
            ev.set()
            context_.state = False

        with Autoprolong(
                timeout=0.05, frequency=5,
                prolong_callback=fail_prolong_callback,
                fail_callback=fail_callback):
            assert ev.wait(0.1)
        assert context_.state is False

    def test_false_prolong(self):
        ev = threading.Event()
        context_ = type('', (), {})()
        context_.state = None

        def prolong_callback():
            ev.set()
            return False

        def fail_callback():
            context_.state = False

        with Autoprolong(
                timeout=0.05, frequency=5,
                prolong_callback=prolong_callback,
                fail_callback=fail_callback):
            assert ev.wait(0.03)
        assert context_.state is False
