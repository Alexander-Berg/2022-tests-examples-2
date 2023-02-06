# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.email.forms import (
    ConfirmEmailForm,
    DeleteEmailByAdminForm,
    SendConfirmationEmailForm,
    SetupConfirmedEmailFormV1,
)
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings(
    PASSPORT_TLDS=('ru', 'en', 'by'),
)
class TestForms(unittest.TestCase):
    def test_modify_confirmed_email_form(self):
        invalid_params = [
            ({},
             ['uid.empty', 'email.empty']),
            ({'uid': '', 'email': '', 'is_silent': ''},
             ['uid.empty', 'email.empty', 'is_silent.empty']),
            ({'uid': 1234, 'email': u'невалидный_email'},
             ['email.invalid']),
        ]

        valid_params = [
            ({'uid': 1234, 'email': 'mail@yandex.ru'},
             {'uid': 1234, 'email': 'mail@yandex.ru', 'is_silent': None}),
            ({'uid': 1234, 'email': 'mail@yandex.ru', 'is_silent': 'yes'},
             {'uid': 1234, 'email': 'mail@yandex.ru', 'is_silent': True}),
        ]

        check_form(SetupConfirmedEmailFormV1(), invalid_params, valid_params, None)

    def test_confirm_email_form(self):
        invalid_params = [
            (
                {},
                ['key.empty'],
            ),
            (
                {'uid': '', 'key': ''},
                ['uid.empty', 'key.empty'],
            ),
        ]

        valid_params = [
            (
                {'key': 'foo'},
                {'uid': None, 'key': 'foo'},
            ),
            (
                {'uid': 1234, 'key': 'foo'},
                {'uid': 1234, 'key': 'foo'},
            ),
        ]

        check_form(ConfirmEmailForm(), invalid_params, valid_params, None)

    def test_delete_email_by_admin_form(self):
        invalid_params = [
            (
                {},
                ['uid.empty', 'email.empty', 'admin_name.empty'],
            ),
            (
                {'uid': '', 'email': '', 'admin_name': '', 'comment': ''},
                ['uid.empty', 'email.empty', 'admin_name.empty', 'comment.empty'],
            ),
            (
                {'uid': 1234, 'admin_name': 'foo', 'email': u'невалидный_email'},
                ['email.invalid'],
            ),
        ]

        valid_params = [
            (
                {'uid': 1234, 'email': 'mail@yandex.ru', 'admin_name': 'foo'},
                {'uid': 1234, 'email': 'mail@yandex.ru', 'admin_name': 'foo', 'comment': ''},
            ),
            (
                {'uid': 1234, 'email': 'mail@yandex.ru', 'admin_name': 'foo', 'comment': 'bar'},
                {'uid': 1234, 'email': 'mail@yandex.ru', 'admin_name': 'foo', 'comment': 'bar'},
            ),
        ]

        check_form(DeleteEmailByAdminForm(), invalid_params, valid_params, None)

    def test_send_confirmation_email_form(self):
        invalid_params = [
            (
                {'code_only': ''},
                ['email.empty', 'retpath.empty', 'validator_ui_url.empty', 'code_only.empty'],
            ),
            (
                {
                    'email': u'невалидный_email',
                    'retpath': 'zar',
                    'validator_ui_url': 'xar',
                    'uid': 'foo',
                    'language': 'bar',
                    'code_only': 'wat',
                    'is_safe': 'nooo',
                },
                [
                    'uid.invalid',
                    'email.invalid',
                    'language.invalid',
                    'retpath.invalid',
                    'validator_ui_url.invalid',
                    'code_only.invalid',
                    'is_safe.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'email': 'mail@yandex.ru',
                    'retpath': 'http://ya.ru',
                    'validator_ui_url': 'http://yandex.com',
                },
                {
                    'uid': None,
                    'email': 'mail@yandex.ru',
                    'language': None,
                    'retpath': 'http://ya.ru',
                    'validator_ui_url': 'http://yandex.com',
                    'code_only': False,
                    'is_safe': True,
                },
            ),
            (
                {
                    'uid': 1234,
                    'email': 'mail@gmail.com',
                    'language': 'en',
                    'retpath': 'http://yandex.com',
                    'validator_ui_url': 'http://yandex.com',
                    'code_only': 'yes',
                    'is_safe': 'no',
                },
                {
                    'uid': 1234,
                    'email': 'mail@gmail.com',
                    'language': 'en',
                    'retpath': 'http://yandex.com',
                    'validator_ui_url': 'http://yandex.com',
                    'code_only': True,
                    'is_safe': False,
                },
            ),
        ]

        check_form(SendConfirmationEmailForm(), invalid_params, valid_params, None)
