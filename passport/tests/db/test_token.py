# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import re
from time import time

from django.conf import settings
from django.test.utils import override_settings
import mock
from nose.tools import (
    assert_almost_equal,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_oauth_token_response,
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.oauth.core.common.blackbox import get_blackbox
from passport.backend.oauth.core.common.utils import from_base64_url
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBIntegrityError,
    DBTemporaryError,
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.attributes import (
    attr_by_name,
    VIRTUAL_ATTR_ENTITY_ID,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.eav.types import DB_NULL
from passport.backend.oauth.core.db.errors import (
    PaymentAuthNotPassedError,
    TokenLimitExceededError,
)
from passport.backend.oauth.core.db.schemas import TOKEN_VIRTUAL_ATTR_IS_STATELESS
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    delete_single_token,
    get_access_token_from_refresh_token,
    get_already_granted_scopes,
    invalidate_single_token,
    invalidate_tokens,
    issue_token,
    list_app_passwords,
    list_clients_by_user,
    list_tokens_by_uid,
    list_tokens_by_user_and_device,
    list_tokens_with_clients_by_user,
    parse_token,
    StatelessToken,
    Token,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.db.token.normal_token import get_max_tokens_per_uid_and_client
from passport.backend.oauth.core.env import Environment
from passport.backend.oauth.core.test.base_test_data import (
    TEST_CIPHER_KEYS,
    TEST_HOST,
)
from passport.backend.oauth.core.test.db_utils import model_to_bb_response
from passport.backend.oauth.core.test.framework.testcases import DBTestCase
from passport.backend.oauth.core.test.utils import (
    iter_eq,
    parse_tskv_log_entry,
)


TEST_UID = 1
TEST_IP = '1.2.3.4'
TEST_STATELESS_TOKEN = 'state.less.signature'
TEST_STATELESS_TOKEN_MASKED = 'state.less.*'
TEST_DEVICE_ID = 'dev-id'
TEST_DEVICE_NAME = 'dev-name'

TIME_DELTA = timedelta(seconds=5)


@override_settings(FORBID_NONPUBLIC_GRANT_TYPES=False)
class BaseTokenTestCase(DBTestCase):
    def setUp(self):
        super(BaseTokenTestCase, self).setUp()

        self.env = Environment(
            user_ip=TEST_IP,
            consumer_ip=TEST_IP,
            user_agent=None,
            raw_cookies=None,
            cookies={},
            host=TEST_HOST,
            request_id=None,
            authorization=None,
            service_ticket=None,
            user_ticket=None,
        )

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Test client',
        )) as client:
            self.test_client = client

        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 2)  # auto_id, атрибуты
        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        self.fake_db.reset_mocks()

        self.token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta',
        )

        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # auto_id для нового токена
        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # поиск существующего токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # выдача токена (атрибуты)

        with UPDATE(self.token) as token:
            token.created = token.issued = datetime.now() - timedelta(seconds=120)
        self.fake_db.reset_mocks()


