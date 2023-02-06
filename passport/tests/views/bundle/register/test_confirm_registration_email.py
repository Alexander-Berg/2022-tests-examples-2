# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_NON_NATIVE_EMAIL,
    TEST_SHORT_CODE,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.time import get_unixtime


TEST_YANDEXUID = 'yuid12345'


@with_settings_hosts(
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=5,
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=10,
)
class TestConfirmRegistrationEmail(BaseBundleTestViews, EmailTestMixin):
    track_type = 'register'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }
    default_url = '/1/bundle/account/register/confirm_email/by_code/?consumer=dev'

    def setUp(self):
        super(TestConfirmRegistrationEmail, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_mail'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)

        self.http_query_args = {
            'track_id': self.track_id,
            'key': TEST_SHORT_CODE,
        }

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        self.env.statbox.bind_entry(
            'confirm_email',
            mode='register_by_email',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            track_id=self.track_id,
            confirmation_checks_count='1',
            yandexuid=TEST_YANDEXUID,
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager
        super(TestConfirmRegistrationEmail, self).tearDown()

    def test_no_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = None
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION[::-1]
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_confirm_registration_email_ok(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        rv = self.make_request()
        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)

        eq_(track.email_confirmation_passed_at, TimeNow())
        eq_(track.email_confirmation_checks_count.get(), 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'confirm_email',
                action='email_confirmed',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])

    def test_confirm_registration_email_ok__yandexuid_is_optional_in_statbox_log(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        rv = self.make_request(exclude_headers=['cookie'])
        self.assert_ok_response(rv)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'confirm_email',
                action='email_confirmed',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                _exclude=['yandexuid'],
            ),
        ])

    def test_confirm_registration_email_no_address(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

        eq_(track.email_confirmation_passed_at, None)
        eq_(track.email_confirmation_checks_count.get(), None)

    def test_confirm_registration_email_no_code(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

        eq_(track.email_confirmation_passed_at, None)
        eq_(track.email_confirmation_checks_count.get(), None)

    def test_confirm_registration_email_invalid_code(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE[::-1]
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['email.incorrect_key'],
            email_confirmation_attempts_left=settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT - 1,
        )

        track = self.track_manager.read(self.track_id)

        eq_(track.email_confirmation_passed_at, None)
        eq_(track.email_confirmation_checks_count.get(), 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'confirm_email',
                action='incorrect_key',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])

    def test_confirm_attempts_left_reaches_zero(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE[::-1]
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        for i in range(settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT):
            rv = self.make_request()
            self.assert_error_response(
                rv,
                ['email.incorrect_key'],
                email_confirmation_attempts_left=settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT - (i + 1),
            )

    def test_confirm_limit_error(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE  # валидный код, но подтвердиться он не должен
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL
            for _ in range(settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT):
                track.email_confirmation_checks_count.incr()

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['email_confirmations_limit.exceeded'],
        )

        track = self.track_manager.read(self.track_id)

        eq_(track.email_confirmation_passed_at, None)
        eq_(track.email_confirmation_checks_count.get(), settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT)

    def test_already_confirmed(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE  # валидный код, но подтвердиться он не должен
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL
            track.email_confirmation_checks_count.incr()  # 1
            track.email_confirmation_passed_at = get_unixtime() - 3600

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['email.already_confirmed'],
        )

        track = self.track_manager.read(self.track_id)
        # email_confirmation_passed_at не увеличилось в следствие запроса
        eq_(track.email_confirmation_passed_at, TimeNow(offset=-3600))
        # поличество проверок не увеличилось (проверки не было, т.к. email подтверждён)
        eq_(track.email_confirmation_checks_count.get(), 1)

        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)
