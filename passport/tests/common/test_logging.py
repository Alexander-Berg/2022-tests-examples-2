# -*- coding: utf-8 -*-

from library.python.vault_client.auth import RSAPrivateKeyAuth
from passport.backend.vault.api import errors
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_OAUTH_TOKEN_1,
    TEST_RSA_PRIVATE_KEY_1,
    TEST_RSA_PUBLIC_KEY_1,
    VALID_SERVICE_TICKET_1,
    VALID_SERVICE_TICKET_SINGLESS_1,
    VALID_USER_TICKET_1,
    VALID_USER_TICKET_SIGNLESS_1,
)


class TestLogging(BaseTestClass):
    send_user_ticket = False

    def test_user_ticket_auth_logging(self):
        with PermissionsMock(uid=100, service_ticket=VALID_SERVICE_TICKET_1):
            with LoggingMock() as logging_mock:
                self.client.rsa_auth = False
                self.client.user_ticket = VALID_USER_TICKET_1
                secret = self.client.create_secret('secret_password')

            assert logging_mock.getLogger('statbox').entries == [
                ({'action': 'enter',
                  'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                  'auth_tvm_app_id': 1,
                  'auth_type': 'user_ticket',
                  'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                  'mode': 'create_secret',
                  'tvm_grants': 'granted',
                  'auth_uid': 100}, 'INFO', None, None,),
                ({'action': 'success',
                  'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                  'auth_tvm_app_id': 1,
                  'auth_type': 'user_ticket',
                  'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                  'created_by': 100,
                  'mode': 'create_secret',
                  'name': u'secret_password',
                  'secret_uuid': secret,
                  'tvm_grants': 'granted',
                  'auth_uid': 100}, 'INFO', None, None,),
                ({'action': 'exit',
                  'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                  'auth_tvm_app_id': 1,
                  'auth_type': 'user_ticket',
                  'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                  'mode': 'create_secret',
                  'tvm_grants': 'granted',
                  'auth_uid': 100}, 'INFO', None, None,),
            ]

    def test_oauth_auth_logging(self):
        with PermissionsMock(oauth={'uid': 100, 'scope': 'vault:use'}):
            self.client.authorization = TEST_OAUTH_TOKEN_1
            with LoggingMock() as logging_mock:
                secret = self.client.create_secret('secret_password')

            assert logging_mock.getLogger('statbox').entries == [
                ({'action': 'enter',
                  'auth_oauth_token': 'token-o*******',
                  'auth_type': 'oauth',
                  'mode': 'create_secret',
                  'auth_uid': 100},
                 'INFO', None, None,),
                ({'action': 'success',
                  'auth_oauth_token': 'token-o*******',
                  'auth_type': 'oauth',
                  'created_by': 100,
                  'mode': 'create_secret',
                  'name': u'secret_password',
                  'secret_uuid': secret,
                  'auth_uid': 100},
                 'INFO', None, None,),
                ({'action': 'exit',
                  'auth_oauth_token': 'token-o*******',
                  'auth_type': 'oauth',
                  'mode': 'create_secret',
                  'auth_uid': 100},
                 'INFO', None, None,),
            ]

    def test_rsa_auth_logging(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.client.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
            self.client.rsa_login = 'user'
            with LoggingMock() as logging_mock:
                secret = self.client.create_secret('secret_password')

            assert logging_mock.getLogger('statbox').entries == [
                ({'action': 'enter',
                  'auth_rsa_signature_version': 3,
                  'auth_type': 'rsa',
                  'mode': 'create_secret',
                  'auth_uid': 100,
                  'auth_login': 'user'},
                 'INFO', None, None,),
                ({'action': 'success',
                  'auth_rsa_signature_version': 3,
                  'auth_type': 'rsa',
                  'created_by': 100,
                  'mode': 'create_secret',
                  'name': u'secret_password',
                  'secret_uuid': secret,
                  'auth_uid': 100,
                  'auth_login': 'user'},
                 'INFO', None, None,),
                ({'action': 'exit',
                  'auth_rsa_signature_version': 3,
                  'auth_type': 'rsa',
                  'mode': 'create_secret',
                  'auth_uid': 100,
                  'auth_login': 'user'},
                 'INFO', None, None,)
            ]

    def test_errors_logging(self):
        with PermissionsMock(uid=100, service_ticket=VALID_SERVICE_TICKET_1):
            with LoggingMock() as logging_mock:
                self.client.rsa_auth = False
                self.client.user_ticket = VALID_USER_TICKET_1
                r = self.client.get_secret('sec-00000000000000000000000000', return_raw=True)
                self.assertResponseError(r, errors.NonexistentEntityError)

            assert logging_mock.getLogger('statbox').entries == [
                ({'action': 'enter',
                  'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                  'auth_tvm_app_id': 1,
                  'auth_type': 'user_ticket',
                  'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                  'mode': 'secret',
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
                  'mode': 'secret',
                  'class': 'Secret',
                  'code': 'nonexistent_entity_error',
                  'id': u'sec-00000000000000000000000000',
                  'message': 'Requested a non-existent entity (Secret, sec-00000000000000000000000000)',
                  'status': 'error',
                  'tvm_grants': 'granted',
                  'auth_uid': 100},
                 'INFO',
                 None,
                 None),
            ]