class TestTokenCommon(BaseTokenTestCase):
    def test_ttl(self):
        with UPDATE(self.token):
            self.token.expires = datetime.now() + timedelta(seconds=10, milliseconds=500)
        ok_(isinstance(self.token.ttl, int))
        ok_(not self.token.is_expired)

    def test_is_invalidated_by_client_glogout(self):
        ok_(not self.token.is_invalidated_by_client_glogout(self.test_client))
        ok_(self.token.is_valid(self.test_client, revoke_time=None))

        self.test_client.glogout()
        ok_(self.token.is_invalidated_by_client_glogout(self.test_client))
        ok_(not self.token.is_valid(self.test_client, revoke_time=None))

    @raises(ValueError)
    def test_is_invalidated_by_client_glogout_bad_client(self):
        self.token.is_invalidated_by_client_glogout(Client(entity_id=42))

    def test_invalidate_tokens(self):
        invalidate_tokens([self.token], self.test_client, self.env, reason=None)
        ok_(all(token.is_expired for token in list_tokens_by_uid(TEST_UID)))

    def test_invalidate_single_token(self):
        invalidate_single_token(self.token, self.test_client, self.env, reason=None)
        ok_(all(token.is_expired for token in list_tokens_by_uid(TEST_UID)))

    def test_delete_token(self):
        delete_single_token(self.token, self.test_client, self.env, reason=None)
        eq_(list_tokens_by_uid(TEST_UID), [])

    def test_clients_by_user(self):
        with DELETE(self.test_client):
            pass

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='Test client 2',
        )) as other_client:
            pass

        issue_token(
            uid=TEST_UID,
            client=other_client,
            grant_type='password',
            env=self.env,
            device_id=None,
        )
        iter_eq(
            [client.id for client in list_clients_by_user(TEST_UID)],
            [other_client.id],
        )

    def test_clients_by_user_for_glogouted(self):
        iter_eq(
            list_clients_by_user(TEST_UID, tokens_revoked_at=datetime.now() + timedelta(seconds=10)),
            [],
        )

    def test_tokens_with_clients_by_user(self):
        with DELETE(self.test_client):
            pass

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='Test client 2',
        )) as other_client:
            pass

        other_token = issue_token(
            uid=TEST_UID,
            client=other_client,
            grant_type='password',
            env=self.env,
            device_id=None,
        )
        iter_eq(
            list_tokens_with_clients_by_user(TEST_UID),
            [
                (other_token, other_client, True),
            ],
        )

    def test_tokens_with_clients_by_user_for_glogouted(self):
        iter_eq(
            list_tokens_with_clients_by_user(TEST_UID, tokens_revoked_at=datetime.now() + timedelta(seconds=10)),
            [
                (self.token, self.test_client, False),
            ],
        )

    def test_tokens_with_clients_by_user_for_deleted_clients(self):
        with DELETE(self.test_client):
            pass

        iter_eq(
            list_tokens_with_clients_by_user(TEST_UID, omit_deleted_clients=False),
            [
                (self.token, None, False),
            ],
        )

    def test_count_app_passwords_ok(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='Test client 2',
        )) as other_client:
            pass

        app_password_1 = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='1',
            make_alias=True,
        )
        app_password_2 = issue_token(
            uid=TEST_UID,
            client=other_client,
            grant_type='password',
            env=self.env,
            device_id='2',
            make_alias=True,
        )
        iter_eq(
            list_app_passwords(TEST_UID),
            [
                (app_password_1, self.test_client),
                (app_password_2, other_client),
            ],
        )

    def test_count_app_passwords_glogouted(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='1',
            make_alias=True,
        )
        eq_(
            list_app_passwords(
                TEST_UID,
                revoked_at=datetime.now() + timedelta(seconds=20),
            ),
            [],
        )

    def test_tokens_by_user_and_device_ok(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='Test client 2',
        )) as other_client:
            pass

        token1 = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='1',
        )
        app_password1 = issue_token(
            uid=TEST_UID,
            client=other_client,
            grant_type='password',
            env=self.env,
            device_id='1',
            make_alias=True,
        )
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='2',
        )
        iter_eq(
            list_tokens_by_user_and_device(TEST_UID, device_id=1),
            [
                (token1, self.test_client),
                (app_password1, other_client),
            ],
        )

    def test_tokens_by_user_and_device_glogouted(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='1',
        )
        eq_(
            list_tokens_by_user_and_device(
                TEST_UID,
                device_id=1,
                revoked_at=datetime.now() + timedelta(seconds=20),
            ),
            [],
        )


