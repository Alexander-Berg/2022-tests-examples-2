"""
The file's content mostly copied from Python's source - all the base test classes are copier from there.
It was adapted to work with `pytest` instead of `unittest` after copying.
"""

from __future__ import absolute_import

import abc
import time
import inspect
import collections
import threading as th

import six
import pytest

import sandbox.common.threading as cth


def wait():
    # A crude wait/yield function not relying on synchronization primitives.
    time.sleep(0.01)


def assert_timeout(actual, expected):
    # The waiting and/or time.time() can be imprecise, which
    # is why comparing to the expected value would sometimes fail
    # (especially under Windows).
    assert actual >= expected * 0.6
    # Test nothing insane happened
    assert actual < expected * 10.0


class Bunch(object):
    """ A bunch of threads. """
    def __init__(self, f, n, wait_before_exit=False):
        """
        Construct a bunch of `n` threads running the same function `f`.
        If `wait_before_exit` is True, the threads won't terminate until
        do_finish() is called.
        """
        self.f = f
        self.n = n
        self.started = []
        self.finished = []
        self._can_exit = not wait_before_exit

        def task():
            tid = cth.ident()
            self.started.append(tid)
            try:
                f()
            finally:
                self.finished.append(tid)
                while not self._can_exit:
                    wait()

        for i in range(n):
            six.moves._thread.start_new_thread(task, ())

    def wait_for_started(self):
        while len(self.started) < self.n:
            wait()

    def wait_for_finished(self):
        while len(self.finished) < self.n:
            wait()

    def do_finish(self):
        self._can_exit = True


