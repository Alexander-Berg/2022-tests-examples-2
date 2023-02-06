# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import TestCase

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.complete import forms
from passport.backend.core import validators
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    FakeBlackbox,
)
from passport.backend.core.conf import settings
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils.mock_objects import (
    mock_env,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types import birthday
from passport.backend.core.types.gender import Gender
from passport.backend.utils.common import merge_dicts
import pytz


@with_settings_hosts(
    DISPLAY_LANGUAGES=['en', 'ru', 'tr', 'uk'],
    PORTAL_LANGUAGES=['en', 'ru', 'tr', 'uk'],
    LANGUAGE_TO_TLD_MAPPING={
        'en': 'com',
        'ru': 'ru',
        'tr': 'com.tr',
        'uk': 'ua',
    },
    PASSPORT_DEFAULT_TLD='ru',
)
class TestCompleteForms(TestCase):
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

        self.track_id = "0a" * settings.TRACK_RANDOM_BYTES_COUNT + "00"
        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()

        self.fake_grants = FakeGrants()
        self.fake_grants.start()
        self.fake_grants.set_grants_return_value(mock_grants())

        self.fake_blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'userlogin': 'free'}),
        )

    def tearDown(self):
        self.fake_blackbox.stop()
        self.fake_grants.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        del self.fake_blackbox
        del self.fake_grants

    def test_complete_status(self):
        invalid_params = [
            (
                {
                    'completion_postponed_at': 'foo',
                },
                [
                    'completion_postponed_at.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'language': 'ru',
                    'completion_postponed_at': None,
                }
            ),
            (
                {
                    'language': 'klgn',
                },
                {
                    'language': None,
                    'completion_postponed_at': None,
                }
            ),
            (
                {
                    'language': 'en',
                    'completion_postponed_at': 42,
                },
                {
                    'language': 'en',
                    'completion_postponed_at': datetime.fromtimestamp(42),
                }
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteStatusForm(), invalid_params, valid_params, state)

    def test_complete_commit_base(self):
        DEFAULT_VALID_PARAMS = {
            'track_id': self.track_id,
            'display_language': 'ru',
            # Персональные данные
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            # Язык
            'language': 'ru',
            'country': 'ru',
            'gender': 'm',
            'birthday': '1950-05-01',
            'timezone': 'Europe/Moscow',
            'validation_method': 'captcha',
            # КВ/КО
            'question': 'question',
            'question_id': 1,
            'answer': 'answer',
        }

        def build_params(params, expected):
            return (merge_dicts(DEFAULT_VALID_PARAMS, params), expected)

        invalid_params = [
            # missing
            (
                {},
                ['display_language.empty'],
            ),
            # empty
            (
                {
                    'track_id': self.track_id, 'display_language': '',
                    'firstname': '', 'lastname': '', 'language': '',
                    'country': '', 'gender': '', 'birthday': '', 'timezone': '',
                    'validation_method': '',
                },
                ['country.empty', 'display_language.empty', 'language.empty'],
            ),
            # display_language
            build_params(
                {'display_language': 'bad language'},
                ['display_language.invalid'],
            ),
            # validation_method
            build_params(
                {'validation_method': 'abcdefg'},
                ['validation_method.invalid'],
            ),
        ]

        valid_params = [
            # all fields (except question)
            build_params(
                {'question_id': 1, 'answer': 'answer'},
                {
                    'birthday': birthday.Birthday.parse('1950-05-01'),
                    'country': 'ru',
                    'display_language': 'ru',
                    'gender': Gender.Male,
                    'question_id': 1,
                    'question': 'question',
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'answer': 'answer',
                    'language': 'ru',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'validation_method': 'captcha',
                    'force_clean_web': False,
                }
            ),
            # Только необходимые поля
            (
                {
                    'track_id': self.track_id, 'display_language': 'ru',
                    'login': 'userlogin',
                    'firstname': 'fn', 'lastname': 'ln',
                },
                {
                    'birthday': None,
                    'country': None,
                    'display_language': 'ru',
                    'gender': None,
                    'question_id': None,
                    'question': None,
                    'answer': None,
                    'firstname': 'fn',
                    'lastname': 'ln',
                    'language': None,
                    'timezone': None,
                    'validation_method': None,
                    'force_clean_web': False,
                }
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteCommitBaseForm(), invalid_params, valid_params, state)

    def test_complete_commit_social(self):
        invalid_params = [
            (
                {},
                ['password.empty'],
            ),
            (
                {'password': ''},
                ['password.empty'],
            ),
        ]

        valid_params = [
            (
                {'password': 'pass'},
                {'password': 'pass'},
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteCommitSocialForm(), invalid_params, valid_params, state)

    def test_complete_commit_social_with_login(self):
        invalid_params = [
            (
                {},
                ['password.empty', 'login.empty'],
            ),
            (
                {'password': '', 'login': ''},
                ['password.empty', 'login.empty'],
            ),
            (
                {'login': '.blahblah', 'password': 'pass'},
                ['login.startswithdot'],
            ),
        ]

        valid_params = [
            (
                {'password': 'pass', 'login': 'userlogin'},
                {'password': 'pass', 'login': 'userlogin'},
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteCommitSocialWithLoginForm(), invalid_params, valid_params, state)

    def test_complete_commit_lite(self):
        invalid_params = [
            (
                {},
                ['login.empty', 'eula_accepted.empty', 'password.empty'],
            ),
            (
                {'login': '', 'eula_accepted': '', 'password': ''},
                ['login.empty', 'eula_accepted.empty', 'password.empty'],
            ),
            (
                {'login': 'abc', 'password': 'pass'},
                ['eula_accepted.empty'],
            ),
        ]

        valid_params = [
            (
                {'eula_accepted': '1', 'login': 'userlogin', 'password': 'pass'},
                {'eula_accepted': True, 'login': 'userlogin', 'password': 'pass'},
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteCommitLiteForm(), invalid_params, valid_params, state)

    def test_complete_commit_neophonish(self):
        invalid_params = [
            (
                {},
                ['login.empty', 'password.empty'],
            ),
            (
                {'login': '', 'password': ''},
                ['login.empty', 'password.empty'],
            ),
        ]

        valid_params = [
            (
                {'login': 'userlogin', 'password': 'pass'},
                {'login': 'userlogin', 'password': 'pass'},
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteCommitNeophonishForm(), invalid_params, valid_params, state)

    def test_complete_submit(self):
        invalid_params = []

        valid_params = [
            (
                {'retpath': 'http://yandex.ru'},
                {'retpath': 'http://yandex.ru', 'can_handle_neophonish': True},
            ),
            (
                {'retpath': 'abc', 'can_handle_neophonish': 'no'},
                {'retpath': None, 'can_handle_neophonish': False},
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_form(forms.CompleteSubmitForm(), invalid_params, valid_params, state)
