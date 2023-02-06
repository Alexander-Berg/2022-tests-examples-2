# -*- coding: utf-8 -*-

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
from passport.backend.oauth.tvm_api.tvm_api.management.commands.save_tvm_secrets_to_vault import (
    Command as SaveSecretsToVaultCommand,
)

from ..base import BaseTVMManagementCommandTestCase


class TestSaveSecretsToVaultCommand(BaseTVMManagementCommandTestCase, VaultMockMixin):
    command_class = SaveSecretsToVaultCommand
    default_command_kwargs = {
        'chunk_size': 10,
        'use_pauses': False,
        'pause_length': 1.0,
    }
    logger_name = 'management.save_tvm_secrets_to_vault'

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
        )
        self.create_client(
            name='APP #4',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 2,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_2,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_2,
        )

        with self.vault_mock() as vault:
            self.register_default_mocks(vault)
            self.run_command()

        self.assert_log('Task complete. 2 clients updated. 0 clients failed.', level='info')
        eq_(
            self.log_messages(level='debug'),
            [
                'Store TVM secrets to Vault (ABC: {}; vault: {}, {}) for client 2'.format(
                    TEST_ABC_SERVICE_ID,
                    TEST_VAULT_SECRET_UUID_1,
                    TEST_VAULT_VERSION_UUID_1,
                ),
                'Store TVM secrets to Vault (ABC: {}; vault: {}, {}) for client 3'.format(
                    TEST_ABC_SERVICE_ID,
                    TEST_VAULT_SECRET_UUID_1,
                    TEST_VAULT_VERSION_UUID_1,
                ),
            ],
        )

    def test_nothing_to_do(self):
        for i in range(10):
            self.create_client('APP without service id #{}'.format(i))

        for i in range(10):
            self.create_client(
                name='APP #{}'.format(i),
                abc_service_id=TEST_ABC_SERVICE_ID,
                abc_request_id=TEST_ABC_REQUEST_ID + i,
                vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
                vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
            )

        self.run_command()
        self.assert_log('Task complete. 0 clients updated. 0 clients failed.', level='info')

    def test_vault_error(self):
        self.create_client(
            name='APP #1',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
        )
        self.create_client(
            name='APP #2',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 1,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_2,
        )
        with self.vault_mock() as vault:
            self.register_default_mocks(vault)
            self.vault_register_create_secret_version_error(vault, secret_uuid=TEST_VAULT_SECRET_UUID_2)
            self.run_command()

        self.assert_log('Task complete. 1 clients updated. 1 clients failed.', level='info')
        eq_(
            self.log_messages(level='debug'),
            [
                'Store TVM secrets to Vault (ABC: {}; vault: {}, {}) for client 1'.format(
                    TEST_ABC_SERVICE_ID,
                    TEST_VAULT_SECRET_UUID_1,
                    TEST_VAULT_VERSION_UUID_1,
                ),
                'Failed to save TVM secrets to Vault (ABC: {}) for client 2'.format(
                    TEST_ABC_SERVICE_ID,
                ),
            ],
        )

    def test_db_error(self):
        self.create_client(
            name='APP #1',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
        )

        with self.vault_mock() as vault:
            self.register_default_mocks(vault)

            get_dbm('oauthdbcentral').transaction.side_effect = DBTemporaryError('DB is down')
            with assert_raises(SystemExit):
                self.run_command()

        self.assert_log('DB error: DB is down', level='warning')
