# coding: utf-8

import json

from passport.backend.vault.api.test.secrets_mock import SecretsMock

from .base import (
    BaseCLICommandRSATestCaseMixin,
    BaseCLICommandTestCase,
)


class TestListTokensCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_list_tokens_ok(self):
        self.fixture.fill_tvm_apps()
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_123456',
                        tvm_client_id='2000367',
                        comment='Test token with comment',
                    )
                with SecretsMock('sec-ygj0-delegation-token_2'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                with SecretsMock('sec-ygj0-delegation-token_3'):
                    _, token_3_tid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                    self.vault_client.revoke_token(token_3_tid)

        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'tokens', 'sec-0000000000000000000000ygj0'])
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertEqual(
                result.stdout,
                u'+---------------------+----------------------------+-------------------+---------------------------+--------------------------------+---------+\n'
                u'| created             | tvm_client_id              | signature         | comment                   | token_uuid                     | state   |\n'
                u'|---------------------+----------------------------+-------------------+---------------------------+--------------------------------+---------|\n'
                u'| 2015-10-21 00:00:15 | 2000367 (social api (dev)) | token_sign_123456 | Test token with comment   | tid-0000000000000000000001x140 | normal  |\n'
                u'| 2015-10-21 00:00:15 | 2000355 (passport_likers3) | token_sign_098765 | Test token with comment 2 | tid-0000000000000000000001x141 | normal  |\n'
                u'+---------------------+----------------------------+-------------------+---------------------------+--------------------------------+---------+\n'
            )

    def test_rsa_list_tokens_compact_ok(self):
        self.fixture.fill_tvm_apps()
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_123456',
                        tvm_client_id='2000367',
                        comment='Test token with comment',
                    )
                with SecretsMock('sec-ygj0-delegation-token_2'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                with SecretsMock('sec-ygj0-delegation-token_3'):
                    _, token_3_tid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                    self.vault_client.revoke_token(token_3_tid)

        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'tokens', 'sec-0000000000000000000000ygj0', '--compact'])
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertEqual(
                result.stdout,
                u'created              tvm_client_id               signature          comment                    token_uuid                      state\n'
                u'-------------------  --------------------------  -----------------  -------------------------  ------------------------------  -------\n'
                u'2015-10-21 00:00:15  2000367 (social api (dev))  token_sign_123456  Test token with comment    tid-0000000000000000000001x140  normal\n'
                u'2015-10-21 00:00:15  2000355 (passport_likers3)  token_sign_098765  Test token with comment 2  tid-0000000000000000000001x141  normal\n'
            )

    def test_rsa_list_tokens_with_revoked_ok(self):
        self.fixture.fill_tvm_apps()
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_123456',
                        tvm_client_id='2000355',
                        comment='Test token with comment',
                    )
                with SecretsMock('sec-ygj0-delegation-token_2'):
                    _, token_2_tid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                    self.vault_client.revoke_token(token_2_tid)

        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'tokens', 'sec-0000000000000000000000ygj0', '--with-revoked', '--compact'])
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertEqual(
                result.stdout,
                u'created              tvm_client_id               signature          comment                    token_uuid                      state\n'
                u'-------------------  --------------------------  -----------------  -------------------------  ------------------------------  -------\n'
                u'2015-10-21 00:00:15  2000355 (passport_likers3)  token_sign_123456  Test token with comment    tid-0000000000000000000001x140  normal\n'
                u'2015-10-21 00:00:15  2000355 (passport_likers3)  token_sign_098765  Test token with comment 2  tid-0000000000000000000001x141  revoked\n'
            )

    def test_rsa_list_tokens_ok_json(self):
        self.fixture.fill_tvm_apps()
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_123456',
                        tvm_client_id='2000355',
                    )

        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'tokens', 'sec-0000000000000000000000ygj0', '-j'])
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                json.loads(result.stdout),
                [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'state_name': 'normal',
                        'secret_uuid': 'sec-0000000000000000000000ygj0',
                        'signature': 'token_sign_123456',
                        'tvm_client_id': 2000355,
                        u'tvm_app': {
                            u'abc_department': {
                                u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                u'id': 14,
                                u'unique_name': u'passp',
                            },
                            u'abc_state': u'granted',
                            u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                            u'name': u'passport_likers3',
                            u'tvm_client_id': 2000355,
                        },
                        'token_uuid': 'tid-0000000000000000000001x140',
                    },
                ],
            )


class TestCreateTokenCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_create_token_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    command_args = [
                        'create', 'token',
                        'sec-0000000000000000000000ygj0',
                        '-s', 'token_signature_123',
                        '-tvm', '567',
                        '--comment', 'Token comment',
                    ]

                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)
                    self.assertListEqual(
                        result.stdout_as_list(),
                        [
                            'secret uuid: sec-0000000000000000000000ygj0',
                            'token: sec-ygj0-delegation-token.1.eef3d2ada88c4642',
                            'token uuid: tid-0000000000000000000001x140',
                            '',
                        ],
                    )

        with self.user_permissions_and_time_mock():
            self.assertEqual(
                self.vault_client.list_tokens(
                    'sec-0000000000000000000000ygj0',
                ),
                [{
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'state_name': 'normal',
                    'secret_uuid': 'sec-0000000000000000000000ygj0',
                    'signature': 'token_signature_123',
                    'token_uuid': 'tid-0000000000000000000001x140',
                    'tvm_client_id': 567,
                    'comment': 'Token comment',
                }],
            )


