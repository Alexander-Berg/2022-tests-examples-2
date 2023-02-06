# -*- coding: utf-8 -*-
from time import time

from django.conf import settings
from django.test.utils import override_settings
from nose.tools import (
    assert_false,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox import (
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NEED_RESET_STATUS,
    BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
    BlackboxInvalidParamsError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
    CommonRateLimitsTests,
    TEST_IP,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ANOTHER_UID,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_UID,
)
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


TEST_COOKIE_HOST = 'passport.yandex.ru'
TEST_SESSIONID = '3:1111111'
TEST_SESSGUARD = '3:2222222'
TEST_AUTH_ID = '123:1422501443:126'


@override_settings(
    ALLOW_SKIP_SESSGUARD_FOR_LEGACY_GT_SESSIONID_USERS=False,
    REQUIRE_PASSPORT_HOST_FOR_XTOKEN_BY_GT_SESSIONID=True,
)
class TestIssueTokenBySessionId(BaseIssueTokenTestCase, CommonIssueTokenTests, CommonRateLimitsTests):
    grant_type = 'sessionid'

    def credentials(self):
        return {
            'sessionid': TEST_SESSIONID,
            'host': TEST_COOKIE_HOST,
        }

    def assert_blackbox_ok(self, sessguard=None, host=TEST_COOKIE_HOST):
        super(TestIssueTokenBySessionId, self).assert_blackbox_ok()

        expected_kwargs = {
            'method': 'sessionid',
            'sessionid': TEST_SESSIONID,
            'host': host,
            'userip': TEST_IP,
        }
        if sessguard:
            expected_kwargs['sessguard'] = sessguard
        self.fake_blackbox.requests[0].assert_query_contains(expected_kwargs)

    def assert_statbox_ok(self, **kwargs):
        kwargs.setdefault('all_cookies_passed', '0')
        kwargs.setdefault('old_authid', TEST_AUTH_ID)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            kwargs,
        )

    def specific_antifraud_values(self):
        return {
            'login_id': TEST_LOGIN_ID,
            'previous_login_id': TEST_LOGIN_ID,
        }

    def test_credentials_missing(self):
        # Оверрайдим тест из миксина: для кук отдаётся специфическая ошибка
        rv = self.make_request(expected_status=400, exclude=['host'])
        self.assert_error(rv, error='invalid_request', error_description='host not in POST')
        rv = self.make_request(expected_status=400, exclude=['sessionid'])
        self.assert_error(rv, error='invalid_request', error_description='Cookie header is missing')

    def test_ok_for_not_default_uid(self):
        rv = self.make_request(uid=TEST_ANOTHER_UID)
        self.assert_token_response_ok(rv, uid=TEST_ANOTHER_UID)
        self.assert_blackbox_ok()

    def test_ok_for_need_reset_cookie(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_NEED_RESET_STATUS,
                uid=self.uid,
                attributes={settings.BB_ATTR_GLOGOUT: 0},
                login_id=TEST_LOGIN_ID,
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()

    def test_ok_for_overridden_host(self):
        with override_settings(ALLOW_SKIP_SESSGUARD_FOR_LEGACY_GT_SESSIONID_USERS=True):
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok(host='yandex.ru')

    def test_ok_for_cookies_from_header(self):
        # настройка ни на что не влияет: хост не модифицируем
        with override_settings(ALLOW_SKIP_SESSGUARD_FOR_LEGACY_GT_SESSIONID_USERS=True):
            rv = self.make_request(
                exclude=['sessionid'],
                headers=dict(
                    self.default_headers(),
                    HTTP_COOKIE='Session_id=%s;sessguard=%s' % (TEST_SESSIONID, TEST_SESSGUARD),
                ),
            )
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok(sessguard=TEST_SESSGUARD)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok(all_cookies_passed='1')

    def test_cookies_both_in_header_and_params(self):
        rv = self.make_request(
            headers=dict(
                self.default_headers(),
                HTTP_COOKIE='foo=bar',
            ),
        )
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_ok_for_xtoken(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:xtoken')],
            redirect_uris=['https://callback'],
            default_title='xtoken app',
        )) as xtoken_client:
            pass

        rv = self.make_request(
            client_id=xtoken_client.display_id,
            client_secret=xtoken_client.secret,
        )
        self.assert_token_response_ok(rv)

    def test_xtoken_bad_host(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:xtoken')],
            redirect_uris=['https://callback'],
            default_title='xtoken app',
        )) as xtoken_client:
            pass

        rv = self.make_request(
            expected_status=400,
            client_id=xtoken_client.display_id,
            client_secret=xtoken_client.secret,
            host='yandex.ru',
        )
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='host.not_passport',
            client_id=xtoken_client.display_id,
            all_cookies_passed='0',
        )

    def test_xtoken_bad_host_but_allowed(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:xtoken')],
            redirect_uris=['https://callback'],
            default_title='xtoken app',
        )) as xtoken_client:
            pass

        with override_settings(REQUIRE_PASSPORT_HOST_FOR_XTOKEN_BY_GT_SESSIONID=False):
            rv = self.make_request(
                client_id=xtoken_client.display_id,
                client_secret=xtoken_client.secret,
                host='yandex.ru',
            )
        self.assert_token_response_ok(rv)

    def test_no_reuse_for_glogouted(self):
        token = issue_token(uid=self.uid, client=self.test_client, grant_type=self.grant_type, env=self.env)
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=self.uid,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
                aliases={'portal': TEST_LOGIN},
                login_id=TEST_LOGIN_ID,
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != token.access_token)

    def test_login_id_stored(self):
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)

    def test_uid_invalid(self):
        rv = self.make_request(uid='foo', expected_status=400)
        self.assert_error(rv, error='invalid_request', error_description='uid must be a number')

    def test_session_empty(self):
        rv = self.make_request(expected_status=400, sessionid='')
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='sessionid.empty',
            all_cookies_passed='0',
        )
        assert_false(self.fake_blackbox.requests)

    def test_blackbox_sessguard_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='sessguard.invalid',
            cookie_status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            all_cookies_passed='0',
        )

    def test_blackbox_session_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='sessionid.invalid',
            cookie_status=BLACKBOX_SESSIONID_INVALID_STATUS,
            all_cookies_passed='0',
        )

    def test_blackbox_user_session_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='sessionid.invalid',
            user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
            all_cookies_passed='0',
        )

    def test_blackbox_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Invalid parameters passed to Blackbox')
        self.check_statbox_last_entry(status='error', reason='blackbox_params.invalid', all_cookies_passed='0')

    def test_blackbox_session_expired(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_EXPIRED_STATUS,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Session not valid')
        self.check_statbox_last_entry(
            status='error',
            reason='sessionid.invalid',
            cookie_status=BLACKBOX_SESSIONID_EXPIRED_STATUS,
            all_cookies_passed='0',
        )

    def test_blackbox_user_not_in_session(self):
        rv = self.make_request(uid=42, expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Uid not in session')
        self.check_statbox_last_entry(
            status='error',
            reason='sessionid.no_uid',
            known_uids='%s,%s' % (TEST_UID, TEST_ANOTHER_UID),
            all_cookies_passed='0',
        )
        self.check_statbox_entry(
            {
                'mode': 'check_cookies',
                'host': TEST_COOKIE_HOST,
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            entry_index=0,
        )

    def test_blackbox_default_user_session_invalid_but_selected_is_glogouted(self):
        token = issue_token(uid=TEST_ANOTHER_UID, client=self.test_client, grant_type=self.grant_type, env=self.env)
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
                    login_id=TEST_LOGIN_ID,
                ),
                uid=TEST_ANOTHER_UID,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
                aliases={'portal': TEST_LOGIN},
            ),
        )
        rv = self.make_request(uid=TEST_ANOTHER_UID)
        self.assert_token_response_ok(rv, uid=TEST_ANOTHER_UID)
        ok_(rv['access_token'] != token.access_token)

    def test_rate_limit_exceeded_uid(self):
        self.fake_kolmogor.set_response_value('get', '2,3')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=429)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Too many requests',
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
        )
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)

    def test_rate_limit_exceeded_ip(self):
        self.fake_kolmogor.set_response_value('get', '3,2')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=429)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Too many requests',
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
        )
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
