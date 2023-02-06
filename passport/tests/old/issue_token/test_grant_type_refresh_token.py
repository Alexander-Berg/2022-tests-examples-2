# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.conf import settings
from django.test.utils import override_settings
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_oauth_token_response,
    blackbox_oauth_response,
)
from passport.backend.oauth.api.api.old.error_descriptions import TOKEN_EXPIRED
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
    TIME_DELTA,
)
from passport.backend.oauth.core.db.eav import (
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
    TOKEN_TYPE_NORMAL,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN_ID,
    TEST_UID,
)
from passport.backend.oauth.core.test.db_utils import model_to_bb_response
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


TEST_STATELESS_TOKEN = 'state.less.signature'


@override_settings(
    MINIMAL_TTL_FOR_OPERATING=1,
    TOKEN_REFRESH_RATIO=0.2,
)
class TestIssueTokenByRefreshToken(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'refresh_token'

    def setUp(self):
        super(TestIssueTokenByRefreshToken, self).setUp()
        self.make_token_and_setup_blackbox()

    def make_token_and_setup_blackbox(self, token_age=30, device_id=None, device_name=None, meta=None, stateless=False,
                                      karma=0, is_child=False):
        self.token = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type='authorization_code',
            env=self.env,
            device_id=device_id,
            device_name=device_name,
            meta=meta,
            token_type=TOKEN_TYPE_STATELESS if stateless else TOKEN_TYPE_NORMAL,
        )
        if stateless:
            self.token.created = self.token.issued = datetime.now() - timedelta(seconds=token_age)
            self.token.expires = self.token.issued + timedelta(seconds=self.token.ttl or settings.DEFAULT_TOKEN_TTL)
        else:
            with UPDATE(self.token) as token:
                token.created = token.issued = datetime.now() - timedelta(seconds=token_age)
                token.expires = token.issued + timedelta(seconds=token.ttl) if token.ttl else None

        attributes = {}
        if is_child:
            attributes['account.is_child'] = '1'
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                client_id=self.test_client.display_id,
                scope=' '.join(map(str, self.token.scopes)),
                uid=self.token.uid,
                attributes=attributes,
                oauth_token_info={
                    'token_id': str(self.token.id),
                    'device_id': device_id or '',
                    'device_name': device_name or '',
                    'meta': meta or '',
                    'token_attributes': model_to_bb_response(self.token),
                },
                karma=karma,
            ),
        )
        self.statbox_handle_mock.reset_mock()

    def credentials(self):
        return {
            'refresh_token': self.token.refresh_token,
        }

    def assert_statbox_ok(self):
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(token_id=str(self.token.id)),
        )

    def test_limited_by_karma(self):
        # тест переопределен из базового класса, т.к. требуется особенный мок
        self.make_token_and_setup_blackbox(karma=1100)
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_is_child_error(self):
        # тест переопределен из базового класса, т.к. требуется особенный мок
        self.make_token_and_setup_blackbox(is_child=True)
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_ok_with_app_platform(self):
        # Оверрайдим тест из миксина
        # Для этого grant_type перезапись платформы невозможна, так как всегда выдаём существующий токен
        pass

    def test_on_limit_error(self):
        # Оверрайдим тест из миксина
        # Для этого grant_type переполнение невозможно, так как всегда выдаём существующий токен
        pass

    def test_ok_with_empty_scopes(self):
        # Оверрайдим тест из миксина
        # Тут всё равно вернётся непустой токен, так как всегда выдаём существующий токен
        pass

    def test_scope_subset_with_dupes_ok(self):
        # Оверрайдим тест из миксина
        # В отличие от остальных методов, проверим, что значение параметра scope игнорируется
        rv = self.make_request(scope='test:foo')
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()

    def test_db_error(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:ttl'),
            ])
            client.glogout()
        self.make_token_and_setup_blackbox(token_age=49)
        super(TestIssueTokenByRefreshToken, self).test_db_error()

    def test_fallback_to_stateless_on_db_error(self):
        # Оверрайдим тест из миксина
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:ttl'),
            ])
            client.glogout()
        self.make_token_and_setup_blackbox(token_age=49)

        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        with override_settings(
            ALLOW_FALLBACK_TO_STATELESS_TOKENS=True,
            ALLOW_FALLBACK_TO_STATELESS_TOKENS_FOR_NON_YANDEX_CLIENTS_AND_PUBLIC_GRANT_TYPES=True,
        ):
            rv = self.make_request(expected_status=503, decode_response=False)
        eq_(rv, 'Service temporarily unavailable')

    def test_ok_for_expirable_token(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:ttl'),
            ])
            client.glogout()
        self.make_token_and_setup_blackbox(token_age=49)
        super(TestIssueTokenByRefreshToken, self).test_ok_for_expirable_token()

    def test_refresh_token_empty(self):
        rv = self.make_request(refresh_token='', expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='expired_token')

    def test_refresh_token_invalid(self):
        rv = self.make_request(refresh_token='foo', expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='expired_token')

    def test_access_token_expired(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS, error=TOKEN_EXPIRED),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='expired_token')
        self.check_statbox(
            status='error',
            reason='refresh_token.invalid',
            bb_status=BLACKBOX_OAUTH_INVALID_STATUS,
            bb_error=TOKEN_EXPIRED,
        )

    def test_refresh_token_from_another_client(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                client_id='foo',
                scope=' '.join(map(str, self.token.scopes)),
                uid=self.token.uid,
                oauth_token_info={
                    'token_id': str(self.token.id),
                    'device_id': '',
                    'device_name': '',
                    'meta': '',
                },
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Token doesn\'t belong to client')
        self.check_statbox(
            status='error',
            reason='client.not_matched',
            token_id=str(self.token.id),
            refresh_token_client_id='foo',
        )

    def test_token_reused_but_not_updated(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:ttl')])
            client.glogout()  # отзываем старые токены
        self.make_token_and_setup_blackbox()
        # Проверим, что новый токен не выдаётся
        rv = self.make_request()
        self.assert_token_response_ok(rv, expire_time=30)
        eq_(rv['access_token'], self.token.access_token)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.access_token, self.token.access_token)
        eq_(token.device_id, '-')
        eq_(token.device_name, '')
        eq_(token.meta, '')
        # Проверим, что токен не подновляли
        self.assertAlmostEqual(
            token.expires,
            datetime.now() + timedelta(seconds=30),
            delta=TIME_DELTA,
        )

    def test_device_specific_token_reused_but_not_updated(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:ttl')])
            client.glogout()  # отзываем старые токены
        self.make_token_and_setup_blackbox(
            device_id='device_id',
            device_name='device_name',
            meta='meta',
        )
        # Проверим, что новый токен не выдаётся и поля токена не изменяются
        rv = self.make_request()
        self.assert_token_response_ok(rv, expire_time=30)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.access_token, self.token.access_token)
        eq_(token.device_id, 'device_id')
        eq_(token.device_name, 'device_name')
        eq_(token.meta, 'meta')
        # Проверим, что токен не подновляли
        self.assertAlmostEqual(
            token.expires,
            datetime.now() + timedelta(seconds=30),
            delta=TIME_DELTA,
        )

    def test_token_updated(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:ttl')])
            client.glogout()  # отзываем старые токены
        self.make_token_and_setup_blackbox(token_age=49)
        # Проверим, что токен подновился
        rv = self.make_request()
        self.assert_token_response_ok(rv, expire_time=60)
        eq_(rv['access_token'], self.token.access_token)
        token = Token.by_access_token(rv['access_token'])
        self.assertAlmostEqual(
            token.expires,
            datetime.now() + timedelta(seconds=60),
            delta=TIME_DELTA,
        )

    def test_ok_for_stateless_token(self):
        stateless_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
        )
        ok_(stateless_token.access_token != TEST_STATELESS_TOKEN)

        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                client_id=self.test_client.display_id,
                scope=' '.join(map(str, stateless_token.scopes)),
                uid=self.token.uid,
                oauth_token_info={
                    'token_id': str(stateless_token.id),
                    'device_id': '',
                    'device_name': '',
                    'meta': '',
                    'token_attributes': model_to_bb_response(stateless_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )
        self.fake_blackbox.set_response_value(
            'create_oauth_token',
            blackbox_create_oauth_token_response(
                access_token=TEST_STATELESS_TOKEN,
            ),
        )
        rv = self.make_request()
        eq_(rv['access_token'], TEST_STATELESS_TOKEN)

    def test_stateless_token_ok(self):
        self.make_token_and_setup_blackbox(stateless=True)
        super(TestIssueTokenByRefreshToken, self).test_stateless_token_ok()

    def test_stateless_token_for_special_client(self):
        self.make_token_and_setup_blackbox(stateless=True)
        super(TestIssueTokenByRefreshToken, self).test_stateless_token_for_special_client()
