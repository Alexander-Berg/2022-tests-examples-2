# -*- coding: utf-8 -*-

import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.phone import forms
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.types.phone_number import phone_number


@with_settings(
    DISPLAY_LANGUAGES=['ru'],
)
class TestForms(unittest.TestCase):
    def test_base_submit_form(self):
        invalid_params = [
            ({}, ['display_language.empty']),
            ({'display_language': 'rt'}, ['display_language.invalid']),
            ({'display_language': ' rt '}, ['display_language.invalid']),
        ]

        valid_params = [
            ({'display_language': 'ru'}, {'display_language': 'ru', 'route': None, 'return_unmasked_number': True}),
            ({'display_language': ' ru '}, {'display_language': 'ru', 'route': None, 'return_unmasked_number': True}),
            (
                {'display_language': 'ru', 'route': 'default', 'return_unmasked_number': 'false'},
                {'display_language': 'ru', 'route': 'default', 'return_unmasked_number': False},
            ),
        ]

        check_form(forms.BaseSubmitForm(), invalid_params, valid_params, None)

    def test_confirm_tracked_secure_submit_form(self):
        # в тесте только отличия от BaseSubmitForm
        invalid_params = [
            (
                {'gps_package_name': '', 'display_language': 'ru', 'code_format': ''},
                ['gps_package_name.empty', 'code_format.empty'],
            ),
            (
                {'gps_package_name': '    ', 'display_language': 'ru', 'code_format': 'BAD'},
                ['gps_package_name.invalid', 'code_format.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'gps_package_name': 'com.yandex.foo',
                    'display_language': 'ru',
                },
                {
                    'gps_package_name': 'com.yandex.foo',
                    'display_language': 'ru',
                    'return_unmasked_number': True,
                    'route': None,
                    'code_format': None,
                },
            ),
            (
                {
                    'gps_package_name': 'com.yandex.foo',
                    'display_language': 'ru',
                    'code_format': 'by_3_dash',
                },
                {
                    'gps_package_name': 'com.yandex.foo',
                    'display_language': 'ru',
                    'return_unmasked_number': True,
                    'route': None,
                    'code_format': 'by_3_dash',
                },
            ),
        ]

        check_form(forms.ConfirmTrackedSecureSubmitForm(), invalid_params, valid_params, None)

    def test_numbered_submit_form(self):
        invalid_params = [
            ({}, ['display_language.empty', 'number.empty']),
            ({'country': '  ', 'display_language': 'ru'}, ['country.invalid', 'number.empty']),
            ({'country': '', 'display_language': 'ru'}, ['country.empty', 'number.empty']),
            ({'number': 'bla', 'display_language': 'ru'}, ['number.invalid']),
            ({'number': '9034u4u', 'display_language': 'ru', 'country': 'ru'}, ['number.invalid']),
            ({'code_format': '', 'number': '89261234567', 'display_language': 'ru'}, ['code_format.empty']),
            ({'code_format': 'bla', 'number': '89261234567', 'display_language': 'ru'}, ['code_format.invalid']),
            (
                {'gps_package_name': '', 'number': '+79261234567', 'display_language': 'ru'},
                ['gps_package_name.empty'],
            ),
            (
                {'gps_package_name': '    ', 'number': '+79261234567', 'display_language': 'ru'},
                ['gps_package_name.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'number': '+79261234567',
                    'display_language': 'ru',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'code_format': None,
                    'country': None,
                    'display_language': 'ru',
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'code_format': None,
                    'country': 'ru',
                    'display_language': 'ru',
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                    'code_format': 'by_3',
                    'gps_package_name': 'com.yandex.foo',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'code_format': 'by_3',
                    'country': 'ru',
                    'display_language': 'ru',
                    'route': None,
                    'gps_package_name': 'com.yandex.foo',
                    'return_unmasked_number': True,
                },
            ),
        ]

        check_form(forms.NumberedSubmitForm(), invalid_params, valid_params, None)

    def test_confirm_submit_form(self):
        invalid_params = [
            ({}, ['display_language.empty']),
            ({'country': '  ', 'display_language': 'ru'}, ['country.invalid']),
            ({'country': '', 'display_language': 'ru'}, ['country.empty']),
            ({'number': 'bla', 'display_language': 'ru'}, ['number.invalid']),
            ({'phone_id': 'bla', 'display_language': 'ru'}, ['phone_id.invalid']),
            ({'display_language': 'ru'}, ['form.invalid']),
            ({'number': '9034u4u', 'display_language': 'ru', 'country': 'ru'}, ['number.invalid']),
            ({'code_format': '', 'number': '89261234567', 'display_language': 'ru'}, ['code_format.empty']),
            ({'code_format': 'bla', 'number': '89261234567', 'display_language': 'ru'}, ['code_format.invalid']),
            ({'number': '89261234567', 'display_language': 'ru', 'confirm_method': 'by_'}, ['confirm_method.invalid']),
            ({'number': '89261234567', 'display_language': 'ru', 'confirm_method': ''}, ['confirm_method.empty']),
            (
                {'gps_package_name': '', 'number': '+79261234567', 'display_language': 'ru'},
                ['gps_package_name.empty'],
            ),
            (
                {'gps_package_name': '    ', 'number': '+79261234567', 'display_language': 'ru'},
                ['gps_package_name.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'number': '+79261234567',
                    'display_language': 'ru',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'phone_id': None,
                    'code_format': None,
                    'country': None,
                    'display_language': 'ru',
                    'gps_package_name': None,
                    'route': None,
                    'confirm_method': 'by_sms',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                    'confirm_method': 'by_call',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'phone_id': None,
                    'code_format': None,
                    'country': 'ru',
                    'display_language': 'ru',
                    'gps_package_name': None,
                    'route': None,
                    'confirm_method': 'by_call',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                    'confirm_method': 'by_flash_call',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'phone_id': None,
                    'code_format': None,
                    'country': 'ru',
                    'display_language': 'ru',
                    'gps_package_name': None,
                    'route': None,
                    'confirm_method': 'by_flash_call',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '+79261234567',
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'confirm_method': 'by_sms',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'phone_id': None,
                    'code_format': None,
                    'country': None,
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'route': None,
                    'confirm_method': 'by_sms',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '+79261234567',
                    'display_language': 'ru',
                    'gps_package_name': 'c123.y123',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'phone_id': None,
                    'code_format': None,
                    'country': None,
                    'display_language': 'ru',
                    'gps_package_name': 'c123.y123',
                    'route': None,
                    'confirm_method': 'by_sms',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '+79261234567',
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'code_format': 'by_3',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'phone_id': None,
                    'code_format': 'by_3',
                    'country': None,
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'route': None,
                    'confirm_method': 'by_sms',
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'phone_id': 1,
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'code_format': 'by_3',
                },
                {
                    'number': None,
                    'phone_id': 1,
                    'code_format': 'by_3',
                    'country': None,
                    'display_language': 'ru',
                    'gps_package_name': 'com.yandex.foo',
                    'route': None,
                    'confirm_method': 'by_sms',
                    'return_unmasked_number': True,
                },
            ),
        ]

        check_form(forms.ConfirmSubmitForm(), invalid_params, valid_params, None)

    def test_accounted_submit_form(self):
        invalid_params = []

        valid_params = [
            (
                {'display_language': 'ru', 'uid': '1234'},
                {'sessionid': None, 'uid': 1234, 'display_language': 'ru', 'route': None, 'return_unmasked_number': True},
            ),
            (
                {'display_language': 'ru', 'sessionid': '1234'},
                {'sessionid': '1234', 'uid': None, 'display_language': 'ru', 'route': None, 'return_unmasked_number': True},
            ),
        ]

        check_form(forms.AccountedSubmitForm(), invalid_params, valid_params, None)

    def test_accounted_numbered_submit_form(self):
        invalid_params = [
            (
                {'display_language': 'ru'},
                ['number.empty'],
            ),
            (
                {
                    'display_language': 'ru',
                    'number': '89261234567',
                    'country': 'bla',
                    'uid': '1234',
                    'sessionid': '1234',
                },
                ['country.invalid'],
            ),
            (
                {
                    'display_language': 'ru',
                    'number': '89261234567',
                    'code_format': '',
                },
                ['code_format.empty'],
            ),
            (
                {
                    'display_language': 'ru',
                    'number': '89261234567',
                    'code_format': 'bla',
                },
                ['code_format.invalid'],
            ),
        ]

        valid_params = [
            (
                {'display_language': 'ru',
                 'number': '+79261234567',
                 'uid': '1234',
                 },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'code_format': None,
                    'country': None,
                    'sessionid': None,
                    'uid': 1234,
                    'display_language': 'ru',
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'display_language': 'ru',
                    'number': '+79261234567',
                    'sessionid': '1234',
                },
                {
                    'number': phone_number.PhoneNumber.parse('+79261234567'),
                    'code_format': None,
                    'country': None,
                    'sessionid': '1234',
                    'uid': None,
                    'display_language': 'ru',
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                    'uid': '1234',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'code_format': None,
                    'country': 'ru',
                    'display_language': 'ru',
                    'sessionid': None,
                    'uid': 1234,
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
            (
                {
                    'number': '89261234567',
                    'country': 'ru',
                    'display_language': 'ru',
                    'uid': '1234',
                    'code_format': 'by_3',
                },
                {
                    'number': phone_number.PhoneNumber.parse('89261234567', 'RU'),
                    'code_format': 'by_3',
                    'country': 'ru',
                    'display_language': 'ru',
                    'sessionid': None,
                    'uid': 1234,
                    'route': None,
                    'gps_package_name': None,
                    'return_unmasked_number': True,
                },
            ),
        ]

        check_form(forms.AccountedNumberedSubmitForm(), invalid_params, valid_params, None)

    def test_base_commit_form(self):
        invalid_params = [
            ({}, ['code.empty']),
            ({'code': ''}, ['code.empty']),
            ({'code': '    '}, ['code.empty']),
        ]

        valid_params = [
            (
                {'code': 'test1   '},
                {'code': 'test1', 'return_unmasked_number': True},
            ),
            (
                {'code': 'test1', 'return_unmasked_number': 'false'},
                {'code': 'test1', 'return_unmasked_number': False},
            ),
        ]

        check_form(forms.BaseCommitForm(), invalid_params, valid_params, None)

    def test_delete_alias_commit_form(self):
        valid_params = [
            (
                dict(),
                dict(password=None),
            ),
            (
                dict(password=''),
                dict(password=''),
            ),
            (
                dict(password=' ' * 2),
                dict(password=''),
            ),
            (
                dict(password='testpassword1'),
                dict(password='testpassword1'),
            ),
        ]

        invalid_params = list()

        check_form(forms.DeleteAliasCommitForm(), invalid_params, valid_params, None)
