# -*- coding: utf-8 -*-
from copy import deepcopy
import json
import re
from time import time

from django.conf import settings
from django.test.utils import override_settings
import mock
from nose.tools import (
    assert_false,
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.antifraud import (
    BaseAntifraudApiError,
    ScoreAction,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox import (
    BLACKBOX_LOGIN_V1_DISABLED_STATUS,
    BLACKBOX_LOGIN_V1_EXPIRED_STATUS,
    BLACKBOX_LOGIN_V1_INVALID_STATUS,
    BLACKBOX_LOGIN_V1_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
    BlackboxInvalidParamsError,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SECOND_STEP_RFC_TOTP
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_build_badauth_counts,
    blackbox_login_response,
)
from passport.backend.core.builders.captcha import (
    CaptchaLocateError,
    CaptchaServerError,
)
from passport.backend.core.builders.captcha.faker import captcha_response_check
from passport.backend.core.builders.passport import PassportTemporaryError
from passport.backend.core.builders.passport.faker import passport_ok_response
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
    CommonRateLimitsTests,
    TEST_IP,
)
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_DEVICE_ID,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_NORMALIZED_LOGIN,
    TEST_UID,
)
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


TEST_PASSWORD = 'password'
TEST_MAGNITOLA_APP_ID = 'magnitola_app_id'
TEST_TOKEN_REQUEST_VALIDATORS = {
    'ignore_for': [
        {
            'class': 'FieldValueMatch',
            'field': 'app_id',
            'value_in': {TEST_MAGNITOLA_APP_ID},
        },
    ],
    'validators': [
        {
            'class': 'RequiredFields',
            'fields': ['deviceid', 'app_id', 'env.user_agent'],
        },
        {
            'class': 'FieldValueMatch',
            'field': 'app_id',
            'value_in': [
                'abc.def',
                '123.456',
            ],
        },
        {
            'class': 'FieldValueMatch',
            'field': 'app_id2',
            'value_in': [
                'abc.def',
            ],
            'lowercase': True,
        },
        {
            'class': 'FieldValueMatch',
            'field': 'env.user_agent',
            'regex': re.compile(r'^com.yandex.mobile.auth.sdk/([^ ]+)'),
        },
        {
            'class': 'FieldValueMatch',
            'field': 'non-existent',
            'value_in': {'some_value'},
        },
    ],
}
TEST_TOKEN_REQUEST_VALIDATORS_JSON = {
    'validators': [
        {
            'class': 'RequiredFields',
            'fields': ['env.user_agent'],
        },
        {
            'class': 'FieldValueMatch',
            'field': 'env.user_agent',
            'regex': re.compile(r'^Some\.UserAgent (?P<ua_json>.+)$'),
            're_group_validators': [
                {
                    'class': 'FieldValueJson',
                    'field': 'ua_json',
                    'to_statbox': False,
                    'validators': [
                        {
                            'class': 'RequiredFields',
                            'fields': ['os', 'vsn'],
                        },
                        {
                            'class': 'FieldValueMatch',
                            'field': 'os',
                            'value_in': ['windows', 'mac', 'cli'],
                            'statbox_alias': 'app_platform',
                        },
                        {
                            # Просто чтобы залогировать
                            'class': 'FieldDummy',
                            'field': 'vsn',
                            'statbox_alias': 'app_version',
                        },
                    ],
                },
            ],
        },
    ],
}
TEST_WHITELISTED_USER_AGENT = 'com.yandex.mobile.auth.sdk/app1'

TEST_OUTDATED_CLIENT_MESSAGE = 'You are using an outdated version of the application https://ya.cc/some_link'
TEST_OUTDATED_CLIENT_MESSAGE_RU = 'Вы используете устаревшую версию приложения: https://ya.cc/some_link1'


