# -*- coding: utf-8 -*-

from library.python.vault_client import TokenizedRequest
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api import errors
from passport.backend.vault.api.models import DelegationToken
from passport.backend.vault.api.models.secret import SecretUUIDType
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import (
    FakeServiceContext,
    PermissionsMock,
    VALID_SERVICE_TICKET_1,
    VALID_SERVICE_TICKET_SINGLESS_1,
    VALID_USER_TICKET_SIGNLESS_1,
)
from passport.backend.vault.api.test.secrets_mock import SecretsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestTokensViews(BaseTestClass):
    fill_database = False
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestTokensViews, self).setUp()
        self.fixture.fill_abc()
        self.fixture.fill_staff()
        self.fixture.fill_tvm_apps()
        self.fixture.add_user(uid=200)

    def test_token_mask(self):
        token = DelegationToken.build_token()
        tests = [
            ('', r'^$'),
            ('invalid_token', r'^\*{13}$'),
            ('t' * 20, r'^\*{20}$'),
            ('t' * 21, r'^ttttttttt\*\*\*ttttttttt$'),
            (token, r'^[^*]{9}\*+[^*]{9}$'),
            (token + token, r'^[^*]{9}\*+[^*]{9}$'),
            (token + token + token, r'^[^*]{9}\*+[^*]{9}$'),
            (token.split('.')[0], r'^[^*]{9}\*+[^*]{9}$'),
        ]
        for t in tests:
            self.assertRegexpMatches(DelegationToken.mask_token(t[0]), t[1])

        self.assertEqual(len(token), len(DelegationToken.mask_token(token)))

    def test_create_token_for_non_existent_secret(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            r = self.client.create_token(
                'sec-1100000000000000000000ygj0',
                signature='1',
                return_raw=True,
            )
            self.assertResponseError(r, errors.NonexistentEntityError)

    def test_create_token_ok(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            with SecretsMock(token_urlsafe_value='secret-token'):
                with UuidMock():
                    secret = self.client.create_secret('tokenized')
                    r = self.client.create_token(
                        secret,
                        signature=1,
                        return_raw=True,
                    )
                    self.assertResponseEqual(r, {
                        'token': 'secret-token.1.3837c674ecc2a232',
                        'token_uuid': 'tid-0000000000000000000000ygj2',
                        'secret_uuid': secret,
                        'status': 'ok',
                    })

    def test_create_token_with_tvm_id(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            with SecretsMock(token_urlsafe_value='secret-token'):
                with UuidMock():
                    secret = self.client.create_secret('tokenized')
                    r = self.client.create_token(
                        secret,
                        tvm_client_id=2000367,
                        signature=1,
                        return_raw=True,
                    )
                    self.assertResponseEqual(r, {
                        'token': 'secret-token.1.3837c674ecc2a232',
                        'token_uuid': 'tid-0000000000000000000000ygj2',
                        'secret_uuid': secret,
                        'tvm_app': {
                            u'abc_department': {
                                u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                u'id': 14,
                                u'unique_name': u'passp',
                            },
                            u'abc_state': u'granted',
                            u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                            u'name': u'social api (dev)',
                            u'tvm_client_id': 2000367,
                        },
                        'status': 'ok',
                    })

    def test_create_token_with_unknown_tvm_id(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            with SecretsMock(token_urlsafe_value='secret-token'):
                with UuidMock():
                    secret = self.client.create_secret('tokenized')
                    r = self.client.create_token(
                        secret,
                        tvm_client_id=9999999,
                        signature=1,
                        return_raw=True,
                    )
                    self.assertResponseEqual(r, {
                        'token': 'secret-token.1.3837c674ecc2a232',
                        'token_uuid': 'tid-0000000000000000000000ygj2',
                        'secret_uuid': secret,
                        'status': 'ok',
                    })

    def test_revoke_token_ok(self):
        self.fixture.insert_data(skip_staff=True, skip_abc=True, skip_tvm=True)
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('tokenized')
                _, token_1 = self.client.create_token(secret, signature='1')
                _, token_2 = self.client.create_token(secret, signature='2')
                _, token_3 = self.client.create_token(secret, signature='3')

                with LoggingMock() as log:
                    self.assertResponseEqual(
                        self.client.revoke_token(token_2, return_raw=True),
                        {'status': 'ok'},
                    )

                    self.assertListEqual(
                        log.getLogger('statbox').entries,
                        [
                            ({
                                'action': 'enter',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'revoke_token',
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                            }, 'INFO', None, None,),
                            ({
                                'action': 'success',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'revoke_token',
                                'source': 'owner',
                                'token_uuid': token_2,
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                                'uid': 100
                            }, 'INFO', None, None,),
                            ({
                                'action': 'exit',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'revoke_token',
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                            }, 'INFO', None, None,),
                        ]
                    )

            self.assertListEqual(
                self.client.list_tokens(secret),
                [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '1',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_1,
                    },
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '3',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_3,
                    },
                ],
            )

            self.assertListEqual(
                self.client.list_tokens(secret, with_revoked=True),
                [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '1',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_1,
                    },
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'revocation_login': 'vault-test-100',
                        'revoked_at': 1445385615.0,
                        'signature': '2',
                        'secret_uuid': secret,
                        'state_name': 'revoked',
                        'token_uuid': token_2,
                    },
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '3',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_3,
                    },
                ],
            )

            # Проверяем, что ручка идемпотентная
            self.client.revoke_token(token_2)

    def test_revoke_unexists_token(self):
        with PermissionsMock(uid=100):
            with LoggingMock() as log:
                self.assertResponseError(
                    self.client.revoke_token('tid-1110000000000000000001x142', return_raw=True),
                    errors.NonexistentEntityError(
                        entity_class=DelegationToken,
                        entity_id='tid-1110000000000000000001x142',
                    ),
                )

                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [
                        ({'action': 'enter',
                          'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                          'auth_tvm_app_id': 1,
                          'auth_type': 'user_ticket',
                          'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                          'mode': 'revoke_token',
                          'tvm_grants': 'granted',
                          'auth_uid': 100},
                         'INFO',
                         None,
                         None),
                        ({'action': 'error',
                          'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                          'auth_tvm_app_id': 1,
                          'auth_type': 'user_ticket',
                          'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                          'mode': 'revoke_token',
                          'class': 'DelegationToken',
                          'code': 'nonexistent_entity_error',
                          'id': u'tid-1110000000000000000001x142',
                          'message': 'Requested a non-existent entity (DelegationToken, tid-1110000000000000000001x142)',
                          'status': 'error',
                          'tvm_grants': 'granted',
                          'auth_uid': 100},
                         'INFO',
                         None,
                         None),
                    ]
                )

    def test_revoke_token_fail_if_not_owner(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock(offset=15):
                    secret = self.client.create_secret('tokenized')
                    _, token_1 = self.client.create_token(secret, signature='1')
                    _, token_2 = self.client.create_token(secret, signature='2')
                    _, token_3 = self.client.create_token(secret, signature='3')

                    self.client.add_user_role_to_secret(secret, 'reader', uid=200)

        with PermissionsMock(uid=200):
            self.assertResponseError(
                self.client.revoke_token(token_2, return_raw=True),
                errors.AccessError(),
            )

        with PermissionsMock(uid=101):
            self.assertResponseError(
                self.client.revoke_token(token_2, return_raw=True),
                errors.AccessError(),
            )

        with PermissionsMock(uid=100):
            self.assertTrue(
                self.client.revoke_token(token_2),
            )

    def test_get_tokens_list(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                secret_uuid = self.client.create_secret(
                    name='secret_1',
                )
                self.client.add_user_role_to_secret(secret_uuid, 'READER', uid=101)
                with TimeMock(offset=100):
                    _, token_1_uuid = self.client.create_token(
                        secret_uuid,
                        tvm_client_id='2000367',
                        signature='123',
                    )
                    _, token_2_uuid = self.client.create_token(
                        secret_uuid,
                        tvm_client_id='2000734',
                        comment='Test token',
                    )

        with PermissionsMock(uid=101):
            r = self.client.list_tokens(secret_uuid)
            self.assertListEqual(r, [
                {
                    'created_at': 1445385700.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'signature': '123',
                    'secret_uuid': secret_uuid,
                    'state_name': 'normal',
                    'tvm_app': {
                        u'abc_department': {
                            u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                            u'id': 14,
                            u'unique_name': u'passp',
                        },
                        u'abc_state': u'granted',
                        u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                        u'name': u'social api (dev)',
                        u'tvm_client_id': 2000367,
                    },
                    'tvm_client_id': 2000367,
                    'token_uuid': token_1_uuid,
                },
                {
                    'created_at': 1445385700.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_uuid': secret_uuid,
                    'state_name': 'normal',
                    'tvm_client_id': 2000734,
                    'token_uuid': token_2_uuid,
                    'comment': 'Test token',
                },
            ])

    def test_get_tokens_with_paging(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                secret = self.client.create_secret(
                    name='secret_1',
                )
                self.client.add_user_role_to_secret(secret, 'READER', uid=101)
                with TimeMock(offset=100):
                    _, token_1_uuid = self.client.create_token(
                        secret,
                        signature='token 1',
                    )
                    _, token_2_uuid = self.client.create_token(
                        secret,
                        signature='token 2',
                    )
                    _, token_3_uuid = self.client.create_token(
                        secret,
                        signature='token 3',
                    )
                    _, token_4_uuid = self.client.create_token(
                        secret,
                        signature='token 4',
                    )
                    _, token_5_uuid = self.client.create_token(
                        secret,
                        signature='token 5',
                    )

        with PermissionsMock(uid=101):
            self.assertEqual(len(self.client.list_tokens(secret)), 5)

            r = self.client.list_tokens(secret, page_size=3)
            self.assertListEqual(
                r,
                [{u'created_at': 1445385700.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'secret_uuid': secret,
                  u'signature': u'token 1',
                  u'state_name': u'normal',
                  u'token_uuid': token_1_uuid},
                 {u'created_at': 1445385700.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'secret_uuid': secret,
                  u'signature': u'token 2',
                  u'state_name': u'normal',
                  u'token_uuid': token_2_uuid},
                 {u'created_at': 1445385700.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'secret_uuid': secret,
                  u'signature': u'token 3',
                  u'state_name': u'normal',
                  u'token_uuid': token_3_uuid}],
            )

            r = self.client.list_tokens(secret, page=1, page_size=3)
            self.assertListEqual(
                r,
                [{u'created_at': 1445385700.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'secret_uuid': secret,
                  u'signature': u'token 4',
                  u'state_name': u'normal',
                  u'token_uuid': token_4_uuid},
                 {u'created_at': 1445385700.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'secret_uuid': secret,
                  u'signature': u'token 5',
                  u'state_name': u'normal',
                  u'token_uuid': token_5_uuid}],
            )

    def test_list_secrets_with_tokens(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_uuid = self.client.create_secret(
                        name='secret_1',
                    )
                    self.client.add_user_role_to_secret(secret_uuid, 'READER', uid=101)
                    secret_version = self.client.create_secret_version(
                        secret_uuid,
                        value={'key': 'value'},
                    )
                    _, token_1_uuid = self.client.create_token(
                        secret_uuid,
                        tvm_client_id='2000367',
                        signature='123',
                    )
                    _, token_2_uuid = self.client.create_token(
                        secret_uuid,
                        tvm_client_id='2000734',
                    )
                r = self.client.list_secrets()
                self.assertListEqual(
                    r,
                    [{u'acl': [{u'created_at': 1445385615.0,
                                u'created_by': 100,
                                u'creator_login': u'vault-test-100',
                                u'login': u'vault-test-100',
                                u'role_slug': u'OWNER',
                                u'uid': 100}],
                      u'created_at': 1445385615.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'effective_role': u'OWNER',
                      u'last_secret_version': {u'version': secret_version},
                      u'name': u'secret_1',
                      u'secret_roles': [{u'created_at': 1445385615.0,
                                         u'created_by': 100,
                                         u'creator_login': u'vault-test-100',
                                         u'login': u'vault-test-100',
                                         u'role_slug': u'OWNER',
                                         u'uid': 100},
                                        {u'created_at': 1445385615.0,
                                         u'created_by': 100,
                                         u'creator_login': u'vault-test-100',
                                         u'login': u'vault-test-101',
                                         u'role_slug': u'READER',
                                         u'uid': 101}],
                      u'tokens_count': 2,
                      u'updated_at': 1445385615.0,
                      u'updated_by': 100,
                      u'uuid': secret_uuid,
                      u'versions_count': 1}]
                )

    def test_restore_token_ok(self):
        self.fixture.insert_data(skip_staff=True, skip_abc=True, skip_tvm=True)
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('tokenized')
                _, token_1 = self.client.create_token(secret, signature='1')
                _, token_2 = self.client.create_token(secret, signature='2')
                _, token_3 = self.client.create_token(secret, signature='3')
                self.client.revoke_token(token_2)

                self.assertListEqual(
                    self.client.list_tokens(secret, with_revoked=True),
                    [
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'signature': '1',
                            'secret_uuid': secret,
                            'state_name': 'normal',
                            'token_uuid': token_1,
                        },
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'revocation_login': 'vault-test-100',
                            'revoked_at': 1445385615.0,
                            'signature': '2',
                            'secret_uuid': secret,
                            'state_name': 'revoked',
                            'token_uuid': token_2,
                        },
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'signature': '3',
                            'secret_uuid': secret,
                            'state_name': 'normal',
                            'token_uuid': token_3,
                        },
                    ],
                )

                with LoggingMock() as log:
                    self.assertResponseEqual(
                        self.client.restore_token(token_2, return_raw=True),
                        {'status': 'ok'},
                    )

                    self.assertListEqual(
                        log.getLogger('statbox').entries,
                        [
                            ({
                                'action': 'enter',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'restore_token',
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                            }, 'INFO', None, None,),
                            ({
                                'action': 'success',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'restore_token',
                                'source': 'owner',
                                'token_uuid': token_2,
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                                'uid': 100,
                            }, 'INFO', None, None,),
                            ({
                                'action': 'exit',
                                'auth_type': 'user_ticket',
                                'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                                'auth_tvm_app_id': 1,
                                'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                                'mode': 'restore_token',
                                'tvm_grants': 'granted',
                                'auth_uid': 100,
                            }, 'INFO', None, None,),
                        ]
                    )

            self.assertListEqual(
                self.client.list_tokens(secret),
                [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '1',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_1,
                    },
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '2',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_2,
                    },
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'signature': '3',
                        'secret_uuid': secret,
                        'state_name': 'normal',
                        'token_uuid': token_3,
                    },
                ],
            )

            # Проверяем, что ручка идемпотентная
            self.client.restore_token(token_2)

    def test_restore_unexists_token(self):
        with PermissionsMock(uid=100):
            with LoggingMock() as log:
                self.assertResponseError(
                    self.client.restore_token('tid-1110000000000000000001x142', return_raw=True),
                    errors.NonexistentEntityError(
                        entity_class=DelegationToken,
                        entity_id='tid-1110000000000000000001x142',
                    ),
                )

                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [
                        ({'action': 'enter',
                          'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                          'auth_tvm_app_id': 1,
                          'auth_type': 'user_ticket',
                          'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                          'mode': 'restore_token',
                          'tvm_grants': 'granted',
                          'auth_uid': 100},
                         'INFO',
                         None,
                         None),
                        ({'action': 'error',
                          'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                          'auth_tvm_app_id': 1,
                          'auth_type': 'user_ticket',
                          'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                          'mode': 'restore_token',
                          'class': 'DelegationToken',
                          'code': 'nonexistent_entity_error',
                          'id': u'tid-1110000000000000000001x142',
                          'message': 'Requested a non-existent entity (DelegationToken, tid-1110000000000000000001x142)',
                          'status': 'error',
                          'tvm_grants': 'granted',
                          'auth_uid': 100},
                         'INFO',
                         None,
                         None),
                    ]
                )

    def test_restore_token_fail_if_not_owner(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock(offset=15):
                    secret = self.client.create_secret('tokenized')
                    _, token_1 = self.client.create_token(secret, signature='1')
                    _, token_2 = self.client.create_token(secret, signature='2')
                    _, token_3 = self.client.create_token(secret, signature='3')

                    self.client.add_user_role_to_secret(secret, 'reader', uid=200)
                    self.client.revoke_token(token_2)

        with PermissionsMock(uid=200):
            self.assertResponseError(
                self.client.restore_token(token_2, return_raw=True),
                errors.AccessError(),
            )

        with PermissionsMock(uid=101):
            self.assertResponseError(
                self.client.restore_token(token_2, return_raw=True),
                errors.AccessError(),
            )

        with PermissionsMock(uid=100):
            self.assertTrue(
                self.client.restore_token(token_2),
            )

    def test_get_token_info_ok(self):
        self.fixture.insert_data(skip_staff=True, skip_abc=True, skip_tvm=True)
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('tokenized')
                token_1, token_1_uuid = self.client.create_token(
                    secret,
                    tvm_client_id='2000367',
                    signature='1',
                )
                self.client.add_user_role_to_secret(secret, 'reader', uid=101)
                self.client.add_user_role_to_secret(secret, 'owner', uid=200)

        self.assertDictEqual(
            self.client.get_token_info(token_uuid=token_1_uuid),
            {'owners': [{u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                        {u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 200}],
             'readers': [{u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'login': u'vault-test-100',
                          u'role_slug': u'OWNER',
                          u'uid': 100},
                         {u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'role_slug': u'OWNER',
                          u'uid': 200},
                         {u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'login': u'vault-test-101',
                          u'role_slug': u'READER',
                          u'uid': 101}],
             'token_info': {u'created_at': 1445385615.0,
                            u'created_by': 100,
                            u'creator_login': u'vault-test-100',
                            u'secret_uuid': secret,
                            u'state_name': u'normal',
                            u'token_uuid': token_1_uuid,
                            u'tvm_app': {u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                                             u'id': 14,
                                                             u'unique_name': u'passp'},
                                         u'abc_state': u'granted',
                                         u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                         u'name': u'social api (dev)',
                                         u'tvm_client_id': 2000367},
                            u'tvm_client_id': 2000367}},
        )

        self.assertDictEqual(
            self.client.get_token_info(token=token_1),
            {'owners': [{u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                        {u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 200}],
             'readers': [{u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'login': u'vault-test-100',
                          u'role_slug': u'OWNER',
                          u'uid': 100},
                         {u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'role_slug': u'OWNER',
                          u'uid': 200},
                         {u'created_at': 1445385615.0,
                          u'created_by': 100,
                          u'creator_login': u'vault-test-100',
                          u'login': u'vault-test-101',
                          u'role_slug': u'READER',
                          u'uid': 101}],
             'token_info': {u'created_at': 1445385615.0,
                            u'created_by': 100,
                            u'creator_login': u'vault-test-100',
                            u'secret_uuid': secret,
                            u'state_name': u'normal',
                            u'token_uuid': token_1_uuid,
                            u'tvm_app': {u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                                             u'id': 14,
                                                             u'unique_name': u'passp'},
                                         u'abc_state': u'granted',
                                         u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                         u'name': u'social api (dev)',
                                         u'tvm_client_id': 2000367},
                            u'tvm_client_id': 2000367}},
        )

    def test_get_token_info_errors(self):
        self.assertResponseError(
            self.client.get_token_info(
                token_uuid='tid-9990000000000000000000ygj2',
                return_raw=True,
            ),
            errors.NonexistentEntityError(),
        )

        token = DelegationToken.build_token()
        self.assertResponseError(
            self.client.get_token_info(
                token=token,
                return_raw=True,
            ),
            errors.NonexistentEntityError(),
        )

        r = self.client.get_token_info(
            token_uuid='tid-9990000000000000000000ygj2',
            token=token,
            return_raw=True,
        )
        self.assertResponseError(
            r,
            errors.ValidationError({
                u'token_uuid': u'Only one parameter must be set among token_uuid, token',
                u'token': u'Only one parameter must be set among token_uuid, token',
            }),
        )


class TestTokenizedViews(BaseTestClass):
    fill_database = False
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestTokenizedViews, self).setUp()
        self.fixture.fill_abc()
        self.fixture.fill_staff()
        self.fixture.fill_tvm_apps()
        self.fixture.add_user(uid=200)

    def test_get_by_token_without_factors(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
            )

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                ),
            ],
            return_raw=True,
        )
        self.assertResponseEqual(r, {
            'secrets': [{
                'token': token,
                'token_uuid': token_uuid,
                'secret_version': secret_version,
                'status': 'ok',
                'value': [{'key': 'password', 'value': '123'}],
            }],
            'status': 'ok',
        })

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                ),
            ],
        )
        self.assertListEqual(r, [{
            'token': token,
            'token_uuid': token_uuid,
            'secret_version': secret_version,
            'status': 'ok',
            'value': [{'key': 'password', 'value': '123'}],
        }])

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                ),
            ],
            return_raw=True,
        )
        self.assertResponseOk(r)

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                    signature='123',
                ),
            ],
            return_raw=True,
        )
        self.assertResponseOk(r)

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                    service_ticket='123',
                ),
            ],
            return_raw=True,
        )
        self.assertResponseOk(r)

    def test_get_by_token_with_only_tvm(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
            )

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    secret_version=secret_version,
                ),
            ],
            return_raw=True,
        )
        self.assertResponseEqual(r, {
            'secrets': [{
                'token': token,
                'token_uuid': token_uuid,
                'code': 'service_ticket_required_error',
                'message': 'Service ticket required',
                'secret_version': secret_version,
                'status': 'error',
            }],
            'status': 'ok',
        })
        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token, secret_version=secret_version, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [{
                    'token': token,
                    'token_uuid': token_uuid,
                    'secret_version': secret_version,
                    'status': 'ok',
                    'value': [{'key': 'password', 'value': '123'}],
                }],
                'status': 'ok',
            })

        with FakeServiceContext(tvm_client_id=2000734):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token, secret_version=secret_version, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [{
                    'token': token,
                    'token_uuid': token_uuid,
                    'secret_version': secret_version,
                    'status': 'error',
                    'code': 'delegation_access_error',
                    'message': 'Access error by delegation token',
                    'reason': 'The token was issued to another TVM application',
                }],
                'status': 'ok',
            })

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                    service_ticket='invalid_service_ticket'
                ),
            ],
            return_raw=True,
        )
        self.assertResponseEqual(
            r,
            {u'secrets': [{u'code': u'service_ticket_parsing_error',
                           u'message': u'Invalid service ticket',
                           u'status': u'error',
                           u'ticket_message': u'Malformed ticket',
                           u'ticket_status': 5,
                           u'token': token,
                           u'token_uuid': token_uuid}],
             u'status': u'ok'},
        )

    def test_get_by_token_with_signature(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='token signature',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [{
                    'token': token,
                    'token_uuid': token_uuid,
                    'secret_version': secret_version,
                    'status': 'ok',
                    'value': [{'key': 'password', 'value': '123'}],
                }],
                'status': 'ok',
            })

            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [{
                    'code': 'delegation_access_error',
                    'message': 'Access error by delegation token',
                    'reason': 'Does not match the signature of the token',
                    'secret_version': secret_version,
                    'status': 'error',
                    'token': token,
                    'token_uuid': token_uuid,
                }],
                'status': 'ok',
            })

    def test_get_by_token_with_nonexistent_and_invalid_tokens(self):
        with PermissionsMock(uid=100):
            secret_uuid_1 = self.client.create_secret(name='secret_1')
            self.client.create_secret(name='secret_2')
            secret_version_1 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_version_2 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid_1,
                tvm_client_id='2000367',
                signature='123',
            )
        with FakeServiceContext(tvm_client_id=2000367):
            with LoggingMock() as log:
                unknown_token = DelegationToken.build_token()
                r = self.client.send_tokenized_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            secret_version=secret_version_1,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token=token_1.split('.')[0],
                            secret_version=secret_version_1,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token=unknown_token,
                            secret_version=secret_version_1,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token=unknown_token,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token='invalid_token',
                            secret_version=secret_version_2,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                    ],
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'secrets': [
                        {
                            'token': token_1,
                            'token_uuid': token_1_uuid,
                            'secret_version': secret_version_1,
                            'status': 'ok',
                            'value': [{'key': 'password', 'value': '123'}],
                        },
                        {
                            'token': token_1.split('.')[0],
                            'token_uuid': token_1_uuid,
                            'secret_version': secret_version_1,
                            'status': 'ok',
                            'value': [{'key': 'password', 'value': '123'}],
                        },
                        {
                            'code': 'nonexistent_entity_error',
                            'message': 'Requested a non-existent entity',
                            'token': unknown_token,
                            'secret_version': secret_version_1,
                            'status': 'error',
                        },
                        {
                            'code': 'nonexistent_entity_error',
                            'message': 'Requested a non-existent entity',
                            'token': unknown_token,
                            'status': 'error',
                        },
                        {
                            'code': 'invalid_token',
                            'message': 'Invalid delegation token',
                            'secret_version': secret_version_2,
                            'status': 'error',
                            'token': 'invalid_token',
                        },
                    ],
                    'status': 'ok',
                })
            self.assertListEqual(
                log.getLogger('statbox').entries,
                [({'action': 'enter',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests'},
                  'INFO',
                  None,
                  None),
                 ({'action': 'success',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_version_1,
                   'source': 'tvm',
                   'token_uuid': token_1_uuid,
                   'tvm_client_id': 2000367},
                  'INFO', None, None,),
                 ({'action': 'success',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_version_1,
                   'source': 'tvm',
                   'token_uuid': token_1_uuid,
                   'tvm_client_id': 2000367},
                  'INFO', None, None,),
                 ({'action': 'error',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'code': 'nonexistent_entity_error',
                   'has_x_ya_service_ticket': True,
                   'hashed_token': DelegationToken.hash_token(unknown_token),
                   'message': 'Requested a non-existent entity',
                   'mode': 'tokenized_requests',
                   'secret_version': secret_version_1,
                   'source': 'tvm',
                   'status': 'error'},
                  'INFO', None, None,),
                 ({'action': 'error',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'code': 'nonexistent_entity_error',
                   'has_x_ya_service_ticket': True,
                   'hashed_token': DelegationToken.hash_token(unknown_token),
                   'message': 'Requested a non-existent entity',
                   'mode': 'tokenized_requests',
                   'secret_version': 'None',
                   'source': 'tvm',
                   'status': 'error'},
                  'INFO', None, None,),
                 ({'action': 'error',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'code': 'invalid_token',
                   'has_x_ya_service_ticket': True,
                   'hashed_token': DelegationToken.hash_token('invalid_token'),
                   'message': 'Invalid delegation token',
                   'mode': 'tokenized_requests',
                   'secret_version': secret_version_2,
                   'source': 'tvm',
                   'status': 'error',
                   'token': '*************'},
                  'INFO', None, None,),
                 ({'action': 'exit',
                   'auth_service_ticket': u'service_ticket',
                   'auth_tvm_app_id': 2000367,
                   'auth_type': 'service_ticket',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests'},
                  'INFO',
                  None,
                  None)]
            )

    def test_good_and_invalid_tokenized_requests(self):
        """
        Проверяем, что ошибки в «подзапросах» не проваливаются на верхний уровень
        ответа ручки.
        """
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature=u'п'*128,
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature=u'п'*128,
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='sec-12345',
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version='bad_version_uuid',
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version='ver-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid='bad_uid',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        secret_version='bad_secret_version',
                        service_ticket='service_ticket',
                        signature=u'подпись'*50,
                        uid='bad_uid',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_version,
                        secret_version=secret_uuid,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token='',
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                u'secrets': [{'token': token,
                              'token_uuid': token_uuid,
                              'secret_version': secret_version,
                              'status': 'ok',
                              'value': [{'key': 'password', 'value': '123'}],
                              'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 1,
                                          u'secret_uuid': [u'invalid_uuid_value']},
                              u'message': u'Validation error',
                              u'secret_uuid': u'bad_secret_uuid',
                              u'secret_version': secret_version,
                              u'status': u'error',
                              u'token': token,
                              u'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 2,
                                          u'secret_uuid': [u'invalid_uuid_value']},
                              u'message': u'Validation error',
                              u'secret_uuid': u'sec-12345',
                              u'secret_version': secret_version,
                              u'status': u'error',
                              u'token': token,
                              u'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 3,
                                          u'secret_version': [u'invalid_uuid_value']},
                              u'message': u'Validation error',
                              u'secret_uuid': secret_uuid,
                              u'secret_version': u'bad_version_uuid',
                              u'status': u'error',
                              u'token': token,
                              u'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 4,
                                          u'secret_version': [u'invalid_uuid_value']},
                              u'message': u'Validation error',
                              u'secret_uuid': secret_uuid,
                              u'secret_version': u'ver-12345',
                              u'status': u'error',
                              u'token': token,
                              u'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 5, u'uid': [u'not_integer']},
                              u'message': u'Validation error',
                              u'secret_uuid': secret_uuid,
                              u'secret_version': secret_version,
                              u'status': u'error',
                              u'token': token,
                              u'uid': u'bad_uid'},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 6,
                                          u'secret_uuid': [u'invalid_uuid_value'],
                                          u'secret_version': [u'invalid_uuid_value'],
                                          u'signature': [u'length: 1_to_255'],
                                          u'uid': [u'not_integer']},
                              u'message': u'Validation error',
                              u'secret_uuid': u'bad_secret_uuid',
                              u'secret_version': u'bad_secret_version',
                              u'status': u'error',
                              u'token': token,
                              u'uid': u'bad_uid'},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 7,
                                          u'secret_uuid': [u'invalid_uuid_prefix'],
                                          u'secret_version': [u'invalid_uuid_prefix']},
                              u'message': u'Validation error',
                              u'secret_uuid': secret_version,
                              u'secret_version': secret_uuid,
                              u'status': u'error',
                              u'token': token,
                              u'uid': 100},
                             {u'code': u'validation_error',
                              u'errors': {u'index': 8, u'token': [u'required']},
                              u'message': u'Validation error',
                              u'secret_uuid': secret_uuid,
                              u'secret_version': secret_version,
                              u'status': u'error',
                              u'uid': 100}],
                u'status': u'ok'
            })

    def test_only_invalid_tokenized_requests(self):
        """
        Проверяем, что корректно отрабатываем, если все запросы плохие.
        """
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='token signature',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='sec-12345',
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version='bad_version_uuid',
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version='ver-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid='bad_uid',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        secret_version='bad_secret_version',
                        service_ticket='service_ticket',
                        signature=u'подпись'*50,
                        uid='bad_uid',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_version,
                        secret_version=secret_uuid,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token='',
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseOk(r)
            self.assertEqual(
                8,
                reduce(
                    lambda c, y: c + 1 if y['status'] == 'error' else c,
                    r.json()['secrets'],
                    0,
                ),
            )

    def test_more_than_100_tokenized_requests(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token, _ = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='token signature',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    )
                    for i in range(105)
                ],
                return_raw=True,
            )
            self.assertResponseError(
                r,
                errors.ValidationError({
                    'tokenized_requests': 'size_1_100',
                }),
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        secret_version=secret_version,
                        service_ticket='service_ticket',
                        signature='token signature',
                        uid=100,
                    )
                    for i in range(100)
                ],
                return_raw=True,
            )
            self.assertResponseOk(r)

    def test_log_consumer_tvm_app(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1}, ttl=30)
                    token_1, token_1_uuid = self.client.create_token(
                        secret_1,
                        tvm_client_id='2000367',
                        signature='123',
                    )

        self.client.rsa_auth = False
        self.client.service_ticket = VALID_SERVICE_TICKET_1
        with LoggingMock() as log:
            with FakeServiceContext(tvm_client_id=2000367):
                self.client.send_tokenized_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            secret_version=version_1,
                            signature='123',
                            service_ticket=VALID_SERVICE_TICKET_1,
                        ),
                    ],
                    consumer='dev',
                    return_raw=True,
                )
        self.assertListEqual(
            log.getLogger('statbox').entries,
            [({'action': 'enter',
               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
               'auth_tvm_app_id': 2000367,
               'auth_type': 'service_ticket',
               'consumer': 'dev',
               'has_x_ya_service_ticket': True,
               'mode': 'tokenized_requests'},
              'INFO',
              None,
              None),
             ({'action': 'success',
               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
               'auth_tvm_app_id': 2000367,
               'auth_type': 'service_ticket',
               'consumer': 'dev',
               'has_x_ya_service_ticket': True,
               'mode': 'tokenized_requests',
               'secret_version': version_1,
               'source': 'tvm',
               'token_uuid': token_1_uuid,
               'tvm_client_id': 2000367},
              'INFO',
              None,
              None),
             ({'action': 'exit',
               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
               'auth_tvm_app_id': 2000367,
               'auth_type': 'service_ticket',
               'consumer': 'dev',
               'has_x_ya_service_ticket': True,
               'mode': 'tokenized_requests'},
              'INFO',
              None,
              None)]
        )

        self.client.service_ticket = None
        with LoggingMock() as log:
            with FakeServiceContext(tvm_client_id=2000367):
                self.client.send_tokenized_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            secret_version=version_1,
                            signature='123',
                            service_ticket=VALID_SERVICE_TICKET_1,
                        ),
                    ],
                    return_raw=True,
                )
        self.assertListEqual(
            log.getLogger('statbox').entries,
            [({'action': 'enter',
               'has_x_ya_service_ticket': False,
               'mode': 'tokenized_requests'},
              'INFO',
              None,
              None),
             ({'action': 'success',
               'has_x_ya_service_ticket': False,
               'mode': 'tokenized_requests',
               'secret_version': version_1,
               'source': 'tvm',
               'token_uuid': token_1_uuid,
               'tvm_client_id': 2000367},
              'INFO',
              None,
              None),
             ({'action': 'exit',
               'has_x_ya_service_ticket': False,
               'mode': 'tokenized_requests'},
              'INFO',
              None,
              None)]
        )

    def test_token_with_expired_version(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1}, ttl=30)
                    token_1, token_1_uuid = self.client.create_token(
                        secret_1,
                        tvm_client_id='2000367',
                        signature='123',
                    )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token_1,
                        secret_version=version_1,
                        signature='123',
                        service_ticket='service_ticket',
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(
                r,
                {
                    'secrets': [{
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                        'secret_version': version_1,
                        'status': 'warning',
                        'value': [{'key': 'a', 'value': '1'}],
                        'warning_message': 'version is expired',
                    }],
                    'status': 'ok',
                },
            )

    def test_get_head_version_by_token(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret(
                name='secret_1',
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret,
            )
            self.client.create_secret_version(
                secret_uuid=secret,
                value=[{'key': 'password', 'value': '123'}],
            )
            self.client.create_secret_version(
                secret_uuid=secret,
                value=[{'key': 'password', 'value': '456'}],
            )
            version = self.client.create_secret_version(
                secret_uuid=secret,
                value=[{'key': 'password', 'value': '789'}],
            )

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token,
                ),
            ],
            return_raw=True,
        )
        self.assertResponseEqual(r, {
            'secrets': [{
                'token': token,
                'token_uuid': token_uuid,
                'secret_version': version,
                'status': 'ok',
                'value': [{'key': 'password', 'value': '789'}],
            }],
            'status': 'ok',
        })

    def test_get_mixed_versions_by_token(self):
        with PermissionsMock(uid=100):
            secret_1 = self.client.create_secret(
                name='secret_1',
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid=secret_1,
                comment='secret_1 token',
            )
            self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_1_version_2 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '456'}],
            )
            secret_1_version_3 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '789'}],
            )

            secret_2 = self.client.create_secret(
                name='secret_2',
            )
            token_2, token_2_uuid = self.client.create_token(
                secret_uuid=secret_2,
            )
            secret_2_version_1 = self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'password2', 'value': '321'}],
            )
            secret_2_version_2 = self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'password2', 'value': '654'}],
            )
            secret_2_version_3 = self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'password2', 'value': '010'}],
            )
            self.client.update_version(secret_2_version_3, state='hidden')

        with LoggingMock() as log:
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token_1,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        secret_version=secret_1_version_2,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        secret_version=secret_2_version_1,
                    ),
                    TokenizedRequest(
                        token=token_2,
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [
                    {
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                        'secret_version': secret_1_version_3,
                        'status': 'ok',
                        'value': [{'key': 'password', 'value': '789'}],
                        'comment': 'secret_1 token',
                    },
                    {
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                        'secret_version': secret_1_version_2,
                        'status': 'ok',
                        'value': [{'key': 'password', 'value': '456'}],
                        'comment': 'secret_1 token',
                    },
                    {
                        'secret_version': secret_2_version_1,
                        'status': 'ok',
                        'token': token_2,
                        'token_uuid': token_2_uuid,
                        'value': [{'key': 'password2', 'value': '321'}],
                    },
                    {
                        'secret_version': secret_2_version_2,
                        'status': 'ok',
                        'token': token_2,
                        'token_uuid': token_2_uuid,
                        'value': [{'key': 'password2', 'value': '654'}],
                    },
                ],
                'status': 'ok',
            })
            self.assertListEqual(
                log.getLogger('statbox').entries,
                [({'action': 'enter',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests'},
                  'INFO',
                  None,
                  None),
                 ({'action': 'success',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_1_version_3,
                   'source': 'tvm',
                   'token_uuid': token_1_uuid,
                   'tvm_client_id': None},
                  'INFO',
                  None,
                  None),
                 ({'action': 'success',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_1_version_2,
                   'source': 'tvm',
                   'token_uuid': token_1_uuid,
                   'tvm_client_id': None},
                  'INFO',
                  None,
                  None),
                 ({'action': 'success',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_2_version_1,
                   'source': 'tvm',
                   'token_uuid': token_2_uuid,
                   'tvm_client_id': None},
                  'INFO',
                  None,
                  None),
                 ({'action': 'success',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests',
                   'secret_version': secret_2_version_2,
                   'source': 'tvm',
                   'token_uuid': token_2_uuid,
                   'tvm_client_id': None},
                  'INFO',
                  None,
                  None),
                 ({'action': 'exit',
                   'has_x_ya_service_ticket': True,
                   'mode': 'tokenized_requests'},
                  'INFO',
                  None,
                  None)],
            )

    def test_get_deleted_secret_versions_by_token(self):
        with PermissionsMock(uid=100):
            secret_1 = self.client.create_secret(
                name='secret_1',
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid=secret_1,
            )
            self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_1_version_2 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '456'}],
            )
            secret_1_version_3 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '789'}],
            )
            self.client.update_secret(secret_1, state='hidden')

        r = self.client.send_tokenized_requests(
            tokenized_requests=[
                TokenizedRequest(
                    token=token_1,
                ),
                TokenizedRequest(
                    token=token_1,
                    secret_version=secret_1_version_2,
                ),
            ],
            return_raw=True,
        )
        self.assertResponseEqual(r, {
            'secrets': [
                {
                    'token': token_1,
                    'token_uuid': token_1_uuid,
                    'secret_version': secret_1_version_3,
                    'status': 'warning',
                    'value': [{'key': 'password', 'value': '789'}],
                    'warning_message': 'version is hidden',
                },
                {
                    'token': token_1,
                    'token_uuid': token_1_uuid,
                    'secret_version': secret_1_version_2,
                    'status': 'warning',
                    'value': [{'key': 'password', 'value': '456'}],
                    'warning_message': 'version is hidden',
                },
            ],
            'status': 'ok',
        })

    def test_get_by_revoked_token(self):
        with PermissionsMock(uid=100):
            secret_uuid_1 = self.client.create_secret(name='secret_1')
            self.client.create_secret(name='secret_2')
            secret_version_1 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_version_2 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid_1,
                tvm_client_id='2000367',
                signature='123',
            )

            token_2, token_2_uuid = self.client.create_token(
                secret_uuid_1,
                tvm_client_id='2000367',
                signature='123',
            )
            self.client.revoke_token(token_2_uuid)

        with FakeServiceContext(tvm_client_id=2000367):
            with LoggingMock() as log:
                r = self.client.send_tokenized_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            secret_version=secret_version_1,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token=token_2,
                            secret_version=secret_version_2,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                        TokenizedRequest(
                            token=token_2,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                    ],
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'secrets': [
                        {
                            'secret_version': secret_version_1,
                            'status': 'ok',
                            'token': token_1,
                            'token_uuid': token_1_uuid,
                            'value': [{'key': 'password', 'value': '123'}]
                        },
                        {
                            'code': 'token_revoked',
                            'message': 'Delegation token revoked',
                            'secret_version': secret_version_2,
                            'status': 'error',
                            'token': token_2,
                            'token_uuid': token_2_uuid,
                        },
                        {
                            'code': 'token_revoked',
                            'message': 'Delegation token revoked',
                            'status': 'error',
                            'token': token_2,
                            'token_uuid': token_2_uuid,
                        },
                    ],
                    'status': 'ok'
                })
                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests'},
                      'INFO',
                      None,
                      None),
                     ({'action': 'success',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests',
                       'secret_version': secret_version_1,
                       'source': 'tvm',
                       'token_uuid': token_1_uuid,
                       'tvm_client_id': 2000367},
                      'INFO', None, None,),
                     ({'action': 'error',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'code': 'token_revoked',
                       'has_x_ya_service_ticket': True,
                       'hashed_token': DelegationToken.hash_token(token_2),
                       'message': 'Delegation token revoked',
                       'mode': 'tokenized_requests',
                       'secret_version': secret_version_2,
                       'source': 'tvm',
                       'status': 'error',
                       'token_uuid': token_2_uuid},
                      'INFO', None, None,),
                     ({'action': 'error',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'code': 'token_revoked',
                       'has_x_ya_service_ticket': True,
                       'hashed_token': DelegationToken.hash_token(token_2),
                       'message': 'Delegation token revoked',
                       'mode': 'tokenized_requests',
                       'secret_version': 'None',
                       'source': 'tvm',
                       'status': 'error',
                       'token_uuid': token_2_uuid},
                      'INFO', None, None,),
                     ({'action': 'exit',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests'},
                      'INFO',
                      None,
                      None)],
                )

    def test_check_secret_uuid_for_token(self):
        with PermissionsMock(uid=100):
            secret_uuid_1 = self.client.create_secret(name='secret_1')
            self.client.create_secret(name='secret_2')
            secret_version_1 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_version_2 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid_1,
                tvm_client_id='2000367',
                signature='123',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            invalid_secret_uuid = SecretUUIDType.create_ulid()
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token_1,
                        secret_version=secret_version_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_uuid_1),
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_uuid_1),
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(invalid_secret_uuid),
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [
                    {
                        'secret_version': secret_version_1,
                        'status': 'ok',
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                        'value': [{'key': 'password', 'value': '123'}]
                    },
                    {
                        'secret_version': secret_version_2,
                        'status': 'ok',
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                        'value': [{'key': 'password', 'value': '123'}]
                    },
                    {
                        'code': 'token_does_not_match_secret',
                        'message': 'Token does not match secret uuid',
                        'status': 'error',
                        'secret_uuid': invalid_secret_uuid,
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                    }
                ],
                'status': 'ok'
            })

    def test_revoke_tokens_from_tvm_app(self):
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
            )
            token_2, token_2_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
            )
            token_3, token_3_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='sig 3'
            )
            token_4, token_4_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
            )
            token_5, token_5_uuid = self.client.create_token(
                tvm_client_id='2000367',
                secret_uuid=secret_uuid,
            )

        with FakeServiceContext(tvm_client_id=2000734):
            invalid_secret_uuid = SecretUUIDType.create_ulid()
            with LoggingMock() as log:
                r = self.client.send_tokenized_revoke_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            service_ticket='service_ticket',
                            secret_uuid=str(invalid_secret_uuid),
                        ),
                    ],
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'result': [{
                        'code': 'token_does_not_match_secret',
                        'message': 'Token does not match secret uuid',
                        'status': 'error',
                        'secret_uuid': invalid_secret_uuid,
                        'token': token_1,
                        'token_uuid': token_1_uuid,
                    }],
                    'status': 'ok'
                })
                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000734,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens'},
                      'INFO', None, None,),
                     ({'action': 'error',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000734,
                       'auth_type': 'service_ticket',
                       'code': 'token_does_not_match_secret',
                       'has_x_ya_service_ticket': True,
                       'hashed_token': DelegationToken.hash_token(token_1),
                       'message': 'Token does not match secret uuid',
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'status': 'error',
                       'token_uuid': token_1_uuid},
                      'INFO', None, None,),
                     ({'action': 'exit',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000734,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens'},
                      'INFO', None, None,)]
                )

        with FakeServiceContext(tvm_client_id=2000734):
            r = self.client.send_tokenized_revoke_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token_1, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'result': [{
                    'token': token_1,
                    'token_uuid': token_1_uuid,
                    'status': 'error',
                    'code': 'delegation_access_error',
                    'message': 'Access error by delegation token',
                    'reason': 'The token was issued to another TVM application',
                }],
                'status': 'ok',
            })

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_revoke_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token_3, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'result': [{
                    'token': token_3,
                    'token_uuid': token_3_uuid,
                    'status': 'error',
                    'code': 'delegation_access_error',
                    'message': 'Access error by delegation token',
                    'reason': 'Does not match the signature of the token',
                }],
                'status': 'ok',
            })

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_revoke_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token_4, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'result': [{
                    'code': 'token_not_associated_with_tvm_app',
                    'message': 'Delegation token is not associated with the tvm-app',
                    'status': 'error',
                    'token': token_4,
                    'token_uuid': token_4_uuid,
                }],
                'status': u'ok',
            })

        with FakeServiceContext(tvm_client_id=2000367):
            unknown_token = DelegationToken.build_token()
            with LoggingMock() as log:
                r = self.client.send_tokenized_revoke_requests(
                    tokenized_requests=[
                        TokenizedRequest(token=token_1, service_ticket='service_ticket'),
                        TokenizedRequest(token=token_3, service_ticket='service_ticket', signature='sig 3'),
                        TokenizedRequest(token=token_5, service_ticket='service_ticket', secret_uuid=secret_uuid),
                        TokenizedRequest(token=unknown_token, service_ticket='service_ticket'),
                        TokenizedRequest(token='invalid_token', service_ticket='service_ticket'),
                    ],
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'result': [
                        {'status': 'ok', 'token': token_1, 'token_uuid': token_1_uuid},
                        {'status': 'ok', 'token': token_3, 'token_uuid': token_3_uuid},
                        {'status': 'ok', 'token': token_5, 'token_uuid': token_5_uuid},
                        {
                            'code': 'nonexistent_entity_error',
                            'message': 'Requested a non-existent entity',
                            'status': 'error',
                            'token': unknown_token,
                        },
                        {
                            'code': 'invalid_token',
                            'message': 'Invalid delegation token',
                            'status': 'error',
                            'token': 'invalid_token',
                        },
                    ],
                    'status': 'ok',
                })
                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens'},
                      'INFO', None, None,),
                     ({'action': 'success',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'token_uuid': token_1_uuid,
                       'tvm_client_id': 2000367},
                      'INFO', None, None,),
                     ({'action': 'success',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'token_uuid': token_3_uuid,
                       'tvm_client_id': 2000367},
                      'INFO', None, None,),
                     ({'action': 'success',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'token_uuid': token_5_uuid,
                       'tvm_client_id': 2000367},
                      'INFO', None, None,),
                     ({'action': 'error',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'code': 'nonexistent_entity_error',
                       'has_x_ya_service_ticket': True,
                       'hashed_token': DelegationToken.hash_token(unknown_token),
                       'message': 'Requested a non-existent entity',
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'status': 'error'},
                      'INFO', None, None,),
                     ({'action': 'error',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'code': 'invalid_token',
                       'has_x_ya_service_ticket': True,
                       'hashed_token': 'f81df2268c4358fa03ee70f3c76d3e5d70d5de33a5043649ee72362284b7c5f6',
                       'message': 'Invalid delegation token',
                       'mode': 'tokenized_revoke_tokens',
                       'source': 'tvm',
                       'status': 'error',
                       'token': '*************'},
                      'INFO', None, None,),
                     ({'action': 'exit',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_revoke_tokens'},
                      'INFO', None, None,)]
                )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(token=token_1, service_ticket='service_ticket'),
                    TokenizedRequest(token=token_2, service_ticket='service_ticket'),
                    TokenizedRequest(token=token_3, service_ticket='service_ticket', signature='sig 3'),
                    TokenizedRequest(token=token_4, service_ticket='service_ticket'),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'secrets': [
                    {'code': 'token_revoked',
                     'message': 'Delegation token revoked',
                     'status': 'error',
                     'token': token_1,
                     'token_uuid': token_1_uuid},
                    {'secret_version': secret_version,
                     'status': 'ok',
                     'token': token_2,
                     'token_uuid': token_2_uuid,
                     'value': [{'key': 'password', 'value': '123'}]},
                    {'code': 'token_revoked',
                     'message': 'Delegation token revoked',
                     'status': 'error',
                     'token': token_3,
                     'token_uuid': token_3_uuid},
                    {'secret_version': secret_version,
                     'status': 'ok',
                     'token': token_4,
                     'token_uuid': token_4_uuid,
                     'value': [{'key': 'password', 'value': '123'}]},
                ],
                'status': 'ok'
            })

    def test_good_and_invalid_tokenized_revoke_requests(self):
        """
        Проверяем, что ошибки в «подзапросах» не проваливаются на верхний уровень
        ответа ручки.
        """
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='token signature',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_revoke_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid=secret_uuid,
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='sec-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='ver-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token='',
                        secret_uuid=secret_uuid,
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                u'result': [{u'status': u'ok',
                             u'token': token,
                             u'token_uuid': token_uuid},
                            {u'code': u'validation_error',
                             u'errors': {u'index': 1,
                                         u'secret_uuid': [u'invalid_uuid_value']},
                             u'message': u'Validation error',
                             u'status': u'error',
                             u'secret_uuid': 'bad_secret_uuid',
                             u'token': token},
                            {u'code': u'validation_error',
                             u'errors': {u'index': 2,
                                         u'secret_uuid': [u'invalid_uuid_value']},
                             u'message': u'Validation error',
                             u'status': u'error',
                             u'secret_uuid': u'sec-12345',
                             u'token': token},
                            {u'code': u'validation_error',
                             u'errors': {u'index': 3,
                                         u'secret_uuid': [u'invalid_uuid_prefix']},
                             u'message': u'Validation error',
                             u'status': u'error',
                             u'secret_uuid': u'ver-12345',
                             u'token': token},
                            {u'code': u'validation_error',
                             u'errors': {u'index': 4, u'token': [u'required']},
                             u'message': u'Validation error',
                             u'status': u'error',
                             u'secret_uuid': secret_uuid}],
                u'status': u'ok',
            })

    def test_only_invalid_tokenized_revoke_requests(self):
        """
        Проверяем, что корректно отрабатываем, если все запросы плохие.
        """
        with PermissionsMock(uid=100):
            secret_uuid = self.client.create_secret(
                name='secret_1',
            )
            token, token_uuid = self.client.create_token(
                secret_uuid=secret_uuid,
                tvm_client_id='2000367',
                signature='token signature',
            )

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_revoke_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token,
                        secret_uuid='bad_secret_uuid',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='sec-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token=token,
                        secret_uuid='ver-12345',
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                    TokenizedRequest(
                        token='',
                        secret_uuid=secret_uuid,
                        service_ticket='service_ticket',
                        signature='token signature',
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseOk(r)
            self.assertEqual(
                4,
                reduce(
                    lambda c, y: c + 1 if y['status'] == 'error' else c,
                    r.json()['result'],
                    0,
                ),
            )

    def test_check_uid_for_token(self):
        with PermissionsMock(uid=100):
            secret_1 = self.client.create_secret(name='secret_1')
            secret_1_version_1 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            secret_1_version_2 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_1,
                tvm_client_id='2000367',
                signature='123',
            )

            secret_2 = self.client.create_secret(name='secret_2')
            self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'login', 'value': '123'}],
            )
            secret_2_version_2 = self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'login', 'value': '123'}],
            )
            token_2, token_2_uuid = self.client.create_token(
                secret_2,
                tvm_client_id='2000367',
                signature='123',
            )
            self.client.add_user_role_to_secret(secret_1, 'READER', uid=101)
            self.client.add_user_role_to_secret(secret_2, 'OWNER', uid=101)
            self.client.add_user_role_to_secret(secret_2, 'APPENDER', uid=102)
            self.client.add_user_role_to_secret(secret_2, 'APPENDER', uid=102)
            self.client.add_user_role_to_secret(secret_1, 'READER', staff_id=2864)
            self.client.add_user_role_to_secret(secret_1, 'READER', abc_id=14, abc_scope='tvm_management')
            self.client.add_user_role_to_secret(secret_1, 'READER', abc_id=50)

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token_1,
                        secret_version=secret_1_version_1,
                        signature='123',
                        service_ticket='service_ticket',
                    ),
                    TokenizedRequest(
                        token=token_1,
                        secret_version=secret_1_version_1,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=100,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_1),
                        uid=101,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=101,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=102,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=102,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_1),
                        uid=1120000000038274,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_1),
                        uid=1120000000005594,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        secret_uuid=str(secret_1),
                        uid=1120000000027354,
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                u'secrets': [
                    {u'secret_version': secret_1_version_1,
                     u'status': u'ok',
                     u'token': token_1,
                     u'token_uuid': str(token_1_uuid),
                     u'value': [{u'key': u'password', u'value': u'123'}]},
                    {u'secret_version': secret_1_version_1,
                     u'status': u'ok',
                     u'token': token_1,
                     u'token_uuid': str(token_1_uuid),
                     u'uid': 100,
                     u'value': [{u'key': u'password', u'value': u'123'}]},
                    {u'secret_version': secret_1_version_2,
                     u'status': u'ok',
                     u'token': token_1,
                     u'token_uuid': str(token_1_uuid),
                     u'uid': 101,
                     u'value': [{u'key': u'password', u'value': u'123'}]},
                    {u'secret_version': secret_2_version_2,
                     u'status': u'ok',
                     u'token': token_2,
                     u'token_uuid': str(token_2_uuid),
                     u'uid': 101,
                     u'value': [{u'key': u'login', u'value': u'123'}]},
                    {u'code': u'access_error',
                     u'message': u'Access denied',
                     u'status': u'error',
                     u'token': token_1,
                     u'token_uuid': str(token_1_uuid),
                     u'uid': 102},
                    {u'code': u'access_error',
                     u'message': u'Access denied',
                     u'status': u'error',
                     u'token': token_2,
                     u'token_uuid': str(token_2_uuid),
                     u'uid': 102},
                    {u'secret_version': secret_1_version_2,
                     u'status': u'ok',
                     u'token': token_1,
                     u'token_uuid': token_1_uuid,
                     u'uid': 1120000000038274,
                     u'value': [{u'key': u'password', u'value': u'123'}]},
                    {u'secret_version': secret_1_version_2,
                     u'status': u'ok',
                     u'token': token_1,
                     u'token_uuid': token_1_uuid,
                     u'uid': 1120000000005594,
                     u'value': [{u'key': u'password', u'value': u'123'}]},
                    {u'code': u'access_error',
                     u'message': u'Access denied',
                     u'status': u'error',
                     u'secret_uuid': secret_1,
                     u'token': token_1,
                     u'token_uuid': token_1_uuid,
                     u'uid': 1120000000027354},
                ],
                u'status': u'ok',
            })

    def test_check_uid_for_abc_scopes_and_roles(self):
        with PermissionsMock(uid=100):
            secret_1 = self.client.create_secret(name='secret_1')
            secret_1_version_1 = self.client.create_secret_version(
                secret_uuid=secret_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_1,
                tvm_client_id='2000367',
                signature='123',
            )

            secret_2 = self.client.create_secret(name='secret_2')
            secret_2_version_1 = self.client.create_secret_version(
                secret_uuid=secret_2,
                value=[{'key': 'login2', 'value': '456'}],
            )
            token_2, token_2_uuid = self.client.create_token(
                secret_2,
                tvm_client_id='2000367',
                signature='123',
            )

            self.client.add_user_role_to_secret(secret_1, 'READER', abc_id=14, abc_scope='tvm_management')
            self.client.add_user_role_to_secret(secret_2, 'READER', abc_id=14, abc_role_id=5)

            self.fixture.assign_abc_role_or_scope_to_uid(uid=101, abc_id=14, abc_scope_id=17)
            self.fixture.assign_abc_role_or_scope_to_uid(uid=102, abc_id=14, abc_role_id=5)

            # 103 uid не должен иметь доступ ни к одному из секретов
            self.fixture.assign_abc_role_or_scope_to_uid(uid=103, abc_id=14, abc_role_id=17)
            self.fixture.assign_abc_role_or_scope_to_uid(uid=103, abc_id=14, abc_scope_id=4)

        with FakeServiceContext(tvm_client_id=2000367):
            r = self.client.send_tokenized_requests(
                tokenized_requests=[
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=101,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=101,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=102,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=102,
                    ),
                    TokenizedRequest(
                        token=token_1,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=103,
                    ),
                    TokenizedRequest(
                        token=token_2,
                        signature='123',
                        service_ticket='service_ticket',
                        uid=103,
                    ),
                ],
                return_raw=True,
            )
            self.assertResponseEqual(
                r,
                {u'secrets': [{u'secret_version': secret_1_version_1,
                               u'status': u'ok',
                               u'token': token_1,
                               u'token_uuid': token_1_uuid,
                               u'uid': 101,
                               u'value': [{u'key': u'password', u'value': u'123'}]},
                              {u'code': u'access_error',
                               u'message': u'Access denied',
                               u'status': u'error',
                               u'token': token_2,
                               u'token_uuid': token_2_uuid,
                               u'uid': 101},
                              {u'code': u'access_error',
                               u'message': u'Access denied',
                               u'status': u'error',
                               u'token': token_1,
                               u'token_uuid': token_1_uuid,
                               u'uid': 102},
                              {u'secret_version': secret_2_version_1,
                               u'status': u'ok',
                               u'token': token_2,
                               u'token_uuid': token_2_uuid,
                               u'uid': 102,
                               u'value': [{u'key': u'login2', u'value': u'456'}]},
                              {u'code': u'access_error',
                               u'message': u'Access denied',
                               u'status': u'error',
                               u'token': token_1,
                               u'token_uuid': token_1_uuid,
                               u'uid': 103},
                              {u'code': u'access_error',
                               u'message': u'Access denied',
                               u'status': u'error',
                               u'token': token_2,
                               u'token_uuid': token_2_uuid,
                               u'uid': 103}],
                 u'status': u'ok'},
            )

    def test_send_tokenized_request_for_token_without_signature(self):
        """
        Проверяем логирование запросов с подписью к токенам без подписи.
        Ожидаем в statbox-логе поле skipped_signature_check
        """
        with PermissionsMock(uid=100):
            secret_uuid_1 = self.client.create_secret(name='secret_1')
            secret_version_1 = self.client.create_secret_version(
                secret_uuid=secret_uuid_1,
                value=[{'key': 'password', 'value': '123'}],
            )
            token_1, token_1_uuid = self.client.create_token(
                secret_uuid_1,
                tvm_client_id='2000367',
                signature=None,
            )

        with FakeServiceContext(tvm_client_id=2000367):
            with LoggingMock() as log:
                r = self.client.send_tokenized_requests(
                    tokenized_requests=[
                        TokenizedRequest(
                            token=token_1,
                            secret_version=secret_version_1,
                            signature='123',
                            service_ticket='service_ticket',
                        ),
                    ],
                    consumer='dev',
                    return_raw=True,
                )
                self.assertResponseOk(r)
                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'consumer': u'dev',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests'},
                      'INFO',
                      None,
                      None),
                     ({'action': 'success',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'consumer': u'dev',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests',
                       'secret_version': secret_version_1,
                       'skipped_signature_check': u'123',
                       'source': 'tvm',
                       'token_uuid': token_1_uuid,
                       'tvm_client_id': 2000367},
                      'INFO',
                      None,
                      None),
                     ({'action': 'exit',
                       'auth_service_ticket': u'service_ticket',
                       'auth_tvm_app_id': 2000367,
                       'auth_type': 'service_ticket',
                       'consumer': u'dev',
                       'has_x_ya_service_ticket': True,
                       'mode': 'tokenized_requests',
                       'skipped_signature_check': u'123'},
                      'INFO',
                      None,
                      None)]
                )
