# coding: utf-8

import mock
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.models.secret import SecretUUIDType
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import PermissionsMock


class TestRolesCommands(BaseTestClass):
    maxDiff = None
    send_user_ticket = True

    def setUp(self):
        super(TestRolesCommands, self).setUp()
        self.runner = self.app.test_cli_runner()

        self.patches = [
            mock.patch.dict('os.environ', {'SUDO_USER': ''}),
            mock.patch('socket.getfqdn', return_value='test_hostname'),
            mock.patch('getpass.getuser', return_value='test_username'),
        ]
        map(lambda x: x.start(), self.patches)

        self._old_robot_login = self.config['cli']['robot_login']
        self.config['cli']['robot_login'] = 'ppodolsky'

    def tearDown(self):
        super(TestRolesCommands)
        self.config['cli']['robot_login'] = self._old_robot_login
        map(lambda x: x.stop(), reversed(self.patches))

    def make_secret(self, with_extended_roles=False):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret_uuid = self.client.create_secret('test_secret')

                if with_extended_roles:
                    self.client.add_user_role_to_secret(
                        secret_uuid,
                        'owner',
                        abc_id=14,
                        abc_scope='development',
                    )
                    self.client.add_user_role_to_secret(
                        secret_uuid,
                        'reader',
                        abc_id=14,
                        abc_role_id='1',
                    )
                    self.client.add_user_role_to_secret(
                        secret_uuid,
                        'appender',
                        staff_id=38096,
                    )

        return secret_uuid

    def test_roles_info_unknown_secret_uuid(self):
        with self.app.app_context():
            secret_uuid = str(SecretUUIDType.create_ulid())

            result = self.runner.invoke(
                self.cli,
                ['roles', 'info', secret_uuid],
                catch_exceptions=False,
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                u'Environment: development\n'
                u'\n'
                u'Secret "{}" not found\n'.format(secret_uuid)
            )

    def test_roles_info_invalid_secret_uuid(self):
        with self.app.app_context():
            secret_uuid = 'blahblahblah'

            result = self.runner.invoke(
                self.cli,
                ['roles', 'info', secret_uuid],
                catch_exceptions=False,
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                u'Environment: development\n'
                u'\n'
                u'u\'blahblahblah\' is an invalid UUID value\n'
            )

    def test_roles_info_ok(self):
        with self.app.app_context():
            secret_uuid = self.make_secret(with_extended_roles=True)

            with LoggingMock() as logging_mock:
                with TimeMock():
                    result = self.runner.invoke(
                        self.cli,
                        ['roles', 'info', secret_uuid],
                        catch_exceptions=False,
                    )
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'Secret UUID: {}\n'
                        u'Name: test_secret\n'
                        u'\n'
                        u'Roles:\n'
                        u'+----------+--------------------------------------------------------------------------------+\n'
                        u'| owner    | owner:user:vault-test-100                                                      |\n'
                        u'| owner    | owner:abc:passp:scope:development (Паспорт. Scope: Разработка)                 |\n'
                        u'| reader   | reader:abc:passp:role:1 (Паспорт. Role: Руководитель сервиса)                  |\n'
                        u'| appender | appender:staff:yandex_search_tech_sq (Управление качества поисковых продуктов) |\n'
                        u'+----------+--------------------------------------------------------------------------------+\n'
                        u''.format(secret_uuid)
                    )

                self.assertListEqual(
                    logging_mock.getLogger('statbox').entries,
                    [({'action': u'info',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'cli_roles',
                       'secret_uuid': secret_uuid},
                      'INFO',
                      None,
                      None)],
                )

    def test_roles_add_ok(self):
        with self.app.app_context():
            secret_uuid = self.make_secret()

            with LoggingMock() as logging_mock:
                with TimeMock():
                    roles = [
                        'owner:staff:yandex_personal_com_aux_sec',
                        'reader:staff:2',
                        'appender:user:ppodolsky',
                        'appender:user:1120000000038274',
                        'owner:abc:14:scope:development',
                        'owner:abc:passp:scope:development',
                        'owner:abc:14:role:1',
                        'owner:abc:passp:role:1',
                    ]
                    for r in roles:
                        result = self.runner.invoke(
                            self.cli,
                            ['roles', 'add', secret_uuid, r],
                            catch_exceptions=False,
                        )
                        self.assertEqual(result.exit_code, 0, result.output)

                    result = self.runner.invoke(
                        self.cli,
                        ['roles', 'add', secret_uuid, roles[1]],
                        catch_exceptions=False,
                    )
                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'Secret UUID: {}\n'
                        u'Name: test_secret\n'
                        u'\n'
                        u'Roles:\n'
                        u'+----------+----------------------------------------------------------------------------------------------+\n'
                        u'| owner    | owner:user:vault-test-100                                                                    |\n'
                        u'| owner    | owner:staff:yandex_personal_com_aux_sec (Группа аналитики и безопасности систем авторизации) |\n'
                        u'| owner    | owner:abc:passp:role:1 (Паспорт. Role: Руководитель сервиса)                                 |\n'
                        u'| owner    | owner:abc:passp:scope:development (Паспорт. Scope: Разработка)                               |\n'
                        u'| reader   | reader:staff:_vault_test_group_1 (Тестовая группа Секретницы 1)                              |\n'
                        u'| appender | appender:user:ppodolsky                                                                      |\n'
                        u'+----------+----------------------------------------------------------------------------------------------+\n'
                        u''.format(secret_uuid)
                    )

                    self.assertListEqual(
                        logging_mock.getLogger('statbox').entries,
                        [({'action': u'add_role',
                           'creator_uid': 1120000000038274,
                           'fqdn': 'test_hostname',
                           'login': 'test_username',
                           'mode': 'cli_roles',
                           'raw_role': u'owner:staff:yandex_personal_com_aux_sec',
                           'role': 'Roles.OWNER',
                           'secret_uuid': secret_uuid,
                           'staff_id': 2864},
                          'INFO',
                          None,
                          None),
                         ({'action': u'add_role',
                           'creator_uid': 1120000000038274,
                           'fqdn': 'test_hostname',
                           'login': 'test_username',
                           'mode': 'cli_roles',
                           'raw_role': u'reader:staff:2',
                           'role': 'Roles.READER',
                           'secret_uuid': secret_uuid,
                           'staff_id': u'2'},
                          'INFO',
                          None,
                          None),
                         ({'action': u'add_role',
                           'creator_uid': 1120000000038274,
                           'fqdn': 'test_hostname',
                           'login': 'test_username',
                           'mode': 'cli_roles',
                           'raw_role': u'appender:user:ppodolsky',
                           'role': 'Roles.APPENDER',
                           'secret_uuid': secret_uuid,
                           'uid': 1120000000038274},
                          'INFO',
                          None,
                          None),
                         ({'abc_id': u'14',
                           'abc_scope': u'development',
                           'action': u'add_role',
                           'creator_uid': 1120000000038274,
                           'fqdn': 'test_hostname',
                           'login': 'test_username',
                           'mode': 'cli_roles',
                           'raw_role': u'owner:abc:14:scope:development',
                           'role': 'Roles.OWNER',
                           'secret_uuid': secret_uuid},
                          'INFO',
                          None,
                          None),
                         ({'abc_id': u'14',
                           'abc_role_id': u'1',
                           'action': u'add_role',
                           'creator_uid': 1120000000038274,
                           'fqdn': 'test_hostname',
                           'login': 'test_username',
                           'mode': 'cli_roles',
                           'raw_role': u'owner:abc:14:role:1',
                           'role': 'Roles.OWNER',
                           'secret_uuid': secret_uuid},
                          'INFO',
                          None,
                          None)],
                    )
