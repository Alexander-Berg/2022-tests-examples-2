# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.otp.migrate import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class OtpMigrateFormsTestCase(unittest.TestCase):
    def test_submit_form(self):
        invalid_cases = []
        valid_cases = [
            (
                {},
                {
                    'retpath': None,
                },
            ),
            (
                {
                    'retpath': '  ',
                },
                {
                    'retpath': None,
                },
            ),
            (
                {
                    'retpath': 'https://ya.ru',
                },
                {
                    'retpath': 'https://ya.ru',
                },
            ),
        ]
        check_form(forms.OtpMigrateSubmitForm(), invalid_cases, valid_cases)

    def test_check_otp_form(self):
        invalid_cases = [
            (
                {},
                [
                    'otp.empty',
                ],
            ),
            (
                {
                    'otp': '   ',
                },
                [
                    'otp.empty',
                ],
            ),
        ]
        valid_cases = [
            (
                {
                    'otp': ' foobar ',
                },
                {
                    'otp': 'foobar',
                },
            ),
        ]
        check_form(forms.OtpMigrateCheckOtpForm(), invalid_cases, valid_cases)
