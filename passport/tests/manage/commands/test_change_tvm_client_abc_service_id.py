# -*- coding: utf-8 -*-

from django.conf import settings
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.oauth.core.common.utils import now
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ABC_SERVICE_ID,
    TEST_UID,
)
from passport.backend.oauth.tvm_api.tests.base import TEST_ABC_REQUEST_ID
from passport.backend.oauth.tvm_api.tests.base.vault_test import (
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_VERSION_UUID_1,
    VaultMockMixin,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient
from passport.backend.oauth.tvm_api.tvm_api.management.commands.change_tvm_client_abc_service_id import (
    Command as ChangeTvmClientAbcServiceId,
)

from ..base import BaseTVMManagementCommandTestCase


TEST_NEW_ABC_SERVICE_ID = TEST_ABC_SERVICE_ID + 1


class TestChangeTvmClientAbcSericeId(BaseTVMManagementCommandTestCase, VaultMockMixin):
    command_class = ChangeTvmClientAbcServiceId
    logger_name = 'console'
    default_command_kwargs = {
        'allow_deleted': False,
        'allow_overwrite': False,
    }

    def create_client(self, name='APP', abc_service_id=None, abc_request_id=None, vault_secret_uuid=None, vault_version_uuid=None):
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
        return client

    def assert_vault_called(self, request_history, abc_id, secret_uuid):
        eq_(len(request_history), 2)

        for i, role_id in enumerate(settings.VAULT_SECRET_TVM_ROLES):
            self.assert_vault_request_equals(
                request_history[i],
                {
                    'body': {
                        'abc_id': abc_id,
                        'abc_role_id': role_id,
                        'role': 'OWNER',
                    },
                    'method': 'POST',
                    'path': '/1/secrets/{}/roles/'.format(secret_uuid),
                    'query': '',
                },
            )

    def test_change_normal_app(self):
        client = self.create_client(
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )

        with self.vault_mock() as vault:
            self.vault_register_add_user_role_to_secret_ok(vault, TEST_VAULT_SECRET_UUID_1)
            self.run_command(
                client_id=client.id,
                abc_service_id=TEST_NEW_ABC_SERVICE_ID,
                allow_overwrite=True,
            )

        eq_(
            self.log_messages(level='info'),
            [
                'Old abc_service_id: %s' % TEST_ABC_SERVICE_ID,
                'Done',
            ],
        )

        eq_(
            TVMClient.by_id(client.id).abc_service_id,
            TEST_NEW_ABC_SERVICE_ID,
        )

        self.assert_vault_called(vault.request_history, abc_id=TEST_NEW_ABC_SERVICE_ID, secret_uuid=TEST_VAULT_SECRET_UUID_1)

    def test_change_deleted_app(self):
        client = self.create_client(
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )
        with UPDATE(client):
            client.deleted = now()

        with self.vault_mock() as vault:
            self.vault_register_add_user_role_to_secret_ok(vault, TEST_VAULT_SECRET_UUID_1)

            with assert_raises(SystemExit):
                self.run_command(
                    client_id=client.id,
                    abc_service_id=TEST_NEW_ABC_SERVICE_ID,
                    allow_overwrite=True,
                )
            self.assert_log(
                'Client %s not found. Add --allow_deleted if you are sure.' % client.id,
                level='error',
            )

            self.run_command(
                client_id=client.id,
                abc_service_id=TEST_NEW_ABC_SERVICE_ID,
                allow_overwrite=True,
                allow_deleted=True,
            )

        eq_(
            self.log_messages(level='info'),
            [
                'Old abc_service_id: %s' % TEST_ABC_SERVICE_ID,
                'Done',
            ],
        )

        eq_(
            TVMClient.by_id(client.id, allow_deleted=True).abc_service_id,
            TEST_NEW_ABC_SERVICE_ID,
        )

        self.assert_vault_called(vault.request_history, abc_id=TEST_NEW_ABC_SERVICE_ID, secret_uuid=TEST_VAULT_SECRET_UUID_1)

    def test_vault_error(self):
        client = self.create_client(
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )

        with self.vault_mock() as vault:
            self.vault_register_add_user_role_to_secret_error(vault, TEST_VAULT_SECRET_UUID_1)
            self.run_command(
                client_id=client.id,
                abc_service_id=TEST_NEW_ABC_SERVICE_ID,
                allow_overwrite=True,
            )

        eq_(
            self.log_messages(level='info'),
            [
                'Old abc_service_id: %s' % TEST_ABC_SERVICE_ID,
                'Done',
            ],
        )

        eq_(
            TVMClient.by_id(client.id).abc_service_id,
            TEST_NEW_ABC_SERVICE_ID,
        )

        eq_(
            self.log_messages(level='debug'),
            [
                'Failed to update roles (secret_uuid: {secret_uuid}, ABC: {abc_id}) for client {client_id}. '
                'Errors: Mocked add user role to secret error, Mocked add user role to secret error'.format(
                    client_id=client.id,
                    secret_uuid=TEST_VAULT_SECRET_UUID_1,
                    abc_id=TEST_NEW_ABC_SERVICE_ID,
                ),
            ],
        )

        self.assert_vault_called(vault.request_history, abc_id=TEST_NEW_ABC_SERVICE_ID, secret_uuid=TEST_VAULT_SECRET_UUID_1)

    def test_db_error(self):
        client = self.create_client(
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID,
            vault_secret_uuid=TEST_VAULT_SECRET_UUID_1,
            vault_version_uuid=TEST_VAULT_VERSION_UUID_1,
        )

        with self.vault_mock() as vault:
            self.register_default_mocks(vault)

            get_dbm('oauthdbcentral').execute.side_effect = DBTemporaryError('DB is down')
            with assert_raises(SystemExit):
                self.run_command(
                    client_id=client.id,
                    abc_service_id=TEST_NEW_ABC_SERVICE_ID,
                    allow_overwrite=True,
                )

        self.assert_log('DB error: DB is down', level='warning')
