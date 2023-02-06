# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_USER_IP
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_STRONG_PASSWORD = 'strong_password1234'
TEST_NORMAL_PASSWORD = 'simple123'
TEST_MEDIUM_PASSWORD = 'aaabbbcdef'
TEST_WEAK_PASSWORD = 'password'


@with_settings_hosts()
class TestValidatePasswordView(BaseBundleTestViews):
    default_url = '/1/bundle/validate/password/'
    http_method = 'POST'
    consumer = 'dev'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'password': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = {'track_id': self.track_id}
        self.setup_statbox_templates()
        self.setup_shakur()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'password_validation_error',
            track_id=self.track_id,
            action='password_validation_error',
            weak='1',
            password_quality='0',
            length='8',
            classes_number='1',
            sequences_number='1',
            is_sequence='0',
            is_word='1',
            is_additional_word='0',
            additional_subwords_number='0',
        )

    def setup_shakur(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def test_ok(self):
        rv = self.make_request(query_args={'password': TEST_NORMAL_PASSWORD})
        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)
        eq_(track.password_validation_count.get(), 1)
        eq_(track.password_validation_first_call, TimeNow())
        eq_(track.password_validation_last_call, TimeNow())

    def test_weak_warning(self):
        rv = self.make_request(query_args={'password': TEST_MEDIUM_PASSWORD})
        self.assert_ok_response(rv, warnings=['password.weak'])

    def test_weak_error(self):
        rv = self.make_request(query_args={'password': TEST_WEAK_PASSWORD})
        self.assert_error_response(rv, ['password.weak'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('password_validation_error'),
        ])

    def test_password_short_for_strong_policy(self):
        rv = self.make_request(query_args={'password': TEST_NORMAL_PASSWORD, 'policy': 'strong'})
        self.assert_error_response(rv, ['password.short'])

    def test_strong_policy_ok(self):
        rv = self.make_request(query_args={'password': TEST_STRONG_PASSWORD, 'policy': 'strong'})
        self.assert_ok_response(rv)

    def test_password_eq_login(self):
        rv = self.make_request(query_args={
            'login': TEST_NORMAL_PASSWORD,
            'password': TEST_NORMAL_PASSWORD,
        })
        self.assert_error_response(rv, ['password.likelogin'])

    def test_password_eq_login_from_track(self):
        with self.track_transaction(self.track_id) as track:
            track.login = TEST_NORMAL_PASSWORD
        rv = self.make_request(query_args={'password': TEST_NORMAL_PASSWORD})
        self.assert_error_response(rv, ['password.likelogin'])

    def test_password_like_phone_number(self):
        rv = self.make_request(query_args={
            'password': '8(926)123-45-67',
            'phone_number': '89261234567',
            'country': 'ru',
        })
        self.assert_error_response(rv, ['password.likephonenumber'])

    def test_ok_with_process(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self.make_request(query_args={'password': TEST_NORMAL_PASSWORD})
        self.assert_ok_response(rv)
