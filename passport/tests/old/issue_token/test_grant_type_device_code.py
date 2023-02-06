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
    Request,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.test.base_test_data import TEST_UID


class TestIssueTokenByDeviceCode(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'device_code'

    def make_code(self):
        if not hasattr(self, 'request'):
            with CREATE(Request.create(
                uid=TEST_UID,
                client=self.test_client,
                is_token_response=True,
            )) as request:
                pass
            self.request = accept_request(request)
        return self.request.display_id

    def credentials(self):
        return {
            'code': self.make_code(),
        }

    def specific_statbox_values(self):
        return {
            'token_request_id': self.request.display_id,
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

    def test_client_id_mismatch(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=self.test_client.scopes,
            default_title='test_app_2',
        )) as other_client:
            pass

        rv = self.make_request(client_id=other_client.display_id, client_secret=other_client.secret, expected_status=400)
        self.assert_error(
            rv,
            error='invalid_grant',
            error_description='Code was issued for another client',
        )

    def test_scope_invalid(self):
        # Оверрайдим тест из миксина - тут он смысла не имеет
        pass

    def test_scope_not_matching(self):
        # Оверрайдим тест из миксина
        # Кейс недостижимый, но всё же проверим
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
        # Убедимся, что берутся скоупы из реквеста, а не из запроса
        self.make_code()
        with UPDATE(self.request):
            self.request.scope_ids = {Scope.by_keyword('test:foo').id}
        rv = self.make_request(scope='test:bar')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv, scopes='test:foo')
        self.assert_statbox_ok()

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
        self.assert_error(rv, error='invalid_grant', error_description='Code has expired')

    def test_code_not_found(self):
        rv = self.make_request(expected_status=400, code='1234567')
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
        self.assert_error(
            rv,
            error='authorization_pending',
            error_description='User has not yet authorized your application',
        )

    def test_wrong_uid_from_request(self):
        self.make_code()
        with UPDATE(self.request):
            self.request.uid = None
        rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='authorization_pending',
            error_description='User has not yet authorized your application',
        )

    def test_code_is_one_time(self):
        self.make_code()
        rv = self.make_request()
        self.assert_token_response_ok(rv)

        rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='authorization_pending',
            error_description='User has not yet authorized your application',
        )

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
