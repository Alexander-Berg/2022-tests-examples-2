# -*- coding: utf-8 -*-
import unittest

from passport.backend.utils.errors import unsafe


class _NewError(Exception):
    pass


class _NewPassportError(_NewError):
    pass


class _UnknownException(Exception):
    pass


class TestUnsafeContextManager(unittest.TestCase):
    def test_unsafe_ok(self):
        with unsafe() as result:
            pass

        self.assertDictEqual(
            result,
            {
                'exception': None,
                'status': True,
            },
        )

    def test_unsafe_pass_any_exception_ok(self):
        with unsafe() as result:
            raise Exception()

        self.assertFalse(result['status'])
        self.assertIsInstance(result['exception'], Exception)

    def test_unsafe_catch_exceptions_ok(self):
        with unsafe([_NewError]) as result:
            raise _NewPassportError()

        self.assertFalse(result['status'])
        self.assertIsInstance(result['exception'], _NewPassportError)

    def test_unsafe_catch_exceptions_fail(self):
        with self.assertRaises(_UnknownException):
            with unsafe([_NewError]) as result:
                raise _UnknownException()

        self.assertFalse(result['status'])
        self.assertIsInstance(result['exception'], _UnknownException)
