# coding: utf-8 -*-

from mock import (
    call,
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.utils import (
    Envs,
    FooBarSplitter,
    round_robin_iter,
    Throttler,
    ThrottlerControl,
)


TEST_SIGNUM1 = 1
TEST_SIGNUM2 = 2


def test_foo_bar_splitter():
    eq_(FooBarSplitter([]).split(), ([], []))
    eq_(FooBarSplitter([0]).split(), ([], [0]))
    eq_(FooBarSplitter([1]).split(), ([1], []))
    eq_(FooBarSplitter([0, 1]).split(), ([1], [0]))
    eq_(FooBarSplitter([1, 0]).split(), ([1], [0]))
    eq_(FooBarSplitter([0, 1, 2]).split(), ([1], [0, 2]))
    eq_(FooBarSplitter([0, 1, 2, 3]).split(), ([1, 3], [0, 2]))
    eq_(FooBarSplitter([2, 1, 0]).split(), ([1], [2, 0]))
    eq_(FooBarSplitter([3, 2, 1, 0]).split(), ([3, 1], [2, 0]))
    eq_(FooBarSplitter([0, 2, 4, 6]).split(), ([], [0, 2, 4, 6]))
    eq_(FooBarSplitter([1, 3, 5]).split(), ([1, 3, 5], []))
    eq_(FooBarSplitter([2, 1, 4, 3, 6, 5]).split(), ([1, 3, 5], [2, 4, 6]))


class TestThrottler(TestCase):
    def setUp(self):
        super(TestThrottler, self).setUp()
        self._throttler = Throttler(1)
        self._get_time_patch = patch.object(self._throttler, '_get_time')
        self._sleep_patch = patch.object(
            self._throttler,
            '_sleep',
            Mock(side_effect=self._sleep),
        )

        self._get_time_patch.start()
        self._sleep_patch.start()

    def tearDown(self):
        self._get_time_patch.stop()
        self._sleep_patch.stop()
        super(TestThrottler, self).tearDown()

    def _sleep(self, seconds):
        self._throttler._get_time.return_value += seconds

    def _let_rps(self, rps):
        self._throttler._rps = float(rps)

    def _let_calls(self, calls):
        self._throttler._latest_moment = None if not calls else calls[-1]

    def _let_now(self, timestamp):
        self._throttler._get_time.return_value = timestamp

    def _throttle(self, events_passed=1):
        self._throttler.throttle(events_passed=events_passed)

    def _assert_throttled_for(self, seconds):
        if seconds > 0.:
            self._throttler._sleep.assert_called_once_with(seconds)
        else:
            eq_(self._throttler._sleep.call_count, 0)

    def _assert_latest_call_equals(self, latest_moment):
        eq_(self._throttler._latest_moment, latest_moment)

    def test_no_calls(self):
        self._let_rps(.001)
        self._let_calls([])
        self._let_now(0.)

        self._throttle()

        self._assert_throttled_for(0.)
        self._assert_latest_call_equals(0.)

    def test_calls_hit_limit(self):
        self._let_rps(1.)
        self._let_calls([0.])
        self._let_now(0.)

        self._throttle()

        self._assert_throttled_for(1.)
        self._assert_latest_call_equals(1.)

    def test_calls_hit_limit_multiple_requests(self):
        self._let_rps(2)
        self._let_calls([0.])
        self._let_now(0.)

        self._throttle(2)

        self._assert_throttled_for(1.)
        self._assert_latest_call_equals(1.)

    def test_some_calls_done_but_limit_not_hit(self):
        self._let_rps(2.)
        self._let_calls([0.])
        self._let_now(0.)

        self._throttle()

        self._assert_throttled_for(.5)
        self._assert_latest_call_equals(.5)

    def test_multiple_calls_done_but_limit_not_hit(self):
        self._let_rps(4)
        self._let_calls([0.])
        self._let_now(0.)

        self._throttle(3)

        self._assert_throttled_for(0.75)
        self._assert_latest_call_equals(0.75)

    def test_some_calls_done_but_limit_not_hit__deferred_call(self):
        self._let_rps(2.)
        self._let_calls([0.])
        self._let_now(.1)

        self._throttle()

        self._assert_throttled_for(.4)
        self._assert_latest_call_equals(.5)

    def test_multiple_calls_done_but_limit_not_hit__deferred_call(self):
        self._let_rps(4.)
        self._let_calls([0.])
        self._let_now(.1)

        self._throttle(3)

        self._assert_throttled_for(.65)
        self._assert_latest_call_equals(.75)

    def test_calls_very_old(self):
        self._let_rps(1.)
        self._let_calls([0.])
        self._let_now(1.)

        self._throttle()

        self._assert_throttled_for(0.)
        self._assert_latest_call_equals(1.)

    def test_calls_very_old_multiple_calls(self):
        self._let_rps(2.)
        self._let_calls([0.])
        self._let_now(1.)

        self._throttle(2)

        self._assert_throttled_for(0.)
        self._assert_latest_call_equals(1.)

    def test_calls_very_very_old(self):
        self._let_rps(1.)
        self._let_calls([0., .5, 1.])
        self._let_now(5.)

        self._throttle()

        self._assert_throttled_for(0.)
        self._assert_latest_call_equals(5.)

    def test_calls_very_very_old_multiple_calls(self):
        self._let_rps(2.)
        self._let_calls([0., .5, 1.])
        self._let_now(5.)

        self._throttle(2)

        self._assert_throttled_for(0.)
        self._assert_latest_call_equals(5.)

    def test_very_low_rps(self):
        self._let_rps(.5)
        self._let_calls([0.])
        self._let_now(.3)

        self._throttle()

        self._assert_throttled_for(1.7)
        self._assert_latest_call_equals(2.)

    def test_very_low_rps_multiple_call(self):
        self._let_rps(.5)
        self._let_calls([0.])
        self._let_now(.3)

        self._throttle(2)

        self._assert_throttled_for(3.7)
        self._assert_latest_call_equals(4.)


class TestThrottlerControl(TestCase):
    def setUp(self):
        super(TestThrottlerControl, self).setUp()
        self._throttler = Throttler(1)
        self._control = ThrottlerControl(
            self._throttler,
            decrease_signum=TEST_SIGNUM1,
            increase_signum=TEST_SIGNUM2,
        )

    def test_decrease(self):
        self._control.handle_signal(TEST_SIGNUM1, frame=None)
        eq_(self._throttler._rps, 0.9)

    def test_increase(self):
        self._control.handle_signal(TEST_SIGNUM2, frame=None)
        eq_(self._throttler._rps, 1.1)

    def test_setup(self):
        with patch.object(self._control, '_signal') as signal_mock:
            self._control.setup()

        eq_(
            signal_mock.mock_calls,
            [
                call(TEST_SIGNUM1, self._control.handle_signal),
                call(TEST_SIGNUM2, self._control.handle_signal),
            ],
        )


class TestRoundRobinIter(TestCase):
    def round_robin_iter(self, iterables):
        return list(round_robin_iter(iterables))

    def test_empty(self):
        self.assertEqual(
            self.round_robin_iter(list()),
            list(),
        )

    def test_single(self):
        self.assertEqual(self.round_robin_iter([[1, 3]]), [1, 3])

    def test_equal_lengths(self):
        self.assertEqual(
            self.round_robin_iter(
                [
                    [1, 3],
                    [2, 4],
                ],
            ),
            [1, 2, 3, 4],
        )

    def test_last_longer(self):
        self.assertEqual(
            self.round_robin_iter(
                [
                    [1],
                    [2, 4],
                ],
            ),
            [1, 2, 4],
        )

    def test_last_shorter(self):
        self.assertEqual(
            self.round_robin_iter(
                [
                    [1, 3],
                    [2],
                ],
            ),
            [1, 2, 3],
        )


class TestEnvs(TestCase):
    def env(self, name, type):
        m = Mock(name=name+'/'+type)
        m.name = name
        m.type = type
        return m

    def test(self):
        envs = Envs.from_tuples([('*', '*')])
        e = self.env

        assert envs.match(e('foo', 'foo'))
        assert envs.match(e('foo', 'bar'))

        envs = Envs.from_tuples([('foo', '*')])
        assert envs.match(e('foo', 'bar'))
        assert not envs.match(e('bar', 'foo'))

        envs = Envs.from_tuples([('*', 'foo')])
        assert not envs.match(e('bar', 'bar'))
        assert envs.match(e('bar', 'foo'))

        envs = Envs.from_tuples([('foo', 'bar')])
        assert envs.match(e('foo', 'bar'))
        assert not envs.match(e('foo', 'foo'))

        envs = Envs.from_tuples(
            [
                ('foo', 'foo'),
                ('foo', 'bar'),
                ('bar', 'foo'),
            ],
        )
        assert envs.match(e('foo', 'foo'))
        assert envs.match(e('foo', 'bar'))
        assert envs.match(e('bar', 'foo'))

        envs = Envs.from_tuples(
            [
                ('foo', '*'),
                ('*', 'foo'),
            ],
        )
        assert envs.match(e('foo', 'foo'))
        assert envs.match(e('foo', 'bar'))
        assert envs.match(e('bar', 'foo'))
        assert not envs.match(e('bar', 'bar'))
