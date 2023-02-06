import pytest
import mock
import unittest

from dmp_suite.datetime_utils import date_period
from dmp_suite.decorators import (
    deprecated, try_except, try_pass,
    log_exception, current_version,
    compose
)


def test_deprecated():
    @deprecated()
    def deprecated_fn():
        pass

    with pytest.warns(DeprecationWarning):
        deprecated_fn()


def test_exceptions_arg_validation():

    def _test_decorator(decorator):
        def f():
            raise KeyError()

        with pytest.raises(ValueError):
            decorator(exceptions=[ValueError])(f)

        with pytest.raises(ValueError):
            decorator(exceptions=ValueError())(f)

    _test_decorator(try_except)
    _test_decorator(try_pass)


def test_try_except():
    def f():
        raise KeyError()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        with pytest.raises(KeyError):
            try_except(times=5, sleep=0.01, exceptions=(KeyError,))(f)()

        mock_logging.warning.assert_has_calls([
            mock.call('Exception happened on %s call. Attempt %d.',
                      'f', attempt, exc_info=True)
            for attempt in range(5)
        ])


def test_try_pass():
    def f():
        raise KeyError()

    with pytest.raises(KeyError):
        try_pass(exceptions=(ValueError,))(f)()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        res = try_pass(exceptions=(KeyError,))(f)()
        assert res is None
        mock_logging.exception.assert_called_once_with(
            'Exception happened on %s call', 'f'
        )


class TestVersionedFunction(unittest.TestCase):
    def test_handles_single_version(self):
        @current_version
        def f(x):
            return x

        period = date_period("2019-01-01", "2019-01-01")
        assert f("hello", use_version_from=period) == "hello"
        assert f("hello", use_version_from='2019-01-01') == "hello"

    def test_handles_three_versions(self):
        @current_version
        def f(x):
            return x

        @f.version(date_period("2018-01-01", "2018-12-31"))
        def _(x):
            return "{} 2018".format(x)

        @f.version(date_period("2017-01-01", "2017-12-31"))
        def _(x):
            return "{} 2017".format(x)

        period = date_period("2019-01-01", "2019-01-01")
        assert f("hello", use_version_from=period) == "hello"

        period = date_period("2018-01-01", "2018-01-01")
        assert f("hello", use_version_from=period) == "hello 2018"

        period = date_period("2017-01-01", "2017-01-01")
        assert f("hello", use_version_from=period) == "hello 2017"

        period = date_period("2016-01-01", "2016-01-01")
        assert f("hello", use_version_from=period) == "hello"

        assert f("hello", use_version_from='2019-01-01 10:10:15') == "hello"
        assert f("hello", use_version_from='2017-05-05 10:10:15') == "hello 2017"
        assert f("hello", use_version_from='2018-05-05 10:10:15') == "hello 2018"
        assert f("hello", use_version_from='2016-05-05 10:10:15') == "hello"

    def test_passes_kwargs(self):
        @current_version
        def f(x, **kwargs):
            return kwargs

        @f.version(date_period("2018-01-01", "2018-12-31"))
        def _(x, **kwargs):
            return kwargs

        period = date_period("2019-01-01", "2019-01-01")
        assert f("hello", a=42, use_version_from=period) == {"a": 42}

        period = date_period("2018-01-01", "2018-01-01")
        assert f("hello", a=42, use_version_from=period) == {"a": 42}

    def test_fails_on_ambiguous_period(self):
        @current_version
        def f():
            pass

        @f.version(date_period("2018-01-01", "2018-12-31"))
        def _():
            pass

        @f.version(date_period("2017-01-01", "2017-12-31"))
        def _():
            pass

        period = date_period("2018-12-31", "2019-01-01")
        with self.assertRaisesRegexp(ValueError, "^Function version changes"):
            f(use_version_from=period)

        period = date_period("2017-12-31", "2018-01-01")
        with self.assertRaisesRegexp(ValueError, "^Function version changes"):
            f(use_version_from=period)

        period = date_period("2016-12-31", "2017-01-01")
        with self.assertRaisesRegexp(ValueError, "^Function version changes"):
            f(use_version_from=period)

    def test_fails_on_overlapping_periods(self):
        @current_version
        def f():
            pass

        @f.version(date_period("2018-01-01", "2018-12-31"))
        def _():
            pass

        with self.assertRaisesRegexp(ValueError, "version periods overlap$"):
            @f.version(date_period("2017-01-01", "2018-01-01"))
            def _():
                pass

        with self.assertRaisesRegexp(ValueError, "version periods overlap$"):
            @f.version(date_period("2018-12-31", "2019-12-31"))
            def _():
                pass

        with self.assertRaisesRegexp(ValueError, "version periods overlap$"):
            @f.version(date_period("2017-01-01", "2019-12-31"))
            def _():
                pass

    def test_detects_argument_name_collision(self):
        with self.assertRaisesRegexp(ValueError, "shouldn't take .* argument"):
            @current_version
            def f(use_version_from):
                pass

        @current_version
        def g():
            pass

        with self.assertRaisesRegexp(ValueError, "shouldn't take .* argument"):
            @g.version(date_period("2018-01-01", "2018-12-31"))
            def _(use_version_from=None):
                pass