class TestFindRestoreAndRevokeTokenCommands(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def setUp(self):
        super(TestFindRestoreAndRevokeTokenCommands, self).setUp()

        self.fixture.fill_tvm_apps()
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                with SecretsMock('sec-ygj0-delegation-token'):
                    self.token_1, self.token_1_uuid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_123456',
                        tvm_client_id='2000367',
                        comment='Test token with comment',
                    )
                with SecretsMock('sec-ygj0-delegation-token_2'):
                    self.token_2, self.token_2_uuid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                    )
                with SecretsMock('sec-ygj0-delegation-token_3'):
                    self.token_3, self.token_3_uuid = self.vault_client.create_token(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        signature='token_sign_098765',
                        tvm_client_id='2000355',
                        comment='Test token with comment 2',
                    )
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'READER',
                    uid=102,
                )

    def test_find_token_by_token_ok(self):
        with self.rsa_permissions_and_time_mock():
            command_args = [
                'find', 'token',
                self.token_1,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    u'secret_uuid: sec-0000000000000000000000ygj0',
                    u'token uuid: tid-0000000000000000000001x140',
                    u'state: normal',
                    u'comment: Test token with comment',
                    u'',
                    u'tvm app: 2000367 (social api (dev), granted, \u041f\u0430\u0441\u043f\u043e\u0440\u0442)',
                    u'',
                    u'creator: vault-test-100 (100)',
                    u'created: 2015-10-21 00:00:15',
                    u'',
                    u'owners:',
                    u'owner:user:vault-test-100',
                    u'',
                    u'readers:',
                    u'owner:user:vault-test-100',
                    u'reader:user:vault-test-102',
                    u'',
                ]
            )

    def test_find_token_by_token_uuid_ok(self):
        with self.rsa_permissions_and_time_mock():
            command_args = [
                'find', 'token',
                self.token_1_uuid,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    u'secret_uuid: sec-0000000000000000000000ygj0',
                    u'token uuid: tid-0000000000000000000001x140',
                    u'state: normal',
                    u'comment: Test token with comment',
                    u'',
                    u'tvm app: 2000367 (social api (dev), granted, \u041f\u0430\u0441\u043f\u043e\u0440\u0442)',
                    u'',
                    u'creator: vault-test-100 (100)',
                    u'created: 2015-10-21 00:00:15',
                    u'',
                    u'owners:',
                    u'owner:user:vault-test-100',
                    u'',
                    u'readers:',
                    u'owner:user:vault-test-100',
                    u'reader:user:vault-test-102',
                    u'',
                ]
            )

    def test_find_token_by_token_uuid_2_ok(self):
        with self.user_permissions_and_time_mock():
            self.vault_client.revoke_token(self.token_2_uuid)

        with self.rsa_permissions_and_time_mock():
            command_args = [
                'find', 'token',
                self.token_2_uuid,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    u'secret_uuid: sec-0000000000000000000000ygj0',
                    u'token uuid: tid-0000000000000000000001x141',
                    u'state: revoked (vault-test-100, 2015-10-21 00:00:15)',
                    u'comment: ',
                    u'',
                    u'tvm app: -',
                    u'',
                    u'creator: vault-test-100 (100)',
                    u'created: 2015-10-21 00:00:15',
                    u'',
                    u'owners:',
                    u'owner:user:vault-test-100',
                    u'',
                    u'readers:',
                    u'owner:user:vault-test-100',
                    u'reader:user:vault-test-102',
                    u'',
                ]
            )

    def test_revoke_token_ok(self):
        with self.rsa_permissions_and_time_mock():
            command_args = [
                'revoke', 'token',
                self.token_2_uuid,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    u'secret_uuid: sec-0000000000000000000000ygj0',
                    u'token uuid: tid-0000000000000000000001x141',
                    u'state: revoked (vault-test-100, 2015-10-21 00:00:15)',
                    u'comment: ',
                    u'',
                    u'tvm app: -',
                    u'',
                    u'creator: vault-test-100 (100)',
                    u'created: 2015-10-21 00:00:15',
                    u'',
                    u'owners:',
                    u'owner:user:vault-test-100',
                    u'',
                    u'readers:',
                    u'owner:user:vault-test-100',
                    u'reader:user:vault-test-102',
                    u'',
                ]
            )

    def test_restore_token_ok(self):
        with self.user_permissions_and_time_mock():
            self.vault_client.revoke_token(self.token_2_uuid)

        with self.rsa_permissions_and_time_mock():
            command_args = [
                'restore', 'token',
                self.token_2_uuid,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    u'secret_uuid: sec-0000000000000000000000ygj0',
                    u'token uuid: tid-0000000000000000000001x141',
                    u'state: normal',
                    u'comment: ',
                    u'',
                    u'tvm app: -',
                    u'',
                    u'creator: vault-test-100 (100)',
                    u'created: 2015-10-21 00:00:15',
                    u'',
                    u'owners:',
                    u'owner:user:vault-test-100',
                    u'',
                    u'readers:',
                    u'owner:user:vault-test-100',
                    u'reader:user:vault-test-102',
                    u'',
                ]
            )
