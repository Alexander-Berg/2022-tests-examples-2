# -*- coding: utf-8 -*-

import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.change_password import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_submit_form(self):

        valid_params = [
            (
                {},
                {
                    'origin': None,
                    'retpath': None,
                    'is_pdd': False,
                },
            ),
            (
                {
                    'retpath': 'http://yandex.ru',
                    'origin': '',
                },
                {
                    'origin': '',
                    'retpath': 'http://yandex.ru',
                    'is_pdd': False,
                },
            ),
            (
                {
                    'origin': 'test ',
                    'is_pdd': '1',
                },
                {
                    'origin': 'test',
                    'retpath': None,
                    'is_pdd': True,
                },
            ),
        ]

        check_form(forms.ChangePasswordSubmitForm(), [], valid_params, None)

    def test_commit_form(self):
        """Действующий пароль и новый пароль передаются БЕЗ изменений(no strip)"""

        valid_params = [
            (
                {
                    'current_password': 'qwerty \t',
                    'password': '  ytrewq',
                },
                {
                    'current_password': 'qwerty \t',
                    'password': '  ytrewq',
                    'is_pdd': False,
                    'revoke_web_sessions': True,
                    'revoke_tokens': True,
                    'revoke_app_passwords': True,
                },
            ),
            (
                {
                    'current_password': 'qwerty \t',
                    'password': '  ytrewq',
                    'is_pdd': '1',
                    'revoke_web_sessions': '0',
                    'revoke_tokens': '0',
                    'revoke_app_passwords': '0',
                },
                {
                    'current_password': 'qwerty \t',
                    'password': '  ytrewq',
                    'is_pdd': True,
                    'revoke_web_sessions': False,
                    'revoke_tokens': False,
                    'revoke_app_passwords': False,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'current_password': '',
                    'password': '',
                },
                ['current_password.empty', 'password.empty'],
            ),
        ]

        check_form(forms.ChangePasswordCommitForm(), invalid_params, valid_params, None)

    def test_optional_logout_form(self):
        valid_params = [
            (
                {},
                {
                    'revoke_web_sessions': False,
                    'revoke_tokens': False,
                    'revoke_app_passwords': False,
                },
            ),
            (
                {
                    'revoke_web_sessions': '1',
                    'revoke_tokens': '1',
                    'revoke_app_passwords': '1',
                },
                {
                    'revoke_web_sessions': True,
                    'revoke_tokens': True,
                    'revoke_app_passwords': True,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'revoke_web_sessions': 'x',
                    'revoke_tokens': 'asdf',
                    'revoke_app_passwords': 'z',
                },
                [
                    'revoke_web_sessions.invalid',
                    'revoke_tokens.invalid',
                    'revoke_app_passwords.invalid',
                ],
            ),
        ]

        check_form(forms.ChangePasswordOptionalLogoutForm(), invalid_params, valid_params, None)
