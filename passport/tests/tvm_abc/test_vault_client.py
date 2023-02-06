# -*- coding: utf-8 -*-

from io import StringIO

from django.conf import settings
from library.python.vault_client.errors import ClientError
import paramiko
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.settings.tvm_settings import (
    VAULT_USER_LOGIN,
    VAULT_USER_PRIVATE_KEY,
)
from passport.backend.oauth.tvm_api.tests.base.vault_test import VaultMockMixin
from passport.backend.oauth.tvm_api.tvm_api.db.vault_client import get_vault_client


class CreateVaultNativeClientTestcase(BundleApiTestCase):
    enable_vault = False

    def test_create_client(self):
        nvc = get_vault_client().native_vault_client
        self.assertEqual(nvc.host, settings.VAULT_API_URL)
        self.assertEqual(nvc.rsa_login, VAULT_USER_LOGIN)
        self.assertEqual(
            nvc.rsa_auth()[0].get_fingerprint(),
            paramiko.RSAKey.from_private_key(
                StringIO(VAULT_USER_PRIVATE_KEY),
            ).get_fingerprint(),
        )


class VaultMockTestcase(BundleApiTestCase, VaultMockMixin):
    def test_mock_mixin(self):
        with self.vault_mock() as vault:
            client = get_vault_client().native_vault_client
            self.register_default_mocks(vault)

            self.assertDictEqual(
                client.get_status(),
                {'_mocked': True, 'is_deprecated_client': False, 'status': 'ok'},
            )

            self.assertEqual(client.ping().text, 'Mocked ping')

            secret_uuid = client.create_secret('name')
            self.assertEqual(
                secret_uuid,
                'sec-0000000000000000000000ygj0',
            )

            version_uuid = client.create_secret_version(secret_uuid, {'key': 'value'})
            self.assertEqual(
                version_uuid,
                'ver-0000000000000000000000ygj5',
            )

    def test_mocked_errors(self):
        with self.vault_mock() as vault:
            client = get_vault_client().native_vault_client
            self.register_default_mocks(vault)

            self.vault_register_create_secret_error(vault)
            with self.assertRaises(ClientError) as cm:
                client.create_secret('name')
            self.assertEqual(
                cm.exception.kwargs['message'],
                'Mocked create secret error',
            )

            self.vault_register_create_secret_version_error(vault)
            with self.assertRaises(ClientError) as cm:
                client.create_secret_version('sec-0000000000000000000000ygj0', {'key': 'value'})
            self.assertEqual(
                cm.exception.kwargs['message'],
                'Mocked create secret version error',
            )
