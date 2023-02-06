# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import *
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONNECTION_ID_VALUE,
    TEST_YANDEXUID_VALUE,
)
from passport.backend.api.views.bundle.account.logout import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestLogoutForm(unittest.TestCase):

    def test_logout_form(self):
        invalid_params = [
            (
                {},
                ['form.invalid'],
            ),
            (
                {'yu': '', 'ci': ''},
                ['form.invalid'],
            ),
            (
                {'yu': '  ', 'ci': '  '},
                ['form.invalid'],
            ),
            (
                {'yu': TEST_YANDEXUID_VALUE, 'target': 'default', 'is_global': 'yep'},
                ['is_global.invalid'],
            ),
            (
                {'yu': {}, 'ci': {}, 'target': 'default', 'is_global': 'yes', 'retpath': '123'},
                ['yu.invalid', 'ci.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'target': '   fault ',
                    'is_global': 1,
                    'retpath': 'http://passport-test.yandex.ru',
                    'origin': '         ',
                },
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'ci': None,
                    'target': 'default',
                    'is_global': True,
                    'retpath': 'http://passport-test.yandex.ru',
                    'origin': '',
                },
            ),
            (
                {
                    'ci': TEST_CONNECTION_ID_VALUE,
                    'is_global': 1,
                    'retpath': 'http://passport-test.yandex.ru',
                },
                {
                    'yu': None,
                    'ci': TEST_CONNECTION_ID_VALUE,
                    'target': 'default',
                    'is_global': True,
                    'retpath': 'http://passport-test.yandex.ru',
                    'origin': None,
                },
            ),
            (
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'target': ' everybody ',
                    'is_global': 'off',
                    'origin': TEST_ORIGIN,
                },
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'ci': None,
                    'target': 'everybody',
                    'is_global': False,
                    'retpath': None,
                    'origin': TEST_ORIGIN,
                },
            ),
            (
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'target': 'default',
                    'is_global': 'yes',
                    'retpath': 'http://passport-test.google.com',
                },
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'ci': None,
                    'target': 'default',
                    'is_global': True,
                    'retpath': None,
                    'origin': None,
                },
            ),
            (
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'target': '',
                    'is_global': 'no',
                    'retpath': 'http://passport-test.google.com',
                },
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'ci': None,
                    'target': 'default',
                    'is_global': False,
                    'retpath': None,
                    'origin': None,
                },
            ),
            (
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'is_global': 'no',
                    'retpath': 'http://passport-test.google.com',
                },
                {
                    'yu': TEST_YANDEXUID_VALUE,
                    'ci': None,
                    'target': 'default',
                    'is_global': False,
                    'retpath': None,
                    'origin': None,
                },
            ),
        ]

        check_form(forms.LogoutForm(), invalid_params, valid_params, None)