class TestTokenParse(BaseTokenTestCase):
    def setUp(self):
        super(TestTokenParse, self).setUp()
        self.fake_blackbox = FakeBlackbox()
        self._apply_patches({
            'blackbox': self.fake_blackbox,
        })

    @staticmethod
    def attr_type(attr_name):
        attr_type_, _ = attr_by_name('token', attr_name)
        return str(attr_type_)

    def test_ok_normal_synthetic(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'token_attributes': {
                    self.attr_type('access_token'): 'access_token*',
                    self.attr_type('scope_ids'): '|%s|' % Scope.by_keyword('test:foo').id,
                    self.attr_type('uid'): str(TEST_UID),
                    self.attr_type('client_id'): str(self.test_client.id),
                    self.attr_type('device_id'): DB_NULL,
                    self.attr_type('created'): str(int(time())),
                    self.attr_type('meta'): 'meta*',
                    str(VIRTUAL_ATTR_ENTITY_ID): '123',
                },
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        token = parse_token(bb_response)
        ok_(isinstance(token, Token))
        eq_(token.id, 123)
        eq_(token.access_token, 'access_token*')
        eq_(token.scopes, {Scope.by_keyword('test:foo')})
        eq_(token.uid, TEST_UID)
        eq_(token.get_client().display_id, self.test_client.display_id)
        eq_(token.device_id, DB_NULL)
        eq_(token.created, DatetimeNow())
        eq_(token.meta, 'meta*')

    def test_ok_normal_existing(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'token_attributes': model_to_bb_response(self.token),
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        parsed_token = parse_token(bb_response)
        ok_(isinstance(parsed_token, Token))
        eq_(parsed_token, self.token)

    def test_ok_stateless_synthetic(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'token_attributes': {
                    self.attr_type('access_token'): 'access_token*',
                    self.attr_type('scope_ids'): '|%s|' % Scope.by_keyword('test:foo').id,
                    self.attr_type('uid'): str(TEST_UID),
                    self.attr_type('client_id'): str(self.test_client.id),
                    self.attr_type('device_id'): DB_NULL,
                    self.attr_type('created'): str(int(time())),
                    self.attr_type('meta'): 'meta*',
                    str(VIRTUAL_ATTR_ENTITY_ID): '123',
                    str(TOKEN_VIRTUAL_ATTR_IS_STATELESS): '1',
                },
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        token = parse_token(bb_response)
        ok_(isinstance(token, StatelessToken))
        eq_(token.id, 123)
        eq_(token.access_token, 'access_token*')
        eq_(token.scopes, {Scope.by_keyword('test:foo')})
        eq_(token.uid, TEST_UID)
        eq_(token.get_client().display_id, self.test_client.display_id)
        eq_(token.device_id, DB_NULL)
        eq_(token.created, DatetimeNow())
        eq_(token.meta, 'meta*')

    def test_ok_stateless_existing(self):
        self.fake_blackbox.set_response_value(
            'create_oauth_token',
            blackbox_create_oauth_token_response(
                access_token=TEST_STATELESS_TOKEN,
            ),
        )
        stateless_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
        )

        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'token_attributes': model_to_bb_response(
                    stateless_token,
                ),
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        parsed_token = parse_token(bb_response)
        ok_(isinstance(parsed_token, StatelessToken))
        eq_(parsed_token, stateless_token)


@override_settings(
    TOKEN_41_BYTE_FORMAT=False,
    REFRESH_TOKEN_GENERATION_KEYS=TEST_CIPHER_KEYS
    )
class TestRefreshDeprecatedTokens(BaseTokenTestCase):
    def test_refresh_token_ok(self):
        eq_(
            len(self.token.access_token),
            39,
        )
        eq_(
            len(self.token.refresh_token),
            94,
        )


@override_settings(
    TOKEN_41_BYTE_FORMAT=True,
    REFRESH_TOKEN_GENERATION_KEYS=TEST_CIPHER_KEYS
    )
class TestRefreshTokens(BaseTokenTestCase):
    def test_refresh_token_ok(self):
        eq_(
            len(self.token.access_token),
            58,
        )
        eq_(
            len(self.token.refresh_token),
            120,
        )

    def test_refresh_token__unavailable_for_app_passwords(self):
        self.token.alias = 'alias'
        with assert_raises(ValueError):
            self.token.refresh_token

    def test_refresh_token__unavailable_for_tokens_wo_uid(self):
        self.token.uid = None
        with assert_raises(ValueError):
            self.token.refresh_token

    def test_get_token_from_refresh_token__ok(self):
        eq_(
            get_access_token_from_refresh_token(self.token.refresh_token),
            self.token.access_token,
        )

    def test_get_access_token_from_refresh_token__decrypt_failed(self):
        ok_(get_access_token_from_refresh_token('foo') is None)


@override_settings(
    MINIMAL_TIME_BETWEEN_TOKEN_UPDATING=60,
    MINIMAL_TTL_FOR_OPERATING=5,
    TOKEN_REFRESH_RATIO=0.5,
)
class TestTokenIssue(BaseTokenTestCase):
    def test_ok(self):
        ok_(not self.token.has_xtoken_grant)
        ok_(self.token.ttl is None)
        ok_(not self.token.can_be_refreshed)

        eq_(list_tokens_by_uid(TEST_UID), [self.token])

    def test_ok_without_optional_params(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
        )
        ok_(not token.has_xtoken_grant)
        ok_(token.ttl is None)
        ok_(not token.can_be_refreshed)
        eq_(len(list_tokens_by_uid(TEST_UID)), 1)

    def test_reuse(self):
        eq_(self.token.meta, 'meta')

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta2',
        )
        eq_(self.token.access_token, new_token.access_token)
        eq_(new_token.meta, 'meta2')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # reuse токена
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        eq_(list_tokens_by_uid(TEST_UID), [new_token])

    @raises(DBTemporaryError)
    def test_reuse_db_failed_error(self):
        eq_(self.token.meta, 'meta')

        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta2',
        )

    def test_reuse_no_vital_changes_db_failed(self):
        eq_(self.token.meta, 'meta')

        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta',  # meta не изменилась
        )
        eq_(self.token, new_token)

    def test_reuse_too_frequent_no_db_write(self):
        eq_(self.token.meta, 'meta')
        with UPDATE(self.token) as token:
            token.issued = datetime.now() - timedelta(seconds=20)
        self.fake_db.reset_mocks()

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta',  # meta не изменилась
        )
        eq_(self.token, new_token)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)  # в шард и не пытались писать

    def test_reuse_disallowed(self):
        eq_(self.token.meta, 'meta')

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta2',
            allow_reuse=False,
        )
        ok_(self.token.id != new_token.id)
        ok_(self.token.access_token != new_token.access_token)
        eq_(new_token.meta, 'meta2')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение старого токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 2)  # удаление старого токена, выдача нового
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # id для нового токена

        eq_(list_tokens_by_uid(TEST_UID), [new_token])

    def test_no_reuse_for_expired(self):
        eq_(self.token.meta, 'meta')
        with UPDATE(self.token):
            self.token.expires = datetime.now() - timedelta(seconds=10)
        self.fake_db.reset_mocks()

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta2',
        )
        ok_(new_token.id > self.token.id)
        ok_(new_token.access_token != self.token.access_token)
        eq_(new_token.meta, 'meta2')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 2)  # удаление старого токена, выдача нового
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # id для нового токена

        eq_(list_tokens_by_uid(TEST_UID), [new_token])

    def test_no_reuse_for_glogouted(self):
        eq_(self.token.meta, 'meta')

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id=None,
            meta='meta2',
            tokens_revoked_at=datetime.now() + timedelta(seconds=10),
        )
        ok_(new_token.id > self.token.id)
        ok_(new_token.access_token != self.token.access_token)
        eq_(new_token.meta, 'meta2')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 2)  # удаление старого токена, выдача нового
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # id для нового токена

        eq_(list_tokens_by_uid(TEST_UID), [new_token])

    def test_refresh_ok(self):
        with UPDATE(self.token):
            self.token.set_scopes([Scope.by_keyword('test:ttl')])
            self.token.expires = datetime.now() + timedelta(seconds=29)
        self.fake_db.reset_mocks()
        with UPDATE(self.token) as token:
            token.try_refresh()

        self.assertAlmostEqual(
            token.expires,
            datetime.now() + timedelta(seconds=60),
            delta=TIME_DELTA,
        )

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # подновление токена
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

    def test_refresh_not_required(self):
        with UPDATE(self.token):
            self.token.set_scopes([Scope.by_keyword('test:ttl')])
            self.token.expires = datetime.now() + timedelta(seconds=31)
        self.fake_db.reset_mocks()
        with UPDATE(self.token) as token:
            token.try_refresh()

        self.assertAlmostEqual(
            token.expires,
            datetime.now() + timedelta(seconds=31),
            delta=TIME_DELTA,
        )

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

    def test_payment_auth_not_passed(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('money:all')],
            default_title='test money app',
        )) as test_client:
            pass

        with assert_raises(PaymentAuthNotPassedError):
            issue_token(
                uid=TEST_UID,
                client=test_client,
                grant_type='password',
                env=self.env,
            )

    def test_payment_auth_passed_ok(self):
        with CREATE(Client.create(
                uid=TEST_UID,
                scopes=[Scope.by_keyword('money:all')],
                default_title='test money app',
        )) as test_client:
            pass

        token = issue_token(
            uid=TEST_UID,
            client=test_client,
            grant_type='password',
            env=self.env,
            payment_auth_context_id='context_id',
            payment_auth_scope_addendum='addendum',
        )
        eq_(token.payment_auth_context_id, 'context_id')
        eq_(token.payment_auth_scope_addendum, 'addendum')


