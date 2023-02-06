# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.templatetags import markdown_email
from passport.backend.api.views.bundle.constants import CHANGE_PASSWORD_REASON_EXPIRED
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SECOND_STEP_EMAIL_CODE
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base import BaseMultiStepTestcase
from .base_test_data import (
    TEST_HOST,
    TEST_IP,
    TEST_LANGUAGE,
    TEST_LOGIN,
    TEST_PDD_DOMAIN_INFO,
    TEST_PDD_LOGIN,
    TEST_REFERER,
    TEST_TRACK_ID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)


TEST_EMAIL = '@'.join([TEST_LOGIN, 'yandex.ru'])
TEST_ANOTHER_EMAIL = 'vasya@yandex.ru'
TEST_CODE_LENGTH = 6
TEST_CODE = '3' * TEST_CODE_LENGTH
TEST_INPUT_CODE = '333-333'
TEST_ANOTHER_CODE = '4' * TEST_CODE_LENGTH


@with_settings_hosts(
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=TEST_CODE_LENGTH,
    EMAIL_VALIDATOR_SHORT_CODE_DELIMITER='-',
    **mock_counters()
)
class TestEmailCodeSubmitTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/email_code/submit/'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_query_args = {
        'track_id': TEST_TRACK_ID,
    }

    def setUp(self):
        super(TestEmailCodeSubmitTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self._code_generator_faker = CodeGeneratorFaker()
        self._code_generator_faker.set_return_value(TEST_CODE)
        self._code_generator_faker.start()

        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.is_second_step_required = True
            track.allowed_second_steps = [BLACKBOX_SECOND_STEP_EMAIL_CODE]

    def tearDown(self):
        self._code_generator_faker.stop()
        del self._code_generator_faker
        del self.track_id
        super(TestEmailCodeSubmitTestCase, self).tearDown()

    def build_email(self, address, code, language):
        data = {
            'language': language,
            'addresses': [address],
            'SHORT_CODE': code,
            'subject': 'email_code_sent.subject',
            'tanker_keys': {
                'email_code_sent.message': {
                    'EMAIL': markdown_email(TEST_EMAIL),
                },
                'email_code_sent.enter_code': {},
                'email_code_sent.security': {},
            },
        }
        return data

    def assert_track_ok(self, code=TEST_CODE):
        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.email_confirmation_address, TEST_EMAIL)
        eq_(track.email_confirmation_code, code)

    def assert_mail_sent(self, code=TEST_INPUT_CODE):
        self.assert_emails_sent([
            self.build_email(
                language=TEST_LANGUAGE,
                address=TEST_EMAIL,
                code=code,
            ),
        ])

    def test_sent__ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok()
        self.assert_mail_sent()

    def test_track_with_code__ok(self):
        with self.track_transaction(self.track_id) as track:
            track.email_confirmation_address = TEST_EMAIL
            track.email_confirmation_code = TEST_ANOTHER_CODE

        resp = self.make_request()
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok(code=TEST_ANOTHER_CODE)
        self.assert_mail_sent(code=TEST_ANOTHER_CODE)

    def test_track_with_code_but_email_changed(self):
        with self.track_transaction(self.track_id) as track:
            track.email_confirmation_address = TEST_ANOTHER_EMAIL
            track.email_confirmation_code = TEST_ANOTHER_CODE

        resp = self.make_request()
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok()
        self.assert_mail_sent()

    def test_invalid_track_state__error(self):
        with self.track_transaction(self.track_id) as track:
            track.allowed_second_steps = 'foo,bar'

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)
        self.assert_no_emails_sent()

    def test_auth_already_passed__error(self):
        with self.track_transaction(self.track_id) as track:
            track.session = 'session'
            track.session_created_at = 42

        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=self.track_id)
        self.assert_no_emails_sent()

    def test_no_email__error(self):
        self.setup_blackbox_responses(emails=[])

        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)
        self.assert_no_emails_sent()


@with_settings_hosts(
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=3,
)
class TestEmailCodeCommitTestCase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/email_code/commit/'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_IP,
        'cookie': 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'referer': TEST_REFERER,
    }
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'code': TEST_INPUT_CODE,
    }

    def setUp(self):
        super(TestEmailCodeCommitTestCase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.setup_blackbox_responses(emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')])
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.is_second_step_required = True
            track.allowed_second_steps = [BLACKBOX_SECOND_STEP_EMAIL_CODE]
            track.email_confirmation_address = TEST_EMAIL
            track.email_confirmation_code = TEST_CODE

    def assert_track_ok(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        ok_(not track.allow_oauth_authorization)
        ok_(track.is_session_restricted)
        eq_(track.password_verification_passed_at, TimeNow())

    def test_checked__ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok()

    def test_code_invalid__error(self):
        resp = self.make_request(query_args={'code': TEST_ANOTHER_CODE})
        self.assert_error_response(resp, ['code.invalid'], track_id=self.track_id)

        track = self.track_manager.read(self.track_id)
        eq_(track.email_confirmation_checks_count.get(), 1)

    def test_invalid_track_state__error(self):
        with self.track_transaction(self.track_id) as track:
            track.allowed_second_steps = 'foo,bar'

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_invalid_none_track_state__error(self):
        with self.track_transaction(self.track_id) as track:
            track.allowed_second_steps = None

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_email_not_sent__error(self):
        with self.track_transaction(self.track_id) as track:
            track.email_confirmation_address = None
            track.email_confirmation_code = None

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_no_email__error(self):
        self.setup_blackbox_responses(emails=[])

        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)

    def test_email_sent_for_another_account__error(self):
        with self.track_transaction(self.track_id) as track:
            track.email_confirmation_address = TEST_ANOTHER_EMAIL

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_auth_already_passed__error(self):
        with self.track_transaction(self.track_id) as track:
            track.session = 'session'
            track.session_created_at = 42

        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=self.track_id)

    def test_limit_exceeded(self):
        with self.track_transaction(self.track_id) as track:
            for _ in range(3):
                track.email_confirmation_checks_count.incr()

        resp = self.make_request()
        self.assert_error_response(resp, ['email_confirmations_limit.exceeded'], track_id=self.track_id)

    def test_pdd_completion_required(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[
                self.env.email_toolkit.create_native_email(*TEST_PDD_LOGIN.split('@')),
            ],
        )
        with self.track_transaction(self.track_id) as track:
            track.email_confirmation_address = TEST_PDD_LOGIN

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='complete_pdd',
            account=self.account_response_values(login=TEST_PDD_LOGIN, domain=TEST_PDD_DOMAIN_INFO),
            track_id=self.track_id,
        )

    def test_password_expired(self):
        with self.track_transaction(self.track_id) as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_EXPIRED

        resp = self.make_request()
        expected_response_values = dict(
            state='change_password',
            change_password_reason='password_expired',
            validation_method=None,
            account=self.account_response_values(),
            track_id=self.track_id,
        )
        self.assert_ok_response(resp, **expected_response_values)
        track = self.track_manager.read(self.track_id)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_EXPIRED)
        eq_(
            track.submit_response_cache,
            dict(
                expected_response_values,
                status='ok',
            ),
        )
