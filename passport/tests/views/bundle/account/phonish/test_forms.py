# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.test_base_data import TEST_PHONE_NUMBER
from passport.backend.api.views.bundle.account.phonish.forms import AccountPhonishCanLoginForm
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestPhonishCanLoginForms(unittest.TestCase):
    def test_phonish_can_login_form(self):
        valid_params = [
            (
                {
                    'uid': '123',
                    'phone_number': TEST_PHONE_NUMBER.international,
                },
                {
                    'uid': 123,
                    'phone_number': TEST_PHONE_NUMBER,
                    'country': None,
                },
            ),
            (
                {
                    'uid': '123',
                    'phone_number': '9261234567',  # телефон без кода страны
                    'country': 'ru',
                },
                {
                    'uid': 123,
                    'phone_number': TEST_PHONE_NUMBER,
                    'country': 'ru',
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'uid': '',
                },
                ['uid.empty', 'phone_number.empty'],
            ),
            (
                {
                    'uid': '123',
                },
                ['phone_number.empty'],
            ),
            (
                {
                    'phone_number': '+79261234567',
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'bla',
                    'phone_number': 'bla',
                },
                ['uid.invalid'],
            ),
            (
                {
                    'uid': '123',
                    'country': 'keck',
                },
                ['country.invalid', 'phone_number.empty'],
            ),
        ]

        check_form(AccountPhonishCanLoginForm(), invalid_params, valid_params, None)
