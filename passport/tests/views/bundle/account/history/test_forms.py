# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.history import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    ACCOUNT_HISTORY_MAX_LIMIT=10,
    ACCOUNT_HISTORY_DEFAULT_LIMIT=50,
)
class TestHistoryForms(unittest.TestCase):
    def test_history_form(self):
        valid_params = [
            (
                {
                    'uid': '123',
                    'limit': '1',
                    'from_auth_row': '',
                },
                {
                    'uid': 123,
                    'limit': 1,
                    'from_auth_row': None,
                    'password_auths': None,
                    'hours_limit': None,
                },
            ),
            (
                {
                    'uid': '123',
                    'limit': '10',
                    'hours_limit': '10',
                },
                {
                    'uid': 123,
                    'limit': 10,
                    'from_auth_row': None,
                    'password_auths': None,
                    'hours_limit': 10,
                },
            ),
            (
                {
                    'uid': '123',
                    'limit': '1',
                    'from_auth_row': '//nhk3dlYw==',
                },
                {
                    'uid': 123,
                    'limit': 1,
                    'from_auth_row': '//nhk3dlYw==',
                    'password_auths': None,
                    'hours_limit': None,
                },
            ),
            (
                {
                    'limit': 1,
                },
                {
                    'uid': None,
                    'limit': 1,
                    'from_auth_row': None,
                    'password_auths': None,
                    'hours_limit': None,
                },
            ),
            (
                {
                    'uid': '123',
                    'password_auths': 'true',
                },
                {
                    'uid': 123,
                    'limit': 50,
                    'from_auth_row': None,
                    'password_auths': True,
                    'hours_limit': None,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'uid': '',
                    'hours_limit': '',
                },
                ['uid.empty', 'hours_limit.empty'],
            ),
            (
                {
                    'uid': 'bla',
                    'limit': 'bla',
                    'hours_limit': 'bla',
                },
                ['uid.invalid', 'limit.invalid', 'hours_limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'limit': '0',
                    'hours_limit': '0',
                },
                ['uid.invalid', 'limit.invalid', 'hours_limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'limit': '11',
                    'hours_limit': str(24 * 365 * 31)
                },
                ['uid.invalid', 'limit.invalid', 'hours_limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'password_auths': 'bla',
                },
                ['uid.invalid', 'password_auths.invalid'],
            ),
        ]

        check_form(forms.HistoryForm(), invalid_params, valid_params, None)