def test_log_exception_on_func():
    def f():
        raise ValueError()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        log_decorator = log_exception()
        log_decorator(f)()
        mock_logging.log.assert_called()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        log_decorator = log_exception(exceptions=ValueError)
        log_decorator(f)()
        mock_logging.log.assert_called()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        log_decorator = log_exception(exceptions=(ValueError,))
        log_decorator(f)()
        mock_logging.log.assert_called()

    with pytest.raises(ValueError):
        with mock.patch('dmp_suite.decorators.logger') as mock_logging:
            log_decorator = log_exception(
                exceptions=(ValueError,),
                suppress_exception=False
            )
            log_decorator(f)()
            mock_logging.log.assert_called()


def test_log_exception_on_callable_class():
    class Callable(object):
        def __call__(self, *args, **kwargs):
            raise ValueError()

    with mock.patch('dmp_suite.decorators.logger') as mock_logging:
        log_decorator = log_exception(exceptions=ValueError)
        log_decorator(Callable())()
        mock_logging.log.assert_called()

    with pytest.raises(ValueError):
        with mock.patch('dmp_suite.decorators.logger') as mock_logging:
            log_decorator = log_exception(
                exceptions=(ValueError,),
                suppress_exception=False
            )
            log_decorator(Callable())()
            mock_logging.log.assert_called()


def decorator_helper(mock_obj):
    def _decorate_with_mock(origin_func):
        def _decorate(*args, **kwargs):
            mock_obj()
            origin_func(*args, **kwargs)
        return _decorate
    return _decorate_with_mock


class TestComposeDecorator(object):
    def test_one_decorator(self):
        mock1 = mock.MagicMock()
        mock_f = mock.MagicMock()

        @compose(decorator_helper(mock1))
        def foo():
            mock_f()

        foo()
        mock1.assert_called_once()
        mock_f.assert_called_once()

    def test_multiple_decorator(self):
        mock1 = mock.MagicMock()
        mock2 = mock.MagicMock()
        mock_f = mock.MagicMock()

        @compose(decorator_helper(mock1), decorator_helper(mock2))
        def foo():
            mock_f()

        foo()
        mock1.assert_called_once()
        mock2.assert_called_once()
        mock_f.assert_called_once()

    def test_compose_of_composed(self):
        order = 1

        def mock_wrapper(function):
            def inner():
                nonlocal order
                function(order)
                order += 1
            return inner

        mock1, mock2, mock3, mock_f = (mock.MagicMock() for _ in range(4))

        wrapped_mock1 = mock_wrapper(mock1)
        wrapped_mock2 = mock_wrapper(mock2)
        wrapped_mock3 = mock_wrapper(mock3)
        wrapped_mock_f = mock_wrapper(mock_f)

        composed = compose(decorator_helper(wrapped_mock1), decorator_helper(wrapped_mock2))

        @compose(composed, decorator_helper(wrapped_mock3))
        def foo():
            wrapped_mock_f()

        foo()
        mock1.assert_called_once()
        mock2.assert_called_once()
        mock3.assert_called_once()
        mock_f.assert_called_once()

        # Ensure that the order of calls is expected
        assert mock1.call_args == mock.call(1)
        assert mock2.call_args == mock.call(2)
        assert mock3.call_args == mock.call(3)
        assert mock_f.call_args == mock.call(4)
