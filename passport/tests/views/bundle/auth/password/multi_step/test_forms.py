# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.password.multi_step import forms
from passport.backend.core.services import get_service
from passport.backend.core.test.consts import TEST_TRACK_ID1
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings
class TestForms(unittest.TestCase):

    def test_start_form(self):
        invalid_params = [
            ({}, ['login.empty']),
            ({'login': ' '}, ['login.empty']),
            ({'login': 'a' * 256}, ['login.long']),
        ]

        valid_params = [
            (
                {
                    'login': 'abc',
                },
                {
                    'allow_scholar': False,
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'clean': None,
                    'client_id': None,
                    'client_secret': None,
                    'cloud_token': None,
                    'display_language': None,
                    'force_register': False,
                    'fretpath': None,
                    'is_pdd': False,
                    'login': 'abc',
                    'origin': None,
                    'payment_auth_retpath': None,
                    'policy': 'long',
                    'process_uuid': None,
                    'retpath': None,
                    'service': None,
                    'social_track_id': None,
                    'old_track_id': None,
                    'x_token_client_id': None,
                    'x_token_client_secret': None,
                    'with_2fa_pictures': False,
                },
            ),
            (
                {
                    'allow_scholar': '1',
                    'avatar_size': 'small',
                    'captcha_scale_factor': '2',
                    'clean': 'cl',
                    'client_id': 'clid',
                    'client_secret': 'cls',
                    'cloud_token': 'clt',
                    'display_language': 'en',
                    'force_register': 'true',
                    'fretpath': 'fr',
                    'is_pdd': '1',
                    'login': 'a' * 255,
                    'origin': 'or',
                    'payment_auth_retpath': 'https://ya.ru',
                    'policy': 'sessional',
                    'process_uuid': 'diuu',
                    'retpath': 'http://yandex.ru',
                    'service': 'mail',
                    'social_track_id': TEST_TRACK_ID1,
                    'old_track_id': TEST_TRACK_ID1,
                    'x_token_client_id': 'xclid',
                    'x_token_client_secret': 'xcls',
                    'with_2fa_pictures': '1',
                },
                {
                    'allow_scholar': True,
                    'avatar_size': 'small',
                    'captcha_scale_factor': 2,
                    'clean': 'cl',
                    'client_id': 'clid',
                    'client_secret': 'cls',
                    'cloud_token': 'clt',
                    'display_language': 'en',
                    'force_register': True,
                    'fretpath': 'fr',
                    'is_pdd': True,
                    'login': 'a' * 255,
                    'origin': 'or',
                    'payment_auth_retpath': 'https://ya.ru',
                    'policy': 'sessional',
                    'process_uuid': 'diuu',
                    'retpath': 'http://yandex.ru',
                    'service': get_service(slug='mail'),
                    'social_track_id': TEST_TRACK_ID1,
                    'old_track_id': TEST_TRACK_ID1,
                    'x_token_client_id': 'xclid',
                    'x_token_client_secret': 'xcls',
                    'with_2fa_pictures': True,
                },
            ),
        ]

        check_form(forms.MultiStepStartForm(), invalid_params, valid_params, None)

    def test_commit_password_form(self):
        invalid_params = [
            ({}, ['password.empty']),
            ({'password': ' '}, ['password.empty']),
        ]

        valid_params = [
            ({'password': 'def'}, {'password': 'def'}),
        ]

        check_form(forms.MultiStepPasswordForm(), invalid_params, valid_params, None)

    def test_commit_magic_form(self):
        invalid_params = [
            ({}, ['csrf_token.empty']),
            ({'csrf_token': ' '}, ['csrf_token.empty']),
        ]

        valid_params = [
            ({'csrf_token': 'abc'}, {'csrf_token': 'abc'}),
        ]

        check_form(forms.MultiStepMagicForm(), invalid_params, valid_params, None)

    def test_magic_link_submit_form(self):
        invalid_params = [
            ({'send_to': ' '}, ['send_to.empty']),
            ({'send_to': 'unknown'}, ['send_to.invalid']),
        ]

        valid_params = [
            ({}, {'send_to': 'email'}),
            ({'send_to': 'email'}, {'send_to': 'email'}),
        ]

        check_form(forms.MultiStepMagicLinkSendForm(), invalid_params, valid_params, None)

    def test_magic_link_confirm_form(self):
        invalid_params = [
            ({}, ['secret.empty']),
            ({'secret': ' '}, ['secret.empty']),
            ({'secret': 'asd'}, ['secret.invalid']),
        ]

        valid_params = [
            (
                {'secret': ' d80fc3dda7fb002fe8951\t'},
                {
                    'secret': {'secret': 'd80fc3dda7fb002fe8951', 'key': 'd80fc3dda7fb002fe895', 'uid': 1},
                    'redirect': False,
                },
            ),
            (
                {
                    'secret': 'd80fc3dda7fb002fe8951',
                    'redirect': 'true',
                },
                {
                    'secret': {'secret': 'd80fc3dda7fb002fe8951', 'key': 'd80fc3dda7fb002fe895', 'uid': 1},
                    'redirect': True,
                },
            ),
        ]

        check_form(forms.MultiStepMagicLinkConfirmForm(), invalid_params, valid_params, None)

    def test_magic_link_confirm_registration_form(self):
        invalid_params = [
            ({}, ['secret.empty']),
            ({'secret': ' '}, ['secret.empty']),
            ({'secret': 'a' * 19}, ['secret.short']),
            ({'secret': 'a' * 21}, ['secret.long']),
        ]

        valid_params = [
            (
                {
                    'secret': ' d80fc3dda7fb002fe895 ',
                },
                {
                    'secret': 'd80fc3dda7fb002fe895',
                    'redirect': False,
                },
            ),
            (
                {
                    'secret': 'd80fc3dda7fb002fe895',
                    'redirect': 'true',
                },
                {
                    'secret': 'd80fc3dda7fb002fe895',
                    'redirect': True,
                },
            ),
        ]

        check_form(forms.MultiStepMagicLinkConfirmRegistrationForm(), invalid_params, valid_params, None)

    def test_magic_link_info_form(self):
        invalid_params = [
            ({}, ['avatar_size.empty']),
            ({'avatar_size': ' '}, ['avatar_size.empty']),
            ({'avatar_size': 'a' * 101}, ['avatar_size.long']),
        ]

        valid_params = [
            (
                {'avatar_size': ' islands-123\t'},
                {'avatar_size': 'islands-123'},
            ),
            (
                {'avatar_size': 'a' * 100},
                {'avatar_size': 'a' * 100},
            ),
        ]

        check_form(forms.MultiStepMagicLinkInfoForm(), invalid_params, valid_params, None)
