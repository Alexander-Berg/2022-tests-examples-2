# -*- coding: utf-8 -*-
from datetime import datetime
from time import time

from django.conf import settings
from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.money_api import (
    MoneyApiUnknownSchemeError,
    PAYMENT_AUTH_SUCCEEDED_STATUS,
)
from passport.backend.core.builders.money_api.faker import (
    money_payment_api_auth_context_response,
    money_payment_api_error_response,
    TEST_AUTH_CONTEXT_ID,
    TEST_REDIRECT_URI,
    TEST_SCOPE_ADDENDUM,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.oauth.api.api.iface.utils import (
    client_to_response,
    scopes_to_response,
)
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
    CommonTokenTests,
    TEST_ANDROID_FINGERPRINT,
    TEST_ANDROID_PACKAGE_NAME,
    TEST_AUTHORIZATION,
    TEST_CODE_CHALLENGE,
    TEST_CYRILLIC_REDIRECT_URI,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_IDNA_ENCODED_REDIRECT_URI,
    TEST_IOS_APP_ID,
    TEST_PAYMENT_AUTH_RETPATH,
    TEST_PAYMENT_AUTH_SCHEME,
)
from passport.backend.oauth.core.db.client import ApprovalStatus
from passport.backend.oauth.core.db.eav import (
    DBIntegrityError,
    DBTemporaryError,
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.request import (
    CodeChallengeMethod,
    Request,
    REQUEST_CODE_GENERATION_RETRIES,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
    Token,
    TOKEN_TYPE_NORMAL,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_AVATAR_ID,
    TEST_DISPLAY_NAME,
    TEST_GRANT_TYPE,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_NORMALIZED_LOGIN,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.fake_configs import (
    mock_grants,
    mock_scope_grant,
)
from passport.backend.oauth.core.test.utils import (
    assert_params_in_tskv_log_entry,
    set_side_effect_errors,
)


@override_settings(
    ALLOW_ISSUE_TOKEN_FOR_INSECURE_REDIRECT_URI=False,
    ALLOW_INSECURE_URIS_FOR_CLIENTS_CREATED_BEFORE=datetime(2017, 1, 1),
    TURBO_APP_MAX_SCOPE_COUNT=2,
)
class TestAuthorize(BaseIfaceApiTestCase, CommonCookieTests, CommonTokenTests):
    http_method = 'POST'
    url_submit = reverse_lazy('iface_authorize_submit')
    url_get_state = reverse_lazy('iface_authorize_get_state')
    url_commit = reverse_lazy('iface_authorize_commit')

    default_url = url_submit

    def setUp(self):
        super(TestAuthorize, self).setUp()
        self.setup_blackbox_response()
        self.patch_ydb()
        self.setup_ydb_response(found=False)

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'uid': TEST_UID,
            'user_ip': TEST_USER_IP,
            'language': 'ru',
            'client_id': self.test_client.display_id,
            'response_type': 'token'
        }

    def setup_ydb_response(self, found=False):
        rows = []
        if found:
            rows.append({
                'host': 'test-host',
                'partner_id': 'test-partner-id',
                'allow_psuid': True,
            })
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet(rows)],
        )

    def test_token_ok(self):
        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )
        eq_(
            rv['client'],
            client_to_response(self.test_client),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, rv['redirect_uri'])
        ok_(not request.device_id)
        ok_(not request.device_name)

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)

        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_request',
                'status': 'ok',
                'reason': 'iface_authorize',
                'response_type': 'token',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'redirect_uri': 'https://callback',
                'token_request_id': request.display_id,
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'action': 'issue',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_id': str(token.id),
                'login_id': TEST_LOGIN_ID,
                'token_type': TOKEN_TYPE_NORMAL,
                'scopes': 'test:foo,test:bar',
                'grant_type': 'authorization_code',
                'create_time': str(token.created),
                'issue_time': str(token.issued),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
                'has_alias': '0',
                'password_passed': '0',
                'token_reused': '0',
            },
        ])
        self.check_historydb_event_entries([
            {
                'action': 'create',
                'target': 'token',
                'grant_type': 'authorization_code',
                'uid': str(TEST_UID),
                'token_id': str(token.id),
                'token_type': TOKEN_TYPE_NORMAL,
                'client_id': self.test_client.display_id,
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
                'has_alias': '0',
                'password_passed': '0',
            },
        ])
        self.check_credentials_entry({
            'client_id': self.test_client.display_id,
            'credential_type': 'token',
            'ip': TEST_USER_IP,
            'is_new': '1',
            'login': TEST_NORMALIZED_LOGIN,
            'region_id': '110357',
            'surface': 'oauth_authorization_code',
            'token_id': '1',
            'uid': str(TEST_UID),
            'uids_count': '1',
            'user_agent': 'curl',
            'yandexuid': 'yu',
        })

    def test_code_ok(self):
        rv = self.make_request(url=self.url_submit, response_type='code', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, rv['redirect_uri'])
        eq_(request.login_id, TEST_LOGIN_ID)

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('code' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_request',
                'status': 'ok',
                'reason': 'iface_authorize',
                'response_type': 'code',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'redirect_uri': 'https://callback',
                'token_request_id': request.display_id,
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_code',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_request_id': request.display_id,
                'code_strength': 'basic',
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        ])

    def test_ok_with_device_id(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.device_id, 'iFridge')
        eq_(request.device_name, 'My refrigerator')

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.device_id, TEST_DEVICE_ID)
        eq_(token.device_name, TEST_DEVICE_NAME)

        self.check_antifraud_entry({
            'channel': 'auth',
            'sub_channel': 'login',
            'external_id': 'req-request-id',
            'status': 'OK',
            'grant_type': 'authorization_code',
            'token_id': '1',
            'uid': str(TEST_UID),
            'client_id': self.test_client.display_id,
            'is_client_yandex': False,
            'device_id': TEST_DEVICE_ID,
            'scopes': ','.join(map(str, self.test_client.scopes)),
            'login_id': TEST_LOGIN_ID,
            'previous_login_id': TEST_LOGIN_ID,
            'password_passed': False,
            'is_app_password': False,
            'ip': TEST_USER_IP,
            'AS': 'AS15169',
            'user_agent': 'curl',
            'yandexuid': 'yu',
            'request': 'auth',
        })

    def test_ok_for_cyrillic_redirect_uri(self):
        # выдадим токен, чтобы не пропускать часть важных проверок в коде
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [TEST_CYRILLIC_REDIRECT_URI]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])
        eq_(rv['redirect_uri'], TEST_CYRILLIC_REDIRECT_URI)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, TEST_CYRILLIC_REDIRECT_URI)

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], TEST_CYRILLIC_REDIRECT_URI)

    def test_ok_for_idna_encoded_redirect_uri(self):
        # выдадим токен, чтобы не пропускать часть важных проверок в коде
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [TEST_IDNA_ENCODED_REDIRECT_URI]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
            redirect_uri=TEST_CYRILLIC_REDIRECT_URI,
        )
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])
        eq_(rv['redirect_uri'], TEST_CYRILLIC_REDIRECT_URI)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, TEST_CYRILLIC_REDIRECT_URI)

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], TEST_CYRILLIC_REDIRECT_URI)

    def test_scope_restricted_on_submit(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
            requested_scopes=['test:foo'],
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([Scope.by_keyword('test:foo')]),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.scopes, {Scope.by_keyword('test:foo')})

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        ok_('scope' not in rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo')})

    def test_scope_restricted_on_commit(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.scopes, self.test_client.scopes)

        rv = self.make_request(
            url=self.url_commit,
            request_id=request.display_id,
            granted_scopes='test:foo',
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        eq_(rv['scope'], 'test:foo')

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo')})

    def test_token_reuse(self):
        """Запрашиваются ранее выданные права"""
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_ok(rv)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(token_reused='1'),
        )

        self.check_credentials_entry({
            'client_id': self.test_client.display_id,
            'credential_type': 'token',
            'ip': TEST_USER_IP,
            'is_new': '0',
            'login': TEST_NORMALIZED_LOGIN,
            'region_id': '110357',
            'surface': 'oauth_authorization_code',
            'token_id': '1',
            'uid': str(TEST_UID),
            'uids_count': '1',
            'user_agent': 'curl',
            'yandexuid': 'yu',
        })

    def test_not_reusing_scopes_missing_from_client(self):
        """У токена как-то оказались права, отсуствующие у приложения"""
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        with UPDATE(self.test_client) as client:
            client.scope_ids = [Scope.by_keyword('test:foo').id]

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response(client.scopes),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_ok(rv)

    def test_no_token_reuse_after_revoking_tokens(self):
        token = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_TOKENS: int(time() + 5)},
        )
        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)

        ok_(rv['access_token'] != token.access_token)

    def test_verification_code_collizion_retries(self):
        rv = self.make_request(url=self.url_submit, response_type='code', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        set_side_effect_errors(
            get_dbm('oauthdbcentral').transaction,
            [DBIntegrityError for _ in range(REQUEST_CODE_GENERATION_RETRIES - 1)],
        )

        request_id = rv['request_id']
        rv = self.make_request(url=self.url_commit, request_id=request_id)
        self.assert_status_ok(rv)
        ok_(rv.get('code'))

        request = Request.by_display_id(request_id)
        ok_(request is not None)
        ok_(request.is_accepted)

    def test_verification_code_collizion_error(self):
        rv = self.make_request(url=self.url_submit, response_type='code', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        get_dbm('oauthdbcentral').transaction.side_effect = DBIntegrityError

        rv = self.make_request(url=self.url_commit, request_id=rv['request_id'])
        self.assert_status_error(rv, ['backend.failed'])

    def test_db_error(self):
        get_dbm('oauthdbcentral').transaction.side_effect = DBTemporaryError

        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['backend.failed'])

    def test_fallback_to_stateless_on_db_error(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError

        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
            ALLOW_FALLBACK_TO_STATELESS_TOKENS_FOR_NON_YANDEX_CLIENTS_AND_PUBLIC_GRANT_TYPES=True,
        ):
            rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)

    def test_no_fallback_to_stateless_on_db_error_for_non_yandex(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError

        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
        ):
            rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_error(rv, ['backend.failed'])

    def test_fallback_to_stateless_on_db_error_for_yandex(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError

        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
        ):
            rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('access_token' in rv)

    def test_unhandled_error(self):
        get_dbm('oauthdbcentral').execute.side_effect = ValueError('Some unexpected error')

        rv = self.make_request(url=self.url_submit, response_type='code', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['exception.unhandled'])

    def test_params_missing(self):
        rv = self.make_request(url=self.url_submit, exclude=['uid', 'client_id'])
        self.assert_status_error(rv, ['client_id.missing'])
        ok_('redirect_uri' not in rv)

    def test_secondary_params_invalid(self):
        rv = self.make_request(url=self.url_submit, device_id='foo', code_challenge='foo', requested_scopes='foo')
        self.assert_status_error(
            rv,
            ['device_id.too_short', 'code_challenge.too_short', 'requested_scopes.invalid'],
        )
        eq_(rv['redirect_uri'], self.test_client.default_redirect_uri)

    def test_client_not_found(self):
        rv = self.make_request(url=self.url_submit, response_type='token', client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_bad_karma_on_submit(self):
        self.setup_blackbox_response(karma=1100)
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_error(rv, ['access.denied'])
        ok_('request_id' not in rv)
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.karma',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_bad_karma_but_yandex_client_on_submit(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        self.setup_blackbox_response(karma=1100)
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_ok(rv)

    def test_is_child(self):
        self.setup_blackbox_response(is_child=True)
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_error(rv, ['account.is_child'])
        ok_('request_id' not in rv)
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.account_type',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_is_child_but_client_is_yandex(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        self.setup_blackbox_response(is_child=True)
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_ok(rv)

    def test_permission_denied_on_submit(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['password']),
        })
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_error(rv, ['access.denied'])
        ok_('request_id' not in rv)
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.grant_type',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_permission_denied_on_submit_scope_grant_type_ip_incorrect(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['authorization_code']),
            'test:foo/authorization_code': mock_scope_grant(networks=['127.0.0.1']),
        })
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_error(rv, ['access.denied'])
        ok_('request_id' not in rv)
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.ip',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_submit_ok_scope_grant_type_ip_correct(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['authorization_code']),
            'test:foo/authorization_code': mock_scope_grant(
                networks=[TEST_USER_IP],
            ),
        })
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, rv['redirect_uri'])
        ok_(not request.device_id)
        ok_(not request.device_name)

    def test_submit_ok_scope_grant_type_client_id_incorrect(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['authorization_code']),
            'test:foo/authorization_code': mock_scope_grant(
                networks=[TEST_USER_IP],
                client_ids=['wrong_client_id'],
            ),
        })
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
        )
        self.assert_status_error(rv, ['access.denied'])
        ok_('request_id' not in rv)
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.client_id',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_permission_denied_on_commit(self):
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)

        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['password']),
        })
        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_error(rv, ['access.denied'])
        ok_('access_token' not in rv)
        self.check_statbox_entry(
            {
                'mode': 'issue_token',
                'grant_type': 'authorization_code',
                'status': 'error',
                'reason': 'limited_by.grant_type',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        )

    def test_commit_request_expired(self):
        rv = self.make_request(url=self.url_commit, request_id='a' * 32)
        self.assert_status_error(rv, ['request.not_found'])
        ok_('access_token' not in rv)
        ok_('redirect_uri' not in rv)

    def test_commit_request_revoked(self):
        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)

        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_WEB_SESSIONS: int(time() + 5)},
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_error(rv, ['request.not_found'])
        ok_('access_token' not in rv)
        ok_('redirect_uri' not in rv)

    def test_commit_client_deleted(self):
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)

        with DELETE(self.test_client):
            pass
        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_error(rv, ['client.not_found'])
        ok_('access_token' not in rv)

    def test_no_redirect_uri(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = None
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['redirect_uri.not_registered'])
        ok_('redirect_uri' not in rv)

    def test_redirect_uri_not_matched(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            client_id=self.test_client.display_id,
            redirect_uri='http://foo.bar',
        )
        self.assert_status_error(rv, ['redirect_uri.not_matched'])
        ok_('redirect_uri' not in rv)

    def test_client_blocked(self):
        with UPDATE(self.test_client) as client:
            client.block()
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['client.blocked'])
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])

    def test_authorize_client_waiting_for_approval(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Pending
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['client.approval_pending'])
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])

    def test_client_approval_rejected(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Rejected
        rv = self.make_request(url=self.url_submit, response_type='token', client_id=self.test_client.display_id)
        self.assert_status_error(rv, ['client.approval_rejected'])
        eq_(self.test_client.redirect_uris[0], rv['redirect_uri'])

    def test_get_state_ok(self):
        rv = self.make_request(url=self.url_submit, response_type='code')
        self.assert_status_ok(rv)

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, rv['redirect_uri'])

        rv = self.make_request(url=self.url_get_state, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('code' not in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        eq_(rv['response_type'], 'code')

    def test_get_state_request_not_found(self):
        rv = self.make_request(url=self.url_get_state, request_id='a' * 32)
        self.assert_status_error(rv, ['request.not_found'])
        ok_('redirect_uri' not in rv)
        ok_('response_type' not in rv)

    def test_code_with_code_challenge_ok(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='code',
            client_id=self.test_client.display_id,
            code_challenge='a' * 43,
            code_challenge_method='S256',
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        request = Request.by_display_id(rv['request_id'])
        ok_(request is not None)
        eq_(request.redirect_uri, rv['redirect_uri'])
        eq_(request.code_challenge, 'a' * 43)
        eq_(request.code_challenge_method, CodeChallengeMethod.S256)

        rv = self.make_request(url=self.url_commit, request_id=request.display_id)
        self.assert_status_ok(rv)
        ok_('code' in rv)
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_request',
                'status': 'ok',
                'reason': 'iface_authorize',
                'response_type': 'code',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'redirect_uri': 'https://callback',
                'token_request_id': request.display_id,
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_code',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_request_id': request.display_id,
                'code_strength': 'basic',
                'code_challenge_method': 'S256',
                'scopes': 'test:foo,test:bar',
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        ])

    def test_token_reuse_and_extend_scopes(self):
        """Запрашиваются ранее выданные права плюс что-то ещё"""
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([Scope.by_keyword('test:bar')]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response([Scope.by_keyword('test:foo')]),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')})

    def test_token_reuse_and_append_scopes(self):
        """Дозапрашиваются новые права, пользователь их одобряет"""
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        rv = self.make_request(url=self.url_submit, response_type='token', requested_scopes=['test:bar'])
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([Scope.by_keyword('test:bar')]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response([Scope.by_keyword('test:foo')]),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            granted_scopes=['test:foo', 'test:bar'],
        )
        self.assert_status_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')})

    def test_token_reuse_optional_scopes_rejected(self):
        """Дозапрашиваются новые права, пользователь их отклоняет"""
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        rv = self.make_request(url=self.url_submit, response_type='token', requested_scopes=['test:bar'])
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([Scope.by_keyword('test:bar')]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response([Scope.by_keyword('test:foo')]),
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            granted_scopes=['test:foo'],
        )
        self.assert_status_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo')})

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_ios_integrational_ok(self):
        """В iOS SDK вместо куки приходит х-токен, а вместо произвольного redirect_uri - universal link"""
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = TEST_IOS_APP_ID

        universal_link = 'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=universal_link,
            app_platform='iOS',
            app_id=TEST_IOS_APP_ID.split('.', 1)[-1],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], universal_link)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=True)
    def test_ios_app_id_mismatch_dry_run(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = TEST_IOS_APP_ID

        universal_link = 'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=universal_link,
            app_platform='iOS',
            app_id='smth.ru.alien_app',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        self.check_statbox_entry(
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'warning',
                'error': 'app_id.not_matched',
                'passed_value': 'smth.ru.alien_app',
                'app_platform': 'ios',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
            entry_index=-2,
        )

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_ios_app_id_mismatch_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = TEST_IOS_APP_ID

        universal_link = 'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=universal_link,
            app_platform='iOS',
            app_id='smth.ru.alien_app',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['app_id.not_matched'])
        self.check_statbox_entries([
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'error',
                'error': 'app_id.not_matched',
                'passed_value': 'smth.ru.alien_app',
                'app_platform': 'ios',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
        ])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_ios_app_id_not_passed_ok(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = TEST_IOS_APP_ID

        universal_link = 'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=universal_link,
            app_platform='iOS',
            exclude=['app_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        self.check_statbox_entry(
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'no_data',
                'app_platform': 'ios',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
            entry_index=-2,
        )

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_android_integrational_ok(self):
        """
        В Android SDK вместо куки приходит х-токен, а вместо произвольного redirect_uri - app link
        """
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        app_link = 'https://yx%s.oauth.yandex.com/auth/finish?platform=android' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=app_link,
            app_platform='Android',
            app_id=TEST_ANDROID_PACKAGE_NAME,
            fingerprint=TEST_ANDROID_FINGERPRINT,
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], app_link)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_android_integrational_with_urlscheme_ok(self):
        """
        В Android SDK вместо куки приходит х-токен, а вместо произвольного redirect_uri -
        урл с кастомной схемой. При этом права приложению уже выданы, но подтверждение
        всё равно запрашивается.
        """
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        custom_scheme_url = 'yx%s:///auth/finish?platform=android' % self.test_client.display_id

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=custom_scheme_url,
            app_platform='Android',
            app_id=TEST_ANDROID_PACKAGE_NAME,
            fingerprint=TEST_ANDROID_FINGERPRINT,
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(rv['requested_scopes'], {})
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], custom_scheme_url)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=True)
    def test_android_app_id_mismatch_dry_run(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            app_platform='Android',
            app_id='package_name.other',
            fingerprint=TEST_ANDROID_FINGERPRINT,
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        self.check_statbox_entry(
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'warning',
                'error': 'app_id.not_matched',
                'passed_value': 'package_name.other',
                'app_platform': 'android',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
            entry_index=-2,
        )

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=True)
    def test_android_fingerprint_mismatch_dry_run(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            app_platform='Android',
            app_id=TEST_ANDROID_PACKAGE_NAME,
            fingerprint='some_other_stuff',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        self.check_statbox_entry(
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'warning',
                'error': 'fingerprint.not_matched',
                'passed_value': 'some_other_stuff',
                'app_platform': 'android',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
            entry_index=-2,
        )

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_android_app_id_mismatch_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            app_platform='Android',
            app_id='package_name.other',
            fingerprint=TEST_ANDROID_FINGERPRINT,
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['app_id.not_matched'])
        self.check_statbox_entries([
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'error',
                'error': 'app_id.not_matched',
                'passed_value': 'package_name.other',
                'app_platform': 'android',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
        ])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_android_fingerprint_mismatch_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            app_platform='Android',
            app_id=TEST_ANDROID_PACKAGE_NAME,
            fingerprint='some_other_stuff',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['fingerprint.not_matched'])
        self.check_statbox_entries([
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'error',
                'error': 'fingerprint.not_matched',
                'passed_value': 'some_other_stuff',
                'app_platform': 'android',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
        ])

    @override_settings(AUTH_SDK_PARAM_VALIDATION_DRY_RUN=False)
    def test_android_app_id_and_fingerprint_not_passed_ok(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_ANDROID_PACKAGE_NAME
            client.android_cert_fingerprints = [TEST_ANDROID_FINGERPRINT]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            app_platform='Android',
            exclude=['app_id', 'fingerprint'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        self.check_statbox_entry(
            {
                'mode': 'validate_auth_sdk_params',
                'status': 'no_data',
                'app_platform': 'android',
                'client_id': self.test_client.display_id,
                'client_creator': str(TEST_UID),
            },
            entry_index=-2,
        )

    def test_turboapp_integrational_ok(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )
        self.setup_ydb_response(found=True)

        scopes = {
            Scope.by_keyword('test:foo'),
            Scope.by_keyword('test:bar'),
            Scope.by_keyword('test:default_phone'),
        }

        with UPDATE(self.test_client) as client:
            client.turboapp_base_url = 'https://ozon.ru'
            client.set_scopes(scopes)

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:foo', 'test:default_phone'],
            redirect_uri='yandexta://ozon.ru/some/path',
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['client']['scopes'],
            scopes_to_response(
                [
                    Scope.by_keyword('test:foo'),
                    Scope.by_keyword('test:bar'),
                    Scope.by_keyword('test:default_phone'),
                ],
                group_to_one_fake_service=True,
            ),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response(
                [Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
                short=True,
                group_to_one_fake_service=True,
            ),
        )
        eq_(
            rv['requested_scopes'],
            scopes_to_response(
                [Scope.by_keyword('test:default_phone')],
                short=True,
                group_to_one_fake_service=True,
            ),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )

        eq_(len(self.fake_ydb.executed_queries()), 0)

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)
        eq_(rv['redirect_uri'], 'yandexta://ozon.ru/some/path')
        ok_('scope' not in rv)

        eq_(len(self.fake_ydb.executed_queries()), 1)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.scopes, scopes)  # в том числе есть и скоуп на получение номера телефона

    def test_turboapp_redirect_uri_not_trusted_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        redirect_uri = 'yandexta://ozon.ru'

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [redirect_uri]
            client.set_scopes({
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:default_phone'),
            })

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:foo', 'test:default_phone'],
            redirect_uri=redirect_uri,
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        eq_(rv['already_granted_scopes'], {})
        scopes_to_response(
            [
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:default_phone')
            ],
            short=True,
        ),

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_ok(rv)
        eq_(rv['scope'], 'test:foo')

        eq_(len(self.fake_ydb.executed_queries()), 1)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:foo')})  # телефонного скоупа нет

    def test_turboapp_no_redirect_uri_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        redirect_uri = 'yandexta://ozon.ru'

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [redirect_uri]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:foo'],
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['redirect_uri.missing'])

    def test_turboapp_no_scopes_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        redirect_uri = 'yandexta://ozon.ru'

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [redirect_uri]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            redirect_uri=redirect_uri,
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['requested_scopes.missing'])

    def test_turboapp_too_many_scopes_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        redirect_uri = 'yandexta://ozon.ru'

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [redirect_uri]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:foo', 'test:bar', 'test:premoderate'],
            redirect_uri=redirect_uri,
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['requested_scopes.too_many'])

    def test_turboapp_invalid_scopes_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                attributes={
                    'account.normalized_login': TEST_NORMALIZED_LOGIN,
                },
                scope='test:xtoken',
            ),
        )

        redirect_uri = 'yandexta://ozon.ru'

        with UPDATE(self.test_client) as client:
            client._redirect_uris = [redirect_uri]

        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:bar'],
            redirect_uri=redirect_uri,
            app_platform='Android',
            headers=self.default_headers(authorization=TEST_AUTHORIZATION),
        )
        self.assert_status_error(rv, ['requested_scopes.invalid'])

    def test_scope_expansion_prohibited_on_submit(self):
        rv = self.make_request(
            url=self.url_submit,
            response_type='token',
            requested_scopes=['test:foo', 'test:invisible'],
        )
        self.assert_status_error(rv, ['scopes.not_matched'])

    def test_scope_expansion_prohibited_on_commit(self):
        rv = self.make_request(url=self.url_submit, response_type='token', requested_scopes=['test:foo'])
        self.assert_status_ok(rv)

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
            granted_scopes=['test:foo', 'test:bar'],
        )
        self.assert_status_error(rv, ['scopes.not_matched'])

    def test_insecure_redirect_uri__code_ok(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://callback']

        rv = self.make_request(url=self.url_submit, response_type='code')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])

    def test_insecure_redirect_uri__code_and_pkce_error(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://callback']

        rv = self.make_request(
            url=self.url_submit,
            response_type='code',
            code_challenge=TEST_CODE_CHALLENGE,
            code_challenge_method='plain',
        )
        self.assert_status_error(rv, ['redirect_uri.insecure'])

    def test_insecure_redirect_uri__token_error(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://callback']

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_error(rv, ['redirect_uri.insecure'])

    def test_insecure_redirect_uri__token_for_old_client(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://callback']
            client.created = datetime(2016, 1, 1)

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])

    @override_settings(ALLOW_ISSUE_TOKEN_FOR_INSECURE_REDIRECT_URI=True)
    def test_insecure_redirect_uri__token_allowed_by_settings(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://callback']

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])

    def test_whitelisted_client__user_confirm_not_required(self):
        with override_settings(SKIP_USER_CONFIRM_FOR_CLIENTS=[self.test_client.display_id]):
            rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])

    def test_authsdk__confirm_always_required(self):
        # Хоть токен и есть, подтверждение запрашиваем всегда
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        rv = self.make_request(url=self.url_submit, response_type='token', app_platform='Android 20')
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])

    def test_payment_auth_params_missing(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)

        rv = self.make_request(
            url=self.url_commit,
            request_id=rv['request_id'],
        )
        self.assert_status_error(rv, ['payment_auth_retpath.missing'])

    def test_response_type_token_with_payment_auth__ok(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.required'])
        eq_(rv['payment_auth_context_id'], TEST_AUTH_CONTEXT_ID)
        eq_(rv['payment_auth_app_ids'], ['money.app.1', 'money.app.2'])
        eq_(rv['payment_auth_url'], TEST_REDIRECT_URI)

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(status=PAYMENT_AUTH_SUCCEEDED_STATUS, request_id=request_id),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.payment_auth_context_id, TEST_AUTH_CONTEXT_ID)
        eq_(token.payment_auth_scope_addendum, TEST_SCOPE_ADDENDUM)

    def test_response_type_code_with_payment_auth__ok(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='code')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.required'])
        eq_(rv['payment_auth_context_id'], TEST_AUTH_CONTEXT_ID)
        eq_(rv['payment_auth_app_ids'], ['money.app.1', 'money.app.2'])
        eq_(rv['payment_auth_url'], TEST_REDIRECT_URI)

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(status=PAYMENT_AUTH_SUCCEEDED_STATUS, request_id=request_id),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_ok(rv)
        ok_('code' in rv)

        request = Request.by_display_id(request_id)
        ok_(request is not None)
        eq_(request.payment_auth_context_id, TEST_AUTH_CONTEXT_ID)
        eq_(request.payment_auth_scope_addendum, TEST_SCOPE_ADDENDUM)

    def test_payment_auth_with_custom_scheme__ok(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token', payment_auth_scheme=TEST_PAYMENT_AUTH_SCHEME)
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.required'])

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(status=PAYMENT_AUTH_SUCCEEDED_STATUS, request_id=request_id),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_ok(rv)
        ok_('access_token' in rv)

        self.fake_money_api.get_requests_by_method('create_auth_context')[0].assert_query_equals({
            'scheme': TEST_PAYMENT_AUTH_SCHEME,
        })
        self.fake_money_api.get_requests_by_method('check_auth_context')[0].assert_query_equals({
            'authContextId': TEST_AUTH_CONTEXT_ID,
            'scheme': TEST_PAYMENT_AUTH_SCHEME,
        })

    def test_payment_auth_scheme_unknown(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token', payment_auth_scheme='foo')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        self.fake_money_api.set_response_side_effect(
            'create_auth_context',
            MoneyApiUnknownSchemeError(),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth_scheme.unknown'])

    def test_payment_auth_not_passed__bad_status(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.required'])

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(status='nothing_good', request_id=request_id),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.not_passed'])
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        eq_(rv['response_type'], 'token')

    def test_payment_auth_not_passed__bad_request_id(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.required'])

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(request_id='nothing_good'),
        )
        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['payment_auth.not_passed'])
        eq_(rv['redirect_uri'], self.test_client.redirect_uris[0])
        eq_(rv['response_type'], 'token')

    def test_money_api_failed(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(url=self.url_submit, response_type='token')
        self.assert_status_ok(rv)
        request_id = rv['request_id']

        self.fake_money_api.set_response_value(
            'create_auth_context',
            money_payment_api_error_response(),
            status=500,
        )

        rv = self.make_request(
            url=self.url_commit,
            request_id=request_id,
            payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH,
        )
        self.assert_status_error(rv, ['backend.failed'])

    def test_delete_code_in_redirect_uri(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['https://yandex.ru?code=123&test=test']

        rv = self.make_request(url=self.url_submit, response_type='code')
        self.assert_status_ok(rv)
        eq_(rv['redirect_uri'], 'https://yandex.ru?test=test')
