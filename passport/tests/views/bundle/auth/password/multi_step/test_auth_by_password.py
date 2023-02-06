# -*- coding: utf-8 -*-

import hashlib
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import SessionScope
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_AVATAR_DEFAULT_KEY,
    TEST_AVATAR_SECRET,
    TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
    TEST_LOGIN,
    TEST_PASSWORD,
    TEST_PDD_DOMAIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_RETPATH,
    TEST_TRACK_ID,
    TEST_UID,
)
from passport.backend.api.views.bundle.constants import CHANGE_PASSWORD_REASON_EXPIRED
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.antifraud.exceptions import BaseAntifraudApiError
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
    ScoreAction,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_SECOND_STEP_EMAIL_CODE,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_sign_response,
)
from passport.backend.core.builders.push_api import PushApiTemporaryError
from passport.backend.core.builders.shakur.faker.fake_shakur import shakur_check_password_no_postfix
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.common import deep_merge

from .base import (
    BaseMultiStepTestcase,
    CommonAuthTests,
    TEST_RUSSIAN_IP,
)


@with_settings_hosts(
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    CHECK_AVATARS_SECRETS_DENOMINATOR=1,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
    EMAIL_CODE_CHALLENGE_ENABLED=False,
)
class CommitPasswordWithAntifraudTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/commit_password/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'password': TEST_PASSWORD,
    }

    def setUp(self):
        super(CommitPasswordWithAntifraudTestcase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
        )
        self.env.antifraud_api.set_response_value_without_method(
            antifraud_score_response(action=ScoreAction.DENY),
        )

    def tearDown(self):
        del self.track_id
        super(CommitPasswordWithAntifraudTestcase, self).tearDown()

    def assert_ok_antifraud_score_request(self, request, **extra_params):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(mock_headers(**self.http_headers))
        params.external_id = 'track-' + self.track_id
        params.input_login = TEST_LOGIN
        params.uid = TEST_UID
        params.lah_uids = [TEST_UID]
        params.available_challenges = ['email_hint']
        params.surface = 'multi_step_password'

        expected_params = params.as_dict()
        expected_params.update(extra_params)
        # тесты мигают без сортировки
        if 'available_challenges' in expected_params:
            expected_params['available_challenges'] = sorted(expected_params['available_challenges'])
        if 'available_challenges' in request_data:
            request_data['available_challenges'] = sorted(request_data['available_challenges'])
        iterdiff(eq_)(request_data, expected_params)

        request.assert_query_contains(dict(consumer='passport'))

    def test_ok_challenged_by_antifraud_api(self):
        self.env.antifraud_api.set_response_value_without_method(
            antifraud_score_response(action=ScoreAction.ALLOW, tags=['email_hint']),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=dict(
                self.account_response_values(),
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET),
            ),
            state='auth_challenge',
            track_id=TEST_TRACK_ID,
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='1',
                af_reason='some-reason',
                af_tags='email_hint',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
                ufo_status='1',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_deny_by_antifraud_api(self):
        resp = self.make_request()
        self.assert_error_response(
            resp,
            error_codes=['password.not_matched'],
            track_id=TEST_TRACK_ID,
        )
        assert self.env.antifraud_api.requests
        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='DENY',
                af_is_auth_forbidden='1',
                af_is_challenge_required='0',
                af_reason='some-reason',
                af_tags='',
                decision_source='antifraud_api',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_challenge_required='0',
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_is_mobile(self):
        with self.track_transaction(self.track_id) as track:
            track.x_token_client_id = 'xclid'
            track.device_id = 'device-id'
            track.device_name = 'device-name'
            track.device_application = 'app-id'
            track.cloud_token = 'cloud-token'

        self.env.antifraud_api.set_response_value_without_method(
            antifraud_score_response(action=ScoreAction.ALLOW, tags=['email_hint']),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=dict(
                self.account_response_values(),
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET),
            ),
            state='auth_challenge',
            track_id=TEST_TRACK_ID,
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_antifraud_score_request(
            self.env.antifraud_api.requests[0],
            device_id='device-id',
            device_name='device-name',
            device_application='app-id',
            has_cloud_token=True,
            is_mobile=True,
            known_device='unknown',
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile.update(
            cloud_token='cloud-token',
            device_id='device-id',
            ip=TEST_RUSSIAN_IP,
            is_mobile=True,
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='1',
                af_reason='some-reason',
                af_tags='email_hint',
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                decision_source='antifraud_api',
                device_id='device-id',
                full_profile_AS_list='-',
                input_login=TEST_LOGIN,
                is_challenge_required='1',
                is_fresh_profile_passed='0',
                is_full_profile_passed='0',
                is_mobile='1',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_challenged_with_antifraud_score_request_error(self):
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError('Timeout error'))
        self.setup_blackbox_responses(
            with_phonenumber_alias=True,
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )

        with settings_context(
            ANTIFRAUD_FALLBACK_CHALLENGES=['push_2fa', 'phone_confirmation', 'question'],
            ANTIFRAUD_FALLBACK_PHONE_CHALLENGES=['flash_call', 'sms'],
            ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
            ANTIFRAUD_SHOW_CHALLENGE_ON_FAIL=True,
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            EMAIL_CODE_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=dict(
                self.account_response_values(),
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET),
            ),
            state='auth_challenge',
            track_id=TEST_TRACK_ID,
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_antifraud_score_request(
            self.env.antifraud_api.requests[0],
            available_challenges=['phone_hint', 'phone_confirmation', 'question', 'email_hint'],
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='1',
                af_request_error='Timeout error',
                af_tags='flash_call sms question',
                decision_source='antifraud_fallback',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
                ufo_status='1',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['af_fallback.decision.rps'],
            {'antifraud_fallback.decision.challenge_dmmm': 1},
        )

    def test_ok_challenged_with_push_with_antifraud_score_request_error(self):
        # антифрод не ответил
        # но есть возможность отправить пуш
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError('Timeout error'))
        self.setup_push_api_list_response(with_trusted_subscription=True)
        self.setup_bb_get_tokens_response()
        self.setup_blackbox_responses(
            with_phonenumber_alias=True,
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )

        with settings_context(
            ANTIFRAUD_FALLBACK_CHALLENGES=['push_2fa', 'phone_confirmation', 'question'],
            ANTIFRAUD_FALLBACK_PHONE_CHALLENGES=['flash_call', 'sms'],
            ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
            ANTIFRAUD_SHOW_CHALLENGE_ON_FAIL=True,
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
            EMAIL_CODE_CHALLENGE_ENABLED=False,
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=dict(
                self.account_response_values(),
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET),
            ),
            state='auth_challenge',
            track_id=TEST_TRACK_ID,
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_antifraud_score_request(
            self.env.antifraud_api.requests[0],
            available_challenges=['question', 'phone_confirmation', 'push_2fa', 'email_hint', 'phone_hint'],
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='1',
                af_request_error='Timeout error',
                af_tags='push_2fa flash_call sms question',
                decision_source='antifraud_fallback',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
                ufo_status='1',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['af_fallback.decision.rps'],
            {'antifraud_fallback.decision.challenge_dmmm': 1},
        )

    def test_ok_deny_with_antifraud_score_request_error(self):
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError('Timeout error'))

        with settings_context(
            ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
            ANTIFRAUD_SHOW_CHALLENGE_ON_FAIL=True,
        ):
            resp = self.make_request()

        self.assert_error_response(
            resp,
            error_codes=['internal.temporary'],
            track_id=TEST_TRACK_ID,
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='DENY',
                af_is_auth_forbidden='1',
                af_is_challenge_required='0',
                af_request_error='Timeout error',
                af_tags='',
                decision_source='antifraud_fallback',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_challenge_required='0',
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['af_fallback.decision.rps'],
            {'antifraud_fallback.decision.deny_dmmm': 1},
        )

    def test_antifraud_score_request_error_and_counters_exceeded(self):
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError('Connection error'))
        self.env.kolmogor.set_response_side_effect('get', ['1,1'])

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile.update(
            ip=TEST_RUSSIAN_IP,
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                decision_source='settings',
                input_login=TEST_LOGIN,
                is_challenge_required='0',
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
                # суть этого теста
                af_is_limit_exceeded='1',
                af_request_error='Connection error',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['af_fallback.disabled.rps'],
            {'antifraud_fallback.disabled.errors_rate_exceeded_dmmm': 1},
        )

    def test_af_score_and_push_api_error_no_push_challenge(self):
        # И антифрод, и пуш-апи недоступны. Не ломаемся, а показываем доступные челленжи
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError('Timeout error'))
        self.env.push_api.set_response_value('list', PushApiTemporaryError)
        self.setup_bb_get_tokens_response()
        self.setup_blackbox_responses(
            with_phonenumber_alias=True,
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )

        with settings_context(
            ANTIFRAUD_FALLBACK_CHALLENGES=['push_2fa', 'phone_confirmation', 'question'],
            ANTIFRAUD_FALLBACK_PHONE_CHALLENGES=['flash_call', 'sms'],
            ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
            ANTIFRAUD_SHOW_CHALLENGE_ON_FAIL=True,
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            EMAIL_CODE_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=dict(
                self.account_response_values(),
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET),
            ),
            state='auth_challenge',
            track_id=TEST_TRACK_ID,
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_antifraud_score_request(
            self.env.antifraud_api.requests[0],
            available_challenges=['question', 'phone_confirmation', 'email_hint', 'phone_hint'],
        )

        raw_env_profile = TEST_RAW_ENV_FOR_PROFILE
        raw_env_profile['ip'] = TEST_RUSSIAN_IP
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # актуальные для теста проверки
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='1',
                af_request_error='Timeout error',
                af_tags='flash_call sms question',
                decision_source='antifraud_fallback',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(raw_env=raw_env_profile).as_json,
                input_login=TEST_LOGIN,
                is_mobile='0',
                kind='ydb',
                login=TEST_LOGIN,
                type='multi_step_password',
                ufo_distance='0',
                ufo_status='1',
            ),
        ], offset=1)
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['af_fallback.decision.rps'],
            {'antifraud_fallback.decision.challenge_dmmm': 1},
        )


