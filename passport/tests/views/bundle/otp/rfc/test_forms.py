# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.otp.rfc import forms


class FormsTestCase(unittest.TestCase):
    def test_manage_form(self):
        invalid_cases = [
            (
                {},
                ['login.empty'],
            ),
        ]

        valid_cases = [
            (
                {
                    'login': 'test-login',
                },
                {
                    'login': 'test-login',
                },
            ),
        ]

        check_form(forms.RfcOtpManageForm(), invalid_cases, valid_cases)

    def test_set_check_time_form(self):
        invalid_cases = [
            (
                {},
                ['uid.empty', 'totp_check_time.empty'],
            ),
            (
                {
                    'uid': '',
                    'totp_check_time': '',
                },
                ['uid.empty', 'totp_check_time.empty'],
            ),
            (
                {
                    'uid': 'foo',
                    'totp_check_time': 'foo',
                },
                ['uid.invalid', 'totp_check_time.invalid'],
            ),
        ]

        valid_cases = [
            (
                {
                    'uid': 1,
                    'totp_check_time': 100,
                },
                {
                    'uid': 1,
                    'totp_check_time': 100,
                },
            ),
        ]

        check_form(forms.RfcOtpSetCheckTimeForm(), invalid_cases, valid_cases)
