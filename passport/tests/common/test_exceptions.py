# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.adm_api.common.exceptions import (
    BaseAdmError,
    HeadersEmptyError,
    SessionidInvalidError,
    ValidationFailedError,
)
from passport.backend.adm_api.test.utils import with_settings
from passport.backend.adm_api.tests.base.forms import TestForm
from passport.backend.core.validators.validators import (
    _,
    Invalid,
)


class BaseAdmRestoreErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.empty_error = BaseAdmError()
        self.full_error = SessionidInvalidError()

    def test_repr(self):
        eq_(repr(self.empty_error), '<BaseAdmError: errors: []>')
        eq_(repr(self.full_error), '<SessionidInvalidError: errors: [sessionid.invalid]>')

    def test_str(self):
        eq_(str(self.empty_error), 'errors: []')
        eq_(str(self.full_error), 'errors: [sessionid.invalid]')

    def test_errors(self):
        eq_(self.empty_error.errors, [])
        eq_(self.full_error.errors, ['sessionid.invalid'])

    def test_args(self):
        eq_(
            str(BaseAdmError('test', 1, 'привет')),
            'errors: []; args: test, 1, привет',
        )


class HeadersEmptyErrorTestCase(unittest.TestCase):
    def test_empty(self):
        h = HeadersEmptyError(aliases=[])
        eq_(h.aliases, [])
        eq_(h.errors, [])

    def test_simple(self):
        h = HeadersEmptyError(aliases=['a', 'b'])
        eq_(h.aliases, ['a', 'b'])
        eq_(h.errors, ['a.empty', 'b.empty'])


@with_settings(PORTAL_LANGUAGES=['ru'])
class ValidationFailedErrorTestCase(unittest.TestCase):
    def test_simple(self):
        message = ('empty', _('text'))
        value_dict = {'some_field': u'value'}
        state = None

        messages = {
            'empty': _('text'),
        }

        error_list = [
            Invalid((mess, text), value_dict, state) for mess, text in messages.items()
        ]

        vf = ValidationFailedError(
            Invalid(message, value_dict, state,
                    error_dict={'some_field': Invalid(message, value_dict, state, error_list=error_list)})
        )

        eq_(vf.errors, ['some_field.empty'])

    def test_with_form(self):
        try:
            TestForm().to_python({
                'field': 100500,
            })
        except Invalid as e:
            vf = ValidationFailedError(e)

        eq_(vf.errors,
            ['field.invalid'])
