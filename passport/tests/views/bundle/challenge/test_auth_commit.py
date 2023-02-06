# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_DIFFERENT_PHONE_NUMBER,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_UID,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_HINT_ANSWER
from passport.backend.core.test.test_utils import settings_context

from .base import (
    BaseAuthTestCase,
    CommonAuthChallengeTests,
    TEST_IP,
)


class CommitTestCase(BaseAuthTestCase, CommonAuthChallengeTests):
    default_url = '/1/bundle/auth/password/challenge/commit/'

    @property
    def http_query_args(self):
        return dict(
            super(CommitTestCase, self).http_query_args,
            challenge='phone_confirmation',
        )

    def check_statbox_ok(self, challenge, **kwargs):
        expected_values = dict(
            method=challenge,
            challenge=challenge,
            is_mobile='0',
            phone_confirmation_enabled_for_app_id='0',
            uid_in_experiment='1',
            client_can_send_sms='1',
        )
        expected_values.update(**kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                **expected_values
            ),
        ])

    def check_statbox_failed(self, challenge, **kwargs):
        expected_values = dict(
            method=challenge,
            challenge=challenge,
            is_mobile='0',
            phone_confirmation_enabled_for_app_id='0',
            uid_in_experiment='1',
            client_can_send_sms='1',
        )
        expected_values.update(**kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                **expected_values
            ),
        ])

    def check_track_ok(self, challenge, allow_set_xtoken_trusted=None):
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        eq_(track.auth_challenge_type, challenge)
        eq_(track.allow_set_xtoken_trusted, allow_set_xtoken_trusted)

    def assert_social_binding_log_written(self):
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_IP,
            ),
        ])

    def assert_social_binding_log_empty(self):
        self.env.social_binding_logger.assert_has_written([])

    def test_phone_ok(self):
        resp = self.make_request(
            query_args=dict(
                challenge='phone',
                answer=TEST_PHONE_NUMBER.national,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('phone')
        self.check_track_ok('phone')
        self.assert_social_binding_log_empty()
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.phone.rps_dmmm')

    def test_phone_ok_device_info_in_track(self):
        with self.track_transaction() as track:
            track.account_manager_version = '1.2.3'
            track.device_application = 'ru.yandex.app_id'
            track.device_id = 'device-id'

        resp = self.make_request(
            query_args=dict(
                challenge='phone',
                answer=TEST_PHONE_NUMBER.national,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok(
            'phone',
            am_version='1.2.3',
            am_version_name='1.2.3',
            app_id='ru.yandex.app_id',
            device_id='device-id',
            is_mobile='1',
        )
        self.check_track_ok('phone')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.mobile.phone.rps_dmmm')

    def test_phone_confirmation_ok(self):
        self.setup_blackbox_response(is_easily_hacked=True)
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('phone_confirmation')
        self.check_track_ok('phone_confirmation', allow_set_xtoken_trusted=True)
        self.assert_social_binding_log_empty()
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.phone_confirmation.rps_dmmm')

    def test_phone_confirmation_with_bank_phone_ok(self):
        self.setup_blackbox_response(
            bank_phonenumber_alias=TEST_PHONE_NUMBER.digital,
            has_phones=False,
            simple_phone=TEST_PHONE_NUMBER,
        )
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('phone_confirmation')
        self.check_track_ok('phone_confirmation', allow_set_xtoken_trusted=True)
        self.assert_social_binding_log_empty()
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.phone_confirmation.rps_dmmm')

    def test_phone_confirmation_by_flash_call_ok(self):
        self.setup_blackbox_response(is_easily_hacked=True)
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_flash_call'

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('phone_confirmation')
        self.check_track_ok('phone_confirmation', allow_set_xtoken_trusted=True)
        self.assert_social_binding_log_empty()
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.phone_confirmation.rps_dmmm')

    def test_phone_confirmation_not_checked_error(self):
        self.setup_blackbox_response(is_easily_hacked=True)

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )

        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('phone_confirmation')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.phone_confirmation.rps_dmmm')

    def test_phone_confirmation_checked_for_another_number_error(self):
        self.setup_blackbox_response(is_easily_hacked=True)
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('phone_confirmation')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.phone_confirmation.rps_dmmm')

    def test_unknown_phone_error(self):
        resp = self.make_request(
            query_args=dict(
                challenge='phone',
                answer=TEST_DIFFERENT_PHONE_NUMBER.national,
            ),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('phone')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.phone.rps_dmmm')

    def test_not_phone_error(self):
        resp = self.make_request(
            query_args=dict(
                challenge='phone',
                answer='foobar',
            ),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('phone')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.phone.rps_dmmm')

    def test_email_ok(self):
        """Угадан тот email, что мы загадали"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='%s@gmail.com' % TEST_LOGIN,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('email')
        self.check_track_ok('email')
        self.assert_social_binding_log_empty()
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email.rps_dmmm')

    def test_email_other_case_ok(self):
        """Угадан тот email, что мы загадали, но не в том регистре"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='%s@GmAiL.cOm' % TEST_LOGIN,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('email')
        self.check_track_ok('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email.rps_dmmm')

    def test_other_matching_email_ok(self):
        """Угадан другой email, подходящий по заданную маску"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='%s@google-mail.com' % TEST_LOGIN,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('email')
        self.check_track_ok('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email.rps_dmmm')

    def test_unicode_email_ok(self):
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer=u'%s@google-почта.com' % TEST_LOGIN,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('email')
        self.check_track_ok('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email.rps_dmmm')

    def test_punycode_email_ok(self):
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer=u'%s@%s' % (TEST_LOGIN, u'google-почта.com'.encode('idna')),
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('email')
        self.check_track_ok('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email.rps_dmmm')

    def test_other_nonmatching_email_error(self):
        """Угадан другой email, не подходящий по заданную маску"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='%s@mail.ru' % TEST_LOGIN,
            ),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.email.rps_dmmm')

    def test_unknown_matching_email_error(self):
        """Введён "левый" email, однако подходящий по заданную маску"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='%s@google.com' % TEST_LOGIN,
            ),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.email.rps_dmmm')

    def test_not_email_error(self):
        """Введёна какая-то чушь"""
        resp = self.make_request(
            query_args=dict(
                challenge='email',
                answer='foobar',
            ),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('email')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.email.rps_dmmm')

    def test_challenge_not_enabled_error(self):
        self.setup_blackbox_response(has_phones=False)

        resp = self.make_request(
            query_args=dict(
                challenge='phone',
                answer='0000',
            ),
        )

        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])

    def test_no_challenges_error(self):
        self.setup_blackbox_response(has_phones=False, has_emails=False)

        resp = self.make_request()

        self.assert_error_response(resp, ['action.impossible'], track_id=self.track_id)

    def test_bind_phonish_ok(self):
        self.setup_blackbox_response(is_easily_hacked=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.device_application = 'test_app_id'

        with settings_context(BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={'test_app_id'}):
            resp = self.make_request(
                query_args=dict(challenge='phone_confirmation'),
            )

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.assert_social_binding_log_written()

    def test_can_send_sms_0(self):
        self.setup_blackbox_response(is_easily_hacked=True)

        resp = self.make_request(
            query_args=dict(
                challenge='phone_confirmation',
                can_send_sms='0',
            ),
        )

        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
        self.env.statbox.assert_has_written([])

    def test_login_by_phonenumber_alias(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.user_entered_login = TEST_PHONE_NUMBER.national

        resp = self.make_request(
            query_args=dict(challenge='phone_confirmation'),
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_failed('phone_confirmation')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.failed.web.phone_confirmation.rps_dmmm')

    def test_question_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['question', 'sms', 'flash_call', 'phone_hint', 'email_hint']

        resp = self.make_request(
            query_args=dict(
                challenge='question',
                answer=TEST_HINT_ANSWER,
            ),
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('question')
        self.check_track_ok('question')
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.question.rps_dmmm')

    def test_question_wrong_answer(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['question', 'sms', 'flash_call', 'phone_hint', 'email_hint']

        resp = self.make_request(
            query_args=dict(
                challenge='question',
                answer='wrong',
            ),
        )
        self.assert_error_response(resp, ['challenge.not_passed'], track_id=self.track_id)

    def test_question_empty_answer(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['question', 'sms', 'flash_call', 'phone_hint', 'email_hint']

        resp = self.make_request(
            query_args=dict(
                challenge='question',
            ),
        )
        self.assert_error_response(resp, ['challenge.not_passed'], track_id=self.track_id)

    def test_question_unavailable_without_antifraud_tags(self):
        resp = self.make_request(
            query_args=dict(
                challenge='question',
                answer=TEST_HINT_ANSWER,
            ),
        )
        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)

    def test_push_2fa_ok(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='123456',
                ),
            )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok('push_2fa')
        self.check_track_ok('push_2fa', allow_set_xtoken_trusted=True)
        self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.push_2fa.rps_dmmm')

    def test_push_2fa_wrong_answer(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_passed'], track_id=self.track_id)

    def test_push_2fa_not_enabled_by_trusted_xtokens(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_not_enabled_by_trusted_subscriptions(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=False)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)

    def test_push_2fa_not_enabled_by_experiment(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=0.1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_not_enabled_by_antifraud_tags(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = '123456'
            track.antifraud_tags = ['question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_no_code_in_track(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'sms']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='push_2fa',
                    answer='1234567',
                ),
            )
        self.assert_error_response(resp, ['challenge.not_passed'], track_id=self.track_id)

    def test_email_code_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'sms']
            track.email_check_ownership_passed = True

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12345',
                ),
            )
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
            )
            self.check_statbox_ok('email_code')
            self.check_track_ok('email_code')
            self.assert_xunistater('challenges_passed_or_failed', 'challenge.passed.web.email_code.rps_dmmm')

    def test_email_code_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'sms']

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12346',
                ),
            )
            self.assert_error_response(resp, ['challenge.not_passed'], track_id=self.track_id)

    def test_email_code_not_enabled_by_antifraud_tags(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'sms']
            track.email_check_ownership_passed = True

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12345',
                ),
            )
            self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)

    def test_email_code_not_enabled_by_settings(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'sms']
            track.email_check_ownership_passed = True

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=False,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12345',
                ),
            )
            self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)

    def test_email_code_not_enabled_by_experiment(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'sms']
            track.email_check_ownership_passed = True

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=0,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12345',
                ),
            )
            self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)

    def test_email_code_not_enabled_by_account_type(self):
        self.setup_blackbox_response(native_email_only=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'sms']
            track.email_check_ownership_passed = True

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request(
                query_args=dict(
                    challenge='email_code',
                    answer='12345',
                ),
            )
            self.assert_error_response(resp, ['challenge.not_enabled'], track_id=self.track_id)
