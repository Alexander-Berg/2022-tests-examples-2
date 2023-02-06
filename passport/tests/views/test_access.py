# -*- coding: utf-8 -*-

from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.errors import (
    AbcScopeNotFoundError,
    AbcServiceNotFoundError,
    AccessError,
    InvalidOauthTokenError,
    InvalidScopesError,
    LoginHeaderInRsaSignatureRequiredError,
    OutdatedRsaSignatureError,
    RsaSignatureError,
    TimestampHeaderInRsaSignatureRequiredError,
    ZeroDefaultUidError,
)
from passport.backend.vault.api.models import Roles
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.fake_blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_ECDSA_PUBLIC_KEY_1,
    TEST_OAUTH_TOKEN_1,
    TEST_OAUTH_TOKEN_2,
    TEST_RSA_LOGIN_1,
    TEST_RSA_PRIVATE_KEY_1,
    TEST_RSA_PRIVATE_KEY_2,
    TEST_RSA_PUBLIC_KEY_1,
    TEST_RSA_PUBLIC_KEY_2,
    TEST_STRANGE_KEY_1,
)
from passport.backend.vault.api.test.test_vault_client import TestVaultClient
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestAccess(BaseTestClass):
    fill_database = False
    fill_staff = True
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestAccess, self).setUp()
        self.rsa_1_client = TestVaultClient(
            native_client=self.native_client,
            rsa_auth=TEST_RSA_PRIVATE_KEY_1,
            rsa_login=TEST_RSA_LOGIN_1,
        )
        self.rsa_2_client = TestVaultClient(
            native_client=self.native_client,
            rsa_auth=TEST_RSA_PRIVATE_KEY_2,
            rsa_login=TEST_RSA_LOGIN_1,
        )
        self.oauth_client = TestVaultClient(
            native_client=self.native_client,
            authorization=TEST_OAUTH_TOKEN_1,
        )
        self.fixture.add_user(uid=200)
        self.fixture.add_user(uid=201)

    def test_create_new_version_in_alien_secret(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )

        with PermissionsMock(uid=101):
            r = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123456'}],
                return_raw=True,
            )

            self.assertResponseError(r, AccessError)

    def test_set_unknown_abc_group(self):
        self.fixture.fill_abc()
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            r = self.client.add_user_role_to_secret(
                secret_uuid=secret_uuid,
                role=Roles.OWNER.name,
                abc_id=3,
                return_raw=True,
            )
            self.assertResponseError(r, AbcServiceNotFoundError)

    def test_set_unknown_abc_scope(self):
        self.fixture.fill_abc()
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            r = self.client.add_user_role_to_secret(
                secret_uuid=secret_uuid,
                role=Roles.OWNER.name,
                abc_id=14,
                abc_scope='unknown',
                return_raw=True,
            )
            self.assertResponseError(r, AbcScopeNotFoundError)

    def test_create_new_version_in_abc_group(self):
        self.fixture.fill_abc()
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            self.client.add_user_role_to_secret(
                secret_uuid=secret_uuid,
                role=Roles.OWNER.name,
                abc_id=14,
                abc_scope='tvm_management',
            )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 17)]):
            r = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123456'}],
                return_raw=True,
            )

            self.assertResponseOk(r)

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 5)]):
            r = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123456'}],
                return_raw=True,
            )

            self.assertResponseError(r, AccessError)

    def test_create_new_version_in_abc_group_with_default_scope(self):
        self.fixture.fill_abc()
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            self.client.add_user_role_to_secret(
                secret_uuid=secret_uuid,
                role=Roles.OWNER.name,
                abc_id=14,
            )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 5)]):
            r = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123456'}],
                return_raw=True,
            )

            self.assertResponseOk(r)

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 8)]):
            r = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123456'}],
                return_raw=True,
            )

            self.assertResponseError(r, AccessError)

    def test_get_secrets_in_abc_group(self):
        self.fixture.fill_abc()
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret = self.client.create_secret(name='secret_1')
                    version = self.client.create_secret_version(
                        secret_uuid=secret,
                        value=[{'key': 'password', 'value': '123'}],
                    )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret,
                    role=Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='tvm_management',
                )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 17)]):
            r1 = self.client.list_secrets()
            self.assertListEqual(
                r1,
                [{
                    'uuid': secret,
                    'name': 'secret_1',
                    'last_secret_version': {'version': version},
                    'created_at': 1445385600.0,
                    'updated_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'acl': [{
                        'created_at': 1445385600.0,
                        'role_slug': 'OWNER',
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'abc_id': 14,
                        'abc_name': u'Паспорт',
                        'abc_scope': 'tvm_management',
                        'abc_scope_id': 17,
                        'abc_scope_name': u'Управление TVM',
                        'abc_slug': 'passp',
                        'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'effective_role': 'OWNER',
                    'secret_roles': [{
                        'created_at': 1445385600.0,
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }, {
                        'created_at': 1445385600.0,
                        'role_slug': 'OWNER',
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'abc_id': 14,
                        'abc_name': u'Паспорт',
                        'abc_scope': 'tvm_management',
                        'abc_scope_id': 17,
                        'abc_scope_name': u'Управление TVM',
                        'abc_slug': 'passp',
                        'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'updated_by': 100,
                    'versions_count': 1,
                    'tokens_count': 0,
                }]
            )

    def test_get_secrets_in_abc_role(self):
        self.fixture.fill_abc()
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_1 = self.client.create_secret(name='secret_1')
                    secret_2 = self.client.create_secret(name='secret_2')

                self.client.add_user_role_to_secret(
                    secret_uuid=secret_1,
                    role=Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='development',
                )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret_1,
                    role=Roles.OWNER.name,
                    abc_id=14,
                    abc_role_id=8,
                )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret_2,
                    role=Roles.OWNER.name,
                    abc_id=14,
                    abc_role_id=630,
                )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_roles=[(14, 630)]):
            r1 = self.client.list_secrets()
            self.assertListEqual(
                r1,
                [
                    {u'acl': [{u'abc_id': 14,
                               u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                               u'abc_role': 630,
                               u'abc_role_name': u'TVM \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440',
                               u'abc_slug': u'passp',
                               u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                               u'created_at': 1445385600.0,
                               u'created_by': 100,
                               u'creator_login': u'vault-test-100',
                               u'role_slug': u'OWNER'}],
                     u'created_at': 1445385600.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'effective_role': u'OWNER',
                     u'name': u'secret_2',
                     u'secret_roles': [{u'created_at': 1445385600.0,
                                        u'created_by': 100,
                                        u'creator_login': u'vault-test-100',
                                        u'login': u'vault-test-100',
                                        u'role_slug': u'OWNER',
                                        u'uid': 100},
                                       {u'abc_id': 14,
                                        u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                        u'abc_role': 630,
                                        u'abc_role_name': u'TVM \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440',
                                        u'abc_slug': u'passp',
                                        u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                                        u'created_at': 1445385600.0,
                                        u'created_by': 100,
                                        u'creator_login': u'vault-test-100',
                                        u'role_slug': u'OWNER'}],
                     u'tokens_count': 0,
                     u'updated_at': 1445385600.0,
                     u'updated_by': 100,
                     u'uuid': secret_2,
                     u'versions_count': 0}
                ],
            )

    def test_get_secrets_in_abc_group_with_default_scope(self):
        self.fixture.fill_abc()
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret = self.client.create_secret(name='secret_1')
                    version = self.client.create_secret_version(
                        secret_uuid=secret,
                        value=[{'key': 'password', 'value': '123'}],
                    )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret,
                    role=Roles.OWNER.name,
                    abc_id=14,
                )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 5)]):
            r1 = self.client.list_secrets()
            self.assertListEqual(
                r1,
                [{
                    'uuid': secret,
                    'name': 'secret_1',
                    'last_secret_version': {'version': version},
                    'created_at': 1445385600.0,
                    'updated_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'acl': [{
                        'created_at': 1445385600.0,
                        'role_slug': 'OWNER',
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'abc_id': 14,
                        'abc_name': u'Паспорт',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': 'passp',
                        'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'effective_role': 'OWNER',
                    'secret_roles': [{
                        'created_at': 1445385600.0,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_by': 100,
                    }, {
                        'created_at': 1445385600.0,
                        'role_slug': 'OWNER',
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'abc_id': 14,
                        'abc_name': u'Паспорт',
                        'abc_scope': 'development',
                        'abc_scope_id': 5,
                        'abc_scope_name': u'Разработка',
                        'abc_slug': 'passp',
                        'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'updated_by': 100,
                    'versions_count': 1,
                    'tokens_count': 0,
                }]
            )

    def test_get_secret_by_oauth(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid = self.client.create_secret(name='secret_1')
                    secret_version = self.client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value=[{'key': 'password', 'value': '123'}],
                    )
        with PermissionsMock(oauth={'uid': 100, 'scope': 'vault:use'}):
            r = self.oauth_client.get_version(secret_version)
            self.assertDictEqual(r, {
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'secret_name': 'secret_1',
                'value': {'password': '123'},
                'version': 'ver-0000000000000000000000ygj2',
                'secret_uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_get_secret_by_implicit_oauth(self):
        oauth_client = TestVaultClient(
            native_client=self.native_client,
            authorization=TEST_OAUTH_TOKEN_2,
        )
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid = self.client.create_secret(name='secret_1')
                    secret_version = self.client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value=[{'key': 'password', 'value': '123'}],
                    )
        with PermissionsMock(oauth={'uid': 100, 'scope': 'vault:use'}):
            r = oauth_client.get_version(secret_version)
            self.assertDictEqual(r, {
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'secret_name': 'secret_1',
                'value': {'password': '123'},
                'version': 'ver-0000000000000000000000ygj2',
                'secret_uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_oauth_error(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid = self.client.create_secret(name='secret_1')
                    secret_version = self.client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value=[{'key': 'password', 'value': '123'}],
                    )

        with PermissionsMock(oauth={'uid': 101, 'scope': 'vault:use'}):
            r = self.oauth_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, AccessError)

        with PermissionsMock(oauth={'uid': 100}):
            r = self.oauth_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, InvalidScopesError)

        with FakeBlackbox() as fake_bb:
            fake_bb.set_response_value(
                'oauth',
                blackbox_oauth_response(
                    error='wrong_token',
                    status=BLACKBOX_OAUTH_INVALID_STATUS,
                ),
            )
            r = self.oauth_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, InvalidOauthTokenError)

    def test_get_secret_by_rsa(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid = self.client.create_secret(name='secret_1')
                    secret_version = self.client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value=[{'key': 'password', 'value': '123'}],
                    )
        with PermissionsMock(rsa={'uid': 100, 'keys': [
            TEST_STRANGE_KEY_1, TEST_ECDSA_PUBLIC_KEY_1, TEST_RSA_PUBLIC_KEY_1,
        ]}):
            r = self.rsa_1_client.get_version(secret_version)
            self.assertDictEqual(r, {
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'secret_name': 'secret_1',
                'value': {'password': '123'},
                'version': 'ver-0000000000000000000000ygj2',
                'secret_uuid': 'sec-0000000000000000000000ygj0',
            })

        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2, TEST_RSA_PUBLIC_KEY_1]}):
            r = self.rsa_1_client.get_version(secret_version)
            self.assertDictEqual(r, {
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'secret_name': 'secret_1',
                'value': {'password': '123'},
                'version': 'ver-0000000000000000000000ygj2',
                'secret_uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_rsa_access_errors(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid = self.client.create_secret(name='secret_1')
                    secret_version = self.client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value=[{'key': 'password', 'value': '123'}],
                    )

        with PermissionsMock(rsa={'uid': 101, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            r = self.rsa_1_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, AccessError)

        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            r = self.rsa_2_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, RsaSignatureError)

        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]}):
            r = self.rsa_1_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, RsaSignatureError)

        with PermissionsMock(rsa={'uid': 101, 'keys': [TEST_RSA_PUBLIC_KEY_2]}):
            r = self.rsa_2_client.get_version(secret_version, return_raw=True)
            self.assertResponseError(r, AccessError)

        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.rsa_1_client.add_user_role_to_secret(
                secret_uuid=secret_uuid,
                role='READER',
                uid=101,
            )

        with PermissionsMock(rsa={'uid': 101, 'keys': [TEST_RSA_PUBLIC_KEY_2]}):
            r = self.rsa_2_client.get_version(secret_version, return_raw=True)
            self.assertResponseOk(r)

    def test_invalid_rsa_headers(self):
        r = self.native_client.get('/1/versions/123/', headers={'X-Ya-Rsa-Signature': '123'})
        self.assertResponseError(r, LoginHeaderInRsaSignatureRequiredError)

        with PermissionsMock(rsa={'uid': 1120000000038274, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            r = self.native_client.get(
                '/1/versions/123/',
                headers={'X-Ya-Rsa-Signature': '123', 'X-Ya-Rsa-Login': 'ppodolsky'},
            )
            self.assertResponseError(r, TimestampHeaderInRsaSignatureRequiredError)

            with TimeMock(incrementing=31):
                r = self.rsa_1_client.create_secret('test_secret', return_raw=True)
                self.assertResponseError(r, OutdatedRsaSignatureError)

    def test_random_scenario_1(self):
        self.fixture.fill_abc()
        with TimeMock() as time_mock:
            with PermissionsMock(uid=100):
                with UuidMock():
                    secret_uuid_1 = self.client.create_secret(name='secret_1')
                    time_mock.tick()
                    secret_uuid_2 = self.client.create_secret(name='secret_2')
                    time_mock.tick()
                    self.client.create_secret_version(
                        secret_uuid=secret_uuid_1,
                        value=[{'key': 'password', 'value': '123'}],
                    )
                    time_mock.tick()
                    self.client.create_secret_version(
                        secret_uuid=secret_uuid_1,
                        value=[{'key': 'password', 'value': '123456'}],
                    )
                    time_mock.tick()
                    self.client.create_secret_version(
                        secret_uuid=secret_uuid_2,
                        value=[{'key': 'cert', 'value': 'certificate'}],
                    )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret_uuid_1,
                    role=Roles.OWNER.name,
                    abc_id=14,
                )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret_uuid_1,
                    role=Roles.READER.name,
                    uid=101,
                )
                self.client.add_user_role_to_secret(
                    secret_uuid=secret_uuid_2,
                    role=Roles.OWNER.name,
                    uid=101,
                )

        with PermissionsMock(uid=101, fixture=self.fixture, abc_groups=[(14, 5)]):
            r1 = self.client.list_secrets()
            self.assertListEqual(r1, [{
                "name": "secret_2",
                'last_secret_version': {'version': 'ver-0000000000000000000000ygj6'},
                "updated_at": 1445385604.0,
                "secret_roles": [{
                    "role_slug": "OWNER",
                    "uid": 100,
                    'created_at': 1445385601.0,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                }, {
                    "role_slug": "OWNER",
                    "uid": 101,
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'login': 'vault-test-101',
                    'creator_login': 'vault-test-100',
                }],
                "uuid": "sec-0000000000000000000000ygj2",
                "created_by": 100,
                "created_at": 1445385601.0,
                'creator_login': 'vault-test-100',
                "acl": [{
                    "role_slug": "OWNER",
                    "uid": 101,
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'login': 'vault-test-101',
                    'creator_login': 'vault-test-100',
                }],
                'effective_role': 'OWNER',
                "updated_by": 100,
                'versions_count': 1,
                'tokens_count': 0,
            }, {
                'uuid': 'sec-0000000000000000000000ygj0',
                'name': 'secret_1',
                'last_secret_version': {'version': 'ver-0000000000000000000000ygj5'},
                'created_at': 1445385600.0,
                'updated_at': 1445385604.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'acl': [{
                    'created_at': 1445385604.0,
                    'role_slug': 'OWNER',
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'abc_id': 14,
                    'abc_name': u'Паспорт',
                    'abc_scope': 'development',
                    'abc_scope_name': u'Разработка',
                    'abc_scope_id': 5,
                    'abc_slug': 'passp',
                    'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                }, {
                    'created_at': 1445385604.0,
                    'role_slug': 'READER',
                    'uid': 101,
                    'created_by': 100,
                    'login': 'vault-test-101',
                    'creator_login': 'vault-test-100',
                }], 'secret_roles': [{
                    'created_at': 1445385600.0,
                    'role_slug': 'OWNER',
                    'uid': 100,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                }, {
                    'created_at': 1445385604.0,
                    'role_slug': 'OWNER',
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'abc_id': 14,
                    'abc_name': u'Паспорт',
                    'abc_scope': 'development',
                    'abc_scope_id': 5,
                    'abc_scope_name': u'Разработка',
                    'abc_slug': 'passp',
                    'abc_url': 'https://abc.yandex-team.ru/services/passp/',
                }, {
                    'created_at': 1445385604.0,
                    'role_slug': 'READER',
                    'uid': 101,
                    'created_by': 100,
                    'login': 'vault-test-101',
                    'creator_login': 'vault-test-100',
                }],
                'effective_role': 'OWNER',
                'updated_by': 100,
                'versions_count': 2,
                'tokens_count': 0,
            }])

    def test_update_secret_by_other_owner(self):
        with TimeMock() as time_mock:
            with UuidMock():
                with PermissionsMock(uid=200):
                    secret_uuid = self.client.create_secret(
                        name='lol-secret',
                        comment='secret for top secret service',
                    )
                    time_mock.tick()
                    r1 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r1, {
                        'acl': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })
                    self.client.add_user_role_to_secret(
                        secret_uuid=secret_uuid,
                        role=Roles.OWNER.name,
                        uid=201,
                    )

                with PermissionsMock(uid=201):
                    self.client.update_secret(
                        secret_uuid=secret_uuid,
                        name='lol-secret-1',
                    )
                    time_mock.tick()
                    r2 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r2, {
                        'acl': [{
                            'role_slug': 'OWNER',
                            'uid': 201,
                            'created_at': 1445385601.0,
                            'created_by': 200,
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret-1',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }, {
                            'role_slug': 'OWNER',
                            'uid': 201,
                            'created_at': 1445385601.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385601.0,
                        'updated_by': 201,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })

    def test_update_secret_attempt_by_other_reader(self):
        with TimeMock() as time_mock:
            with UuidMock():
                with PermissionsMock(uid=200):
                    secret_uuid = self.client.create_secret(
                        name='lol-secret',
                        comment='secret for top secret service',
                    )
                    time_mock.tick()
                    r1 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r1, {
                        'acl': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })
                    self.client.add_user_role_to_secret(
                        secret_uuid=secret_uuid,
                        role=Roles.READER.name,
                        uid=201,
                    )

                with PermissionsMock(uid=201):
                    r2 = self.client.update_secret(
                        secret_uuid=secret_uuid,
                        name='lol-secret-1',
                        return_raw=True,
                    )
                    time_mock.tick()
                    self.assertResponseError(r2, AccessError)
                    r3 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r3, {
                        'acl': [{
                            'role_slug': 'READER',
                            'uid': 201,
                            'created_at': 1445385601.0,
                            'created_by': 200,
                        }],
                        'effective_role': 'READER',
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }, {
                            'role_slug': 'READER',
                            'uid': 201,
                            'created_at': 1445385601.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385601.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })

    def test_update_secret_attempt_by_other_supervisor(self):
        with TimeMock() as time_mock:
            with UuidMock():
                with PermissionsMock(uid=200, supervisor=True):
                    secret_uuid = self.client.create_secret(
                        name='lol-secret',
                        comment='secret for top secret service',
                    )
                    time_mock.tick()
                    r1 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r1, {
                        'acl': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })
                    self.client.add_supervisor(uid=201)

                with PermissionsMock(uid=201):
                    r2 = self.client.update_secret(
                        secret_uuid=secret_uuid,
                        name='lol-secret-1',
                        return_raw=True,
                    )
                    time_mock.tick()
                    self.assertResponseError(r2, AccessError)
                    r3 = self.client.get_secret(
                        secret_uuid=secret_uuid,
                    )
                    self.assertDictEqual(r3, {
                        'acl': [],
                        'comment': 'secret for top secret service',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'lol-secret',
                        'secret_roles': [{
                            'role_slug': 'OWNER',
                            'uid': 200,
                            'created_at': 1445385600.0,
                            'created_by': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    })

    def test_default_uid_0(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(name='secret_1')
            self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )

        with PermissionsMock(uid=0):
            r = self.client.get_version(secret_uuid, return_raw=True)
            self.assertResponseError(r, ZeroDefaultUidError)
