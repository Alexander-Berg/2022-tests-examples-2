# -*- coding: utf-8 -*-

from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.login.login import masked_login

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_ANOTHER_EMAIL,
    TEST_LOGIN,
    TEST_NATIVE_EMAIL,
    TEST_SHORT_CODE,
    TEST_UID,
)


@with_settings_hosts(
    EMAIL_CODE_CHALLENGE_CODE_LENGTH=5,
    EMAIL_CHECK_OWNERSHIP_CODE_ATTEMPTS=5,
    **mock_counters(
        EMAIL_CHECK_OWNERSHIP_SENT_COUNTER_1H=5,
        EMAIL_CHECK_OWNERSHIP_SENT_COUNTER_24H=10,
    )
)
class TestCheckEmailOwnershipSendCode(BaseEmailBundleTestCase, EmailTestMixin):
    default_url = '/1/bundle/email/check_ownership/send_code/?consumer=dev'

    def setUp(self):
        super(TestCheckEmailOwnershipSendCode, self).setUp()

        self.http_query_args = {
            'language': 'ru',
            'track_id': self.track_id,
        }

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                emails=[
                    {
                        'address': TEST_NATIVE_EMAIL,
                        'validated': True,
                        'default': True,
                        'native': True,
                    },
                    {
                        'address': TEST_ANOTHER_EMAIL,
                        'validated': True,
                        'default': False,
                        'native': False,
                    },
                ],
            ),
        )
        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.setup_kolmogor()

    def tearDown(self):
        self.code_generator_faker.stop()
        super(TestCheckEmailOwnershipSendCode, self).tearDown()

    def setup_kolmogor(self, rate_1h=4, rate_24h=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate_1h),
                str(rate_24h),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def build_email(self, address, is_native, login, browser):
        login = login if is_native else masked_login(login)

        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'emails.check_ownership_code.title',
            'tanker_keys': {
                'greeting.noname': {},
                'emails.check_ownership_code.title': {},
                'emails.check_ownership_code.start': {
                    'MASKED_LOGIN': login,
                    'BROWSER': 'AndroidBrowser 7.0 (Android Nougat)',
                },
                'emails.check_ownership_code.continue': {
                    'MASKED_LOGIN': login,
                },
                'emails.check_ownership.security': {},
                'emails.check_ownership_feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/feedback.html\' target=\'_blank\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
                'signature.secure': {},
            },
        }

    def check_email_sent(self, login=TEST_LOGIN):
        self.assert_emails_sent([
            self.build_email(
                address=TEST_ANOTHER_EMAIL,
                is_native=False,
                login=login,
                browser='123',
            ),
            self.build_email(
                address=TEST_NATIVE_EMAIL,
                is_native=True,
                login=login,
                browser='123',
            ),
        ])

    def check_statbox(self):
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'send_ownership_confirmation_code',
                status='ok',
                track_id=self.track_id,
            ),
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        assert track.email_check_ownership_code == TEST_SHORT_CODE
        assert track.email_ownership_checks_count.get() is None
        self.check_statbox()

    def test_no_account_in_track(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])

    def test_counter_overflow_1h(self):
        self.setup_kolmogor(rate_1h=5)
        rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])

    def test_counter_overflow_24h(self):
        self.setup_kolmogor(rate_24h=10)
        rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])
        self.assert_no_emails_sent()
        self.env.statbox.assert_has_written([])


class TestCheckEmailOwnershipConfirm(BaseEmailBundleTestCase, EmailTestMixin):
    default_url = '/1/bundle/email/check_ownership/confirm/?consumer=dev'

    def setUp(self):
        super(TestCheckEmailOwnershipConfirm, self).setUp()
        self.http_query_args = {
            'language': 'ru',
            'track_id': self.track_id,
            'code': TEST_SHORT_CODE,
        }

    def check_statbox(self):
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'check_ownership_confirmation_code',
                status='ok',
                track_id=self.track_id,
            ),
        )

    def test_ok(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.email_check_ownership_code = TEST_SHORT_CODE
        rv = self.make_request()

        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)
        assert track.email_ownership_checks_count.get() == 1
        assert track.email_check_ownership_passed is True
        self.check_statbox()

    def test_ok_counter_near_max(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.email_check_ownership_code = TEST_SHORT_CODE
            _ = [track.email_ownership_checks_count.incr() for _ in range(4)]
        rv = self.make_request()

        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)
        assert track.email_ownership_checks_count.get() == 5
        self.check_statbox()

    def test_no_uid_in_track(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None
            track.email_check_ownership_code = TEST_SHORT_CODE
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_no_code_in_track(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_check_counter_overflow(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.email_check_ownership_code = TEST_SHORT_CODE
            _ = [track.email_ownership_checks_count.incr() for _ in range(5)]
        rv = self.make_request()

        self.assert_error_response(rv, ['email.key_check_limit_exceeded'])

    def test_wrong_code(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.email_check_ownership_code = TEST_SHORT_CODE
        rv = self.make_request(query_args=dict(code='77777'))

        self.assert_error_response(rv, ['email.incorrect_key'])
