# -*- coding: utf-8 -*-
import base64
from unittest import TestCase

from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.api.validators import (
    Password,
    TrackFlagsList,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_pwdhistory_response,
    blackbox_test_pwd_hashes_response,
)
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_error_codes,
    check_raise_error,
)
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import (
    check_statbox_log_entries,
    with_settings_hosts,
)
from passport.backend.core.validators import State
import pytest


def test_tracks_flag_list():
    valid_data = {
        'f1': 'yes',
        'f2': 'no',
        'f3': '0',
        'f4': '1',
        'f5': 'true',
        'f6': 'false',
    }
    expected_data = {
        'f1': True,
        'f2': False,
        'f3': False,
        'f4': True,
        'f5': True,
        'f6': False,
    }
    check_equality(TrackFlagsList(), (valid_data, expected_data))


@pytest.mark.parametrize(('params', 'code'), [
        ({'f1': 'yes', 'f2': '11', 'f3': 'lala'}, {'f2': ['string'], 'f3': ['string']}),
        ({'f1': None, 'f3': 'yes'}, {'f1': ['empty']}),
    ],
)
def test_tracks_flag_list_error_bad_data(params, code):
    validator = TrackFlagsList()

    check_error_codes(validator, params, code)


@with_settings_hosts(
    BASIC_PASSWORD_POLICY_MIN_QUALITY=10,
)
class PasswordTest(TestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.state = State(mock_env(user_ip='127.0.0.1'))
        self.env.statbox.bind_entry(
            'password_validation_error',
            track_id=self.track_id,
            action='password_validation_error',
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager
        del self.state

    def test_validation(self):
        check_error_codes(Password(), {'password': 'aaabbb'}, {'password': ['weak']}, self.state)

    def test_statbox_logging_empty(self):
        check_error_codes(
            Password(),
            {'password': 'aaabbb'},
            {'password': ['weak']},
            self.state,
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_statbox_logging_weak(self):
        check_raise_error(
            Password(),
            {
                'password': 'aaabbb',
                'track_id': self.track_id,
            },
            self.state,
        )
        entry = self.env.statbox.entry(
            'password_validation_error',
            weak='1',
            policy='basic',
            password_quality='4',
            length='6',
            classes_number='1',
            sequences_number='0',
            is_sequence='0',
            is_word='0',
            is_additional_word='0',
            additional_subwords_number='0',
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [entry])

    def test_statbox_logging_like_phone_number(self):
        check_raise_error(
            Password(),
            {
                'password': '79151231234',
                'track_id': self.track_id,
                'phone_number': '+79151231234',
            },
            self.state,
        )
        entry = self.env.statbox.entry(
            'password_validation_error',
            policy='basic',
            like_phone_number='1',
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [entry])

    def test_statbox_logging_like_login(self):
        check_raise_error(
            Password(),
            {
                'password': 'login',
                'track_id': self.track_id,
                'login': 'login',
                'policy': 'strong',
            },
            self.state,
        )
        entry = self.env.statbox.entry(
            'password_validation_error',
            policy='strong',
            like_login='1',
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [entry])

    def test_statbox_logging_like_old_password(self):
        pwd_hash = '1:$1$H8z/ARIX$BNKjgwx9LtmUpIx5qBUZ.0'
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(pwd_hash): True,
                },
            ),
        )
        check_raise_error(
            Password(),
            {
                'password': 'foobarfoobar',
                'old_password_hash': pwd_hash,
                'track_id': self.track_id,
            },
            self.state,
        )
        entry = self.env.statbox.entry(
            'password_validation_error',
            policy='basic',
            like_old_password='1',
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [entry])

    def test_statbox_logging_found_in_history(self):
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        check_raise_error(
            Password(required_check_password_history=True),
            {
                'password': 'fooooobar2',
                'policy': 'basic',
                'uid': '1',
                'track_id': self.track_id,
            },
            self.state,
        )
        entry = self.env.statbox.entry(
            'password_validation_error',
            policy='basic',
            found_in_history='1',
        )
        check_statbox_log_entries(self.env.statbox_handle_mock, [entry])
