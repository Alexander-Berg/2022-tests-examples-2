# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_TRACK_ID,
    TEST_UID,
)
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.counters import login_restore_counter
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters

from .base import (
    BaseMultiStepTestcase,
    TEST_RUSSIAN_IP,
)


TEST_DEVICE_APPLICATION = 'test.device.application'


@with_settings(
    ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=False,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
    )
)
class AuthAfterLoginRestoreTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/after_login_restore/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'uid': TEST_UID,
        'firstname': TEST_FIRSTNAME,
        'lastname': TEST_LASTNAME,
    }
    statbox_type = 'multi_step_after_login_restore'

    def setUp(self):
        super(AuthAfterLoginRestoreTestcase, self).setUp()
        self.create_and_fill_track()
        self.setup_blackbox_responses(
            aliases={'neophonish': TEST_LOGIN},
            with_phonenumber_alias=True,
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
        )
        self.env.bot_api.set_response_value('send_message', bot_api_response())

    def setup_statbox_templates(self):
        super(AuthAfterLoginRestoreTestcase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'passed',
            _exclude=['origin'],
            action='passed',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
        )

    def create_and_fill_track(self, track_type='authorize'):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.device_application = TEST_DEVICE_APPLICATION

    def test_account_invalid_type(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)

    def test_phone_not_confirmed(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'], track_id=self.track_id)

    def test_compare_not_matched(self):
        resp = self.make_request(query_args={'firstname': 'foo', 'lastname': 'bar'})
        self.assert_error_response(resp, ['compare.not_matched'], track_id=self.track_id)

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.session_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=self.track_id)

    def test_rate_limit_exceeded(self):
        for _ in range(3):
            login_restore_counter.get_per_phone_buckets().incr(TEST_PHONE_NUMBER.digital)
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'], track_id=self.track_id)

    def test_rate_limit_ip_whitelisted(self):
        for _ in range(3):
            login_restore_counter.get_per_ip_buckets().incr(TEST_RUSSIAN_IP)

        with settings_context(
            YANGO_APP_IDS=(TEST_DEVICE_APPLICATION,),
            TRUSTED_YANGO_PHONE_CODES=(TEST_PHONE_NUMBER.e164[:2],),
            ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=False,
            **mock_counters(
                LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
                LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
            )
        ):
            resp = self.make_request()

        self.assert_ok_response(resp, track_id=self.track_id)
        self.env.statbox.assert_contains([self.env.statbox.entry('passed')], offset=-1)
        assert len(self.env.bot_api.requests) == 1

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        ok_(track.allow_set_xtoken_trusted)

    @parameterized.expand([
        ('authorize',),
        ('register',),
        ('restore',),
    ])
    def test_ok_with_different_track_types(self, track_type):
        self.create_and_fill_track(track_type)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry('passed'),
            ],
            offset=-1,
        )
        eq_(len(self.env.bot_api.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        ok_(track.allow_set_xtoken_trusted)

    def test_ok_for_portal(self):
        self.setup_blackbox_responses(
            with_phonenumber_alias=True,
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
        )
        with settings_context(ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=True):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
