# -*- coding: utf-8 -*-
import base64
from datetime import timedelta
import json

from django.test.utils import override_settings
from django.urls import reverse_lazy
from django.utils.encoding import smart_bytes
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.kolmogor import KolmogorTemporaryError
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.api.api.old.error_descriptions import TOKENS_LIMIT_EXCEEDED
from passport.backend.oauth.core.common.constants import (
    DROP,
    ERROR,
    GRANT_TYPE_CLIENT_CREDENTIALS,
    INVALID_REQUEST,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.device_info import AppPlatform
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    get_access_token_from_refresh_token,
    issue_token,
    list_tokens_by_uid,
    Token,
    TOKEN_TYPE_NORMAL,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.db.token.normal_token import get_max_tokens_per_uid_and_client
from passport.backend.oauth.core.test.base_test_data import (
    DELETED_SCOPE_ID,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_NORMALIZED_LOGIN,
    TEST_REMOTE_ADDR,
    TEST_UID,
)
from passport.backend.oauth.core.test.fake_configs import mock_scope_grant
from passport.backend.oauth.core.test.framework import ApiTestCase


TEST_IP = TEST_REMOTE_ADDR
TIME_DELTA = timedelta(seconds=5)


class BaseIssueTokenTestCase(ApiTestCase):
    default_url = reverse_lazy('token')
    http_method = 'POST'
    grant_type = None
    password_passed = False
    uid = TEST_UID

    def credentials(self):
        raise NotImplementedError()  # pragma: no cover

    def default_params(self):
        return dict(
            grant_type=self.grant_type,
            client_id=self.test_client.display_id,
            client_secret=self.test_client.secret,
            **self.credentials()
        )

    def base_statbox_values(self):
        return {
            'mode': 'issue_token',
            'grant_type': self.grant_type,
            'client_id': self.test_client.display_id,
            'user_ip': TEST_IP,
        }

    def specific_statbox_values(self):
        return {}  # pragma: no cover

    # FIXME: проверить все записываемые значения в статбокс
    def assert_statbox_ok(self):
        pass

    def base_antifraud_values(self):
        return {
            'channel': 'auth',
            'sub_channel': 'login',
            'external_id': 'req-request-id',
            'grant_type': self.grant_type,
            'client_id': self.test_client.display_id,
            'is_client_yandex': False,
            'scopes': ','.join(map(str, self.test_client.scopes)),
            'password_passed': True if self.password_passed else False,
            'is_app_password': False,
            'ip': TEST_IP,
            'AS': 'AS15169',
            'user_agent': 'curl',
            'request': 'auth',
        }

    def specific_antifraud_values(self):
        return {}  # pragma: no cover

    def assert_antifraud_log_ok(self, **kwargs):
        self.check_antifraud_entry({
            'status': 'OK',
            'token_id': '1',
            'uid': str(self.uid),
            **self.base_antifraud_values(),
            **self.specific_antifraud_values(),
            **kwargs,
        })

    def assert_antifraud_log_error(self, reason, **kwargs):
        self.check_antifraud_entry({
            'status': 'FAILED',
            'comment': reason,
            **self.base_antifraud_values(),
            **kwargs,
        })

    def assert_antifraud_score_ok(self, **kwargs):
        requests = self.fake_antifraud_api.get_requests_by_method('score')
        self.assertEqual(len(requests), 1)
        data = json.loads(requests[0].post_args)
        expected = {
            'channel': 'auth',
            'sub_channel': 'login',
            'request': 'auth',
            'grant_type': self.grant_type,
            'surface': 'oauth_' + self.grant_type,
            't': TimeNow(as_milliseconds=True),
            'user_ip': TEST_IP,
            'AS': 'AS15169',
            'user_agent': 'curl',
            'external_id': 'req-request-id',
            'uid': TEST_UID,
        }
        expected.update(kwargs)
        self.assertEqual(data, {k: v for k, v in expected.items() if v is not None})

    def assert_antifraud_score_not_sent(self):
        requests = self.fake_antifraud_api.get_requests_by_method('score')
        self.assertEqual(len(requests), 0)

    def base_credentials_log_values(self):
        return {
            'client_id': self.test_client.display_id,
            'credential_type': 'token',
            'ip': TEST_IP,
            'is_new': '1',
            'region_id': '110357',
            'surface': 'oauth_%s' % self.grant_type,
            'token_id': '1',
            'uid': str(self.uid),
            'uids_count': '1',
            'user_agent': 'curl',
        }

    def assert_credentials_log_ok(self, **kwargs):
        self.check_credentials_entry({
            **self.base_credentials_log_values(),
            **kwargs,
        })

    def check_statbox(self, **values):
        self.check_statbox_entries([dict(self.base_statbox_values(), **values)])

    def check_statbox_last_entry(self, **values):
        self.check_statbox_entry(dict(self.base_statbox_values(), **values), entry_index=-1)

    def assert_token_response_ok(self, rv, uid=None, expire_time=None, scopes=None, is_stateless=False):
        if is_stateless:
            ok_(rv['access_token'])  # больше проверять нечего
        else:
            tokens = list_tokens_by_uid(uid or self.uid)
            ok_(tokens)
            tokens_like_one_from_response = [
                token
                for token in tokens
                if rv['access_token'] == token.access_token
            ]
            eq_(len(tokens_like_one_from_response), 1)
            token = tokens_like_one_from_response[0]
            ok_(token)

        # Токен совпал - проверим остальные поля ответа
        eq_(rv['token_type'], 'bearer')

        if expire_time:
            self.assertAlmostEqual(rv['expires_in'], expire_time, delta=TIME_DELTA.seconds)
        else:
            ok_('expires_in' not in rv)

        if self.grant_type in ('password', 'sessionid', 'x-token'):  # уиды отдаются только в этих случаях
            eq_(rv['uid'], uid or self.uid)
        else:
            ok_('uid' not in rv)

        if self.grant_type in ('authorization_code', 'device_code', 'refresh_token'):  # refresh_token отдаётся только в этих случаях
            eq_(
                get_access_token_from_refresh_token(rv['refresh_token']),
                rv['access_token'],
            )
        else:
            ok_('refresh_token' not in rv)

        if scopes:
            eq_(rv['scope'], scopes)
        else:
            ok_('scope' not in rv)

        # Убедимся, что в ответе нет посторонних полей
        eq_(
            set(rv.keys()) - {'access_token', 'token_type', 'expires_in', 'uid', 'refresh_token', 'scope'},
            set(),
        )

    def assert_historydb_ok(self, rv, scopes=None, token_id=None, token_type=TOKEN_TYPE_NORMAL, password_passed=None):
        if token_id is None:
            tokens = list_tokens_by_uid(self.uid)
            token_id = [token.id for token in tokens if token.access_token == rv['access_token']][0]
        if password_passed is None:
            password_passed = self.password_passed
        self.check_historydb_event_entry(
            {
                'action': 'create',
                'target': 'token',
                'grant_type': self.grant_type,
                'uid': str(self.uid),
                'token_id': str(token_id),
                'token_type': token_type,
                'client_id': self.test_client.display_id,
                'scopes': scopes or 'test:foo,test:bar',
                'password_passed': '1' if password_passed else '0',
                'user_ip': TEST_IP,
                'consumer_ip': TEST_IP,
                'user_agent': 'curl',
                'has_alias': '0',
            },
            entry_index=-1,
        )

    def assert_blackbox_ok(self):
        eq_(len(self.fake_blackbox.requests), 1)

    def assert_error(self, rv, error, error_description=None, **kwargs):
        expected = dict(error=error, **kwargs)
        if error_description is not None:
            expected['error_description'] = error_description
        eq_(rv, expected)


class CommonRateLimitsTests(object):
    @staticmethod
    def override_rate_limit_settings(**kwargs):
        settings_ = dict(
            ENABLE_RATE_LIMITS=True,
            TOKEN_RATE_LIMIT_IP=2,
            TOKEN_RATE_LIMIT_CLIENT_ID=2,
            TOKEN_RATE_LIMIT_UID=2,
        )
        settings_.update(kwargs)
        return override_settings(**settings_)

    def test_ok_with_counters(self):
        self.fake_kolmogor.set_response_value('get', '2,2')
        with self.override_rate_limit_settings():
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 2)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('inc')), 1)

    def test_counters_unavailable_ok(self):
        self.fake_kolmogor.set_response_side_effect('get', KolmogorTemporaryError)
        self.fake_kolmogor.set_response_side_effect('inc', KolmogorTemporaryError)
        with self.override_rate_limit_settings():
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 4)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 2)  # 2 ретрая
        eq_(len(self.fake_kolmogor.get_requests_by_method('inc')), 2)  # 2 ретрая


