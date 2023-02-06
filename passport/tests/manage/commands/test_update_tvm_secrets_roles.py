# -*- coding: utf-8 -*-

from django.conf import settings
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBTemporaryError,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ABC_SERVICE_ID,
    TEST_UID,
)
from passport.backend.oauth.tvm_api.tests.base import TEST_ABC_REQUEST_ID
from passport.backend.oauth.tvm_api.tests.base.vault_test import (
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_SECRET_UUID_2,
    TEST_VAULT_VERSION_UUID_1,
    TEST_VAULT_VERSION_UUID_2,
    VaultMockMixin,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient
from passport.backend.oauth.tvm_api.tvm_api.management.commands.update_tvm_secrets_roles import (
    Command as UpdateTVMSecretsRoles,
)

from ..base import BaseTVMManagementCommandTestCase


class TestUpdateTVMSecretsRoles(BaseTVMManagementCommandTestCase, VaultMockMixin):
    command_class = UpdateTVMSecretsRoles
    default_command_kwargs = {
        'chunk_size': 10,
        'use_pauses': False,
        'pause_length': 1.0,
    }
    logger_name = 'management.update_tvm_secrets_roles'

    def create_client(self, name, abc_service_id=None, abc_request_id=None, vault_secret_uuid=None, vault_version_uuid=None):
        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name=name,
        )) as client:
            if abc_service_id is not None:
                client.abc_service_id = abc_service_id
            if abc_request_id is not None:
                client.abc_request_id = abc_request_id
            client.vault_secret_uuid = vault_secret_uuid or ''
            client.vault_version_uuid = vault_version_uuid or ''

    def test_ok(self):
        self.create_client(name='APP #1')
        self.create_client(
            name='APP #2',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
        )
        self.create_client(
            name='APP #3',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 1,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )
        self.create_client(
            name='APP #4',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 2,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_2,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_2,
        )

        with self.vault_mock() as vault:
            self.vault_register_add_user_role_to_secret_ok(vault, TEST_VAULT_SECRET_UUID_1)
            self.vault_register_add_user_role_to_secret_ok(vault, TEST_VAULT_SECRET_UUID_2)
            self.run_command()

        self.assert_log('Task complete. 2 clients updated. 0 clients failed.', level='info')
        eq_(
            self.log_messages(level='debug'),
            [
                'Secrets roles updated (secret_uuid: {}, ABC: {}) for client 3'.format(
                    TEST_VAULT_SECRET_UUID_1,
                    TEST_ABC_SERVICE_ID,
                ),
                'Secrets roles updated (secret_uuid: {}, ABC: {}) for client 4'.format(
                    TEST_VAULT_SECRET_UUID_2,
                    TEST_ABC_SERVICE_ID,
                ),
            ],
        )

        eq_(len(vault.request_history), 4)

        for i in range(2):
            self.assert_vault_request_equals(
                vault.request_history[i],
                {
                    'body': {
                        'abc_id': TEST_ABC_SERVICE_ID,
                        'abc_role_id': settings.VAULT_SECRET_TVM_ROLES[i],
                        'role': 'OWNER',
                    },
                    'method': 'POST',
                    'path': '/1/secrets/{}/roles/'.format(TEST_VAULT_SECRET_UUID_1),
                    'query': '',
                },
            )

        for i in range(2):
            self.assert_vault_request_equals(
                vault.request_history[2 + i],
                {
                    'body': {
                        'abc_id': TEST_ABC_SERVICE_ID,
                        'abc_role_id': settings.VAULT_SECRET_TVM_ROLES[i],
                        'role': 'OWNER',
                    },
                    'method': 'POST',
                    'path': '/1/secrets/{}/roles/'.format(TEST_VAULT_SECRET_UUID_2),
                    'query': '',
                },
            )

    def test_nothing_to_do(self):
        for i in range(10):
            self.create_client('APP without service id #{}'.format(i))

        for i in range(10):
            self.create_client(
                name='APP #{}'.format(i),
                abc_service_id=TEST_ABC_SERVICE_ID,
                abc_request_id=TEST_ABC_REQUEST_ID + i,
            )

        for i in range(11, 20):
            self.create_client(
                name='APP #{}'.format(i),
                abc_service_id=TEST_ABC_SERVICE_ID,
                abc_request_id=TEST_ABC_REQUEST_ID + i,
                vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            )

        self.run_command()
        self.assert_log('Task complete. 0 clients updated. 0 clients failed.', level='info')

    def test_vault_error(self):
        self.create_client(
            name='APP #1',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )
        self.create_client(
            name='APP #2',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 1,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_2,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_2,
        )
        with self.vault_mock() as vault:
            self.vault_register_add_user_role_to_secret_ok(vault, secret_uuid=TEST_VAULT_SECRET_UUID_1)
            self.vault_register_add_user_role_to_secret_error(vault, secret_uuid=TEST_VAULT_SECRET_UUID_2)
            self.run_command()

        self.assert_log('Task complete. 1 clients updated. 1 clients failed.', level='info')
        eq_(
            self.log_messages(level='debug'),
            [
                'Secrets roles updated (secret_uuid: {secret_uuid}, ABC: {abc_id}) for client 1'.format(
                    secret_uuid=TEST_VAULT_SECRET_UUID_1,
                    abc_id=TEST_ABC_SERVICE_ID,
                ),
                'Failed to update roles (secret_uuid: {secret_uuid}, ABC: {abc_id}) for client 2. '
                'Errors: Mocked add user role to secret error, Mocked add user role to secret error'.format(
                    secret_uuid=TEST_VAULT_SECRET_UUID_2,
                    abc_id=TEST_ABC_SERVICE_ID,
                ),
            ],
        )

        for i in range(2):
            self.assert_vault_request_equals(
                vault.request_history[i],
                {
                    'body': {
                        'abc_id': TEST_ABC_SERVICE_ID,
                        'abc_role_id': settings.VAULT_SECRET_TVM_ROLES[i],
                        'role': 'OWNER',
                    },
                    'method': 'POST',
                    'path': '/1/secrets/{}/roles/'.format(TEST_VAULT_SECRET_UUID_1),
                    'query': '',
                },
            )

        for i in range(2):
            self.assert_vault_request_equals(
                vault.request_history[2 + i],
                {
                    'body': {
                        'abc_id': TEST_ABC_SERVICE_ID,
                        'abc_role_id': settings.VAULT_SECRET_TVM_ROLES[i],
                        'role': 'OWNER',
                    },
                    'method': 'POST',
                    'path': '/1/secrets/{}/roles/'.format(TEST_VAULT_SECRET_UUID_2),
                    'query': '',
                },
            )

    def test_db_error(self):
        self.create_client(
            name='APP #1',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_2,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_2,
        )

        with self.vault_mock() as vault:
            self.register_default_mocks(vault)

            get_dbm('oauthdbcentral').execute.side_effect = DBTemporaryError('DB is down')
            with assert_raises(SystemExit):
                self.run_command()

        self.assert_log('DB error: DB is down', level='warning')
