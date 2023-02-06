# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.api.common.format_response import (
    format_error,
    format_errors,
)
from passport.backend.core.validators import Invalid


class TestFormatError(unittest.TestCase):
    def test_format_error(self):
        eq_(format_error('code', 'msg', 'field'), {'code': 'code', 'message': 'msg', 'field': 'field'})

    def test_format_error_lower_code(self):
        eq_(format_error('cOdE', 'msg', 'field'), {'code': 'code', 'message': 'msg', 'field': 'field'})

    def test_format_error_no_field(self):
        eq_(format_error('cOdE', 'msg'), {'code': 'code', 'message': 'msg', 'field': None})


class TestFormatErrors(unittest.TestCase):
    def test_simple_error(self):
        error = Invalid(('code', 'msg'), None, None)
        eq_(format_errors(error), [{'code': 'code', 'message': 'msg', 'field': None}])

    def test_error_list(self):
        error = Invalid(('code', 'msg'), None, None, error_list=[
            Invalid(('code1', 'msg'), None, None),
            Invalid(('code2', 'msg'), None, None),
        ])
        eq_(format_errors(error), [
            {'code': 'code1', 'message': 'msg', 'field': None},
            {'code': 'code2', 'message': 'msg', 'field': None}
        ])

    def test_error_dict(self):
        error = Invalid(('code', 'msg'), None, None, error_dict={
            'field1': Invalid(('code1', 'msg'), None, None),
            'field2': Invalid(('code2', 'msg'), None, None),
        })
        eq_(sorted(format_errors(error)), sorted([
            {'code': 'code1', 'message': 'msg', 'field': 'field1'},
            {'code': 'code2', 'message': 'msg', 'field': 'field2'}
        ]))