@with_settings_hosts(
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    CHECK_AVATARS_SECRETS_DENOMINATOR=1,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    PWNED_PASSWORD_CHANGE_DENOMINATOR=1,
)
class CommitPasswordTestcase(BaseMultiStepTestcase, CommonAuthTests):
    default_url = '/1/bundle/auth/password/multi_step/commit_password/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'password': TEST_PASSWORD,
    }

    def setUp(self):
        super(CommitPasswordTestcase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
        )

    def tearDown(self):
        del self.track_id
        super(CommitPasswordTestcase, self).tearDown()

    def assert_track_ok(
        self,
        auth_method='password',
        session_scope=None,
    ):
        session_scope = session_scope or SessionScope.xsession

        track = self.track_manager.read(TEST_TRACK_ID)
        ok_(track.allow_authorization)
        eq_(track.auth_method, auth_method)
        eq_(track.session_scope, str(session_scope))

    def account_response_values(self, login=TEST_LOGIN, is_workspace_user=False, **kwargs):
        account = super(CommitPasswordTestcase, self).account_response_values(login=login, is_workspace_user=is_workspace_user, **kwargs)
        account['avatar_url'] = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET)
        return account

    def test_ok_with_2fa(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.assert_track_ok(auth_method='otp')
        self.assert_antifraud_auth_fail_not_written()

    def test_long_password(self):
        resp = self.make_request(
            query_args=dict(self.http_query_args, password='a'*256)
        )
        self.assert_error_response(
            resp,
            track_id=self.track_id,
            error_codes=['password.not_matched'],
        )
        eq_(self.env.blackbox._mock.request.call_count, 0)
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_password/invalid_password_format',
            _exclude=['uid'],
        )

    def test_not_long_password(self):
        resp = self.make_request(
            query_args=dict(self.http_query_args, password='a' * 255)
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.assert_track_ok(auth_method='password')
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_with_rfc_2fa(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.rfc_2fa_on': '1',
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='rfc_totp',
            account=self.account_response_values(is_rfc_2fa_enabled=True),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_RFC_TOTP])
        ok_(not track.allow_authorization)
        ok_(not track.change_password_reason)
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_with_rfc_2fa_and_expired_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.rfc_2fa_on': '1',
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='rfc_totp',
            account=self.account_response_values(is_rfc_2fa_enabled=True),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_RFC_TOTP])
        ok_(not track.allow_authorization)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_EXPIRED)
        self.assert_antifraud_auth_fail_not_written()

    def test_password_pwned(self):
        password = b'password'
        encrypted_password = hashlib.sha1(password).hexdigest()

        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'password_quality.quality.uid': 10,
            },
            crypt_password='1:{}'.format(encrypted_password),
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password.upper())),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        resp = self.make_request(query_args=dict(password=password))
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='password_pwned',
            number=dump_number(TEST_PHONE_NUMBER),
            account=self.account_response_values(),
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_password_is_pwned_with_sms2fa_on(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(hashlib.sha1(TEST_PASSWORD).hexdigest().upper())),
        )

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                attributes={
                    'account.sms_2fa_on': '1',
                    'account.2fa_on': '0',
                },
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            status='ok',
        )

        eq_(len(self.env.shakur.requests), 1)
        self.env.db.check_missing('attributes', 'password.is_password_pwned', uid=TEST_UID, db='passportdbshard1')

    def test_ok_with_pdd_account_and_password_is_pwned(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(hashlib.sha1(TEST_PASSWORD).hexdigest())),
        )

        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                can_users_change_password='0',
                domain=TEST_PDD_DOMAIN,
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                attributes={
                    'account.is_pdd_agreement_accepted': '1',
                },
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                dbfields={
                    'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
                    'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                }
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            status='ok',
        )

        eq_(len(self.env.shakur.requests), 1)
        self.env.db.check_missing('attributes', 'password.is_password_pwned', uid=TEST_UID, db='passportdbshard1')

    def test_ok_with_email_code(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_EMAIL_CODE],
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='email_code',
            account=self.account_response_values(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_EMAIL_CODE])
        ok_(not track.allow_authorization)
        ok_(not track.change_password_reason)
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_with_email_code_and_expired_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_EMAIL_CODE],
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='email_code',
            account=self.account_response_values(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_EMAIL_CODE])
        ok_(not track.allow_authorization)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_EXPIRED)
        self.assert_antifraud_auth_fail_not_written()

    def test_response_caching(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            dict(
                self.default_response_values(),
                status='ok',
            ),
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_invalid_password(self):
        self.setup_blackbox_responses(password_status=BLACKBOX_PASSWORD_BAD_STATUS)
        with self.track_transaction() as track:
            track.retpath = TEST_RETPATH
        resp = self.make_request(
            query_args=dict(self.http_query_args, password='a' * 10)
        )
        self.assert_error_response(
            resp,
            track_id=self.track_id,
            error_codes=['password.not_matched'],
        )
        self.assert_antifraud_auth_fail_written(
            comment='multi_step_password/VALID/BAD/-/password.not_matched',
            retpath=TEST_RETPATH,
        )

    def test_allow_scholar(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(is_scholar_session=True),
        )

        with self.track_transaction() as track:
            track.allow_scholar = True

        resp = self.make_request()

        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok(session_scope=SessionScope.scholar)

        assert len(self.env.blackbox.requests) == 1
        calls = self.env.blackbox.get_requests_by_method('login')
        assert len(calls) == 1
        assert calls[0].post_args.get('allow_scholar') == 'yes'

    def test_not_allow_scholar(self):
        with self.track_transaction() as track:
            track.allow_scholar = None

        resp = self.make_request()

        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_ok()

        assert len(self.env.blackbox.requests) == 1
        calls = self.env.blackbox.get_requests_by_method('login')
        assert len(calls) == 1
        assert 'allow_scholar' not in calls[0].post_args
