import unittest
from inspect import ArgSpec
from operator import neg

import pytest

from dmp_suite.func_utils import pipe, get_argument_value, get_arg_spec, \
    get_positional_args_count, get_positional_args, call_with_params, \
    FuncCallError


class DecoratorsTestCase(unittest.TestCase):
    def test_pipe(self):
        def nvl_zero(value):
            return 0 if value is None else value

        def safe_int(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        int_abs = pipe(int, abs)
        safe_int_neg = safe_int | pipe(nvl_zero) | neg

        self.assertEqual(nvl_zero(0), 0)
        self.assertEqual(nvl_zero(None), 0)
        self.assertEqual(nvl_zero(''), '')
        self.assertEqual(nvl_zero(False), False)

        self.assertEqual(safe_int_neg(0), 0)
        self.assertEqual(safe_int_neg(None), 0)
        self.assertEqual(safe_int_neg(-1), 1)
        self.assertEqual(safe_int_neg(False), 0)
        self.assertEqual(safe_int_neg(True), -1)

        self.assertEqual(int_abs(0), 0)
        self.assertEqual(int_abs(-1), 1)
        self.assertEqual(int_abs(42), 42)
        self.assertEqual(int_abs('-42'), 42)
        self.assertEqual(int_abs(False), 0)
        self.assertEqual(int_abs(True), 1)
        self.assertRaises(ValueError, int_abs, '')
        self.assertRaises(TypeError, int_abs, None)

        self.assertListEqual(
            list(map(pipe() | int | abs | neg, [-1, '0', 42, False, True])),
            [-1, 0, -42, 0, -1]
        )

    def test_get_argument_value(self):
        def f(a): pass

        self.assertEqual(1, get_argument_value('a', f, 1))
        self.assertEqual(1, get_argument_value('a', f, a=1))

        def f(a=1): pass

        self.assertEqual(1, get_argument_value('a', f))
        self.assertEqual(2, get_argument_value('a', f, 2))
        self.assertEqual(3, get_argument_value('a', f, a=3))

        def f(a, b=2): pass

        self.assertEqual(1, get_argument_value('a', f, 1))
        self.assertEqual(2, get_argument_value('b', f, 0))
        self.assertEqual(3, get_argument_value('a', f, 3, 0))
        self.assertEqual(4, get_argument_value('b', f, 0, 4))
        self.assertEqual(5, get_argument_value('a', f, 5, b=0))
        self.assertEqual(6, get_argument_value('b', f, 0, b=6))
        self.assertEqual(7, get_argument_value('a', f, a=7))
        self.assertEqual(2, get_argument_value('b', f, a=0))
        self.assertEqual(9, get_argument_value('a', f, a=9, b=0))
        self.assertEqual(10, get_argument_value('b', f, a=0, b=10))
        self.assertRaises(KeyError, get_argument_value, 'c', f)  # not found
        self.assertRaises(ValueError, get_argument_value, 'a', f)  # few args

        def f(*args): pass

        self.assertEqual(1, get_argument_value('a', f, a=1))
        self.assertRaises(KeyError, get_argument_value, 'a', f)
        self.assertRaises(KeyError, get_argument_value, 'a', f, b=0)
        self.assertRaises(KeyError, get_argument_value, 'a', f, 0)
        self.assertRaises(KeyError, get_argument_value, 'a', f, 0, b=0)

        def f(**kwargs): pass

        self.assertEqual(1, get_argument_value('a', f, a=1))
        self.assertIsNone(get_argument_value('a', f))


def test_get_arg_spec():
    def f(): pass

    assert ArgSpec([], None, None, None) == get_arg_spec(f)

    def f(a): pass

    assert ArgSpec(['a'], None, None, None) == get_arg_spec(f)

    class C(object):
        @property
        def p(self):
            return 1

    with pytest.raises(TypeError):
        get_arg_spec(C())
    with pytest.raises(TypeError):
        get_arg_spec(C)
    with pytest.raises(TypeError):
        get_arg_spec(C.p)

    class C(object):
        def __call__(self, a): pass

        @staticmethod
        def s(a):
            pass

        @classmethod
        def c(cls, a):
            pass

    assert ArgSpec(['self', 'a'], None, None, None) == get_arg_spec(C())
    assert ArgSpec(['a'], None, None, None) == get_arg_spec(C.s)
    assert ArgSpec(['cls', 'a'], None, None, None) == get_arg_spec(C.c)


def test_get_arg_spec_and_count():
    def f(): pass

    assert 0 == get_positional_args_count(f)
    assert not get_positional_args(f)

    def f(a): pass

    assert 1 == get_positional_args_count(f)
    assert ['a'] == get_positional_args(f)
    assert 1 == get_positional_args_count(f, exclude_optional=True)
    assert ['a'] == get_positional_args(f, exclude_optional=True)

    def f(*args): pass

    assert 0 == get_positional_args_count(f)
    assert not get_positional_args(f)

    def f(**kwargs): pass

    assert 0 == get_positional_args_count(f)
    assert not get_positional_args(f)

    def f(a, *args, **kwargs): pass

    assert 1 == get_positional_args_count(f)
    assert ['a'] == get_positional_args(f)

    def f(a, b, c, d, e): pass

    assert 5 == get_positional_args_count(f)
    assert ['a', 'b', 'c', 'd', 'e'] == get_positional_args(f)

    def f(a, b=1): pass

    assert 1 == get_positional_args_count(f, exclude_optional=True)
    assert ['a'] == get_positional_args(f, exclude_optional=True)

    def f(a=1): pass

    assert 0 == get_positional_args_count(f, exclude_optional=True)
    assert not get_positional_args(f, exclude_optional=True)

    class C(object):
        def f(self, a): pass

        def g(self, a=1): pass

        def __call__(self, a): pass

        @staticmethod
        def s(a):
            pass

        @staticmethod
        def so(a, b=1):
            pass

        @classmethod
        def c(cls, b=1):
            pass

    assert 1 == get_positional_args_count(C.f)
    assert ['a'] == get_positional_args(C.f)

    assert 1 == get_positional_args_count(C().f)
    assert ['a'] == get_positional_args(C().f)

    assert 1 == get_positional_args_count(C())
    assert ['a'] == get_positional_args(C())

    assert 1 == get_positional_args_count(C.s)
    assert ['a'] == get_positional_args(C.s)

    assert 1 == get_positional_args_count(C.c)
    assert ['b'] == get_positional_args(C.c)

    assert 0 == get_positional_args_count(C.g, exclude_optional=True)
    assert not get_positional_args(C.g, exclude_optional=True)

    assert 1 == get_positional_args_count(C.so, exclude_optional=True)
    assert ['a'] == get_positional_args(C.so, exclude_optional=True)

    assert 0 == get_positional_args_count(C.c, exclude_optional=True)
    assert not get_positional_args(C.c, exclude_optional=True)


def test_call_with_params():
    def f(): pass

    call_with_params(f, {})
    call_with_params(f, dict(a=1))

    def f(a=1): return a

    assert 1 == call_with_params(f, {})
    assert 2 == call_with_params(f, dict(a=2))
    assert 1 == call_with_params(f, dict(b=2))

    def f(a): return a

    with pytest.raises(FuncCallError):
        call_with_params(f, {})

    with pytest.raises(FuncCallError):
        call_with_params(f, dict(b=2))

    assert 2 == call_with_params(f, dict(a=2))

    def f(a, b): return a, b

    with pytest.raises(FuncCallError):
        call_with_params(f, dict(b=2))

    assert 2, 1 == call_with_params(f, dict(a=2, b=1))
