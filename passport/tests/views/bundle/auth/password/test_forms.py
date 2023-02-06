# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.password import forms
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.utils import with_settings_hosts
import pytz


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_submit_form(self):
        invalid_params = [
            (
                {'policy': 'short'},
                ['policy.invalid'],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'login': None,
                    'password': None,
                    'retpath': None,
                    'service': None,
                    'origin': None,
                    'policy': 'long',
                    'is_pdd': False,
                    'fretpath': None,
                    'clean': None,
                },
            ),
            (
                {'policy': 'sessional'},
                {
                    'login': None,
                    'password': None,
                    'retpath': None,
                    'service': None,
                    'origin': None,
                    'policy': 'sessional',
                    'is_pdd': False,
                    'fretpath': None,
                    'clean': None,
                },
            ),
            (
                {
                    'login': 'a',
                    'password': 'bcd',
                    'retpath': 'http://yandex.ru',
                    'service': 'dev',
                    'origin': 'maps',
                    'policy': 'sessional',
                    'is_pdd': 'True',
                    'fretpath': 'http://yandex.com',
                    'clean': 'yes',
                },
                {
                    'login': 'a',
                    'password': 'bcd',
                    'retpath': 'http://yandex.ru',
                    'service': get_service(slug='dev'),
                    'origin': 'maps',
                    'policy': 'sessional',
                    'is_pdd': True,
                    'fretpath': 'http://yandex.com',
                    'clean': 'yes',
                },
            ),
        ]

        check_form(forms.SubmitAuthorizationForm(), invalid_params, valid_params, None)

    def test_complete_pdd_form(self):
        invalid_params = [
            (
                {},
                [
                    'answer.empty',
                    'display_language.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                ],
            ),
            (
                {
                    'display_language': ' ',
                    'eula_accepted': ' ',
                    'firstname': ' ',
                    'lastname': ' ',
                    'answer': ' ',
                },
                [
                    'answer.empty',
                    'display_language.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                ],
            ),
            (
                {
                    'display_language': 'R',
                    'eula_accepted': 'abc',
                    'firstname': 'first',
                    'lastname': 'last',
                    'gender': '3',
                    'birthday': '1-1-1',
                    'timezone': '+4',
                    'country': '-1',
                    'answer': 'a' * 31,
                    'question': 'a' * 38,
                    'question_id': '200',
                },
                [
                    'answer.long',
                    'birthday.invalid',
                    'country.invalid',
                    'display_language.invalid',
                    'eula_accepted.invalid',
                    'gender.invalid',
                    'question.long',
                    'question_id.invalid',
                    'timezone.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'display_language': 'RU',
                    'eula_accepted': 'True',
                    'firstname': 'first',
                    'lastname': 'last',
                    'answer': '42',
                },
                {
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'firstname': 'first',
                    'lastname': 'last',
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'language': None,
                    'timezone': None,
                    'question': None,
                    'question_id': None,
                    'answer': '42',
                    'force_clean_web': False,
                },
            ),
            (
                {
                    'display_language': 'EN',
                    'eula_accepted': 'False',
                    'firstname': 'name',
                    'lastname': 'surname',
                    'gender': '1',
                    'birthday': '1970-01-01',
                    'country': 'ru',
                    'language': 'ru',
                    'timezone': 'Europe/Paris',
                    'question': '?',
                    'question_id': '11',
                    'answer': '42',
                },
                {
                    'display_language': 'en',
                    'eula_accepted': False,
                    'firstname': 'name',
                    'lastname': 'surname',
                    'gender': 1,
                    'birthday': '1970-01-01',
                    'country': 'ru',
                    'language': 'ru',
                    'timezone': pytz.timezone('Europe/Paris'),
                    'question': '?',
                    'question_id': 11,
                    'answer': '42',
                    'force_clean_web': False,
                },
            ),
        ]

        check_form(forms.AccountCompletePdd(), invalid_params, valid_params, None)

    def test_complete_pdd_password_form(self):
        invalid_params = [
            (
                {},
                [
                    'answer.empty',
                    'display_language.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'password.empty',
                ],
            ),
            (
                {
                    'display_language': ' ',
                    'eula_accepted': ' ',
                    'firstname': ' ',
                    'lastname': ' ',
                    'answer': ' ',
                    'password': ' ',
                },
                [
                    'answer.empty',
                    'display_language.empty',
                    'eula_accepted.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'password.empty',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'display_language': 'RU',
                    'eula_accepted': 'True',
                    'firstname': 'first',
                    'lastname': 'last',
                    'answer': '42',
                    'password': 'abc',
                },
                {
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'firstname': 'first',
                    'lastname': 'last',
                    'gender': None,
                    'birthday': None,
                    'country': None,
                    'language': None,
                    'timezone': None,
                    'question': None,
                    'question_id': None,
                    'answer': '42',
                    'password': 'abc',
                    'force_clean_web': False,
                },
            ),
        ]

        check_form(forms.AccountCompletePddPassword(), invalid_params, valid_params, None)

    def test_complete_pdd_workspace_form(self):
        invalid_params = [
            (
                {},
                [
                    'display_language.empty',
                    'eula_accepted.empty',
                ],
            ),
            (
                {
                    'display_language': ' ',
                    'eula_accepted': ' ',
                },
                [
                    'display_language.empty',
                    'eula_accepted.empty',
                ],
            ),
            (
                {
                    'display_language': 'R',
                    'eula_accepted': 'abc',
                    'timezone': '+4',
                    'country': '-1',
                },
                [
                    'country.invalid',
                    'display_language.invalid',
                    'eula_accepted.invalid',
                    'timezone.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'display_language': 'RU',
                    'eula_accepted': 'True',
                },
                {
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'country': None,
                    'timezone': None,
                },
            ),
            (
                {
                    'display_language': 'EN',
                    'eula_accepted': 'False',
                    'country': 'ru',
                    'timezone': 'Europe/Paris',
                },
                {
                    'display_language': 'en',
                    'eula_accepted': False,
                    'country': 'ru',
                    'timezone': pytz.timezone('Europe/Paris'),
                },
            ),
        ]

        check_form(forms.AccountCompleteWorkspacePdd(), invalid_params, valid_params, None)

    def test_complete_pdd_workspace_password_form(self):
        invalid_params = [
            (
                {},
                [
                    'display_language.empty',
                    'eula_accepted.empty',
                    'password.empty',
                ],
            ),
            (
                {
                    'display_language': ' ',
                    'eula_accepted': ' ',
                    'password': ' ',
                },
                [
                    'display_language.empty',
                    'eula_accepted.empty',
                    'password.empty',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'display_language': 'RU',
                    'eula_accepted': 'True',
                    'password': 'abc',
                },
                {
                    'display_language': 'ru',
                    'eula_accepted': True,
                    'country': None,
                    'timezone': None,
                    'password': 'abc',
                },
            ),
        ]

        check_form(forms.AccountCompleteWorkspacePddPassword(), invalid_params, valid_params, None)

    def test_complete_autoregistered_form(self):
        invalid_params = [
            (
                {},
                ['validation_method.empty', 'eula_accepted.empty', 'password.empty'],
            ),
            (
                {'eula_accepted': ' ', 'password': ' '},
                ['validation_method.empty', 'eula_accepted.empty'],
            ),
            (
                {'validation_method': 'abc', 'eula_accepted': 'abc', 'password': 'abc'},
                ['validation_method.invalid', 'eula_accepted.invalid'],
            ),
            (
                {'validation_method': 'captcha', 'eula_accepted': 'True', 'password': 'abc', 'country': '-1'},
                ['country.invalid'],
            ),
            (
                {'validation_method': 'captcha', 'eula_accepted': 'True', 'password': 'abc', 'timezone': '+4'},
                ['timezone.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'validation_method': 'captcha',
                    'eula_accepted': 'True',
                    'password': 'abc',
                },
                {
                    'validation_method': 'captcha',
                    'eula_accepted': True,
                    'country': None,
                    'language': None,
                    'timezone': None,
                    'password': 'abc',
                },
            ),
            (
                {
                    'validation_method': 'phone',
                    'country': 'ru',
                    'language': 'ru',
                    'timezone': 'Europe/Paris',
                    'eula_accepted': 'True',
                    'password': 'abc',
                },
                {
                    'validation_method': 'phone',
                    'eula_accepted': True,
                    'country': 'ru',
                    'language': 'ru',
                    'timezone': pytz.timezone('Europe/Paris'),
                    'password': 'abc',
                },
            ),
        ]

        check_form(forms.CompleteAutoregistered(), invalid_params, valid_params, None)

    def test_change_password_form(self):
        invalid_params = [
            ({}, ['password.empty']),
            ({'password': ' '}, ['password.empty']),
        ]

        valid_params = [
            ({'password': 'abc'}, {'password': 'abc'}),
        ]

        check_form(forms.ChangePasswordForm(), invalid_params, valid_params, None)

    def test_confirm_submit_form(self):
        invalid_params = []

        valid_params = [
            (
                {},
                {'retpath': None, 'origin': None},
            ),
            (
                {'retpath': ' '},
                {'retpath': None, 'origin': None},
            ),
            (
                {'retpath': 'abc'},
                {'retpath': None, 'origin': None},
            ),
            (
                {'retpath': 'http://google.com'},
                {'retpath': None, 'origin': None},
            ),
            (
                {'retpath': 'http://yandex.ru', 'origin': 'test'},
                {'retpath': 'http://yandex.ru', 'origin': 'test'},
            ),
        ]

        check_form(forms.ConfirmSubmitForm(), invalid_params, valid_params, None)

    def test_confirm_commit_password_form(self):
        invalid_params = []

        valid_params = [
            ({}, {'password': None}),
            ({'password': 'abc'}, {'password': 'abc'}),
        ]

        check_form(forms.ConfirmCommitPasswordForm(), invalid_params, valid_params, None)

    def test_confirm_commit_magic_form(self):
        invalid_params = [
            ({}, ['csrf_token.empty']),
            ({'csrf_token': ' '}, ['csrf_token.empty']),
        ]

        valid_params = [
            ({'csrf_token': 'abc'}, {'csrf_token': 'abc'}),
        ]

        check_form(forms.ConfirmCommitMagicForm(), invalid_params, valid_params, None)