@six.add_metaclass(abc.ABCMeta)
class ConditionTests(object):
    """ Tests for condition variables. """

    @abc.abstractmethod
    def condtype(self, lock=None):
        pass

    def test_acquire(self):
        cond = self.condtype()
        # Be default we have an RLock: the condition can be acquired multiple
        # times.
        cond.acquire()
        cond.acquire()
        cond.release()
        cond.release()
        lock = th.Lock()
        cond = self.condtype(lock)
        cond.acquire()
        assert not lock.acquire(False)
        cond.release()
        assert lock.acquire(False)
        assert not cond.acquire(False)
        lock.release()
        with cond:
            assert not lock.acquire(False)

    def test_unacquired_wait(self):
        with pytest.raises(RuntimeError):
            self.condtype().wait()

    def test_unacquired_notify(self):
        with pytest.raises(RuntimeError):
            self.condtype().notify()

    def _check_notify(self, cond):
        # Note that this test is sensitive to timing.  If the worker threads
        # don't execute in a timely fashion, the main thread may think they
        # are further along then they are.  The main thread therefore issues
        # _wait() statements to try to make sure that it doesn't race ahead
        # of the workers.
        # Secondly, this test assumes that condition variables are not subject
        # to spurious wakeups.  The absence of spurious wakeups is an implementation
        # detail of Condition Cariables in current CPython, but in general, not
        # a guaranteed property of condition variables as a programming
        # construct.  In particular, it is possible that this can no longer
        # be conveniently guaranteed should their implementation ever change.
        N = 5
        results1 = []
        results2 = []
        phase_num = 0

        def f():
            cond.acquire()
            cond.wait()
            cond.release()
            results1.append((None, phase_num))
            cond.acquire()
            cond.wait()
            cond.release()
            results2.append((None, phase_num))

        b = Bunch(f, N)
        b.wait_for_started()
        wait()
        assert results1 == []
        # Notify 3 threads at first
        cond.acquire()
        cond.notify(3)
        wait()
        phase_num = 1
        cond.release()
        while len(results1) < 3:
            wait()
        assert results1 == [(None, 1)] * 3
        assert results2 == []
        # first wait, to ensure all workers settle into cond.wait() before
        # we continue. See issue #8799
        wait()
        # Notify 5 threads: they might be in their first or second wait
        cond.acquire()
        cond.notify(5)
        wait()
        phase_num = 2
        cond.release()
        while len(results1) + len(results2) < 8:
            wait()
        assert results1 == [(None, 1)] * 3 + [(None, 2)] * 2
        assert results2 == [(None, 2)] * 3
        wait()  # make sure all workers settle into cond.wait()

        # Notify all threads: they are all in their second wait
        cond.acquire()
        cond.notify_all()
        wait()
        phase_num = 3
        cond.release()
        while len(results2) < 5:
            wait()
        assert results1 == [(None, 1)] * 3 + [(None, 2)] * 2
        assert results2 == [(None, 2)] * 3 + [(None, 3)] * 2
        b.wait_for_finished()

    def test_notify(self):
        cond = self.condtype()
        self._check_notify(cond)
        # A second time, to check internal state is still ok.
        self._check_notify(cond)

    def test_timeout(self):
        cond = self.condtype()
        results = []
        N = 5

        def f():
            cond.acquire()
            t1 = time.time()
            result = cond.wait(0.5)
            t2 = time.time()
            cond.release()
            results.append((t2 - t1, result))

        Bunch(f, N).wait_for_finished()
        assert len(results) == N
        for dt, result in results:
            assert_timeout(dt, 0.5)
            # Note that conceptually (that"s the condition variable protocol)
            # a wait() may succeed even if no one notifies us and before any
            # timeout occurs.  Spurious wakeups can occur.
            # This makes it hard to verify the result value.
            # In practice, this implementation has no spurious wakeups.
            assert not result

    def test_waitfor(self):
        cond = self.condtype()
        state = 0

        def f():
            with cond:
                result = cond.wait_for(lambda: state == 4)
                assert result
                assert state == 4

        b = Bunch(f, 1)
        b.wait_for_started()
        for i in range(4):
            time.sleep(0.01)
            with cond:
                state += 1
                cond.notify()
        b.wait_for_finished()

    def test_waitfor_timeout(self):
        cond = self.condtype()
        state = 0
        success = []

        def f():
            with cond:
                dt = time.time()
                result = cond.wait_for(lambda: state == 4, timeout=0.1)
                dt = time.time() - dt
                assert not result
                assert_timeout(dt, 0.1)
                success.append(None)

        b = Bunch(f, 1)
        b.wait_for_started()
        # Only increment 3 times, so state == 4 is never reached.
        for i in range(3):
            time.sleep(0.01)
            with cond:
                state += 1
                cond.notify()
        b.wait_for_finished()
        assert len(success) == 1