@override_settings(
    GRANT_TYPE_PASSWORD_CAPTCHA_COUNTRIES={'RU', 'ET', 'CF'},
    OUTDATED_CLIENT_MESSAGE=TEST_OUTDATED_CLIENT_MESSAGE,
    OUTDATED_CLIENT_MESSAGE_RU=TEST_OUTDATED_CLIENT_MESSAGE_RU,
    ANTIFRAUD_SCORE_ENABLE=True,
    ANTIFRAUD_SCORE_DRY_RUN=False,
)
class TestIssueTokenByPassword(BaseIssueTokenTestCase, CommonIssueTokenTests, CommonRateLimitsTests):
    grant_type = 'password'
    password_passed = True

    def setUp(self):
        super(TestIssueTokenByPassword, self).setUp()
        self.mock_country_code_by_ip = mock.patch(
            'passport.backend.oauth.api.api.old.bundle_views.views.get_country_code_by_ip',
            mock.Mock(return_value='RU'),
        )
        self.mock_country_code_by_ip.start()

        self.is_yandex_ip_mock = mock.Mock(return_value=False)
        self.is_yandex_ip_patch = mock.patch(
            'passport.backend.oauth.api.api.old.bundle_views.views.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        self.is_yandex_ip_patch.start()

        self.is_yandex_server_ip_mock = mock.Mock(return_value=False)
        self.is_yandex_server_ip_patch = mock.patch(
            'passport.backend.oauth.api.api.old.bundle_views.views.is_yandex_server_ip',
            self.is_yandex_server_ip_mock,
        )
        self.is_yandex_server_ip_patch.start()

    def tearDown(self):
        self.is_yandex_server_ip_patch.stop()
        self.is_yandex_ip_patch.stop()
        self.mock_country_code_by_ip.stop()
        super(TestIssueTokenByPassword, self).tearDown()

    def credentials(self):
        return {
            'username': TEST_LOGIN,
            'password': TEST_PASSWORD,
        }

    def assert_blackbox_ok(self, authtype='oauthcreate'):
        super(TestIssueTokenByPassword, self).assert_blackbox_ok()
        self.fake_blackbox.requests[0].assert_post_data_contains({
            'method': 'login',
            'format': 'json',
            'ver': '1',
            'aliases': 'all',
            'full_info': 'yes',
            'find_by_phone_alias': 'force_on',
            'country': 'RU',
            'userip': TEST_IP,
            'authtype': authtype,
            'get_badauth_counts': 'yes',
        })

    def specific_statbox_values(self, **kwargs):
        values = {
            'login': TEST_LOGIN,
        }
        values.update(kwargs)
        return values

    def assert_antifraud_score_ok(self, **kwargs):
        kwargs.setdefault('badauth_counts', blackbox_build_badauth_counts())
        kwargs.setdefault('input_login', TEST_LOGIN)
        return super(TestIssueTokenByPassword, self).assert_antifraud_score_ok(**kwargs)

    def test_meta_invalid(self):
        rv = self.make_request(expected_status=400, x_meta='bad\0value')
        self.assert_error(rv, error='invalid_request', error_description='meta is not valid')

    def test_no_reuse_for_glogouted(self):
        token = issue_token(uid=self.uid, client=self.test_client, grant_type=self.grant_type, env=self.env)
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != token.access_token)

    def test_ok_with_captcha(self):
        rv = self.make_request(x_captcha_key='key', x_captcha_answer='answer')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.fake_blackbox.requests[0].assert_post_data_contains({'authtype': 'oauthcreate'})
        self.assert_antifraud_score_ok()

    def test_ok_with_cyrillic_login(self):
        rv = self.make_request(username='pdd@закодированныйдомен.рф')
        self.assert_token_response_ok(rv)
        self.assert_antifraud_score_ok(input_login='pdd@закодированныйдомен.рф')

    @override_settings(ACCEPT_LOGIN_ID_FOR_GT_PASSWORD=True)
    def test_ok_with_login_id(self):
        rv = self.make_request(login_id=TEST_LOGIN_ID)
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)
        self.assert_antifraud_score_ok(login_id=TEST_LOGIN_ID)
        self.assert_credentials_log_ok(login=TEST_NORMALIZED_LOGIN)

    def test_captcha_not_in_post(self):
        rv = self.make_request(expected_status=400, x_captcha_key='key')
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='x_captcha_key or x_captcha_answer not in POST',
        )
        assert_false(self.fake_blackbox.requests)
        assert_false(self.fake_captcha.requests)
        self.assert_antifraud_score_not_sent()

    def test_captcha_empty_key(self):
        rv = self.make_request(expected_status=403, x_captcha_key='', x_captcha_answer='answer')
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 1)
        self.assert_antifraud_score_not_sent()

    def test_captcha_empty_answer(self):
        rv = self.make_request(expected_status=403, x_captcha_key='key', x_captcha_answer='')
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 1)

    def test_captcha_not_found(self):
        self.fake_captcha.set_response_side_effect('check', CaptchaLocateError)
        rv = self.make_request(expected_status=403, x_captcha_key='unknown_key', x_captcha_answer='answer')
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 2)
        self.fake_captcha.requests[1].assert_query_contains({'type': 'nbg'})

    def test_captcha_bad_answer(self):
        rv = self.make_request(expected_status=403, x_captcha_key='key', x_captcha_answer='a' * 1000)
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 1)
        self.fake_captcha.requests[0].assert_query_contains({'type': 'nbg'})

    def test_captcha_wrong_answer(self):
        self.fake_captcha.set_response_value(
            'check',
            captcha_response_check(successful=False),
        )
        rv = self.make_request(expected_status=403, x_captcha_key='key', x_captcha_answer='answer')
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 2)
        self.fake_captcha.requests[1].assert_query_contains({'type': 'nbg'})

    def test_captcha_wrong_answer_for_other_scale_factor(self):
        self.fake_captcha.set_response_value(
            'check',
            captcha_response_check(successful=False),
        )
        rv = self.make_request(
            expected_status=403,
            x_captcha_key='key',
            x_captcha_answer='answer',
            x_captcha_scale_factor='2',
        )
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(status='error', reason='captcha.wrong_answer', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')
        eq_(len(self.fake_captcha.requests), 2)
        self.fake_captcha.requests[1].assert_query_contains({'type': 'nbg_s2'})

    @override_settings(DEGRADATE_CAPTCHA_FOR_TEST_LOGINS=True)
    def test_captcha_wrong_answer_accepted_for_test_login(self):
        """Тестовый логин, тестовое окружение - принимаем любой ответ на капчу"""
        self.fake_captcha.set_response_value(
            'check',
            captcha_response_check(successful=False),
        )
        rv = self.make_request(
            x_captcha_key='key',
            x_captcha_answer='answer',
            username='yndx-test',
        )
        self.assert_token_response_ok(rv)

    @override_settings(DEGRADATE_CAPTCHA_FOR_TEST_LOGINS=False)
    def test_captcha_wrong_answer_not_accepted_for_test_login(self):
        """Тестовый логин, но не тестовое окружение - неверный ответ на капчу не принимаем"""
        self.fake_captcha.set_response_value(
            'check',
            captcha_response_check(successful=False),
        )
        rv = self.make_request(
            expected_status=403,
            x_captcha_key='key',
            x_captcha_answer='answer',
            username='yndx-test',
        )
        self.assert_error(
            rv,
            error='403',
            error_description='Wrong CAPTCHA answer',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.wrong_answer',
            **self.specific_statbox_values(login='yndx-test')
        )
        self.assert_antifraud_log_error(reason='captcha.wrong_answer')

    def test_captcha_always_required_for_test_login(self):
        """Тестовый логин "c капчей" - всегда показываем капчу"""
        rv = self.make_request(expected_status=403, username='yndx-captcha-always-test')
        self.assert_error(
            rv, error='403', error_description='CAPTCHA required', x_captcha_key='key', x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='test',
            **self.specific_statbox_values(login='yndx-captcha-always-test')
        )

    @override_settings(DEGRADATE_CAPTCHA_FOR_TEST_LOGINS=True)
    def test_blackbox_not_required_for_test_login(self):
        """Тестовый логин "без капчи", тестовое окружение - делаем вид, что капча разгадана"""
        rv = self.make_request(username='yndx-captcha-never-test')
        self.assert_token_response_ok(rv)
        self.fake_blackbox.requests[0].assert_post_data_contains({
            'captcha': 'no',
        })

    @override_settings(DEGRADATE_CAPTCHA_FOR_TEST_LOGINS=False)
    def test_captcha_required_for_test_login(self):
        """Тестовый логин "без капчи", но не тестовое окружение - показываем капчу по просьбе ЧЯ"""
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        rv = self.make_request(expected_status=403, username='yndx-captcha-never-test')
        self.assert_error(
            rv, error='403', error_description='CAPTCHA required', x_captcha_key='key', x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values(login='yndx-captcha-never-test')
        )
        self.assert_antifraud_log_error(reason='captcha.required')
        ok_('captcha' not in self.fake_blackbox.requests[0].post_args)

    def test_login_empty(self):
        rv = self.make_request(expected_status=400, username='')
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(status='error', reason='login.empty')
        self.assert_antifraud_log_error(reason='login.empty')
        assert_false(self.fake_blackbox.requests)
        self.assert_antifraud_score_not_sent()

    def test_password_empty(self):
        rv = self.make_request(expected_status=400, password='')
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(status='error', reason='password.empty')
        self.assert_antifraud_log_error(reason='password.empty')
        assert_false(self.fake_blackbox.requests)

    def test_user_blocked(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(status='error', reason='user.blocked', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='user.blocked')
        eq_(len(self.fake_blackbox.requests), 1)

    def test_blackbox_login_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'login',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Invalid parameters passed to Blackbox')
        self.check_statbox(status='error', reason='blackbox_params.invalid', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='blackbox_params.invalid')
        self.assert_antifraud_score_not_sent()

    def test_password_expired__sid_67(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_EXPIRED_STATUS,
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(rv, error='403', error_description='Expired password')
        self.check_statbox(
            status='error',
            reason='password.expired',
            password_expire_reason='strong_password_policy',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='password.expired', uid=str(TEST_UID))

    def test_password_expired__flushed_pdd(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                aliases={'pdd': TEST_LOGIN},
                attributes={
                    settings.BB_ATTR_PDD_AGREEMENT_ACCEPTED: '1',
                    settings.BB_ATTR_PASSWORD_CHANGE_REASON: '2',
                },
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(rv, error='403', error_description='Expired password')
        self.check_statbox(
            status='error',
            reason='password.expired',
            password_expire_reason='flushed_pdd',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='password.expired', uid=str(TEST_UID))

    def test_password_expired__pdd_completion_required(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                aliases={'pdd': TEST_LOGIN},
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(rv, error='403', error_description='Expired password')
        self.check_statbox(
            status='error',
            reason='password.expired',
            password_expire_reason='incomplete_pdd',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='password.expired', uid=str(TEST_UID))
        self.assert_antifraud_score_not_sent()

    def test_complete_pdd_ok(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                aliases={'pdd': TEST_LOGIN},
                attributes={settings.BB_ATTR_PDD_AGREEMENT_ACCEPTED: '1'},
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_score_ok()

    def test_password_expired__autoregistered_completion_required(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_PASSWORD_CREATING_REQUIRED: '1'},
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(rv, error='403', error_description='Expired password')
        self.check_statbox(
            status='error',
            reason='password.expired',
            password_expire_reason='incomplete_autoregistered',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='password.expired', uid=str(TEST_UID))

    def test_password_change_required(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_PASSWORD_CHANGE_REASON: '1'},
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(rv, error='403', error_description='Password change required')
        self.check_statbox(
            status='error',
            reason='password.change_required',
            uid=str(TEST_UID),
            **self.specific_statbox_values(),
        )
        self.assert_antifraud_log_error(reason='password.change_required', uid=str(TEST_UID))

    def test_lite_ok(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                aliases={
                    'lite': 'foo@mail.ru',
                },
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        self.assert_antifraud_score_ok()

    def test_blackbox_captcha_required(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        rv = self.make_request(expected_status=403)
        self.assert_error(
            rv, error='403', error_description='CAPTCHA required', x_captcha_key='key', x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='captcha.required')
        self.fake_captcha.requests[0].assert_query_contains({'type': 'nbg'})
        self.assert_antifraud_score_not_sent()

    def test_blackbox_captcha_required_other_scale_factor(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        rv = self.make_request(expected_status=403, x_captcha_scale_factor='2')
        self.assert_error(
            rv, error='403', error_description='CAPTCHA required', x_captcha_key='key', x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='captcha.required')
        self.fake_captcha.requests[0].assert_query_contains({'type': 'nbg_s2'})

    def test_blackbox_captcha_required_unknown_scale_factor(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        rv = self.make_request(expected_status=403, x_captcha_scale_factor='777')
        self.assert_error(
            rv, error='403', error_description='CAPTCHA required', x_captcha_key='key', x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='captcha.required')
        self.fake_captcha.requests[0].assert_query_contains({'type': 'nbg'})

    def test_blackbox_captcha_required_but_failed_to_generate(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        self.fake_captcha.set_response_side_effect(
            'generate',
            CaptchaServerError,
        )
        rv = self.make_request(expected_status=503, decode_response=False)
        eq_(rv, 'Service temporarily unavailable')
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='captcha.required')

    def test_blackbox_password_invalid(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_INVALID_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(status='error', reason='password.invalid', **self.specific_statbox_values())
        self.assert_antifraud_log_error(reason='password.invalid')
        self.assert_antifraud_score_not_sent()

    def test_blackbox_temporary_error(self):
        self.fake_blackbox.set_response_side_effect(
            'login',
            BlackboxTemporaryError,
        )
        rv = self.make_request(decode_response=False, expected_status=503)
        eq_(rv, 'Service temporarily unavailable')

    def test_unhandled_error(self):
        self.fake_blackbox.set_response_side_effect(
            'login',
            RuntimeError,
        )
        rv = self.make_request(decode_response=False, expected_status=500)
        eq_(rv, 'Internal server error')
        self.assert_antifraud_score_not_sent()

    def test_issue_for_unknown_device(self):
        existing_token_without_device_id = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type=self.grant_type,
            env=self.env,
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        eq_(rv['access_token'], existing_token_without_device_id.access_token)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            {
                'auth_on_device': 'unknown',
            },
        )
        self.assert_antifraud_score_ok()

    def test_issue_for_new_device(self):
        existing_token_with_device_id = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type=self.grant_type,
            env=self.env,
            device_id='device1',
        )
        rv = self.make_request(device_id='device2')
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != existing_token_with_device_id.access_token)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            {
                'auth_on_device': 'new',
            },
        )

    def test_issue_for_existing_device(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:xtoken')])
        existing_token_with_device_id = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type=self.grant_type,
            env=self.env,
            device_id='device1',
        )
        rv = self.make_request(device_id='device1')
        self.assert_token_response_ok(rv)
        eq_(rv['access_token'], existing_token_with_device_id.access_token)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            {
                'auth_on_device': 'already_existed',
            },
        )

    @override_settings(BLACKLISTED_AS_LIST={'AS1234'})
    def test_AS_blacklisted_and_new_device(self):
        fake_region = mock.Mock()
        fake_region.AS_list = ['AS1234']
        with mock.patch('passport.backend.oauth.api.api.old.bundle_views.views.Region', mock.Mock(return_value=fake_region)):
            rv = self.make_request(expected_status=403, device_id='device1')
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='profile',
            ip_check_result='AS_blacklisted',
            auth_on_device='new',
            challenge_email_sent='1',
            is_challenged='1',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )
        self.assert_antifraud_score_not_sent()

    @override_settings(BLACKLISTED_AS_LIST={'AS1234'})
    def test_AS_blacklisted_and_existing_device(self):
        existing_token_with_device_id = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type=self.grant_type,
            env=self.env,
            device_id='device1',
        )
        fake_region = mock.Mock()
        fake_region.AS_list = ['AS1234']
        with mock.patch('passport.backend.oauth.api.api.old.bundle_views.views.Region', mock.Mock(return_value=fake_region)):
            rv = self.make_request(device_id='device1')
        self.assert_token_response_ok(rv)
        eq_(rv['access_token'], existing_token_with_device_id.access_token)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            {
                'mode': 'issue_token',
                'action': 'issue',
                'status': 'ok',
                'ip_check_result': 'AS_blacklisted',
                'auth_on_device': 'already_existed',
            },
        )

    @override_settings(BLACKLISTED_AS_LIST={'AS1234'})
    def test_AS_blacklisted_and_new_device__too_many_emails(self):
        self.fake_passport.set_response_value(
            'send_challenge_email',
            passport_ok_response(email_sent=False),
        )
        fake_region = mock.Mock()
        fake_region.AS_list = ['AS1234']
        with mock.patch('passport.backend.oauth.api.api.old.bundle_views.views.Region', mock.Mock(return_value=fake_region)):
            rv = self.make_request(expected_status=403, device_id='device1')
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='profile',
            ip_check_result='AS_blacklisted',
            auth_on_device='new',
            challenge_email_sent='0',
            is_challenged='1',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )

    @override_settings(BLACKLISTED_AS_LIST={'AS1234'})
    def test_AS_blacklisted_and_new_device__failed_to_send_email(self):
        self.fake_passport.set_response_side_effect(
            'send_challenge_email',
            PassportTemporaryError(),
        )
        fake_region = mock.Mock()
        fake_region.AS_list = ['AS1234']
        with mock.patch('passport.backend.oauth.api.api.old.bundle_views.views.Region', mock.Mock(return_value=fake_region)):
            rv = self.make_request(expected_status=403, device_id='device1')
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='profile',
            ip_check_result='AS_blacklisted',
            auth_on_device='new',
            challenge_email_sent='0',
            is_challenged='1',
            uid=str(TEST_UID),
            **self.specific_statbox_values()
        )

    def test_rate_limit_exceeded_uid(self):
        self.fake_kolmogor.set_response_value('get', '2,3')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=403)
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                reason='rate_limit_exceeded',
                status='error',
                key='grant_type:%s:uid:%s' % (self.grant_type, TEST_UID),
                value='3',
                limit='2',
                uid=str(TEST_UID),
                client_id=self.test_client.display_id,
            ),
            entry_index=-2,
        )
        self.assert_antifraud_log_error(reason='captcha.required', uid=str(TEST_UID))
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
        self.assert_antifraud_score_not_sent()

    def test_rate_limit_exceeded_ip(self):
        self.fake_kolmogor.set_response_value('get', '3,2')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=403)
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                reason='rate_limit_exceeded',
                status='error',
                key='grant_type:%s:ip:%s' % (self.grant_type, TEST_IP),
                value='3',
                limit='2',
                uid=str(TEST_UID),
                client_id=self.test_client.display_id,
            ),
            entry_index=-2,
        )
        self.assert_antifraud_log_error(reason='captcha.required', uid=str(TEST_UID))
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
        self.assert_antifraud_score_not_sent()

    def test_ignore_rate_limits_if_captcha_passed(self):
        self.fake_kolmogor.set_response_value('get', '101,101')
        with self.override_rate_limit_settings():
            rv = self.make_request(
                x_captcha_key='key',
                x_captcha_answer='answer',
            )
        self.assert_token_response_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('inc')), 1)
        self.assert_antifraud_score_ok()

    def test_otp_required(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(
            status='error',
            reason='second_step.not_implemented',
            allowed_steps=BLACKBOX_SECOND_STEP_RFC_TOTP,
            uid=str(TEST_UID),
            **self.specific_statbox_values(),
        )
        self.assert_antifraud_log_error(reason='second_step.not_implemented', uid=str(TEST_UID))

    def test_sms_2fa_enabled__error(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_SMS_2FA_ON: '1'},
            ),
        )
        self.fake_kolmogor.set_response_value('get', '0')
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='login or password is not valid')
        self.check_statbox(
            status='error',
            reason='sms_2fa.enabled',
            uid=str(TEST_UID),
            **self.specific_statbox_values(),
        )
        self.assert_antifraud_log_error(reason='sms_2fa.enabled', uid=str(TEST_UID))
        self.assert_antifraud_score_not_sent()

    def test_sms_2fa_enabled__whitelisted(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_SMS_2FA_ON: '1'},
            ),
        )
        self.fake_kolmogor.set_response_value('get', '0')
        with override_settings(ALLOW_SMS_2FA_IN_GT_PASSWORD_FOR_CLIENTS=[self.test_client.display_id]):
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_statbox_ok()

    def test_magnitola_ok(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                attributes={settings.BB_ATTR_APP_PASSWORDS_ON: '1'},
            ),
        )
        with override_settings(
            AM_CLIENT_ID=self.test_client.display_id,
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
            MAGNITOLA_APP_IDS=[TEST_MAGNITOLA_APP_ID],
        ):
            rv = self.make_request(
                app_id=TEST_MAGNITOLA_APP_ID,
            )
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok(authtype='magnitola')
        self.assert_antifraud_score_ok(app_id=TEST_MAGNITOLA_APP_ID)

    def test_magnitola_error__app_passwords_off(self):
        with override_settings(
            AM_CLIENT_ID=self.test_client.display_id,
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
            MAGNITOLA_APP_IDS=['magnitola_app_id'],
        ):
            rv = self.make_request(
                app_id='magnitola_app_id',
                expected_status=400,
            )
        self.assert_error(
            rv, error='invalid_grant',
            error_description='login or password is not valid',
        )
        self.assert_blackbox_ok(authtype='magnitola')
        self.assert_antifraud_score_not_sent()

    def test_validate_request_structure_by_client_id__ok(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=200,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=TEST_WHITELISTED_USER_AGENT,
                ),
                deviceid=TEST_DEVICE_ID,
                app_id='abc.def',
                app_id2='ABC.def',
            )
        self.assert_token_response_ok(rv)
        self.assert_statbox_ok()
        self.assert_antifraud_score_ok(
            user_agent=TEST_WHITELISTED_USER_AGENT,
            app_id='abc.def',
            deviceid=TEST_DEVICE_ID,
            device_id=TEST_DEVICE_ID,
        )

    def test_validate_request_structure_by_client_id_other_client_id__ok(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                '0189abef' * 4: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(expected_status=200)
        self.assert_token_response_ok(rv)
        self.assert_statbox_ok()

    def test_validate_request_structure_by_client_id__checks_ignored(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                app_id=TEST_MAGNITOLA_APP_ID,
            )
            self.assert_token_response_ok(rv)

    def test_validate_request_structure_by_client_id__no_required_fields(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    HTTP_HOST='oauth.yandex.ru',
                ),
            )
            self.assert_error(
                rv,
                error='unauthorized_client',
            )
            self.check_statbox(
                status='error',
                reason='request.invalid_fields',
                fields='deviceid:required,app_id:required,env.user_agent:required',
                user_entered_login=TEST_LOGIN,
            )
            self.assert_antifraud_score_not_sent()

    def test_validate_request_structure_by_client_id__no_required_field(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=TEST_WHITELISTED_USER_AGENT,
                ),
                deviceid=TEST_DEVICE_ID,
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='app_id:required',
            user_entered_login=TEST_LOGIN,
            device_id=TEST_DEVICE_ID,
            **{'env.user_agent': TEST_WHITELISTED_USER_AGENT}
        )
        self.assert_antifraud_log_error(
            reason='request.invalid_fields',
            device_id=TEST_DEVICE_ID,
            user_agent=TEST_WHITELISTED_USER_AGENT,
        )

    def test_validate_request_structure_by_client_id__wrong_re(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT='abad.bbbb',
                ),
                deviceid=TEST_DEVICE_ID,
                app_id='abc.def',
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='env.user_agent:re',
            user_entered_login=TEST_LOGIN,
            device_id=TEST_DEVICE_ID,
            app_id='abc.def',
            **{'env.user_agent': 'abad.bbbb'}
        )
        self.assert_antifraud_log_error(
            reason='request.invalid_fields',
            device_id=TEST_DEVICE_ID,
            user_agent='abad.bbbb',
        )

    def test_validate_request_structure_by_client_id__wrong_oneof(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=TEST_WHITELISTED_USER_AGENT,
                ),
                deviceid=TEST_DEVICE_ID,
                app_id='ABC.def',
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='app_id:value_in',
            user_entered_login=TEST_LOGIN,
            device_id=TEST_DEVICE_ID,
            app_id='ABC.def',
            **{'env.user_agent': TEST_WHITELISTED_USER_AGENT}
        )
        self.assert_antifraud_log_error(
            reason='request.invalid_fields',
            device_id=TEST_DEVICE_ID,
            user_agent=TEST_WHITELISTED_USER_AGENT,
        )

    def test_validate_request_structure_by_client_id__wrong_oneof_lower(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=TEST_WHITELISTED_USER_AGENT,
                ),
                deviceid=TEST_DEVICE_ID,
                app_id='abc.def',
                app_id2='abf.dec',
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='app_id2:value_in',
            user_entered_login=TEST_LOGIN,
            device_id=TEST_DEVICE_ID,
            app_id='abc.def',
            app_id2='abf.dec',
            **{'env.user_agent': TEST_WHITELISTED_USER_AGENT}
        )
        self.assert_antifraud_log_error(
            reason='request.invalid_fields',
            device_id=TEST_DEVICE_ID,
            user_agent=TEST_WHITELISTED_USER_AGENT,
        )

    def test_validate_request_structure_by_client_id__json_ua__wrong_re(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS_JSON,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT='Some.User.Agent',
                ),
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='env.user_agent:re',
            user_entered_login=TEST_LOGIN,
            **{'env.user_agent': 'Some.User.Agent'}
        )

    def test_validate_request_structure_by_client_id__json_ua__wrong_json(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS_JSON,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT='Some.UserAgent not_json',
                ),
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='env.user_agent::ua_json:json',
            user_entered_login=TEST_LOGIN,
            **{'env.user_agent': 'Some.UserAgent not_json'}
        )

    def test_validate_request_structure_by_client_id__json_ua__missing_json_fields(self):
        ua_value = 'Some.UserAgent {"os": "windows"}'
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS_JSON,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=ua_value,
                ),
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='env.user_agent::ua_json::vsn:required',
            user_entered_login=TEST_LOGIN,
            app_platform='windows',
            **{'env.user_agent': ua_value}
        )

    def test_validate_request_structure_by_client_id__json_ua__missing_json_fields__dry_run(self):
        ua_value = 'Some.UserAgent {"os": "windows"}'
        validators = deepcopy(TEST_TOKEN_REQUEST_VALIDATORS_JSON)
        validators['validators'][1]['experiment_denominator'] = 0
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: validators,
            },
        ):
            self.make_request(
                expected_status=200,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=ua_value,
                ),
            )
        self.check_statbox_entry(
            dict(
                status='warning',
                reason='request.invalid_fields',
                fields='env.user_agent::ua_json::vsn:required',
                user_entered_login=TEST_LOGIN,
                app_platform='windows',
                **{'env.user_agent': ua_value},
                **self.base_statbox_values(),
            ),
            entry_index=-2,
        )

    def test_validate_request_structure_by_client_id__json_ua__wrong_json_field_value(self):
        ua_value = 'Some.UserAgent {"os": [5, 3], "vsn": "1.2.3"}'
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS_JSON,
            },
        ):
            rv = self.make_request(
                expected_status=401,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=ua_value,
                ),
            )
        self.assert_error(
            rv,
            error='unauthorized_client',
        )
        self.check_statbox(
            status='error',
            reason='request.invalid_fields',
            fields='env.user_agent::ua_json::os:value_in',
            user_entered_login=TEST_LOGIN,
            app_platform='[5, 3]',
            app_version='1.2.3',
            **{'env.user_agent': ua_value}
        )

    def test_validate_request_structure_by_client_id__json_ua__ok(self):
        ua_value = 'Some.UserAgent {"os": "cli", "vsn": "1.2.3"}'
        with override_settings(
            GRANT_TYPE_PASSWORD_REQUEST_VALIDATORS_BY_CLIENT_ID={
                self.test_client.display_id: TEST_TOKEN_REQUEST_VALIDATORS_JSON,
            },
        ):
            self.make_request(
                expected_status=200,
                headers=dict(
                    self.default_headers(),
                    HTTP_USER_AGENT=ua_value,
                ),
            )
        self.assert_statbox_ok()

    def test_show_captcha_unsupported_country(self):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        with override_settings(GRANT_TYPE_PASSWORD_CAPTCHA_COUNTRIES={'UA', 'ET', 'CF'}):
            rv = self.make_request(expected_status=400)
        self.assert_error(
            rv, error='invalid_grant',
            error_description='login or password is not valid',
        )
        self.check_statbox(
            status='error',
            reason='captcha.unsupported_country',
            captcha_source='blackbox',
            **self.specific_statbox_values()
        )
        self.assert_antifraud_log_error(reason='captcha.unsupported_country')

    @parameterized.expand([(False,), (True,)])
    def test_show_captcha_unsupported_country_yandex_ip(self, is_server):
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(
                version=1,
                uid=self.uid,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        if is_server:
            ip_mock = self.is_yandex_server_ip_mock
        else:
            ip_mock = self.is_yandex_ip_mock
        ip_mock.return_value = True
        with override_settings(GRANT_TYPE_PASSWORD_CAPTCHA_COUNTRIES={'UA', 'ET', 'CF'}):
            rv = self.make_request(expected_status=403)
        self.assert_error(
            rv,
            error='403',
            error_description='CAPTCHA required',
            x_captcha_key='key',
            x_captcha_url='url',
        )
        self.check_statbox(
            status='error',
            reason='captcha.required',
            captcha_source='blackbox',
            **self.specific_statbox_values(login='test.user')
        )
        self.assert_antifraud_log_error(reason='captcha.required')

    def test_outdated_client_message(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_OUTDATED_CLIENTS={
                self.test_client.display_id, 'a' * 32,
            },
            OUTDATED_CLIENT_COUNTRIES_LANG_RU={'TJ', 'AZ'},
        ):
            rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='unauthorized_client',
            error_description=TEST_OUTDATED_CLIENT_MESSAGE,
        )
        self.check_statbox(status='error', reason='client.outdated')
        self.assert_antifraud_log_error(reason='client.outdated')

    def test_outdated_client_message_ru(self):
        with override_settings(
            GRANT_TYPE_PASSWORD_OUTDATED_CLIENTS={
                self.test_client.display_id, 'a' * 32,
            },
            OUTDATED_CLIENT_COUNTRIES_LANG_RU={'RU', 'TJ', 'AZ'},
        ):
            rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='unauthorized_client',
            error_description=TEST_OUTDATED_CLIENT_MESSAGE_RU,
        )
        self.check_statbox(status='error', reason='client.outdated')
        self.assert_antifraud_log_error(reason='client.outdated')

    def test_no_outdated_client_message_yandex_ip(self):
        self.is_yandex_ip_mock.return_value = True
        with override_settings(
            GRANT_TYPE_PASSWORD_OUTDATED_CLIENTS={
                self.test_client.display_id, 'a' * 32,
            },
            OUTDATED_CLIENT_COUNTRIES_LANG_RU={'RU', 'TJ', 'AZ'},
        ):
            self.make_request(expected_status=200)

    def test_no_outdated_client_message_yandex_server_ip(self):
        self.is_yandex_server_ip_mock.return_value = True
        with override_settings(
            GRANT_TYPE_PASSWORD_OUTDATED_CLIENTS={
                self.test_client.display_id, 'a' * 32,
            },
            OUTDATED_CLIENT_COUNTRIES_LANG_RU={'RU', 'TJ', 'AZ'},
        ):
            self.make_request(expected_status=200)

    def test_antifraud_score_disable__ok(self):
        with override_settings(ANTIFRAUD_SCORE_ENABLE=False):
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_score_not_sent()

    def test_antifraud_score_deny__error(self):
        deny_resp = antifraud_score_response(action=ScoreAction.DENY)
        dict_resp = json.loads(deny_resp)
        self.fake_antifraud_api.set_response_value('score', deny_resp)
        rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='invalid_grant',
            error_description='login or password is not valid'
        )
        self.assert_antifraud_score_ok()
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                status='error',
                reason='antifraud_score_deny',
                antifraud_action=str(ScoreAction.DENY),
                antifraud_reason=dict_resp['reason'],
                antifraud_tags='',
            ),
        )

    def test_antifraud_score_deny__dry_run__ok(self):
        deny_resp = antifraud_score_response(action=ScoreAction.DENY)
        dict_resp = json.loads(deny_resp)
        self.fake_antifraud_api.set_response_value('score', deny_resp)
        with override_settings(ANTIFRAUD_SCORE_DRY_RUN=True):
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_score_ok()
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                status='warning',
                reason='antifraud_score_deny',
                antifraud_action=str(ScoreAction.DENY),
                antifraud_reason=dict_resp['reason'],
                antifraud_tags='',
            ),
            entry_index=-2,
        )

    def test_antifraud_score__request_error__ok(self):
        self.fake_antifraud_api.set_response_side_effect('score', BaseAntifraudApiError())
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_score_ok()
