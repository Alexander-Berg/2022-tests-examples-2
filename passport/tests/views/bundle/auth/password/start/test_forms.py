# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.password import forms
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.utils import with_settings


DEFAULT_SUBMIT_FORM = {
    # для AM
    'am_version': None,
    'am_version_name': None,
    'app_id': None,
    'app_platform': None,
    'app_version': None,
    'app_version_name': None,
    'device_id': None,
    'device_name': None,
    'deviceid': None,
    'ifv': None,
    'manufacturer': None,
    'model': None,
    'os_version': None,
    'uuid': None,
    # специфичное для ручки
    'retpath': None,
    'fretpath': None,
    'clean': None,
    'origin': None,
    'service': None,
    'policy': 'long',
    'with_code': False,
}


@with_settings
class TestForms(unittest.TestCase):

    def test_submit_form(self):
        invalid_params = []

        valid_params = [
            (
                {},
                DEFAULT_SUBMIT_FORM,
            ),
            (
                {
                    'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                    'origin': 'or', 'service': 'mail', 'policy': 'sessional',
                    'with_code': '0',
                },
                dict(
                    DEFAULT_SUBMIT_FORM,
                    **{
                        'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                        'origin': 'or', 'service': get_service(slug='mail'), 'policy': 'sessional',
                        'with_code': False,
                    }
                ),
            ),
            (
                {
                    'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                    'origin': 'or', 'service': 'mail', 'policy': 'sessional',
                    'with_code': '1',
                },
                dict(
                    DEFAULT_SUBMIT_FORM,
                    **{
                        'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                        'origin': 'or', 'service': get_service(slug='mail'), 'policy': 'sessional',
                        'with_code': True,
                    }
                ),
            ),
        ]

        check_form(forms.SubmitForm(), invalid_params, valid_params, None)

    def test_commit_password_form(self):
        invalid_params = []

        valid_params = [
            (
                {},
                {
                    'login': None, 'password': None, 'is_pdd': False,
                    'retpath': None, 'fretpath': None, 'clean': None,
                    'origin': None, 'service': None, 'policy': 'long',
                },
            ),
            (
                {
                    'login': 'abc', 'password': 'def', 'is_pdd': 'yes',
                    'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                    'origin': 'or', 'service': 'mail', 'policy': 'sessional',
                },
                {
                    'login': 'abc', 'password': 'def', 'is_pdd': True,
                    'retpath': 'http://yandex.ru', 'fretpath': 'fr', 'clean': 'cl',
                    'origin': 'or', 'service': get_service(slug='mail'), 'policy': 'sessional',
                },
            ),
        ]

        check_form(forms.CommitPasswordForm(), invalid_params, valid_params, None)

    def test_commit_magic_form(self):
        invalid_params = [
            ({}, ['csrf_token.empty']),
            ({'csrf_token': ' '}, ['csrf_token.empty']),
        ]

        valid_params = [
            (
                {
                    'csrf_token': 'abc',
                },
                {
                    'csrf_token': 'abc',
                    'need_oauth_token': False,
                },
            ),
            (
                {
                    'csrf_token': 'abc',
                    'need_oauth_token': 'true',
                },
                {
                    'csrf_token': 'abc',
                    'need_oauth_token': True,
                },
            ),
        ]

        check_form(forms.CommitMagicForm(), invalid_params, valid_params, None)