@override_settings(TOKEN_41_BYTE_FORMAT=False)
class TestDeprecatedTokenIssueMulti(BaseTokenTestCase):
    def setUp(self):
        super(TestDeprecatedTokenIssueMulti, self).setUp()
        self.device_specific_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-uniq-id',
            device_name='iFridge',
            meta='meta',
        )
        self.fake_db.reset_mocks()

    def test_ok(self):
        eq_(len(self.token.access_token), 39)
        eq_(
            from_base64_url(self.token.access_token.encode())[:13],
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01',
        )
        eq_(self.token.masked_body, self.token.access_token[:19] + '*' * 20)


@override_settings(
    MINIMAL_TIME_BETWEEN_TOKEN_UPDATING=60,
    MAX_TOKENS_TO_DELETE_WHEN_ISSUING_NEW=5,
    TOKEN_41_BYTE_FORMAT=True,
)
class TestTokenIssueMulti(BaseTokenTestCase):
    def setUp(self):
        super(TestTokenIssueMulti, self).setUp()
        self.device_specific_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-uniq-id',
            device_name='iFridge',
            meta='meta',
        )
        self.fake_db.reset_mocks()

    def test_ok(self):
        eq_(
            sorted(list_tokens_by_uid(TEST_UID), key=lambda x: x.id),
            sorted([self.token, self.device_specific_token], key=lambda x: x.id),
        )

        eq_(len(self.token.access_token), 58)
        ok_(bool(re.search("y[0-4]_[-_A-Za-z\\d]{50}", self.token.access_token)))
        eq_(
            from_base64_url(self.token.access_token[3:].encode())[:13],
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01',
        )
        eq_(self.token.masked_body, self.token.access_token[:29] + '*' * 29)

    def test_reuse(self):
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-uniq-id',
            device_name='iFridge',
            meta='meta2',
        )
        eq_(self.device_specific_token.access_token, new_token.access_token)
        eq_(new_token.device_name, 'iFridge')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # reuse токена
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        eq_(
            sorted(list_tokens_by_uid(TEST_UID), key=lambda x: x.id),
            sorted([self.token, new_token], key=lambda x: x.id),
        )

    @raises(DBTemporaryError)
    def test_reuse_db_failed_error(self):
        eq_(self.device_specific_token.meta, 'meta')
        eq_(self.device_specific_token.device_name, 'iFridge')

        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-uniq-id',
            device_name='iFridge2',
            meta='meta2',
        )

    def test_reuse_no_vital_changes_db_failed(self):
        eq_(self.device_specific_token.meta, 'meta')
        eq_(self.device_specific_token.device_name, 'iFridge')

        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-uniq-id',
            device_name='iFridge',
            meta='meta',  # device_name и meta не изменились
        )
        eq_(self.device_specific_token, new_token)

    def test_reuse_too_frequent_no_db_write(self):
        eq_(self.token.meta, 'meta')
        with UPDATE(self.token) as token:
            token.issued = datetime.now() - timedelta(seconds=20)
        self.fake_db.reset_mocks()

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_name='iFridge',
            meta='meta',  # device_name и meta не изменились
        )
        eq_(self.token, new_token)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)  # в шард и не пытались писать

    def test_reuse_on_race_condition(self):
        query_result_empty_mock = mock.Mock()
        query_result_empty_mock.fetchall = mock.Mock(return_value=[])
        query_result_mock = mock.Mock()
        query_result_mock.fetchall = mock.Mock(return_value=[
            (1, 4, self.test_client.id),  # client_id
            (1, 7, time() + 60),   # expires
            (1, 10, time()),  # issued
        ])
        get_dbm('oauthdbshard1').execute.side_effect = [
            query_result_empty_mock,
            query_result_mock,
        ]
        get_dbm('oauthdbshard1').transaction.side_effect = DBIntegrityError
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
        )

    @raises(DBIntegrityError)
    def test_reuse_failed_on_race_condition(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBIntegrityError
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
        )

    def test_issue_new(self):
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
            device_name='iFridge',
        )
        eq_(new_token.device_name, 'iFridge')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # reuse токена
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # id для нового токена

        eq_(
            sorted(list_tokens_by_uid(TEST_UID), key=lambda x: x.id),
            sorted([self.token, self.device_specific_token, new_token], key=lambda x: x.id),
        )

    def test_issue_new_without_device_name(self):
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
        )
        eq_(new_token.device_id, 'some-other-uniq-id')
        ok_(not new_token.device_name)

    def test_limit_exceeded(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count - 2):
            device_id = 'some-uniq-id-%d' % i
            token = issue_token(
                uid=TEST_UID,
                client=self.test_client,
                grant_type='password',
                env=self.env,
                device_id=device_id,
                device_name='iFridge',
            )
            eq_(token.device_id, device_id)

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
            device_name='iFridge',
        )
        eq_(new_token.device_id, 'some-other-uniq-id')
        self.check_statbox_entry(
            {
                'mode': 'issue_token',
                'grant_type': 'password',
                'status': 'warning',
                'reason': 'limit.exceeded',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_IP,
                'limit': str(max_token_count),
                'valid_token_count': str(max_token_count),
                'total_token_count': str(max_token_count),
            },
            entry_index=-3,
        )
        # проверяем, что токен с device_id='some-uniq-id' удалился
        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'limit_reached',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'device_id': 'some-uniq-id',
                'device_name': 'iFridge',
                'token_id': str(self.device_specific_token.id),
                'has_alias': '0',
                'created': TimeNow(),
                'user_ip': TEST_IP,
                'consumer_ip': TEST_IP,
            },
            entry_index=-2,
        )
        device_ids = [token_.device_id for token_ in list_tokens_by_uid(TEST_UID)]
        eq_(
            len(device_ids),
            get_max_tokens_per_uid_and_client(),
        )
        eq_(
            sorted(device_ids),
            sorted(
                ['some-uniq-id-%d' % i for i in range(get_max_tokens_per_uid_and_client() - 2)] +
                ['-', 'some-other-uniq-id']
            ),
        )
        # проверяем, что historydb-логи выдачи нового токена и инвалидации старого записались с одним таймстампом
        historydb_timestamps = [
            parse_tskv_log_entry(self.event_log_handle_mock, entry_index)['timestamp']
            for entry_index in (-1, -2)
        ]
        eq_(historydb_timestamps[0], historydb_timestamps[1])

    def test_limits_exceeded_for_special_clients(self):
        grant_type = 'password'
        max_limit = 2
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение',
        )) as test_client:
            pass

        with override_settings(MAX_TOKENS_PER_UID_AND_CLIENT__BY_CLIENT_ID={
            test_client.display_id: max_limit,
            'ya-disk': 10,
        }):
            for i in range(get_max_tokens_per_uid_and_client(client_id=test_client.display_id)):
                issue_token(
                    uid=TEST_UID,
                    client=test_client,
                    grant_type=grant_type,
                    env=self.env,
                    device_id=str(i),
                    device_name='Name #%d' % i,
                )
            # проверим количество устройств на сочетание аккаунт - приложение
            device_ids = [
                token_.device_id
                for token_ in Token.by_index(
                    'params',
                    uid=TEST_UID,
                    client_id=test_client.id,
                )
            ]
            eq_(len(device_ids), max_limit)

            with assert_raises(TokenLimitExceededError):
                issue_token(
                    uid=TEST_UID,
                    client=test_client,
                    grant_type=grant_type,
                    env=self.env,
                    device_id=max_limit,
                    device_name='Name #%d' % max_limit,
                    raise_error_if_limit_exceeded=True,
                )

    def test_limits_exceeded_for_special_uids(self):
        grant_type = 'password'
        max_limit = 2
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение',
        )) as test_client:
            pass

        with override_settings(MAX_TOKENS_PER_UID_AND_CLIENT__BY_CLIENT_ID_AND_UID={
            test_client.display_id: {TEST_UID: max_limit},
            'ya-disk': 10,
        }):
            for i in range(get_max_tokens_per_uid_and_client(uid=TEST_UID, client_id=test_client.display_id)):
                issue_token(
                    uid=TEST_UID,
                    client=test_client,
                    grant_type=grant_type,
                    env=self.env,
                    device_id=str(i),
                    device_name='Name #%d' % i,
                )
            # проверим количество устройств на сочетание аккаунт - приложение
            device_ids = [
                token_.device_id
                for token_ in Token.by_index(
                    'params',
                    uid=TEST_UID,
                    client_id=test_client.id,
                )
            ]
            eq_(len(device_ids), max_limit)

            with assert_raises(TokenLimitExceededError):
                issue_token(
                    uid=TEST_UID,
                    client=test_client,
                    grant_type=grant_type,
                    env=self.env,
                    device_id=max_limit,
                    device_name='Name #%d' % max_limit,
                    raise_error_if_limit_exceeded=True,
                )

    def test_limit_exceeded_for_tokens_with_ttl(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count - 2):
            device_id = 'some-uniq-id-%d' % i
            token = issue_token(
                uid=TEST_UID,
                client=self.test_client,
                grant_type='password',
                env=self.env,
                device_id=device_id,
                device_name='iFridge',
            )
            with UPDATE(token):
                token.expires = datetime.now() + timedelta(seconds=10 + i)
            eq_(token.device_id, device_id)

        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
            device_name='iFridge',
        )
        eq_(new_token.device_id, 'some-other-uniq-id')
        self.check_statbox_entry(
            {
                'mode': 'issue_token',
                'grant_type': 'password',
                'status': 'warning',
                'reason': 'limit.exceeded',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_IP,
                'limit': str(max_token_count),
                'valid_token_count': str(max_token_count),
                'total_token_count': str(max_token_count),
            },
            entry_index=-3,
        )
        # проверяем, что токен с device_id='some-uniq-id-0' удалился
        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'limit_reached',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'device_id': 'some-uniq-id-0',
                'device_name': 'iFridge',
                'token_id': str(self.device_specific_token.id + 1),
                'has_alias': '0',
                'created': TimeNow(),
                'user_ip': TEST_IP,
                'consumer_ip': TEST_IP,
            },
            entry_index=-2,
        )
        device_ids = [token_.device_id for token_ in list_tokens_by_uid(TEST_UID)]
        eq_(
            len(device_ids),
            get_max_tokens_per_uid_and_client(),
        )
        eq_(
            sorted(device_ids),
            sorted(
                ['some-uniq-id-%d' % i for i in range(1, get_max_tokens_per_uid_and_client() - 2)] +
                ['-', 'some-uniq-id', 'some-other-uniq-id']
            ),
        )
        # проверяем, что historydb-логи выдачи нового токена и инвалидации старого записались с одним таймстампом
        historydb_timestamps = [
            parse_tskv_log_entry(self.event_log_handle_mock, entry_index)['timestamp']
            for entry_index in (-1, -2)
        ]
        eq_(historydb_timestamps[0], historydb_timestamps[1])

    def test_limit_exceeded_raise_error(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count - 2):
            device_id = 'some-uniq-id-%d' % i
            token = issue_token(
                uid=TEST_UID,
                client=self.test_client,
                grant_type='password',
                env=self.env,
                device_id=device_id,
                device_name='iFridge',
                raise_error_if_limit_exceeded=True,
            )
            eq_(token.device_id, device_id)

        with assert_raises(TokenLimitExceededError):
            issue_token(
                uid=TEST_UID,
                client=self.test_client,
                grant_type='password',
                env=self.env,
                device_id='some-other-uniq-id',
                device_name='iFridge',
                raise_error_if_limit_exceeded=True,
            )
        self.check_statbox_entry(
            {
                'mode': 'issue_token',
                'grant_type': 'password',
                'status': 'warning',
                'reason': 'limit.exceeded',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_IP,
                'limit': str(max_token_count),
                'valid_token_count': str(max_token_count),
                'total_token_count': str(max_token_count),
            },
            entry_index=-1,
        )

    def test_glogouted_tokens_are_deleted(self):
        for i in range(get_max_tokens_per_uid_and_client() - 2):
            device_id = 'some-uniq-id-%d' % i
            token = issue_token(
                uid=TEST_UID,
                client=self.test_client,
                grant_type='password',
                env=self.env,
                device_id=device_id,
                device_name='iFridge',
                raise_error_if_limit_exceeded=True,
            )
            eq_(token.device_id, device_id)
        eq_(
            len(list_tokens_by_uid(TEST_UID)),
            get_max_tokens_per_uid_and_client(),
        )

        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
            device_name='iFridge',
            raise_error_if_limit_exceeded=True,
            tokens_revoked_at=datetime.now() + timedelta(seconds=10),
        )
        eq_(
            len(list_tokens_by_uid(TEST_UID)),
            get_max_tokens_per_uid_and_client() - 4,  # было N, добавили 1 и ещё 5 удалили
        )

    def test_with_alias(self):
        new_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='some-other-uniq-id',
            device_name='iFridge',
            make_alias=True,
            raise_error_if_limit_exceeded=True,
        )
        eq_(len(new_token.alias), settings.TOKEN_ALIAS_LENGTH)
        ok_(
            all(symbol in settings.TOKEN_ALIAS_ALPHABET for symbol in new_token.alias),
            '"%s" not made from "%s"' % (new_token.alias, settings.TOKEN_ALIAS_ALPHABET),
        )
        eq_(
            new_token.masked_body,
            new_token.alias[:settings.TOKEN_ALIAS_LENGTH // 4] + '*' * (settings.TOKEN_ALIAS_LENGTH * 3 // 4),
        )
        eq_(new_token.device_name, 'iFridge')

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)  # получение токена
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)  # выдача токена
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # id для нового токена

        eq_(
            Token.by_uid_and_alias(uid=TEST_UID, alias=new_token.alias),
            new_token,
        )


