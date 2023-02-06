# -*- coding: utf-8 -*-

import hashlib
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_AVATAR_DEFAULT_KEY,
    TEST_AVATAR_SECRET,
    TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    TEST_DOMAIN,
    TEST_LOGIN,
    TEST_ORIGIN,
    TEST_PASSWORD,
    TEST_PDD_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_RETPATH,
    TEST_SERVICE,
    TEST_UID,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_SECOND_STEP_EMAIL_CODE,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_sign_response,
)
from passport.backend.core.builders.shakur.faker.fake_shakur import shakur_check_password_no_postfix
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import deep_merge

from .base import (
    BaseSubmitTestCase,
    CommonContinueTests,
)


@with_settings_hosts(
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    CHECK_AVATARS_SECRETS_DENOMINATOR=1,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    PWNED_PASSWORD_CHANGE_DENOMINATOR=0,
)
class CommitPasswordTestCase(BaseSubmitTestCase, CommonContinueTests):
    url = '/2/bundle/auth/password/commit_password/?consumer=dev'
    type = 'password'

    def setup_statbox_templates(self):
        super(CommitPasswordTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='submitted',
            input_login=TEST_LOGIN,
            type=self.type,
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from='profile_threshold_exceeded',
            input_login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _inherit_from='ufo_profile_checked',
            input_login=TEST_LOGIN,
            af_action='ALLOW',
            af_is_auth_forbidden='0',
            af_is_challenge_required='0',
            af_reason='some-reason',
            af_tags='',
        )

    def get_base_query_params(self):
        return {
            'track_id': self.track_id,
            'login': TEST_LOGIN,
            'password': TEST_PASSWORD,
        }

    def setUp(self):
        super(CommitPasswordTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN
            track.service = TEST_SERVICE
            track.login = TEST_LOGIN
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
        )

    def account_response_values(self, login=TEST_LOGIN, is_workspace_user=False, domain=None):
        account = super(CommitPasswordTestCase, self).account_response_values(login=login, is_workspace_user=is_workspace_user, domain=domain)
        account['avatar_url'] = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET)
        return account

    def test_pdd_invalid_login_error(self):
        resp = self.make_request(is_pdd='1')
        self.assert_error_response(
            resp,
            ['login.invalid_format'],
            track_id=self.track_id,
        )

    def test_pdd_domain_is_not_hosted_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request(is_pdd='1', login=TEST_PDD_LOGIN)
        self.assert_error_response(
            resp,
            ['domain.not_hosted'],
            track_id=self.track_id,
        )
        self.env.blackbox.requests[0].assert_query_contains({
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_password_change_required(self):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='account_hacked',
            number=dump_number(TEST_PHONE_NUMBER),
            account=self.account_response_values(),
        )

    def test_pwned_password_change_required_and_shakur_experiment_is_off(self):
        password = b'password'
        encrypted_password = hashlib.sha1(password).hexdigest()

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password)),
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:%s' % encrypted_password,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        resp = self.make_request(
            password=password,
        )
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='account_hacked',
            account=self.account_response_values(),
        )

    def test_ok_with_policy(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        resp = self.make_request(
            policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_checked'),
        ])

        track = self.track_manager.read(self.track_id)
        eq_(track.authorization_session_policy, AUTHORIZATION_SESSION_POLICY_PERMANENT)

    def test_ok_without_submit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = None
            track.origin = None
            track.service = None
            track.fretpath = None
            track.clean = None
            track.authorization_session_policy = None

        resp = self.make_request(
            exclude=['track_id'],
            origin=TEST_ORIGIN,
            retpath=TEST_RETPATH,
            service=TEST_SERVICE,
            fretpath='fretpath',
            clean='clean',
            policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                origin=TEST_ORIGIN,
            ),
            self.env.statbox.entry(
                'ufo_profile_checked',
                origin=TEST_ORIGIN,
            ),
        ])

        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.origin, TEST_ORIGIN)
        eq_(track.service, TEST_SERVICE)
        eq_(track.fretpath, 'fretpath')
        eq_(track.clean, 'clean')
        eq_(track.authorization_session_policy, AUTHORIZATION_SESSION_POLICY_SESSIONAL)
        eq_(track.auth_method, 'password')
        eq_(track.surface, 'web_password')

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

    def test_use_blackbox_status_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.blackbox_login_status = blackbox.BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = blackbox.BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request(exclude=['login', 'password'])
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

    def test_blackbox_status_from_track_not_used(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.blackbox_login_status = blackbox.BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = blackbox.BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

    def test_password_not_passed(self):
        resp = self.make_request(exclude=['login', 'password'])
        self.assert_error_response(
            resp,
            ['password.not_matched'],
            **self.default_response_values()
        )

        eq_(len(self.env.blackbox.requests), 0)

    def test_ok_with_2fa(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_otp_magic_passed is None)
        eq_(track.auth_method, 'otp')

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
        account_response_values = self.account_response_values()
        account_response_values['is_rfc_2fa_enabled'] = True
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            account=account_response_values,
            state='rfc_totp',
            **self.default_response_values()
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_otp_magic_passed is None)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_RFC_TOTP])
        ok_(not track.allow_authorization)

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
            state='email_code',
            account=self.account_response_values(),
            **self.default_response_values()
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_otp_magic_passed is None)
        eq_(track.auth_method, 'password')
        ok_(track.is_second_step_required)
        eq_(track.allowed_second_steps, [BLACKBOX_SECOND_STEP_EMAIL_CODE])
        ok_(not track.allow_authorization)


@with_settings_hosts(
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    CHECK_AVATARS_SECRETS_DENOMINATOR=1,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
)
class AntifraudCommitPasswordTestCase(BaseSubmitTestCase):
    url = '/2/bundle/auth/password/commit_password/?consumer=dev'
    type = 'password'

    def get_base_query_params(self):
        return {
            'track_id': self.track_id,
            'login': TEST_LOGIN,
            'password': TEST_PASSWORD,
        }

    def setUp(self):
        super(AntifraudCommitPasswordTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN
            track.service = TEST_SERVICE
            track.login = TEST_LOGIN
        self.env.blackbox.set_response_value('sign', blackbox_sign_response(TEST_AVATAR_SECRET))
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

    def setup_statbox_templates(self):
        super(AntifraudCommitPasswordTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from='profile_threshold_exceeded',
            input_login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _inherit_from='ufo_profile_checked',
            af_action='ALLOW',
            af_is_auth_forbidden='0',
            af_is_challenge_required='0',
            af_reason='some-reason',
            af_tags='',
            input_login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='submitted',
            input_login=TEST_LOGIN,
            type=self.type,
        )

    def account_response_values(self, login=TEST_LOGIN, is_workspace_user=False, domain=None):
        account = super(AntifraudCommitPasswordTestCase, self).account_response_values(
            domain=domain,
            is_workspace_user=is_workspace_user,
            login=login,
        )
        account['avatar_url'] = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_DEFAULT_KEY, TEST_AVATAR_SECRET)
        return account

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(self.get_headers())
        params.external_id = 'track-' + self.track_id
        params.input_login = TEST_LOGIN
        params.uid = TEST_UID
        params.available_challenges = []
        params.surface = 'auth_by_password'
        eq_(request_data, params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def test_ok(self):
        resp = self.make_request()

        self.assert_ok_response(resp, **self.default_response_values())

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('ufo_profile_checked'),
        ])

        eq_(len(self.env.antifraud_api.requests), 1)
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])
