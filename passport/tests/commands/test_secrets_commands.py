# coding: utf-8

import json

from .base import (
    BaseCLICommandRSATestCaseMixin,
    BaseCLICommandTestCase,
)


class TestListSecretsCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_list_secrets_ok(self):
        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'secrets'])
            self.assertEqual(
                result.stdout,
                '+--------------------------------+----------+--------------------------------+-------+-------+-------+---------------------+\n'
                '| secret uuid                    | name     | last version uuid              |   cnt |   tok | acl   | created             |\n'
                '|--------------------------------+----------+--------------------------------+-------+-------+-------+---------------------|\n'
                '| sec-0000000000000000000000ygj5 | secret_2 | ver-0000000000000000000000ygja |     4 |     0 | OWNER | 2015-10-21 00:00:04 |\n'
                '| sec-0000000000000000000000ygj0 | secret_1 | ver-0000000000000000000000ygj4 |     3 |     0 | OWNER | 2015-10-21 00:00:00 |\n'
                '+--------------------------------+----------+--------------------------------+-------+-------+-------+---------------------+\n'
            )
            self.assertEqual(result.exit_code, 0, result.stdout)

    def test_rsa_list_secrets_compact_ok(self):
        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'secrets', '--compact'])
            self.assertEqual(
                result.stdout,
                u'secret uuid                     name      last version uuid                 cnt    tok  acl    created\n'
                u'------------------------------  --------  ------------------------------  -----  -----  -----  -------------------\n'
                u'sec-0000000000000000000000ygj5  secret_2  ver-0000000000000000000000ygja      4      0  OWNER  2015-10-21 00:00:04\n'
                u'sec-0000000000000000000000ygj0  secret_1  ver-0000000000000000000000ygj4      3      0  OWNER  2015-10-21 00:00:00\n',
            )
            self.assertEqual(result.exit_code, 0, result.stdout)

    def test_rsa_list_secrets_tags_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock(base_value=3000000):
                self.client.create_secret('secret_with_tags', tags='test, one')
                result = self.runner.invoke(['list', 'secrets', '-t', 'test'])
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    '+--------------------------------+------------------+---------------------+-------+-------+-------+---------------------+\n'
                    '| secret uuid                    | name             | last version uuid   |   cnt |   tok | acl   | created             |\n'
                    '|--------------------------------+------------------+---------------------+-------+-------+-------+---------------------|\n'
                    '| sec-0000000000000000000002vhp0 | secret_with_tags |                     |     0 |     0 | OWNER | 2015-10-21 00:00:15 |\n'
                    '+--------------------------------+------------------+---------------------+-------+-------+-------+---------------------+\n'
                )

    def test_rsa_list_secrets_ok_json(self):
        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['list', 'secrets', '-j'])
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                json.loads(result.stdout),
                [
                    {
                        'uuid': 'sec-0000000000000000000000ygj5',
                        'last_secret_version': {
                            'version': 'ver-0000000000000000000000ygja',
                        },
                        'created_at': 1445385604.0,
                        'updated_at': 1445385608.0,
                        'created_by': 100,
                        'acl': [
                            {
                                'created_at': 1445385604.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-100',
                                'created_by': 100,
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'effective_role': 'OWNER',
                        'creator_login': 'vault-test-100',
                        'updated_by': 100,
                        'secret_roles': [
                            {
                                'created_at': 1445385604.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-100',
                                'created_by': 100,
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'name': 'secret_2',
                        'versions_count': 4,
                        'tokens_count': 0,
                    },
                    {
                        'uuid': 'sec-0000000000000000000000ygj0',
                        'last_secret_version': {
                            'version': 'ver-0000000000000000000000ygj4',
                        },
                        'created_at': 1445385600.0,
                        'updated_at': 1445385603.0,
                        'created_by': 100,
                        'acl': [
                            {
                                'created_at': 1445385600.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-100',
                                'created_by': 100,
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'effective_role': 'OWNER',
                        'creator_login': 'vault-test-100',
                        'updated_by': 100,
                        'secret_roles': [
                            {
                                'created_at': 1445385600.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-100',
                                'created_by': 100,
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'name': 'secret_1',
                        'versions_count': 3,
                        'tokens_count': 0,
                    },
                ],
            )


class TestCreateSecretCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    fill_database = False
    fill_external_data = True

    def test_rsa_create_secret_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:abc:suggest:administration',
                    '-r', 'appender:abc:passp:scope:tvm_management',
                    '-r', 'appender:abc:passp:role:630',
                    '-r', 'appender:abc:14',
                    '-r', 'appender:staff:84280',
                    '-r', 'reader:102',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: new_secret\n'
                    u'comment: Comment for the new_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'| uuid                           | parent   | created             | creator              |\n'
                    u'|--------------------------------+----------+---------------------+----------------------|\n'
                    u'| ver-0000000000000000000001x145 | -        | 2015-10-21 00:00:15 | vault-test-100 (100) |\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:user:vault-test-102\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'reader:abc:suggest:scope:administration (Перевод саджеста. Scope: Администрирование)\n'
                    u'appender:staff:yandex_rkub_taxi_dev_3231_1747 (Группа по коммуникациям с водителями)\n'
                    u'appender:abc:passp:role:630 (Паспорт. Role: TVM менеджер)\n'
                    u'appender:abc:passp:scope:development (Паспорт. Scope: Разработка)\n'
                    u'appender:abc:passp:scope:tvm_management (Паспорт. Scope: Управление TVM)\n'
                    u'\n'
                )

    def test_rsa_create_secret_compact_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:abc:suggest:scope:administration',
                    '-r', 'reader:abc:passp:role:630',
                    '-r', 'reader:102',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: new_secret\n'
                    u'comment: Comment for the new_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'uuid                            parent    created              creator\n'
                    u'------------------------------  --------  -------------------  --------------------\n'
                    u'ver-0000000000000000000001x145  -         2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:user:vault-test-102\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:passp:role:630 (Паспорт. Role: TVM менеджер)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'reader:abc:suggest:scope:administration (Перевод саджеста. Scope: Администрирование)\n'
                    u'\n',
                )

    def test_rsa_create_secret_kv_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-k', 'username=user', 'password=passw0rd',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000001x140',
                ),
                {
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'new_secret',
                    'secret_uuid': 'sec-0000000000000000000001x140',
                    'value': {'password': 'passw0rd', 'username': 'user'},
                    'version': 'ver-0000000000000000000001x145',
                },
            )

    def test_rsa_create_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:102',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

                self.assertDictEqual(
                    json.loads(result.stdout),
                    {
                        'acl': [{
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                        }, {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'role_slug': 'READER',
                            'staff_id': 2,
                            'staff_name': u'\u0422\u0435\u0441\u0442\u043e\u0432\u0430\u044f \u0433\u0440\u0443\u043f\u043f\u0430 \u0421\u0435\u043a\u0440\u0435\u0442\u043d\u0438\u0446\u044b 1',
                            'staff_slug': u'_vault_test_group_1',
                            'staff_url': u'https://staff.yandex-team.ru/departments/_vault_test_group_1/',
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'Comment for the new_secret',
                        'uuid': 'sec-0000000000000000000001x140',
                        'tags': [
                            'tag1',
                            'tag2',
                            'tag3',
                        ],
                        'created_at': 1445385615.0,
                        'updated_at': 1445385615.0,
                        'created_by': 100,
                        'secret_versions': [
                            {
                                'created_at': 1445385615.0,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000001x145',
                                'created_by': 100,
                                'keys': ['password', 'username'],
                            },
                        ],
                        'tokens': [],
                        'creator_login': 'vault-test-100',
                        'updated_by': 100,
                        'secret_roles': [
                            {
                                'created_at': 1445385615.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-100',
                                'created_by': 100,
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'role_slug': 'OWNER',
                                'login': 'vault-test-101',
                                'created_by': 100,
                                'uid': 101,
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'role_slug': 'READER',
                                'created_by': 100,
                                'uid': 102,
                                'login': 'vault-test-102',
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'role_slug': 'READER',
                                'staff_id': 2,
                                'staff_name': u'\u0422\u0435\u0441\u0442\u043e\u0432\u0430\u044f \u0433\u0440\u0443\u043f\u043f\u0430 \u0421\u0435\u043a\u0440\u0435\u0442\u043d\u0438\u0446\u044b 1',
                                'staff_slug': u'_vault_test_group_1',
                                'staff_url': u'https://staff.yandex-team.ru/departments/_vault_test_group_1/',
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'role_slug': 'READER',
                                'abc_id': 50,
                                'abc_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                                'abc_scope': 'development',
                                'abc_scope_name': u'Разработка',
                                'abc_scope_id': 5,
                                'abc_slug': 'suggest',
                                'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'name': 'new_secret',
                    },
                )

    def test_rsa_create_secret_with_ttl(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:102',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '-j',
                    '--ttl', '30',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertEqual(
                self.vault_client.get_version(json.loads(result.stdout)['uuid'])['expired_at'],
                1445385645.0,
            )


class TestUpdateSecretCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_update_secret_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'update', 'secret',
                    'sec-0000000000000000000000ygj0',
                    '-n', 'old_secret',
                    '-c', 'Comment for the old_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:abc:passp:scope:tvm_management',
                    '-r', 'reader:abc:passp:role:630',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000000ygj0\n'
                    u'name: old_secret\n'
                    u'comment: Comment for the old_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:00\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'uuid                            parent    created              creator\n'
                    u'------------------------------  --------  -------------------  --------------------\n'
                    u'ver-0000000000000000000001x143  -         2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'ver-0000000000000000000000ygj4  -         2015-10-21 00:00:03  vault-test-100 (100)\n'
                    u'ver-0000000000000000000000ygj3  -         2015-10-21 00:00:02  vault-test-100 (100)\n'
                    u'ver-0000000000000000000000ygj2  -         2015-10-21 00:00:01  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:passp:role:630 (Паспорт. Role: TVM менеджер)\n'
                    u'reader:abc:passp:scope:tvm_management (Паспорт. Scope: Управление TVM)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'\n'
                )

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000000ygj0',
                ),
                {
                    'comment': 'Comment for the old_secret',
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'old_secret',
                    'secret_uuid': 'sec-0000000000000000000000ygj0',
                    'value': {'password': 'passw0rd', 'username': 'user'},
                    'version': 'ver-0000000000000000000001x143',
                },
            )

    def test_rsa_update_secret_kv_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'create', 'secret',
                    'new_secret',
                    '-c', 'Comment for the new_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-k', 'username=user', 'password=passw0rd',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000001x140',
                ),
                {
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'new_secret',
                    'secret_uuid': 'sec-0000000000000000000001x140',
                    'value': {'password': 'passw0rd', 'username': 'user'},
                    'version': 'ver-0000000000000000000001x145',
                },
            )

    def test_rsa_update_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'update', 'secret',
                    'sec-0000000000000000000000ygj0',
                    '-n', 'old_secret',
                    '-c', 'Comment for the old_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertDictEqual(
                    json.loads(result.stdout),
                    {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                        }, {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'role_slug': 'READER',
                            'staff_id': 2,
                            'staff_name': u'\u0422\u0435\u0441\u0442\u043e\u0432\u0430\u044f \u0433\u0440\u0443\u043f\u043f\u0430 \u0421\u0435\u043a\u0440\u0435\u0442\u043d\u0438\u0446\u044b 1',
                            'staff_slug': u'_vault_test_group_1',
                            'staff_url': u'https://staff.yandex-team.ru/departments/_vault_test_group_1/',
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'Comment for the old_secret',
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'old_secret',
                        'secret_roles': [
                            {
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'login': 'vault-test-100',
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'created_by': 100,
                                'login': 'vault-test-101',
                                'role_slug': 'OWNER',
                                'uid': 101,
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385615.0,
                                'created_by': 100,
                                'role_slug': 'READER',
                                'staff_id': 2,
                                'staff_name': u'\u0422\u0435\u0441\u0442\u043e\u0432\u0430\u044f \u0433\u0440\u0443\u043f\u043f\u0430 \u0421\u0435\u043a\u0440\u0435\u0442\u043d\u0438\u0446\u044b 1',
                                'staff_slug': u'_vault_test_group_1',
                                'staff_url': u'https://staff.yandex-team.ru/departments/_vault_test_group_1/',
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'abc_id': 50,
                                'abc_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                                'abc_scope': 'development',
                                'abc_scope_name': u'Разработка',
                                'abc_scope_id': 5,
                                'abc_slug': 'suggest',
                                'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                                'created_at': 1445385615.0,
                                'created_by': 100,
                                'role_slug': 'READER',
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'secret_versions': [
                            {
                                'comment': 'Comment for the old_secret',
                                'created_at': 1445385615.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000001x143',
                                'keys': ['password', 'username'],
                            },
                            {
                                'created_at': 1445385603.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj4',
                                'keys': ['password'],
                            },
                            {
                                'created_at': 1445385602.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj3',
                                'keys': ['password'],
                            },
                            {
                                'created_at': 1445385601.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj2',
                                'keys': ['password'],
                            },
                        ],
                        'tags': ['tag1', 'tag2', 'tag3'],
                        'tokens': [],
                        'updated_at': 1445385615.0,
                        'updated_by': 100,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                )

    def test_rsa_update_secret_without_versions_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                    secret_uuid = self.vault_client.create_secret(
                        name='new_secret',
                    )

            with self.rsa_permissions_and_time_mock():
                command_args = [
                    'update', 'secret',
                    secret_uuid,
                    '-n', 'old_secret',
                    '-c', 'Comment for the old_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest',
                    '-r', 'reader:abc:suggest:scope:administration',
                    '-r', 'reader:abc:passp:role:630',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: old_secret\n'
                    u'comment: Comment for the old_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'uuid                            parent    created              creator\n'
                    u'------------------------------  --------  -------------------  --------------------\n'
                    u'ver-0000000000000000000001x145  -         2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:passp:role:630 (Паспорт. Role: TVM менеджер)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'reader:abc:suggest:scope:administration (Перевод саджеста. Scope: Администрирование)\n'
                    u'\n'
                )

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000001x140',
                ),
                {
                    'comment': 'Comment for the old_secret',
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'old_secret',
                    'secret_uuid': 'sec-0000000000000000000001x140',
                    'value': {'password': 'passw0rd', 'username': 'user'},
                    'version': 'ver-0000000000000000000001x145',
                },
            )

    def test_rsa_update_secret_with_diff_versions_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                    secret_uuid = self.vault_client.create_secret(
                        name='new_secret',
                    )
                    self.vault_client.create_secret_version(
                        secret_uuid=secret_uuid,
                        value={'username': 'user', 'password': '2000355'},
                    )

            with self.rsa_permissions_and_time_mock():
                command_args = [
                    'update', 'secret',
                    secret_uuid,
                    '-n', 'old_secret',
                    '-c', 'Comment for the old_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest:scope:development',
                    '-v', '{"hostname": "saas.yt"}',
                    '-u',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: old_secret\n'
                    u'comment: Comment for the old_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)'
                    u'\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'uuid                            parent                          created              creator\n'
                    u'------------------------------  ------------------------------  -------------------  --------------------\n'
                    u'ver-0000000000000000000001x146  ver-0000000000000000000001x142  2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'ver-0000000000000000000001x142  -                               2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'\n'
                )

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000001x140',
                ),
                {
                    'comment': 'Comment for the old_secret',
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'old_secret',
                    'secret_uuid': 'sec-0000000000000000000001x140',
                    'value': {'password': '2000355', 'username': 'user', 'hostname': 'saas.yt'},
                    'version': 'ver-0000000000000000000001x146',
                    'parent_version_uuid': 'ver-0000000000000000000001x142',
                },
            )

    def test_rsa_update_secret_without_version_with_diff_versions_ok(self):
        with self.uuid_mock():
            with self.user_permissions_and_time_mock():
                    secret_uuid = self.vault_client.create_secret(
                        name='new_secret',
                    )

            with self.rsa_permissions_and_time_mock():
                command_args = [
                    'update', 'secret',
                    secret_uuid,
                    '-n', 'old_secret',
                    '-c', 'Comment for the old_secret',
                    '-t', 'tag1, tag2, tag3',
                    '-r', 'owner:vault-test-101',
                    '-r', 'reader:staff:_vault_test_group_1',
                    '-r', 'reader:abc:suggest:scope:development',
                    '-v', '{"hostname": "saas.yt"}',
                    '-u',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: old_secret\n'
                    u'comment: Comment for the old_secret\n'
                    u'tags: tag1, tag2, tag3\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'uuid                            parent    created              creator\n'
                    u'------------------------------  --------  -------------------  --------------------\n'
                    u'ver-0000000000000000000001x145  -         2015-10-21 00:00:15  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:user:vault-test-101\n'
                    u'reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'\n'
                )

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(
                    'sec-0000000000000000000001x140',
                ),
                {
                    'comment': 'Comment for the old_secret',
                    'created_at': 1445385615.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'secret_name': 'old_secret',
                    'secret_uuid': 'sec-0000000000000000000001x140',
                    'value': {'hostname': 'saas.yt'},
                    'version': 'ver-0000000000000000000001x145',
                },
            )

    def test_rsa_update_secret_with_ttl(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                secret_uuid = self.vault_client.create_secret(
                    name='new_secret',
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'update', 'secret',
                    secret_uuid,
                    '-u',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--ttl', '30',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertEqual(
                self.vault_client.get_version(secret_uuid)['expired_at'],
                1445385645.0,
            )

    def test_rsa_update_secret_state(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                secret_uuid = self.vault_client.create_secret(
                    name='new_secret',
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'update', 'secret',
                    secret_uuid,
                    '-u',
                    '-v', '{"username": "user", "password": "passw0rd"}',
                    '--state', 'hidden',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertEqual(
                self.vault_client.get_secret(secret_uuid).get('state_name'),
                'hidden',
            )


class TestGetSecretCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_rsa_error_result(self):
        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['get', 'secret', 'sec-0000000000000000000000ygj6'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.stdout, 'error: Requested a non-existent entity (Secret, sec-0000000000000000000000ygj6)\n')

    def test_rsa_error_result_json(self):
        with self.rsa_permissions_and_time_mock():
            result = self.runner.invoke(['get', 'secret', 'sec-0000000000000000000000ygj6', '-j'])
            self.assertEqual(result.exit_code, 1)
            result_json = json.loads(result.stdout)
            self.assertListEqual(
                [result_json['code'], result_json['message']],
                ['nonexistent_entity_error', 'Requested a non-existent entity (Secret, sec-0000000000000000000000ygj6)'],
            )

    def test_rsa_get_secret_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'READER',
                    abc_id=50,
                )
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'OWNER',
                    staff_id=236,
                )
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'APPENDER',
                    abc_id=14,
                )
                self.vault_client.create_token(
                    'sec-0000000000000000000000ygj0',
                    comment='Token comment',
                    signature='sign1',
                    tvm_client_id='2000367',
                )
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'OWNER',
                    abc_id=14,
                    abc_role_id=630,
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'secret',
                    'sec-0000000000000000000000ygj0',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000000ygj0\n'
                    u'name: secret_1\n'
                    u'comment: \n'
                    u'tags: \n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:00\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'| uuid                           | parent   | created             | creator              |\n'
                    u'|--------------------------------+----------+---------------------+----------------------|\n'
                    u'| ver-0000000000000000000000ygj4 | -        | 2015-10-21 00:00:03 | vault-test-100 (100) |\n'
                    u'| ver-0000000000000000000000ygj3 | -        | 2015-10-21 00:00:02 | vault-test-100 (100) |\n'
                    u'| ver-0000000000000000000000ygj2 | -        | 2015-10-21 00:00:01 | vault-test-100 (100) |\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:staff:yandex_search_tech_spam (Отдел безопасного поиска)\n'
                    u'owner:abc:passp:role:630 (Паспорт. Role: TVM менеджер)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'appender:abc:passp:scope:development (Паспорт. Scope: Разработка)\n'
                    u'\n'
                    u'tokens:\n'
                    u'+---------------------+----------------------------+-------------+---------------+--------------------------------+---------+\n'
                    u'| created             | tvm_client_id              | signature   | comment       | token_uuid                     | state   |\n'
                    u'|---------------------+----------------------------+-------------+---------------+--------------------------------+---------|\n'
                    u'| 2015-10-21 00:00:15 | 2000367 (social api (dev)) | sign1       | Token comment | tid-0000000000000000000001x143 | normal  |\n'
                    u'+---------------------+----------------------------+-------------+---------------+--------------------------------+---------+\n'
                    u'\n'
                )

    def test_rsa_get_secret_compact_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'READER',
                    abc_id=50,
                )
                self.vault_client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    'OWNER',
                    staff_id=236,
                )

        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'get', 'secret',
                    'sec-0000000000000000000000ygj0',
                    '--compact',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000000ygj0\n'
                    u'name: secret_1\n'
                    u'comment: \n'
                    u'tags: \n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:00\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:'
                    u'\nuuid                            parent    created              creator\n'
                    u'------------------------------  --------  -------------------  --------------------\n'
                    u'ver-0000000000000000000000ygj4  -         2015-10-21 00:00:03  vault-test-100 (100)\n'
                    u'ver-0000000000000000000000ygj3  -         2015-10-21 00:00:02  vault-test-100 (100)\n'
                    u'ver-0000000000000000000000ygj2  -         2015-10-21 00:00:01  vault-test-100 (100)\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'owner:staff:yandex_search_tech_spam (Отдел безопасного поиска)\n'
                    u'reader:abc:suggest:scope:development (Перевод саджеста. Scope: Разработка)\n'
                    u'\n',
                )

    def test_rsa_get_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with self.user_permissions_and_time_mock():
                    self.vault_client.create_token(
                        'sec-0000000000000000000000ygj0',
                        comment='Token comment',
                        signature='sign1',
                        tvm_client_id='2000367',
                    )
                    self.vault_client.create_token(
                        'sec-0000000000000000000000ygj0',
                        comment='Token comment',
                        signature='sign1',
                        tvm_client_id='2000355',
                    )
                command_args = [
                    'get', 'secret',
                    'sec-0000000000000000000000ygj0',
                    '-j',
                ]

                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertDictEqual(
                    json.loads(result.stdout),
                    {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                            'creator_login': 'vault-test-100',
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'secret_1',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                            'creator_login': 'vault-test-100',
                        }],
                        'secret_versions': [
                            {
                                'created_at': 1445385603.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj4',
                                'keys': ['password'],
                            },
                            {
                                'created_at': 1445385602.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj3',
                                'keys': ['password'],
                            },
                            {
                                'created_at': 1445385601.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'version': 'ver-0000000000000000000000ygj2',
                                'keys': ['password'],
                            },
                        ],
                        u'tokens': [
                            {
                                u'comment': u'Token comment',
                                u'created_at': 1445385615.0,
                                u'created_by': 100,
                                u'creator_login': u'vault-test-100',
                                u'signature': u'sign1',
                                u'secret_uuid': u'sec-0000000000000000000000ygj0',
                                u'state_name': u'normal',
                                u'token_uuid': u'tid-0000000000000000000001x140',
                                u'tvm_app': {
                                    u'abc_department': {
                                        u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                        u'id': 14,
                                        u'unique_name': u'passp'
                                    },
                                    u'abc_state': u'granted',
                                    u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                    u'name': u'social api (dev)',
                                    u'tvm_client_id': 2000367
                                },
                                u'tvm_client_id': 2000367
                            },
                            {
                                u'comment': u'Token comment',
                                u'created_at': 1445385615.0,
                                u'created_by': 100,
                                u'creator_login': u'vault-test-100',
                                u'signature': u'sign1',
                                u'secret_uuid': u'sec-0000000000000000000000ygj0',
                                u'state_name': u'normal',
                                u'token_uuid': u'tid-0000000000000000000001x141',
                                u'tvm_app': {
                                    u'abc_department': {
                                        u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                        u'id': 14,
                                        u'unique_name': u'passp'
                                    },
                                    u'abc_state': u'granted',
                                    u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                    u'name': u'passport_likers3',
                                    u'tvm_client_id': 2000355,
                                },
                                u'tvm_client_id': 2000355
                            }
                        ],
                        'updated_at': 1445385603.0,
                        'updated_by': 100,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                )

    def test_rsa_get_hidden_version_ok(self):
        with self.user_permissions_and_time_mock():
            with self.uuid_mock():
                secret = self.vault_client.create_secret('tro-lo-lo')
                self.vault_client.update_secret(secret, state='hidden')

        with self.rsa_permissions_and_time_mock():
            command_args = [
                'get', 'secret',
                secret,
            ]
            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertListEqual(
                result.stdout_as_list(),
                [
                    'state: hidden',
                    'uuid: sec-0000000000000000000001x140',
                    'name: tro-lo-lo',
                    'comment: ',
                    'tags: ',
                    '',
                    'creator: vault-test-100 (100)',
                    'created: 2015-10-21 00:00:15',
                    'updated: 2015-10-21 00:00:15',
                    '',
                    'versions:',
                    "The secret hasn't versions.",
                    '',
                    'roles:',
                    'owner:user:vault-test-100',
                    '',
                    '',
                ],
            )