class TestTokenIssueWithCustomScopes(BaseTokenTestCase):
    def setUp(self):
        super(TestTokenIssueWithCustomScopes, self).setUp()

        with DELETE(self.token):
            pass

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            ],
            default_title='Test client',
        )) as client:
            self.test_client = client

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            ],
            default_title='Test client 2',
        )) as client:
            self.other_client = client

        self.token_from_other_device = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='deviceid',
        )
        self.token_from_other_client = issue_token(
            uid=TEST_UID,
            client=self.other_client,
            grant_type='password',
            env=self.env,
        )

    def test__ok(self):
        """Подходящих токенов нет - выдадим новый"""
        eq_(
            get_already_granted_scopes(
                uid=TEST_UID,
                client=self.test_client,
                device_id=None,
            ),
            set(),
        )

        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        eq_(token.scopes, {Scope.by_keyword('test:foo')})
        eq_(
            list_tokens_by_uid(TEST_UID),
            [
                self.token_from_other_device,
                self.token_from_other_client,
                token,
            ],
        )

    def test_reuse(self):
        old_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        eq_(
            get_already_granted_scopes(
                uid=TEST_UID,
                client=self.test_client,
                device_id=None,
            ),
            {Scope.by_keyword('test:foo')},
        )

        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        eq_(token.access_token, old_token.access_token)
        eq_(token.scopes, {Scope.by_keyword('test:foo')})
        iter_eq(
            list_tokens_by_uid(TEST_UID),
            [
                self.token_from_other_device,
                self.token_from_other_client,
                token,
            ],
        )

    def test_reuse_and_extend_scopes(self):
        old_token_with_wide_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
        )
        old_token_with_narrow_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
            allow_reuse=False,
        )
        eq_(len(list_tokens_by_uid(TEST_UID)), 4)
        eq_(
            get_already_granted_scopes(
                uid=TEST_UID,
                client=self.test_client,
                device_id=None,
            ),
            {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
        )

        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')],
        )
        eq_(token.access_token, old_token_with_wide_scope.access_token)
        eq_(
            token.scopes,
            {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')},
        )
        iter_eq(
            list_tokens_by_uid(TEST_UID),
            [
                self.token_from_other_device,
                self.token_from_other_client,
                token,
                old_token_with_narrow_scope,
            ],
        )

    def test_reuse_and_not_restrict_scopes(self):
        old_token_with_narrow_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
        )
        old_token_with_wide_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')],
            allow_reuse=False,
        )
        eq_(len(list_tokens_by_uid(TEST_UID)), 4)
        eq_(
            get_already_granted_scopes(
                uid=TEST_UID,
                client=self.test_client,
                device_id=None,
            ),
            {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')},
        )

        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        eq_(token.access_token, old_token_with_wide_scope.access_token)
        eq_(token.scopes, {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')})
        iter_eq(
            list_tokens_by_uid(TEST_UID),
            [
                self.token_from_other_device,
                self.token_from_other_client,
                old_token_with_narrow_scope,
                token,
            ],
        )

    def test_no_reuse_invalid(self):
        old_token_with_narrow_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],
        )
        old_token_with_medium_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            allow_reuse=False,
        )
        old_token_with_wide_scope = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar'), Scope.by_keyword('test:ttl')],
            allow_reuse=False,
        )
        eq_(len(list_tokens_by_uid(TEST_UID)), 5)
        with UPDATE(self.test_client) as client:
            client.glogout()
        eq_(
            get_already_granted_scopes(
                uid=TEST_UID,
                client=self.test_client,
                device_id=None,
            ),
            set(),
        )

        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
        )
        ok_(token.access_token != old_token_with_medium_scope.access_token)
        eq_(token.scopes, {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')})
        iter_eq(
            list_tokens_by_uid(TEST_UID),
            [
                self.token_from_other_device,
                self.token_from_other_client,
                old_token_with_narrow_scope,
                old_token_with_wide_scope,
                token,
            ],
        )


class TestStatelessTokenIssue(BaseTokenTestCase):
    def setUp(self):
        super(TestStatelessTokenIssue, self).setUp()
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            ],
            default_title='Test client 2',
        )) as client:
            self.other_client = client

        self.fake_blackbox = FakeBlackbox()
        self._apply_patches({
            'blackbox': self.fake_blackbox,
        })
        self.fake_blackbox.set_response_value(
            'create_oauth_token',
            blackbox_create_oauth_token_response(
                access_token=TEST_STATELESS_TOKEN,
                token_id=123,
            ),
        )

    def test_ok(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.other_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
        )
        ok_(not token.has_xtoken_grant)
        assert_almost_equal(token.ttl, 60, delta=5)
        ok_(not token.can_be_refreshed)
        eq_(token.access_token, TEST_STATELESS_TOKEN)
        eq_(token.masked_body, TEST_STATELESS_TOKEN_MASKED)
        eq_(token.id, 123)
        eq_(token.client_id, self.other_client.id)
        eq_(token.device_id, DB_NULL)
        ok_(not token.device_name)
        eq_(
            token.scopes,
            {
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            },
        )

        eq_(len(self.fake_blackbox.requests), 1)
        self.fake_blackbox.requests[0].assert_query_equals({
            'method': 'create_oauth_token',
            'format': 'json',
            'uid': str(TEST_UID),
            'userip': TEST_IP,
            'client_id': str(self.other_client.id),
            'scopes': '1,2,3',
            'create_time': TimeNow(),
            'expire_time': TimeNow(offset=60),
        })

    def test_with_device_and_xtoken_ok(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.other_client,
            grant_type='password',
            env=self.env,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            x_token_id=42,
            token_type=TOKEN_TYPE_STATELESS,
        )
        ok_(not token.has_xtoken_grant)
        assert_almost_equal(token.ttl, 60, delta=5)
        ok_(not token.can_be_refreshed)
        eq_(token.access_token, TEST_STATELESS_TOKEN)
        eq_(token.masked_body, TEST_STATELESS_TOKEN_MASKED)
        eq_(token.id, 123)
        eq_(token.client_id, self.other_client.id)
        eq_(token.device_id, TEST_DEVICE_ID)
        eq_(token.device_name, TEST_DEVICE_NAME)
        eq_(token.x_token_id, 42)
        eq_(
            token.scopes,
            {
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            },
        )

        eq_(len(self.fake_blackbox.requests), 1)
        self.fake_blackbox.requests[0].assert_query_equals({
            'method': 'create_oauth_token',
            'format': 'json',
            'uid': str(TEST_UID),
            'userip': TEST_IP,
            'client_id': str(self.other_client.id),
            'scopes': '1,2,3',
            'create_time': TimeNow(),
            'expire_time': TimeNow(offset=60),
            'device_id': TEST_DEVICE_ID,
            'xtoken_id': '42',
            'xtoken_shard': '1',
        })

    def test_ok_with_expandable_scopes(self):
        with UPDATE(self.other_client) as client:
            client.is_yandex = True

        token = issue_token(
            uid=TEST_UID,
            client=self.other_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
        )
        ok_(not token.has_xtoken_grant)
        assert_almost_equal(token.ttl, 60, delta=5)
        ok_(not token.can_be_refreshed)
        eq_(token.access_token, TEST_STATELESS_TOKEN)
        eq_(token.masked_body, TEST_STATELESS_TOKEN_MASKED)
        eq_(token.id, 123)
        eq_(token.client_id, self.other_client.id)
        eq_(token.device_id, DB_NULL)
        ok_(not token.device_name)
        eq_(
            token.scopes,
            {
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
                Scope.by_keyword('test:ttl'),
            },
        )

        eq_(len(self.fake_blackbox.requests), 1)
        self.fake_blackbox.requests[0].assert_query_equals({
            'method': 'create_oauth_token',
            'format': 'json',
            'uid': str(TEST_UID),
            'userip': TEST_IP,
            'client_id': str(self.other_client.id),
            'create_time': TimeNow(),
            'expire_time': TimeNow(offset=60),
        })

    def test_must_scopes_not_expirable(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
        )
        assert_almost_equal(token.ttl, 3600 * 24 * 365, delta=5)

    def test_payment_auth_passed(self):
        with CREATE(Client.create(
                uid=TEST_UID,
                scopes=[Scope.by_keyword('money:all')],
                default_title='test money app',
        )) as test_client:
            pass

        token = issue_token(
            uid=TEST_UID,
            client=test_client,
            grant_type='password',
            env=self.env,
            token_type=TOKEN_TYPE_STATELESS,
            payment_auth_context_id='context_id',
            payment_auth_scope_addendum='addendum',
        )
        eq_(token.payment_auth_context_id, 'context_id')
        eq_(token.payment_auth_scope_addendum, 'addendum')