class CommonIssueTokenTests(object):
    def _setup_all_blackbox_method_responses(self, **blackbox_kwargs):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(login_id=TEST_LOGIN_ID, **blackbox_kwargs),
        )
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**blackbox_kwargs),
        )
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(version=1, **blackbox_kwargs),
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        self.assert_antifraud_log_ok()

    def test_ok_with_header(self):
        rv = self.make_request(
            exclude=['client_id', 'client_secret'],
            headers=dict(
                self.default_headers(),
                HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(
                    smart_bytes('%s:%s' % (self.test_client.display_id, self.test_client.secret)),
                ).decode(),
            ),
        )
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_ok_with_scope(self):
        rv = self.make_request(scope=' '.join(s.keyword for s in self.test_client.scopes))
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_ok_with_phone_scope(self):
        # По умолчанию этот скоуп не отдаётся
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:default_phone'),
            ])
        rv = self.make_request()
        self.assert_token_response_ok(rv, scopes='test:foo test:bar')
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_ok_for_expirable_token(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:ttl')])
        rv = self.make_request(expected_status=200)
        self.assert_token_response_ok(rv, expire_time=60)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv, scopes='test:ttl')
        self.assert_statbox_ok()

    def test_ok_with_app_platform(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:xtoken')])
        rv = self.make_request(app_platform='Android 9 3/4')
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.app_platform, AppPlatform.Android)

    def test_bad_http_method(self):
        rv = self.make_request(http_method='GET', expected_status=405, decode_response=False)
        eq_(rv, '')

    def test_db_error(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        rv = self.make_request(expected_status=503, decode_response=False)
        eq_(rv, 'Service temporarily unavailable')

    def test_fallback_to_stateless_on_db_error(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
            ALLOW_FALLBACK_TO_STATELESS_TOKENS_FOR_NON_YANDEX_CLIENTS_AND_PUBLIC_GRANT_TYPES=True,
        ):
            rv = self.make_request()
        self.assert_token_response_ok(rv, is_stateless=True, expire_time=3600 * 24 * 365)
        self.assert_historydb_ok(rv, token_id=1, token_type=TOKEN_TYPE_STATELESS)
        self.assert_statbox_ok()

    def test_malformed_header(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={'HTTP_AUTHORIZATION': 'foo'},
        )
        self.assert_error(rv, error='Malformed Authorization header')

    def test_bad_header_type(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Intermediate %s' % base64.b64encode(
                    smart_bytes('%s:%s' % (self.test_client.display_id, self.test_client.secret)),
                ).decode(),
            },
        )
        self.assert_error(rv, error='Basic auth required')

    def test_bad_header_base64(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Basic foo',
            },
        )
        self.assert_error(rv, error='Malformed Authorization header')

    def test_bad_header_encoding(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Basic %s' % base64.b64encode(b'\xdd:').decode(),
            },
        )
        self.assert_error(rv, error='Malformed Authorization header')

    def test_bad_header_content(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Basic %s' % base64.b64encode(
                    self.test_client.display_id.encode(),
                ).decode(),
            },
        )
        self.assert_error(rv, error='Malformed Authorization header')

    def test_duplicate_post_parameter(self):
        rv = self.make_request(expected_status=400, client_id=['a' * 32, 'b' * 32])
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Duplicate POST parameter: client_id',
        )

    def test_grant_type_missing(self):
        rv = self.make_request(expected_status=400, exclude=['grant_type'])
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='grant_type not in POST',
        )

    def test_grant_type_invalid(self):
        rv = self.make_request(expected_status=400, grant_type='test')
        self.assert_error(
            rv,
            error='unsupported_grant_type',
            error_description='Unknown grant_type (must be \'authorization_code\')',
        )

    def test_client_id_missing(self):
        rv = self.make_request(expected_status=400, exclude=['client_id'])
        self.assert_error(rv, error='invalid_request', error_description='client_id not in POST')

    def test_client_id_invalid(self):
        rv = self.make_request(expected_status=400, client_id='foo')
        self.assert_error(rv, error='invalid_client', error_description='Client not found')

    def test_client_blocked(self):
        with UPDATE(self.test_client) as client:
            client.block()
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_client', error_description='Client blocked')

    def test_client_secret_missing(self):
        rv = self.make_request(expected_status=400, exclude=['client_secret'])
        self.assert_error(rv, error='invalid_client', error_description='Wrong client secret')

    def test_client_secret_invalid(self):
        rv = self.make_request(expected_status=400, client_secret='bar')
        self.assert_error(rv, error='invalid_client', error_description='Wrong client secret')

    def test_client_not_approved(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:premoderate')],
            default_title='Тестовое приложение',
        )) as client:
            self.test_client = client
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client', error_description='Client not approved')

    def test_scope_invalid(self):
        for scope in ('test:unknown', 'deleted:xtoken'):
            rv = self.make_request(expected_status=400, scope=scope)
            self.assert_error(rv, error='invalid_scope', error_description='err_scope not empty')
            self.check_statbox_last_entry(
                status='error',
                reason='scopes.invalid',
                requested_scopes=scope,
            )

    def test_scope_not_matching(self):
        rv = self.make_request(expected_status=400, scope='test:ttl')
        self.assert_error(
            rv,
            error='invalid_scope',
            error_description='Scope from POST does not match the client\'s one',
        )
        self.check_statbox(
            status='error',
            reason='scopes.not_match',
            scopes='{}'.format({'test:ttl'}),
            client_scopes='{}'.format(self.test_client.scopes),
        )

    def test_scope_subset_with_dupes_ok(self):
        rv = self.make_request(scope='test:foo test:foo')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv, scopes='test:foo')
        self.assert_statbox_ok()

    def test_device_id_invalid(self):
        rv = self.make_request(device_id='привет', expected_status=400)
        self.assert_error(rv, error='invalid_request', error_description='device_id is not valid')

    def test_credentials_missing(self):
        for key in self.credentials().keys():
            rv = self.make_request(expected_status=400, exclude=[key])
            self.assert_error(rv, error='invalid_request', error_description='%s not in POST' % key)

    def test_limited_by_grant_type__scope_limit(self):
        self.fake_grants.set_data({
            'test:foo': mock_scope_grant(grant_types=[]),
            'test:bar': mock_scope_grant(),
            'grant_type:assertion': mock_scope_grant(grant_types=['assertion']),
        })
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client')
        self.check_statbox_last_entry(status='error', reason='limited_by.grant_type')

    def test_limited_by_grant_type__grant_type_limit(self):
        self.fake_grants.set_data({
            'test:foo': mock_scope_grant(grant_types=[self.grant_type]),
            'test:bar': mock_scope_grant(),
            'grant_type:%s' % self.grant_type: mock_scope_grant(grant_types=[]),
        })
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client')
        self.check_statbox_last_entry(status='error', reason='limited_by.grant_type')

    def test_limited_by_client(self):
        self.fake_grants.set_data({
            'test:foo': mock_scope_grant(client_ids=['a' * 32]),
            'test:bar': mock_scope_grant(),
            'grant_type:assertion': mock_scope_grant(grant_types=['assertion']),
        })
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client')
        self.check_statbox_last_entry(status='error', reason='limited_by.client_id')

    def test_limited_by_ip(self):
        self.fake_grants.set_data({
            'test:foo': mock_scope_grant(networks=['8.8.8.8']),
            'test:bar': mock_scope_grant(),
            'grant_type:assertion': mock_scope_grant(grant_types=['assertion']),
        })
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client')
        self.check_statbox_last_entry(status='error', reason='limited_by.ip')

    def test_limited_by_karma(self):
        blackbox_kwargs = {
            'uid': TEST_UID,
            'aliases': {
                'portal': TEST_LOGIN,
            },
            'attributes': {
                'account.normalized_login': TEST_NORMALIZED_LOGIN,
            },
            'karma': 1100,
        }
        self._setup_all_blackbox_method_responses(**blackbox_kwargs)
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_ok_bad_karma_and_is_shared(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        blackbox_kwargs = {
            'uid': TEST_UID,
            'aliases': {
                'portal': TEST_LOGIN,
            },
            'attributes': {
                'account.normalized_login': TEST_NORMALIZED_LOGIN,
                'account.is_shared': '1',
            },
            'karma': 1100,
        }
        self._setup_all_blackbox_method_responses(**blackbox_kwargs)
        rv = self.make_request()
        self.assert_token_response_ok(rv)

    def test_is_child_error(self):
        blackbox_kwargs = {
            'uid': TEST_UID,
            'aliases': {
                'portal': TEST_LOGIN,
            },
            'attributes': {
                'account.normalized_login': TEST_NORMALIZED_LOGIN,
                'account.is_child': '1',
            },
        }
        self._setup_all_blackbox_method_responses(**blackbox_kwargs)
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_is_child_and_client_is_yandex_ok(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        blackbox_kwargs = {
            'uid': TEST_UID,
            'aliases': {
                'portal': TEST_LOGIN,
            },
            'attributes': {
                'account.normalized_login': TEST_NORMALIZED_LOGIN,
                'account.is_child': '1',
            },
        }
        self._setup_all_blackbox_method_responses(**blackbox_kwargs)
        rv = self.make_request()
        self.assert_token_response_ok(rv)

    def test_ok_with_empty_scopes(self):
        deleted_scope = Scope.by_id(DELETED_SCOPE_ID)  # получить по кейворду не можем - сами закрыли такую возможность
        ok_(deleted_scope.is_deleted)
        with UPDATE(self.test_client) as client:
            client.set_scopes([deleted_scope])
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.scopes, {Scope.by_keyword('test:basic_scope')})

    def test_limited_ok(self):
        mocked_grant = mock_scope_grant(
            grant_types=[self.grant_type],
            client_ids=[self.test_client.display_id],
            networks=[TEST_IP],
        )
        self.fake_grants.set_data({
            'grant_type:assertion': mocked_grant,
            'test:foo': mocked_grant,
            'test:bar': mocked_grant,
        })
        rv = self.make_request()
        self.assert_token_response_ok(rv)

    def test_on_limit_error(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count):
            issue_token(
                uid=self.uid,
                client=self.test_client,
                grant_type=self.grant_type,
                env=self.env,
                device_id='device_%s' % i,
                device_name='Name #%d' % i,
            )
        # c GRANT_TYPE_CLIENT_CREDENTIALS не кидаем такую ошибку
        if self.grant_type == GRANT_TYPE_CLIENT_CREDENTIALS:
            rv = self.make_request(
                on_limit=ERROR,
                device_id='device',
                device_name='Name',
            )
            self.assert_token_response_ok(rv)
            return
        rv = self.make_request(
            expected_status=400,
            on_limit=ERROR,
            device_id='device',
            device_name='Name',
        )
        self.assert_error(rv, error=INVALID_REQUEST, error_description=TOKENS_LIMIT_EXCEEDED)
        self.check_statbox_last_entry(
            status='warning',
            mode='issue_token',
            reason='limit.exceeded',
            grant_type=self.grant_type,
            uid=str(self.uid),
            client_id=str(self.test_client.display_id),
            limit=str(max_token_count),
            valid_token_count=str(max_token_count),
            total_token_count=str(max_token_count),
        )

    def test_on_limit_drop(self):
        for i in range(get_max_tokens_per_uid_and_client()):
            issue_token(
                uid=self.uid,
                client=self.test_client,
                grant_type=self.grant_type,
                env=self.env,
                device_id='device_%s' % i,
                device_name='Name #%d' % i,
            )
        rv = self.make_request(
            on_limit=DROP,
            device_id='device',
            device_name='Name',
        )
        self.assert_token_response_ok(rv)

    def test_external_client(self):
        # проверяем, что внешним приложениям запрещены непубличные grant_type, но разрешены остальные
        with override_settings(
            FORBID_NONPUBLIC_GRANT_TYPES=True,
        ):
            if self.grant_type in ['password', 'sessionid']:
                rv = self.make_request(expected_status=400)
                self.assert_error(rv, error='unauthorized_client')
                self.check_statbox_last_entry(
                    mode='issue_token_by_nonpublic_grant_type',
                    grant_type=self.grant_type,
                    client_id=self.test_client.display_id,
                    action='forbidden',
                    reason='other',
                    is_yandex_ip='0',
                )
                ok_(not self.fake_blackbox.requests)  # до ЧЯ дело не дошло
            else:
                rv = self.make_request()
                self.assert_token_response_ok(rv)
                self.assert_historydb_ok(rv)
                self.assert_statbox_ok()  # ничего лишнего не пишем

    def test_stateless_token_ok(self):
        rv = self.make_request(x_stateless='yes')
        self.assert_token_response_ok(rv, is_stateless=True, expire_time=3600 * 24 * 365)
        self.assert_historydb_ok(rv, token_id=1, token_type=TOKEN_TYPE_STATELESS)
        self.assert_statbox_ok()

    def test_not_stateless_token_because_of_param(self):
        rv = self.make_request(x_stateless='no')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_stateless_token_for_special_client(self):
        self.fake_token_params.set_data({
            'force_stateless': {'rule1': {'client_id': self.test_client.display_id}},
        })
        rv = self.make_request()
        self.assert_token_response_ok(rv, is_stateless=True, expire_time=3600 * 24 * 365)
        self.assert_historydb_ok(rv, token_id=1, token_type=TOKEN_TYPE_STATELESS)
        self.assert_statbox_ok()
