# coding: utf-8

import json

from mock import (
    mock_open,
    patch,
)

from .base import (
    BaseCLICommandRSATestCaseMixin,
    BaseCLICommandTestCase,
)


class TestCreateVersionCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_without_value_error(self):
        with self.rsa_permissions_and_time_mock():
            command_args = [
                'create', 'version',
                'sec-0000000000000000000000ygj0',
                '-r', 'owner:vault-test-101',
                '-r', 'reader:staff:2',
                '-r', 'reader:abc:50',
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 2, result.stdout)
            self.assertRegexpMatches(result.stdout, r'error: No version value specified\n')

    def test_rsa_create_version_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: ',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "password": "passw0rd", ',
                        '    "username": "user"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_from_json_list_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '[{"key": "username", "value": "ppodolsky"}, {"key": "password", "value": "123456"}]',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: ',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "password": "123456", ',
                        '    "username": "ppodolsky"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_kv_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-k', 'username=user', 'password=passw0rd',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: ',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "password": "passw0rd", ',
                        '    "username": "user"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_kv_bad_value(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-k', 'key',
                ]
                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 2, result.stdout)
                self.assertRegexpMatches(result.stderr, r'error: Bad value: key\n')

    def test_rsa_create_version_kv_missing_value(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-k', 'key=',
                ]
                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 2, result.stdout)
                self.assertRegexpMatches(result.stderr, r'error: The value can not be empty or consist only of whitespaces: key=\n')

    def test_rsa_create_version_return_only_value_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--only-value',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        '{',
                        '    "password": "passw0rd", ',
                        '    "username": "user"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertDictEqual(
                    json.loads(result.stdout),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'secret_name': 'secret_1',
                        'secret_uuid': 'sec-0000000000000000000000ygj0',
                        'value': {'password': 'passw0rd', 'username': 'user'},
                        'version': 'ver-0000000000000000000001x140',
                    },
                )

    def test_rsa_create_diff_version_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-c', 'Comment for the version',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"hostname": "saas.yt"}',
                    '-u',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: Comment for the version',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: ver-0000000000000000000000ygj4',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "hostname": "saas.yt", ',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_diff_version_kv_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-c', 'Comment for the version',
                    '-k', 'hostname=saas.yt',
                    '-u',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: Comment for the version',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: ver-0000000000000000000000ygj4',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "hostname": "saas.yt", ',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_delete_keys_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                secret_uuid = self.vault_client.create_secret(
                    name='new_secret',
                )
                secret_version = self.vault_client.create_secret_version(
                    secret_uuid,
                    value=dict(
                        hostname='vault-db.passport.yandex.tld',
                        password='2000355',
                        username='vault-api',
                        encoding='utf-8',
                        name='vault-db',
                    ),
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    secret_version,
                    '-c', 'Comment for the version',
                    '-k', 'password=5678', 'dbname=vault-db',
                    '-d', 'name', 'encoding',
                    '-u',
                ]

                result = self.runner.invoke(command_args, catch_exceptions=False)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'version: ver-0000000000000000000001x140\n'
                    'comment: Comment for the version\n'
                    'secret uuid: sec-0000000000000000000001x140\n'
                    'secret name: new_secret\n'
                    'parent: ver-0000000000000000000001x142\n'
                    '\n'
                    'creator: vault-test-100 (100)\n'
                    'created: 2015-10-21 00:00:15\n'
                    '\n'
                    'value:\n'
                    '{\n'
                    '    "dbname": "vault-db", \n'
                    '    "hostname": "vault-db.passport.yandex.tld", \n'
                    '    "password": "5678", \n'
                    '    "username": "vault-api"\n'
                    '}\n'
                )

    def test_rsa_create_diff_version_for_secret_without_version_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                    secret_uuid = self.vault_client.create_secret(
                        name='new_secret',
                    )

            with self.rsa_permissions_and_time_mock():
                command_args = [
                    'create', 'version',
                    secret_uuid,
                    '-c', 'Comment for the version',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"hostname": "saas.yt"}',
                    '-u',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x142',
                        'comment: Comment for the version',
                        'secret uuid: sec-0000000000000000000001x140',
                        'secret name: new_secret',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        '',
                        'value:',
                        '{',
                        '    "hostname": "saas.yt"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_with_file(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with patch(
                    'vault_client_cli.commands.args.open',
                    mock_open(read_data=u'bin file с русскими буквами'.encode('utf-8')),
                ):
                    with patch('os.path.exists', return_value=True):
                        command_args = [
                            'create', 'version',
                            'sec-0000000000000000000000ygj0',
                            '-k', 'hostname=saas.yt',
                            '-f', 'file1=/usr/local/etc/test_file_1.dat',
                            '-f', 'test_file_1.dat',
                            '-u',
                            '-j', '-O',
                        ]

                        result = self.runner.invoke(command_args)
                        self.assertEqual(result.exit_code, 0, result.stdout)
                        self.assertDictEqual(
                            json.loads(result.stdout),
                            {
                                'test_file_1.dat': 'YmluIGZpbGUg0YEg0YDRg9GB0YHQutC40LzQuCDQsdGD0LrQstCw0LzQuA==',
                                'file1': 'YmluIGZpbGUg0YEg0YDRg9GB0YHQutC40LzQuCDQsdGD0LrQstCw0LzQuA==',
                                'hostname': 'saas.yt',
                                'password': '123',
                            },
                        )

        with self.user_permissions_and_time_mock():
            r = self.vault_client.get_version('sec-0000000000000000000000ygj0', packed_value=False)
            self.assertListEqual(
                r['value'],
                [
                    {'encoding': 'base64', 'key': 'file1', 'value': 'YmluIGZpbGUg0YEg0YDRg9GB0YHQutC40LzQuCDQsdGD0LrQstCw0LzQuA=='},
                    {'key': 'password', 'value': '123'},
                    {'key': 'hostname', 'value': 'saas.yt'},
                    {'encoding': 'base64', 'key': 'test_file_1.dat', 'value': 'YmluIGZpbGUg0YEg0YDRg9GB0YHQutC40LzQuCDQsdGD0LrQstCw0LzQuA=='},
                ],
            )

    def test_rsa_create_version_file_kv_missing_value(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-f', 'key=',
                ]
                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 2, result.stdout)
                self.assertRegexpMatches(result.stderr, r'error: The filename can not be empty or consist only of whitespaces: key=\n')

    def test_rsa_create_version_file_kv_file_not_found(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with patch('os.path.exists', return_value=False):
                    command_args = [
                        'create', 'version',
                        'sec-0000000000000000000000ygj0',
                        '-f', 'key=missing_filename.dat',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 2, result.stdout)
                    self.assertRegexpMatches(result.stderr, r'error: File "missing_filename.dat" not found\n')

    def test_rsa_create_version_with_ttl_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'version',
                    'sec-0000000000000000000000ygj0',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:2',
                    '-r', 'reader:abc:50',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--ttl', '30',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000001x140',
                        'comment: ',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        'expired: 2015-10-21 00:00:45',
                        '',
                        'value:',
                        '{',
                        '    "password": "passw0rd", ',
                        '    "username": "user"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_create_version_as_appender_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                secret = self.vault_client.create_secret('tro-lo-lo')
                self.vault_client.create_secret_version(secret, {'a': 1})
                self.vault_client.add_user_role_to_secret(secret, 'APPENDER', uid=101)

            with self.rsa_permissions_and_time_mock(uid=101):
                command_args = [
                    'create', 'version',
                    secret,
                    '-c', 'Comment for the version',
                    '-v', '{"hostname": "saas.yt"}',
                ]

                result = self.runner.invoke(command_args, catch_exceptions=False)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stderr,
                    'New version uuid is ver-0000000000000000000001x144\n',
                )

            with self.user_permissions_and_time_mock():
                self.assertDictEqual(
                    self.vault_client.get_version(secret),
                    {u'comment': u'Comment for the version',
                     u'created_at': 1445385615.0,
                     u'created_by': 101,
                     u'creator_login': u'vault-test-101',
                     u'secret_name': u'tro-lo-lo',
                     u'secret_uuid': u'sec-0000000000000000000001x140',
                     u'value': {u'hostname': u'saas.yt'},
                     u'version': u'ver-0000000000000000000001x144'},
                )


class TestUpdateVersionCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_update_version_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                secret = self.vault_client.create_secret('tro-lo-lo')
                version = self.vault_client.create_secret_version(secret, {'a': 1})

        with self.rsa_permissions_and_time_mock():
                command_args = [
                    'update', 'version',
                    version,
                    '--ttl', '30',
                    '--state', 'hidden',
                    '--comment', 'New version comment',
                ]
                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'state: hidden',
                        'version: ver-0000000000000000000001x142',
                        'comment: New version comment',
                        'secret uuid: sec-0000000000000000000001x140',
                        'secret name: tro-lo-lo',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:15',
                        'expired: 2015-10-21 00:00:45',
                        '',
                        'value:',
                        '{',
                        '    "a": "1"',
                        '}',
                        '',
                    ],
                )


class TestGetVersionCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_get_version_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'version: ver-0000000000000000000000ygj4',
                        'comment: ',
                        'secret uuid: sec-0000000000000000000000ygj0',
                        'secret name: secret_1',
                        'parent: -',
                        '',
                        'creator: vault-test-100 (100)',
                        'created: 2015-10-21 00:00:03',
                        '',
                        'value:',
                        '{',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_get_version_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertDictEqual(
                    json.loads(result.stdout),
                    {
                        'created_at': 1445385603.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'secret_name': 'secret_1',
                        'secret_uuid': 'sec-0000000000000000000000ygj0',
                        'value': {'password': '123'},
                        'version': 'ver-0000000000000000000000ygj4',
                    },
                )

    def test_rsa_get_only_version_value_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '--only-value',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        '{',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_get_only_version_value_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '-j',
                    '--only-value',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        '{',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_get_only_version_value_with_key_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '--only-value=password',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(result.stdout, '123\n')

    def test_rsa_get_only_version_value_with_key__skip_nl_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '--only-value=password',
                    '-n',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(result.stdout, '123')

    def test_rsa_get_only_version_value_without_key_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '--only-value=password',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        '{',
                        '    "password": "123"',
                        '}',
                        '',
                    ],
                )

    def test_rsa_get_only_version_value_without_key_error(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    'ver-0000000000000000000000ygj4',
                    '--only-value=name',
                ]

                result = self.runner.invoke(command_args, catch_exceptions=False)
                self.assertEqual(result.exit_code, 3, result.stdout)
                self.assertListEqual(
                    result.stdout_as_list(),
                    [
                        'error: "The key \'name\' is not found in the value."',
                        '',
                    ],
                )

    def test_rsa_return_only_value_file(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    [dict(key='file', encoding='base64', value='YmluIGZpbGUg0YEg0YDRg9GB0YHQutC40LzQuCDQsdGD0LrQstCw0LzQuA==')],
                )

        with self.rsa_permissions_and_time_mock():
            command_args = [
                'get', 'version',
                version,
                '-O=file',
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertEqual(result.stdout, u'bin file с русскими буквами')

    def test_rsa_get_expired_version(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    {'a': '1'},
                    ttl=30,
                )

        with self.rsa_permissions_and_time_mock(offset=100):
            command_args = [
                'get', 'version',
                version,
            ]

            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    'version: {}'.format(version),
                    'comment: ',
                    'secret uuid: sec-0000000000000000000000ygj0',
                    'secret name: secret_1',
                    'parent: -',
                    '',
                    'creator: vault-test-100 (100)',
                    'created: 2015-10-21 00:00:15',
                    'expired: 2015-10-21 00:00:45 (expired)',
                    '',
                    'value:',
                    '{',
                    '    "a": "1"',
                    '}',
                    '',
                ],
            )

    def test_rsa_get_version_as_java_properties_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    {
                        'simple_key': 'simple value',
                        'second_key': u'value with spaces, slashes \\,\nCR\n# Comments\n! '
                                      u'Comments and := и русскими буковками',
                    },
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    version,
                    '--format', 'java',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'version: ver-0000000000000000000001x140\n'
                    'comment: \n'
                    'secret uuid: sec-0000000000000000000000ygj0\n'
                    'secret name: secret_1\n'
                    'parent: -\n'
                    '\n'
                    'creator: vault-test-100 (100)\n'
                    'created: 2015-10-21 00:00:15\n'
                    '\n'
                    'value:\n'
                    'simple_key = simple value\n'
                    'second_key = value with spaces, slashes \\,\\\n'
                    'CR\\\n'
                    '\\# Comments\\\n'
                    '\\! Comments and := \\u0438 \\u0440\\u0443\\u0441\\u0441\\u043a\\u0438\\u043c\\u0438 '
                    '\\u0431\\u0443\\u043a\\u043e\\u0432\\u043a\\u0430\\u043c\\u0438\n',
                )

    def test_rsa_get_version_as_java_properties_only_value_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    {
                        'simple_key': 'simple value',
                        'second_key': u'value with spaces, slashes \\,\nCR\n# Comments\n! '
                                      u'Comments and := и русскими буковками',
                    },
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    version,
                    '-o', '--format', 'java',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'simple_key = simple value\n'
                    'second_key = value with spaces, slashes \\,\\\n'
                    'CR\\\n'
                    '\\# Comments\\\n'
                    '\\! Comments and := \\u0438 \\u0440\\u0443\\u0441\\u0441\\u043a\\u0438\\u043c\\u0438 '
                    '\\u0431\\u0443\\u043a\\u043e\\u0432\\u043a\\u0430\\u043c\\u0438\n',
                )

    def test_rsa_get_version_as_yaml_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    {
                        'simple_key': 'simple value',
                        'second_key': u'value with spaces, slashes \\,\nCR\n# Comments\n! '
                                      u'Comments and := и русскими буковками',
                    },
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    version,
                    '--format', 'yaml',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'version: ver-0000000000000000000001x140\n'
                    u'comment: \n'
                    u'secret uuid: sec-0000000000000000000000ygj0\n'
                    u'secret name: secret_1\n'
                    u'parent: -\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'value:\n'
                    u'second_key: \'value with spaces, slashes \\,\n'
                    u'\n'
                    u'    CR\n'
                    u'\n'
                    u'    # Comments\n'
                    u'\n'
                    u'    ! Comments and := \u0438 \u0440\u0443\u0441\u0441\u043a\u0438\u043c\u0438 \u0431\u0443\u043a\u043e\u0432\u043a\u0430\u043c\u0438\'\n'
                    u'simple_key: simple value\n'
                    u'\n',
                )

    def test_rsa_get_version_as_yaml_only_value_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                version = self.vault_client.create_secret_version(
                    'sec-0000000000000000000000ygj0',
                    {
                        'simple_key': 'simple value',
                        'second_key': u'value with spaces, slashes \\,\nCR\n# Comments\n! '
                                      u'Comments and := и русскими буковками',
                    },
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'version',
                    version,
                    '-o', '--format', 'yaml',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'second_key: \'value with spaces, slashes \\,\n'
                    u'\n'
                    u'    CR\n'
                    u'\n'
                    u'    # Comments\n'
                    u'\n'
                    u'    ! Comments and := \u0438 \u0440\u0443\u0441\u0441\u043a\u0438\u043c\u0438 \u0431\u0443\u043a\u043e\u0432\u043a\u0430\u043c\u0438\'\n'
                    u'simple_key: simple value\n',
                )