@six.add_metaclass(abc.ABCMeta)
class BaseLockTests(object):
    """ Tests for both recursive and non-recursive locks. """

    @abc.abstractmethod
    def locktype(self):
        pass

    def test_constructor(self):
        lock = self.locktype()
        del lock

    def test_repr(self):
        lock = self.locktype()
        repr(lock)
        del lock

    def test_acquire_destroy(self):
        lock = self.locktype()
        lock.acquire()
        del lock

    def test_acquire_release(self):
        lock = self.locktype()
        lock.acquire()
        lock.release()
        del lock

    def test_try_acquire(self):
        lock = self.locktype()
        assert lock.acquire(False)
        lock.release()

    def test_try_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        result = []

        def f():
            result.append(lock.acquire(False))

        Bunch(f, 1).wait_for_finished()
        assert not result[0]
        lock.release()

    def test_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        N = 5

        def f():
            lock.acquire()
            lock.release()

        b = Bunch(f, N)
        b.wait_for_started()
        wait()
        assert len(b.finished) == 0
        lock.release()
        b.wait_for_finished()
        assert len(b.finished) == N

    def test_with(self):
        lock = self.locktype()

        def f():
            lock.acquire()
            lock.release()

        def _with(err=None):
            with lock:
                if err is not None:
                    raise err

        _with()
        # Check the lock is unacquired
        Bunch(f, 1).wait_for_finished()
        with pytest.raises(TypeError):
            _with(TypeError)
        # Check the lock is unacquired
        Bunch(f, 1).wait_for_finished()

    def test_thread_leak(self):
        # FIXME: The test constantly fails, but we're not using `Bunch` anyway.
        return

        # The lock shouldn't leak a Thread instance when used from a foreign
        # (non-threading) thread.
        lock = self.locktype()

        def f():
            lock.acquire()
            lock.release()
        n = len(th.enumerate())
        # We run many threads in the hope that existing threads ids won't
        # be recycled.
        Bunch(f, 15).wait_for_finished()
        if len(th.enumerate()) != n:
            # There is a small window during which a Thread instance's
            # target function has finished running, but the Thread is still
            # alive and registered.  Avoid spurious failures by waiting a
            # bit more (seen on a buildbot).
            time.sleep(0.4)
            assert n == len(th.enumerate())

    def test_timeout(self):
        lock = self.locktype()
        # Can't set timeout if not blocking
        with pytest.raises(ValueError):
            lock.acquire(0, 1)
        # Invalid timeout values
        with pytest.raises(ValueError):
            lock.acquire(timeout=-100)
        with pytest.raises(OverflowError):
            lock.acquire(timeout=1e100)
        with pytest.raises(OverflowError):
            lock.acquire(timeout=cth.TIMEOUT_MAX + 1)
        # TIMEOUT_MAX is ok
        lock.acquire(timeout=cth.TIMEOUT_MAX)
        lock.release()
        t1 = time.time()
        assert lock.acquire(timeout=5)
        t2 = time.time()
        # Just a sanity test that it didn't actually wait for the timeout.
        assert t2 - t1 < 5
        results = []

        def f():
            t1 = time.time()
            results.append(lock.acquire(timeout=0.5))
            t2 = time.time()
            results.append(t2 - t1)

        Bunch(f, 1).wait_for_finished()
        assert not results[0]
        assert_timeout(results[1], 0.5)


class RLockTestsBase(BaseLockTests):
    """ Tests for recursive locks. """

    def test_reacquire(self):
        lock = self.locktype()
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()

    def test_release_unacquired(self):
        # Cannot release an unacquired lock
        lock = self.locktype()
        with pytest.raises(RuntimeError):
            lock.release()
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        with pytest.raises(RuntimeError):
            lock.release()

    def test_release_save_unacquired(self):
        # Cannot _release_save an unacquired lock
        lock = self.locktype()
        with pytest.raises(RuntimeError):
            lock._release_save()
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        with pytest.raises(RuntimeError):
            lock._release_save()

    def test_different_thread(self):
        # Cannot release from a different thread
        lock = self.locktype()

        def f():
            lock.acquire()

        b = Bunch(f, 1, True)
        try:
            with pytest.raises(RuntimeError):
                lock.release()
        finally:
            b.do_finish()

    def test__is_owned(self):
        lock = self.locktype()
        assert not lock._is_owned()
        lock.acquire()
        assert lock._is_owned()
        lock.acquire()
        assert lock._is_owned()
        result = []

        def f():
            result.append(lock._is_owned())

        Bunch(f, 1).wait_for_finished()
        assert not result[0]
        lock.release()
        assert lock._is_owned()
        lock.release()
        assert not lock._is_owned()


