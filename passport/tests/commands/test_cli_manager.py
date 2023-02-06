# coding: utf-8

from contextlib import contextmanager
import os
import unittest

from library.python.vault_client.errors import ClientUnknownKeyHashType
from library.python.vault_client.instances import (
    VAULT_PRODUCTION_API,
    VAULT_TESTING_API,
)
from passport.backend.vault.api import get_config
from passport.backend.vault.api.app import create_app
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_OAUTH_TOKEN_1,
    TEST_RSA_LOGIN_2,
    TEST_RSA_PRIVATE_KEY_2,
    TEST_RSA_PRIVATE_KEY_2_MD5_HASH,
    TEST_RSA_PRIVATE_KEY_2_SHA1_HASH,
    TEST_RSA_PRIVATE_KEY_2_SHA256_HASH,
    TEST_RSA_PRIVATE_KEYS,
)
from passport.backend.vault.api.test.test_client import TestClient
from six import StringIO
from vault_client_cli.manager import (
    VaultCLIManager,
    YAV_BACKEND_VAR,
    YAV_OAUTH_TOKEN_VAR,
)


class Args:
    def __init__(self, testing=False, oauth_token=None, rsa_agent_key_num=None, rsa_private_key_file=None,
                 rsa_login=None, rsa_agent_key_hash=None):
        self.testing = testing
        self.oauth_token = oauth_token
        self.rsa_agent_key_num = rsa_agent_key_num
        self.rsa_agent_key_hash = rsa_agent_key_hash
        self.rsa_private_key_file = rsa_private_key_file
        self.rsa_login = rsa_login


class TestManager(unittest.TestCase):
    config = get_config()
    native_client = TestClient(create_app(config))

    def setUp(self):
        self.manager = VaultCLIManager()

    def tearDown(self):
        os.environ[YAV_BACKEND_VAR] = ''

    @contextmanager
    def mock_env(self, env_dict):
        old_env = os.environ
        try:
            os.environ = env_dict
            yield
        finally:
            os.environ = old_env

    def build_client(self, args):
        return self.manager.build_client(args, native_client=self.native_client)

    def test_create_production_client(self):
        args = Args()
        client = self.build_client(args)
        self.assertEqual(
            client.vault_client.host,
            VAULT_PRODUCTION_API,
        )

    def test_create_custom_client(self):
        os.environ[YAV_BACKEND_VAR] = 'http://localhost'
        args = Args()
        client = self.build_client(args)
        self.assertEqual(
            client.vault_client.host,
            'http://localhost',
        )

    def test_create_testing_client(self):
        args = Args(testing=True)
        client = self.build_client(args)
        self.assertEqual(
            client.vault_client.host,
            VAULT_TESTING_API,
        )

    def test_create_oauth_client_from_args(self):
        args = Args(oauth_token=TEST_OAUTH_TOKEN_1.split(' ')[1])
        client = self.build_client(args)
        self.assertEqual(
            client.vault_client.authorization,
            TEST_OAUTH_TOKEN_1,
        )
        self.assertIsNone(client.vault_client.rsa_auth)

    def test_create_oauth_client_from_env(self):
        with self.mock_env({YAV_OAUTH_TOKEN_VAR: TEST_OAUTH_TOKEN_1.split(' ')[1]}):
            client = self.build_client(Args())
            self.assertEqual(
                client.vault_client.authorization,
                TEST_OAUTH_TOKEN_1,
            )
            self.assertIsNone(client.vault_client.rsa_auth)

    def test_get_default_auth(self):
        with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEYS):
            args = Args()
            rsa_login, rsa_auth = self.manager._get_rsa_auth_from_args(args)
            self.assertIsNone(rsa_login)
            self.assertEqual(rsa_auth.__class__.__name__, 'RSASSHAgentAuth')
            self.assertIsNone(rsa_auth.key_num)

            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), len(TEST_RSA_PRIVATE_KEYS))

    def test_load_rsa_key_from_file(self):
        args = Args(rsa_private_key_file=StringIO(TEST_RSA_PRIVATE_KEY_2), rsa_login=TEST_RSA_LOGIN_2)
        rsa_login, rsa_auth = self.manager._get_rsa_auth_from_args(args)
        self.assertEqual(rsa_login, TEST_RSA_LOGIN_2)
        self.assertEqual(rsa_auth.__class__.__name__, 'RSAPrivateKeyAuth')

        args = Args(rsa_private_key_file=StringIO(TEST_RSA_PRIVATE_KEY_2), rsa_login=TEST_RSA_LOGIN_2)
        client = self.build_client(args)
        self.assertEqual(
            client.vault_client.rsa_auth.private_key,
            StringIO(TEST_RSA_PRIVATE_KEY_2).read(),
        )
        self.assertEqual(
            client.vault_client.rsa_login,
            TEST_RSA_LOGIN_2,
        )

    def test_set_rsa_auth_key_num(self):
        with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEYS):
            args = Args(rsa_agent_key_num=0)

            rsa_login, rsa_auth = self.manager._get_rsa_auth_from_args(args)
            self.assertIsNone(rsa_login)
            self.assertEqual(rsa_auth.__class__.__name__, 'RSASSHAgentAuth')
            self.assertEqual(rsa_auth.key_num, 0)

            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

    def test_set_rsa_auth_hash(self):
        with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEYS):
            args = Args(rsa_agent_key_hash=TEST_RSA_PRIVATE_KEY_2_SHA256_HASH)

            rsa_login, rsa_auth = self.manager._get_rsa_auth_from_args(args)
            self.assertIsNone(rsa_login)
            self.assertEqual(rsa_auth.__class__.__name__, 'RSASSHAgentHash')

            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

            args = Args(rsa_agent_key_hash='SHA256:' + TEST_RSA_PRIVATE_KEY_2_SHA256_HASH)
            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

            args = Args(rsa_agent_key_hash=TEST_RSA_PRIVATE_KEY_2_MD5_HASH)
            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

            args = Args(rsa_agent_key_hash='MD5:' + TEST_RSA_PRIVATE_KEY_2_MD5_HASH)
            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

            args = Args(rsa_agent_key_hash=TEST_RSA_PRIVATE_KEY_2_SHA1_HASH)
            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

            args = Args(rsa_agent_key_hash='SHA1:' + TEST_RSA_PRIVATE_KEY_2_SHA1_HASH)
            client = self.build_client(args)
            self.assertEqual(len(client.vault_client.rsa_auth()), 1)

        with self.assertRaises(ClientUnknownKeyHashType):
            args = Args(rsa_agent_key_hash='unknown_hash_type')
            client = self.build_client(args)
