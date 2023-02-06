# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.api.forms import (
    LoginValidation,
    Person,
)
from passport.backend.api.views.bundle.exceptions import (
    AccountDisabledError,
    BaseBundleError,
    HeadersEmptyError,
    ValidationFailedError,
)
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.validators import (
    _,
    Invalid,
)


class BaseBundleErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.empty_error = BaseBundleError()
        self.full_error = AccountDisabledError()

    def test_repr(self):
        eq_(repr(self.empty_error), '<BaseBundleError: errors: []>')
        eq_(repr(self.full_error), '<AccountDisabledError: errors: [account.disabled]>')

    def test_str(self):
        eq_(str(self.empty_error), 'errors: []')
        eq_(str(self.full_error), 'errors: [account.disabled]')

    def test_errors(self):
        eq_(self.empty_error.errors, [])
        eq_(self.full_error.errors, ['account.disabled'])

    def test_args(self):
        eq_(
            str(BaseBundleError('test', 1, u'привет')),
            'errors: []; args: test, 1, \xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82',
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
            'missingValue': _('text'),
            'tooLong': _('text'),
            'tooShort': _('text'),
            'notIn': _('text'),
        }

        error_list = [
            Invalid((mess, text), value_dict, state) for mess, text in messages.items()
        ]

        vf = ValidationFailedError.from_invalid(
            Invalid(message, value_dict, state,
                    error_dict={'some_field': Invalid(message, value_dict, state, error_list=error_list)}),
        )

        eq_(
            vf.errors,
            [
                'some_field.empty',
                'some_field.invalid',
                'some_field.long',
                'some_field.short',
            ],
        )

    def test_with_login_validation_form(self):
        try:
            LoginValidation().to_python({
                'login': '1aaa.-bb&b1' * 100,
                'ignore_stoplist': None,
            })
        except Invalid as e:
            vf = ValidationFailedError.from_invalid(e)

        eq_(
            vf.errors,
            [
                'ignore_stoplist.empty',
                'login.dothyphen',
                'login.long',
                'login.prohibitedsymbols',
                'login.startswithdigit',
            ],
        )

    def test_with_person_form(self):
        try:
            Person().to_python({
                'firstname': 'abc' * 100,
                'lastname': 'abc' * 100,
                'gender': 'bla',
                'birthday': '1800-01-01',
                'country': 'fu',
                'language': 'bvbvbvb',
                'timezone': 'abc',
            })
        except Invalid as e:
            vf = ValidationFailedError.from_invalid(e)
        eq_(
            vf.errors,
            [
                'birthday.invalid',
                'consumer.empty',
                'country.invalid',
                'gender.invalid',
                'language.invalid',
                'timezone.invalid',
                'uid.empty',
            ],
        )