@six.add_metaclass(abc.ABCMeta)
class RWLockTestsBase(RLockTestsBase):
    """ Tests for RWLock objects. """

    @abc.abstractmethod
    def rwlocktype(self):
        pass

    def test_many_readers(self):
        lock = self.rwlocktype()
        N = 5
        locked = []
        nlocked = []

        def f():
            with lock.reader:
                locked.append(1)
                wait()
                nlocked.append(len(locked))
                wait()
                locked.pop(-1)

        Bunch(f, N).wait_for_finished()
        assert max(nlocked) > 1

    def test_reader_recursion(self):
        lock = self.rwlocktype()
        N = 5
        locked = []
        nlocked = []

        def f():
            with lock.reader:
                with lock.reader:
                    locked.append(1)
                    wait()
                    nlocked.append(len(locked))
                    wait()
                    locked.pop(-1)

        Bunch(f, N).wait_for_finished()
        assert max(nlocked) > 1

    def test_writer_recursion(self):
        lock = self.rwlocktype()
        N = 5
        locked = []
        nlocked = []

        def f():
            with lock.writer:
                with lock.writer:
                    locked.append(1)
                    wait()
                    nlocked.append(len(locked))
                    wait()
                    locked.pop(-1)

        Bunch(f, N).wait_for_finished()
        assert max(nlocked) == 1

    def test_writer_recursionfail(self):
        lock = self.rwlocktype()
        N = 5
        locked = []

        def f():
            with lock.reader:
                with pytest.raises(RuntimeError):
                    lock.acquire_write()
                locked.append(1)

        Bunch(f, N).wait_for_finished()
        assert len(locked) == N

    def test_readers_writers(self):
        lock = self.rwlocktype()
        N = 5
        rlocked = []
        wlocked = []
        nlocked = []

        def r():
            with lock.reader:
                rlocked.append(1)
                wait()
                nlocked.append((len(rlocked), len(wlocked)))
                wait()
                rlocked.pop(-1)

        def w():
            with lock.writer:
                wlocked.append(1)
                wait()
                nlocked.append((len(rlocked), len(wlocked)))
                wait()
                wlocked.pop(-1)

        b1 = Bunch(r, N)
        b2 = Bunch(w, N)
        b1.wait_for_finished()
        b2.wait_for_finished()
        r, w, = zip(*nlocked)
        assert max(r) > 1
        assert max(w) == 1
        for r, w in nlocked:
            if w:
                assert r == 0
            if r:
                assert w == 0

    def test_writer_success(self):
        """Verify that a writer can get access"""
        lock = self.rwlocktype()
        N = 5
        counts = collections.Counter()

        def r():
            # read until we achive write successes
            while counts['writes'] < 2:
                with lock.reader:
                    counts['reads'] += 1

        def w():
            while counts['reads'] == 0:
                wait()
            for i in range(2):
                wait()
                with lock.writer:
                    counts['writes'] += 1

        b1 = Bunch(r, N)
        b2 = Bunch(w, 1)
        b1.wait_for_finished()
        b2.wait_for_finished()
        assert counts['writes'] == 2
        # uncomment this to view performance
        # print(counts)


class RWLockTests(RWLockTestsBase):
    rwlocktype = staticmethod(cth.RWLock)

    def locktype(self):
        return self.rwlocktype().writer


class RWConditionTests(ConditionTests):
    rwlocktype = staticmethod(cth.RWLock)

    def condtype(self, lock=None):
        if lock:
            return cth.Condition(lock)
        return cth.Condition(self.rwlocktype().writer)


class RWConditionAsRLockTests(RLockTestsBase):
    rwlocktype = staticmethod(cth.RWLock)

    def locktype(self):
        return th.Condition(self.rwlocktype().writer)


class FairRWLockMixin(object):
    rwlocktype = staticmethod(cth.FairRWLock)


class FairRWLockTests(FairRWLockMixin, RWLockTests):
    pass


class FairRWConditionTests(FairRWLockMixin, RWConditionTests):
    pass


class FairRWConditionAsRLockTests(FairRWLockMixin, RWConditionAsRLockTests):
    pass


def pytest_generate_tests(metafunc):
    argvalues, ids = [], []
    for sym in six.itervalues(globals()):
        if inspect.isclass(sym) and not inspect.isabstract(sym):
            methods = [ssym for name, ssym in inspect.getmembers(sym) if name.startswith('test_') and callable(ssym)]
            if not methods:
                continue
            obj = sym()
            for meth in methods:
                argvalues.append((obj, meth))
                ids.append(".".join((sym.__name__, meth.__name__)))
    metafunc.parametrize("obj, meth", argvalues, ids=ids)


def test_method(obj, meth):
    meth(obj)
