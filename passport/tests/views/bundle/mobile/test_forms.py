# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_CLOUD_TOKEN,
    TEST_TRACK_ID,
)
from passport.backend.api.views.bundle.mixins.challenge import MobilePasswordSource
from passport.backend.api.views.bundle.mobile.forms import (
    MobileRegisterForm,
    MobileRegisterLiteForm,
    PasswordForm,
    RfcOtpForm,
    StartForm,
    StartV1Form,
)
from passport.backend.core import validators
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.common import merge_dicts


@with_settings(
    BLACKBOX_URL='localhost',
)
class TestForms(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.blackbox = FakeBlackbox()
        self.blackbox.start()
        self.state = validators.State(mock_env(user_ip='127.0.0.1'))

    def tearDown(self):
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        del self.blackbox
        del self.state

    def test_start_v1_form(self):
        invalid_params = [
            (
                {},
                ['x_token_client_id.empty', 'x_token_client_secret.empty', 'display_language.empty'],
            ),
            (
                {
                    'display_language': 'ru',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                },
                ['form.invalid'],  # нет ни логина, ни phone_number'а
            ),
            (
                {
                    'login': '',
                    'display_language': 'ru',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                },
                ['form.invalid'],  # логин пустой, phone_number'а нет
            ),
            (
                {
                    'phone_number': '',
                    'display_language': 'ru',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                },
                ['form.invalid'],  # phone_number пустой, логина нет
            ),
            (
                {
                    'login': 'test_login',
                    'phone_number': '8-800-555-35-35',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': 'klingon',
                },
                ['form.invalid'],  # есть и login, и phone_number
            ),
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'display_language': 'ru',
                },
                ['form.invalid'],  # нет client_secret
            ),
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': '',
                    'display_language': 'ru',
                },
                ['form.invalid'],  # client_secret пуст
            ),
            (
                {
                    'login': 'a' * 256,
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'captcha_scale_factor': 'foo',
                    'display_language': 'klingon',
                    'force_register': 'nooo',
                },
                ['login.long', 'captcha_scale_factor.invalid', 'force_register.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': 'ru',
                },
                {
                    'login': 'test_login',
                    'phone_number': None,
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'payment_auth_retpath': None,
                    'cloud_token': None,
                    'display_language': 'ru',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': None,
                    'client_secret': None,
                    'force_register': False,
                },
            ),
            (
                {
                    'login': '  some--invalid..login$  ',
                    'phone_number': '  ',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': '\ntr',
                    'force_register': 'no',
                },
                {
                    'login': 'some--invalid..login$',  # провалидируется во вьюхе
                    'phone_number': None,
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'payment_auth_retpath': None,
                    'cloud_token': None,
                    'display_language': 'tr',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': None,
                    'client_secret': None,
                    'force_register': False,
                },
            ),
            (
                {
                    'phone_number': '8-800-555-35-35',
                    'avatar_size': 'xxl',
                    'captcha_scale_factor': '3',
                    'payment_auth_retpath': 'deeplink://am',
                    'cloud_token': TEST_CLOUD_TOKEN,
                    'display_language': 'en ',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'force_register': '1',
                },
                {
                    'login': None,
                    'phone_number': '8-800-555-35-35',
                    'avatar_size': 'xxl',
                    'captcha_scale_factor': 3,
                    'payment_auth_retpath': 'deeplink://am',
                    'cloud_token': TEST_CLOUD_TOKEN,
                    'display_language': 'en',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'force_register': True,
                },
            ),
            (
                {
                    'login': '  ',
                    'phone_number': '  some-invalid-stuff  ',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': 'klingon',
                    'force_register': 'yes',
                },
                {
                    'login': None,
                    'phone_number': 'some-invalid-stuff',  # провалидируется уже во вьюхе
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'payment_auth_retpath': None,
                    'cloud_token': None,
                    'display_language': '',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': None,
                    'client_secret': None,
                    'force_register': True,
                },
            ),
        ]

        check_form(StartV1Form(), invalid_params, valid_params, None)

    def test_start_form(self):
        invalid_params = [
            (
                {},
                [
                    'login.empty',
                    'x_token_client_id.empty',
                    'x_token_client_secret.empty',
                    'display_language.empty',
                ],
            ),
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'display_language': 'ru',
                },
                ['form.invalid'],  # нет client_secret
            ),
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': '',
                    'display_language': 'ru',
                },
                ['form.invalid'],  # client_secret пуст
            ),
            (
                {
                    'login': 'a' * 256,
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'captcha_scale_factor': 'foo',
                    'display_language': 'klingon',
                    'force_register': 'nooo',
                },
                ['login.long', 'captcha_scale_factor.invalid', 'force_register.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'login': 'test_login',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': 'ru',
                },
                {
                    'login': 'test_login',
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'payment_auth_retpath': None,
                    'cloud_token': None,
                    'display_language': 'ru',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': None,
                    'client_secret': None,
                    'force_register': False,
                    'is_phone_number': False,
                    'old_track_id': None,
                },
            ),
            (
                {
                    'login': '  some--invalid..login$  ',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'display_language': '\ntr',
                    'force_register': 'no',
                    'is_phone_number': '0',
                },
                {
                    'login': 'some--invalid..login$',  # провалидируется во вьюхе
                    'avatar_size': None,
                    'captcha_scale_factor': None,
                    'payment_auth_retpath': None,
                    'cloud_token': None,
                    'display_language': 'tr',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': None,
                    'client_secret': None,
                    'force_register': False,
                    'is_phone_number': False,
                    'old_track_id': None,
                },
            ),
            (
                {
                    'login': '8-800-555-35-35',
                    'avatar_size': 'xxl',
                    'captcha_scale_factor': '3',
                    'payment_auth_retpath': 'deeplink://am',
                    'cloud_token': TEST_CLOUD_TOKEN,
                    'display_language': 'en ',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'force_register': '1',
                    'is_phone_number': 'yes',
                    'old_track_id': TEST_TRACK_ID,
                },
                {
                    'login': '8-800-555-35-35',
                    'avatar_size': 'xxl',
                    'captcha_scale_factor': 3,
                    'payment_auth_retpath': 'deeplink://am',
                    'cloud_token': TEST_CLOUD_TOKEN,
                    'display_language': 'en',
                    'x_token_client_id': 'x_client_id',
                    'x_token_client_secret': 'x_client_secret',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'force_register': True,
                    'is_phone_number': True,
                    'old_track_id': TEST_TRACK_ID,
                },
            ),
        ]

        check_form(StartForm(), invalid_params, valid_params, None)

    def test_password_form(self):
        invalid_params = [
            (
                {},
                ['password.empty'],
            ),
            (
                {
                    'password': 'pass',
                    'captcha_answer': 'a' * 101,
                },
                ['captcha_answer.long'],
            ),
        ]

        valid_params = [
            (
                {
                    'password': 'pass',
                },
                {
                    'password': 'pass',
                    'captcha_answer': None,
                    'password_source': None,
                    'avatar_url': None,
                },
            ),
            (
                {
                    'password': '  pass  ',
                    'captcha_answer': 'ans',
                    'password_source': '  any  ',
                    'avatar_url': '   Https://ololo.edu/   ',
                },
                {
                    'password': 'pass',
                    'captcha_answer': 'ans',
                    'password_source': '',
                    'avatar_url': 'https://ololo.edu/',
                },
            ),
            (
                {
                    'password': '  pass  ',
                    'captcha_answer': 'ans',
                    'password_source': MobilePasswordSource.CAPTCHA,
                    'avatar_url': 'Https://ololo.edu/?secret=super',
                },
                {
                    'password': 'pass',
                    'captcha_answer': 'ans',
                    'password_source': MobilePasswordSource.CAPTCHA,
                    'avatar_url': 'https://ololo.edu/?secret=super',
                },
            ),
        ]

        check_form(PasswordForm(), invalid_params, valid_params, None)

    def test_rfc_otp_form(self):
        invalid_params = [
            (
                {},
                ['rfc_otp.empty'],
            ),
            (
                {
                    'rfc_otp': '123',
                    'captcha_answer': 'a' * 101,
                },
                ['captcha_answer.long'],
            ),
        ]

        valid_params = [
            (
                {
                    'rfc_otp': '123',
                },
                {
                    'rfc_otp': '123',
                    'captcha_answer': None,
                },
            ),
            (
                {
                    'rfc_otp': '  123  ',
                    'captcha_answer': 'ans',
                },
                {
                    'rfc_otp': '123',
                    'captcha_answer': 'ans',
                },
            ),
        ]

        check_form(RfcOtpForm(), invalid_params, valid_params, None)

    def test_register_form(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'login': 'free'}),
        )

        default_params = {
            'login': 'login',
            'firstname': 'name',
            'lastname': 'surname',
            'password': 'testpasswd',
            'eula_accepted': '1',
        }

        invalid_params = [
            (
                {},
                [
                    'login.empty',
                    'password.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'eula_accepted.empty',
                ],
            ),
            (
                merge_dicts(
                    default_params,
                    {
                        'login': 'a--b',
                        'firstname': '',
                        'lastname': '   ',
                    },
                ),
                [
                    'login.doubledhyphen',
                    'firstname.empty',
                    'lastname.empty',
                ],
            ),
            (
                merge_dicts(
                    default_params,
                    {
                        'firstname': 'Visit mail.google.ru',
                        'lastname': 'Visit mail.google.com',
                    },
                ),
                [
                    'firstname.invalid',
                    'lastname.invalid',
                ],
            ),
        ]
        valid_params = [
            (
                default_params.copy(),
                merge_dicts(
                    default_params.copy(),
                    {
                        'eula_accepted': True,
                        'firstname': 'name',
                        'lastname': 'surname',
                        'force_clean_web': False,
                        'unsubscribe_from_maillists': False,
                    },
                ),
            ),
            (
                merge_dicts(
                    default_params.copy(),
                    {
                        'firstname': 'ab' * 26,
                        'lastname': u'Петрович',
                        'language': 'en',
                        'password': 'pass \t',
                        'unsubscribe_from_maillists': 'yes',
                    },
                ),
                merge_dicts(
                    default_params.copy(),
                    {
                        'firstname': 'ab' * 25,
                        'lastname': u'Петрович',
                        'eula_accepted': True,
                        'password': 'pass \t',
                        'force_clean_web': False,
                        'unsubscribe_from_maillists': True,
                    },
                ),
            ),
        ]

        check_form(MobileRegisterForm(), invalid_params, valid_params, self.state)

    def test_register_lite_form(self):
        default_params = {
            'firstname': 'name',
            'lastname': 'surname',
            'password': 'testpasswd',
            'eula_accepted': '1',
        }

        invalid_params = [
            (
                {},
                [
                    'eula_accepted.empty',
                ],
            ),
            (
                merge_dicts(
                    default_params,
                    {
                        'firstname': 'Visit mail.google.ru',
                        'lastname': 'Visit mail.google.com',
                    },
                ),
                [
                    'firstname.invalid',
                    'lastname.invalid',
                ],
            ),
        ]
        valid_params = [
            (
                {
                    'eula_accepted': '1',
                },
                {
                    'firstname': None,
                    'lastname': None,
                    'password': None,
                    'eula_accepted': True,
                    'force_clean_web': False,
                    'unsubscribe_from_maillists': False,
                },
            ),
            (
                default_params,
                merge_dicts(
                    default_params.copy(),
                    {
                        'eula_accepted': True,
                        'firstname': 'name',
                        'lastname': 'surname',
                        'force_clean_web': False,
                        'unsubscribe_from_maillists': False,
                    },
                ),
            ),
            (
                merge_dicts(
                    default_params.copy(),
                    {
                        'firstname': 'ab' * 26,
                        'lastname': u'Петрович',
                        'password': 'pass \t',
                        'unsubscribe_from_maillists': 'yes',
                    },
                ),
                merge_dicts(
                    default_params.copy(),
                    {
                        'firstname': 'ab' * 25,
                        'lastname': u'Петрович',
                        'eula_accepted': True,
                        'password': 'pass \t',
                        'force_clean_web': False,
                        'unsubscribe_from_maillists': True,
                    },
                ),
            ),
        ]

        check_form(MobileRegisterLiteForm(), invalid_params, valid_params, self.state)
