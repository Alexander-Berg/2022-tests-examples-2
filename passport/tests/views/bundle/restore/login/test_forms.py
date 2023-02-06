# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.test_base_data import TEST_RETPATH
from passport.backend.api.views.bundle.restore.login.forms import (
    LoginRestoreCheckNamesForm,
    LoginRestoreCheckNamesSimpleForm,
    LoginRestoreCheckPhoneForm,
    LoginRestoreConfirmPhoneForm,
    LoginRestoreSubmitForm,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import parse_phone_number


@with_settings_hosts()
class TestLoginRestoreForms(unittest.TestCase):
    def test_submit(self):
        invalid_params = [
            (
                {'retpath': '', 'gps_package_name': ''},
                ['retpath.empty', 'gps_package_name.empty'],
            ),
            (
                {'gps_package_name': 'BAD'},
                ['gps_package_name.invalid'],
            ),
        ]

        valid_params = [
            (
                {},
                {'retpath': None, 'gps_package_name': None},
            ),
            (
                {'retpath': TEST_RETPATH, 'gps_package_name': 'com.yandex.maps'},
                {'retpath': TEST_RETPATH, 'gps_package_name': 'com.yandex.maps'},
            ),
            (
                {'retpath': '1234'},
                {'retpath': None, 'gps_package_name': None},
            ),
        ]

        check_form(LoginRestoreSubmitForm(), invalid_params, valid_params, None)

    def test_check_phone(self):
        invalid_params = [
            (
                {},
                ['phone_number.empty', 'display_language.empty'],
            ),
            (
                {'phone_number': '', 'display_language': '', 'country': '', 'confirm_method': '', 'code_format': ''},
                [
                    'phone_number.empty',
                    'display_language.empty',
                    'country.empty',
                    'confirm_method.empty',
                    'code_format.empty',
                ],
            ),
            (
                {
                    'phone_number': '1122',
                    'display_language': 'BAD',
                    'country': 'BAD',
                    'confirm_method': 'BAD',
                    'code_format': 'BAD',
                },
                ['display_language.invalid', 'country.invalid', 'confirm_method.invalid', 'code_format.invalid'],
            ),
            (
                {'phone_number': '89151234567', 'display_language': 'TR', 'country': 'tr', 'confirm_method': 'by_sms'},
                ['phone_number.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'phone_number': '+79151234567',
                    'display_language': 'RU',
                    'confirm_method': 'by_call',
                    'code_format': 'by_3',
                },
                {
                    'phone_number': parse_phone_number('+79151234567'),
                    'display_language': 'ru',
                    'country': None,
                    'confirm_method': 'by_call',
                    'code_format': 'by_3',
                },
            ),
            (
                {'phone_number': '+79151234567', 'display_language': 'RU', 'confirm_method': 'by_flash_call'},
                {
                    'phone_number': parse_phone_number('+79151234567'),
                    'display_language': 'ru',
                    'country': None,
                    'confirm_method': 'by_flash_call',
                    'code_format': None,
                },
            ),
            (
                {'phone_number': '89151234567', 'display_language': 'RU', 'country': 'ru', 'confirm_method': 'by_call'},
                {
                    'phone_number': parse_phone_number('+79151234567'),
                    'display_language': 'ru',
                    'country': 'ru',
                    'confirm_method': 'by_call',
                    'code_format': None,
                },
            ),
        ]

        check_form(LoginRestoreCheckPhoneForm(), invalid_params, valid_params, None)

    def test_confirm_phone(self):
        invalid_params = [
            (
                {},
                ['code.empty'],
            ),
            (
                {'code': '  '},
                ['code.empty'],
            ),
        ]

        valid_params = [
            (
                {'code': ' 123456 '},
                {'code': '123456'},
            ),
        ]

        check_form(LoginRestoreConfirmPhoneForm(), invalid_params, valid_params, None)

    def test_check_names(self):
        invalid_params = [
            (
                {},
                ['firstname.empty', 'lastname.empty'],
            ),
            (
                {'firstname': '', 'lastname': ''},
                ['firstname.empty', 'lastname.empty'],
            ),
        ]

        valid_params = [
            (
                {'firstname': u' Иван ', 'lastname': u' Иванов '},
                {'firstname': u'Иван', 'lastname': u'Иванов'},
            ),
        ]

        check_form(LoginRestoreCheckNamesForm(), invalid_params, valid_params, None)

    def test_check_names_simple(self):
        invalid_params = [
            (
                {},
                ['firstname.empty', 'lastname.empty'],
            ),
            (
                {'firstname': '', 'lastname': ''},
                ['firstname.empty', 'lastname.empty'],
            ),
        ]

        valid_params = [
            (
                {
                    'firstname': u' Иван ',
                    'lastname': u' Иванов ',
                },
                {
                    'firstname': u'Иван',
                    'lastname': u'Иванов',
                    'allow_disabled': True,
                    'allow_social': False,
                    'allow_neophonish': False,
                },
            ),
            (
                {
                    'firstname': u' Иван ',
                    'lastname': u' Иванов ',
                    'allow_disabled': 'false',
                    'allow_social': 'false',
                    'allow_neophonish': 'false',
                },
                {
                    'firstname': u'Иван',
                    'lastname': u'Иванов',
                    'allow_disabled': False,
                    'allow_social': False,
                    'allow_neophonish': False,
                },
            ),
            (
                {
                    'firstname': u' Иван ',
                    'lastname': u' Иванов ',
                    'allow_disabled': 'true',
                    'allow_social': 'true',
                    'allow_neophonish': 'true',
                },
                {
                    'firstname': u'Иван',
                    'lastname': u'Иванов',
                    'allow_disabled': True,
                    'allow_social': True,
                    'allow_neophonish': True,
                },
            ),
        ]

        check_form(LoginRestoreCheckNamesSimpleForm(), invalid_params, valid_params, None)
