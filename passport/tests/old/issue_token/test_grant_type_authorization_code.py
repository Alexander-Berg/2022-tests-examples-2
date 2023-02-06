# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from django.conf import settings
from django.test.utils import override_settings
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    BaseDBError,
    CREATE,
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.request import (
    accept_request,
    ActivationStatus,
    CodeChallengeMethod,
    Request,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
    Token,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN_ID,
    TEST_UID,
)


TEST_CODE_VERIFIER = 'foo'
TEST_CODE_CHALLENGE = 'LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564'
TEST_CODE_VERIFIER_CYRILLIC = 'привет'
TEST_CODE_CHALLENGE_CYRILLIC = '5Y8ejFX6EFvdP0DlA36wsDm1mY1SwF5s2Yh43S2lyrI'


class TestIssueTokenByAuthorizationCode(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'authorization_code'

    def setUp(self):
        super(TestIssueTokenByAuthorizationCode, self).setUp()
        self.patch_ydb()
        self.setup_ydb_response(found=False)

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

    def make_code(self):
        if not hasattr(self, 'request'):
            with CREATE(Request.create(
                uid=TEST_UID,
                client=self.test_client,
                is_token_response=False,
            )) as request:
                pass
            self.request = accept_request(request)
        return self.request.code

    def credentials(self):
        return {
            'code': self.make_code(),
        }

    def specific_statbox_values(self):
        return {
            'token_request_id': self.request.display_id,
            'code_strength': 'basic',
        }

    def test_ok_with_device_id_from_request(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.device_id = 'iFridge'
            self.request.device_name = 'Мой холодильник'
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_log_ok(device_id='iFridge', device_name='Мой холодильник')

        tokens = list_tokens_by_uid(self.uid)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.access_token, rv['access_token'])
        eq_(token.device_id, 'iFridge')
        eq_(token.device_name, 'Мой холодильник')
        self.assert_antifraud_score_not_sent()

    def test_ok_with_login_id(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.login_id = TEST_LOGIN_ID
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_antifraud_log_ok(login_id=TEST_LOGIN_ID, previous_login_id=TEST_LOGIN_ID)

        token = Token.by_access_token(rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)

    def test_scope_invalid(self):
        # Оверрайдим тест из миксина - тут он смысла не имеет
        pass

    def test_ok_with_phone_scope(self):
        # Оверрайдим тест из миксина: в данном grant_type есть возможность получить токен с телефонным скоупом
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:default_phone'),
            ])

        self.make_code()
        with UPDATE(self.request):
            self.request.redirect_uri = 'yandexta://smth'

        self.setup_ydb_response(found=True)

        rv = self.make_request()
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv, scopes='test:foo,test:bar,test:default_phone')
        self.assert_statbox_ok()
        eq_(len(self.fake_ydb.executed_queries()), 1)

    def test_with_phone_scope__not_turboapp(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:default_phone'),
            ])

        self.make_code()
        with UPDATE(self.request):
            self.request.redirect_uri = 'https://smth'

        rv = self.make_request()
        self.assert_token_response_ok(rv, scopes='test:foo test:bar')
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        eq_(len(self.fake_ydb.executed_queries()), 0)

    def test_with_phone_scope__redirect_uri_not_trusted(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:default_phone'),
            ])

        self.make_code()
        with UPDATE(self.request):
            self.request.redirect_uri = 'yandexta://smth'

        self.setup_ydb_response(found=False)

        rv = self.make_request()
        self.assert_token_response_ok(rv, scopes='test:foo test:bar')
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        eq_(len(self.fake_ydb.executed_queries()), 1)

    def test_scope_not_matching(self):
        # Оверрайдим тест из миксина
        # кейс недостижимый, но всё же проверим
        self.make_code()
        with UPDATE(self.request):
            self.request.scope_ids = {Scope.by_keyword('test:ttl').id}
        rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='invalid_scope',
            error_description='Scopes of code and client do not match',
        )
        self.check_statbox(
            status='error',
            reason='scopes.not_match',
            scopes='{}'.format({'test:ttl'}),
            client_scopes='{}'.format(self.test_client.scopes),
            **self.specific_statbox_values()
        )

    def test_scope_subset_with_dupes_ok(self):
        # Оверрайдим тест из миксина
        # В частности, убедимся, что берутся скоупы из реквеста, а не из запроса
        self.make_code()
        with UPDATE(self.request):
            self.request.scope_ids = {Scope.by_keyword('test:foo').id}
        rv = self.make_request(scope='test:bar')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv, scopes='test:foo')
        self.assert_statbox_ok()

    def test_wrong_uid_from_request(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.uid = 0
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')
        self.check_statbox_last_entry(status='error', reason='user.not_found', **self.specific_statbox_values())

    def test_request_revoked(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=self.uid,
                attributes={settings.BB_ATTR_REVOKER_WEB_SESSIONS: time() + 10},
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')
        self.check_statbox_last_entry(status='error', reason='request.expired', **self.specific_statbox_values())

    def test_no_reuse_for_glogouted(self):
        token = issue_token(uid=self.uid, client=self.test_client, grant_type=self.grant_type, env=self.env)
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=self.uid,
                attributes={settings.BB_ATTR_REVOKER_TOKENS: time() + 10},
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != token.access_token)

    def test_code_invalid(self):
        rv = self.make_request(expected_status=400, code='foo')
        self.assert_error(rv, error='bad_verification_code', error_description='Invalid code')

    def test_code_not_found(self):
        rv = self.make_request(expected_status=400, code='1234567')
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_cyrillic_code_not_found(self):
        rv = self.make_request(expected_status=400, code='привет!')
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_code_expired(self):
        self.make_code()
        with UPDATE(self.request) as request:
            request.expires = datetime.now() - timedelta(days=1)
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_request_not_accepted(self):
        self.make_code()
        with UPDATE(self.request) as request:
            request.is_accepted = False
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_code_not_activated(self):
        self.make_code()
        with UPDATE(self.request) as request:
            request.activation_status = ActivationStatus.Pending
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code not activated')
        self.check_statbox_last_entry(status='error', reason='code.not_activated', **self.specific_statbox_values())

    def test_code_from_other_client(self):
        # Реквест ищется в том числе по client_id, поэтому тут мы ожидаем его не найти
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение 2',
        )) as other_client:
            pass
        rv = self.make_request(
            expected_status=400,
            client_id=other_client.display_id,
            client_secret=other_client.secret,
        )
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_code_is_one_time(self):
        self.make_code()
        rv = self.make_request()
        self.assert_token_response_ok(rv)

        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_failed_to_delete_request__code_is_not_one_time(self):
        self.make_code()
        db_result_mock = mock.Mock()
        db_result_mock.inserted_primary_key = [1]
        get_dbm('oauthdbcentral').transaction.side_effect = [
            [db_result_mock],  # успешная выдача токена
            BaseDBError,  # неуспешное удаление реквеста
        ]
        rv = self.make_request()
        self.assert_token_response_ok(rv)

        rv = self.make_request()
        self.assert_token_response_ok(rv)

    def test_code_challenge_plain_ok(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.code_challenge_method = CodeChallengeMethod.Plain
            self.request.code_challenge = TEST_CODE_VERIFIER
        rv = self.make_request(code_verifier=TEST_CODE_VERIFIER)
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_code_challenge_sha256_ok(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.code_challenge_method = CodeChallengeMethod.S256
            self.request.code_challenge = TEST_CODE_CHALLENGE
        rv = self.make_request(code_verifier=TEST_CODE_VERIFIER)
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_code_challenge_cyrillic_sha256_ok(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.code_challenge_method = CodeChallengeMethod.S256
            self.request.code_challenge = TEST_CODE_CHALLENGE_CYRILLIC
        rv = self.make_request(code_verifier=TEST_CODE_VERIFIER_CYRILLIC)
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_code_challenge_invalid(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.code_challenge_method = CodeChallengeMethod.S256
            self.request.code_challenge = TEST_CODE_CHALLENGE
        rv = self.make_request(expected_status=400, code_verifier='something-other')
        self.assert_error(rv, error='invalid_grant', error_description='code_verifier not matched')

    def test_code_challenge_not_required_but_passed(self):
        self.make_code()
        rv = self.make_request(expected_status=400, code_verifier=TEST_CODE_VERIFIER)
        self.assert_error(rv, error='invalid_grant', error_description='code_verifier not matched')

    def test_client_secret_not_required_for_pkce(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.code_challenge_method = CodeChallengeMethod.S256
            self.request.code_challenge = TEST_CODE_CHALLENGE
        rv = self.make_request(code_verifier=TEST_CODE_VERIFIER, exclude=['client_secret'])
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_account_type_forbidden__handicapped_account(self):
        for alias_type, alias in (
            ('phonish', 'phne-123'),
            ('mailish', 'admin@gmail.com'),
        ):
            self.fake_blackbox.set_response_value(
                'userinfo',
                blackbox_userinfo_response(
                    uid=self.uid,
                    aliases={alias_type: alias},
                ),
            )
            rv = self.make_request(expected_status=400)
            self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')
            self.check_statbox_last_entry(
                uid=str(TEST_UID),
                status='error',
                reason='account_type.forbidden',
                account_type=alias_type,
                **self.specific_statbox_values()
            )

    def test_stateless_token_ok(self):
        # оверрайдим тест родителя
        rv = self.make_request(x_stateless='yes')
        self.assert_token_response_ok(rv, is_stateless=False)
        self.assert_historydb_ok(rv, token_id=1)
        self.assert_statbox_ok()

    def test_stateless_token_for_special_client(self):
        # оверрайдим тест родителя
        self.fake_token_params.set_data({
            'force_stateless': {'rule1': {'client_id': self.test_client.display_id}},
        })
        rv = self.make_request()
        self.assert_token_response_ok(rv, is_stateless=False)
        self.assert_historydb_ok(rv, token_id=1)
        self.assert_statbox_ok()

    def test_no_fallback_to_stateless_on_db_error_for_non_yandex(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
            ALLOW_FALLBACK_TO_STATELESS_TOKENS_FOR_NON_YANDEX_CLIENTS_AND_PUBLIC_GRANT_TYPES=False,
        ):
            rv = self.make_request(expected_status=503, decode_response=False)
        eq_(rv, 'Service temporarily unavailable')

    def test_fallback_to_stateless_on_db_error_for_yandex(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
            ALLOW_FALLBACK_TO_STATELESS_TOKENS_FOR_NON_YANDEX_CLIENTS_AND_PUBLIC_GRANT_TYPES=False,
        ):
            rv = self.make_request()
        self.assert_token_response_ok(rv, is_stateless=True, expire_time=3600 * 24 * 365)
        self.assert_historydb_ok(rv, token_id=1, token_type=TOKEN_TYPE_STATELESS)
        self.assert_statbox_ok()
