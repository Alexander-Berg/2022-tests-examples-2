# coding: utf-8

import os
import time

import mock
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock


class TestGrantsCommands(BaseTestClass):
    maxDiff = None

    def setUp(self):
        os.environ["TZ"] = "Europe/Moscow"
        time.tzset()

        super(TestGrantsCommands, self).setUp()
        self.runner = self.app.test_cli_runner()

        self.patches = [
            mock.patch.dict('os.environ', {'SUDO_USER': ''}),
            mock.patch('socket.getfqdn', return_value='test_hostname'),
            mock.patch('getpass.getuser', return_value='test_username'),
        ]
        map(lambda x: x.start(), self.patches)

    def tearDown(self):
        super(TestGrantsCommands)
        map(lambda x: x.stop(), reversed(self.patches))

    def test_grants_commands_ok(self):
        with self.app.app_context():
            with LoggingMock() as logging_mock:
                with TimeMock():
                    result = self.runner.invoke(self.cli, ['grants', 'list'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Vault API grants list\n'
                        u'Environment: development\n'
                        u'\n'
                        u'+-----------------+---------------+----------------------+---------------------+\n'
                        u'|   TVM client ID | Application   | Comment              | Created at          |\n'
                        u'|-----------------+---------------+----------------------+---------------------|\n'
                        u'|               1 | -             | Default external app | 2015-10-21 03:00:00 |\n'
                        u'+-----------------+---------------+----------------------+---------------------+\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'grant', '2000079', 'Test grant'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'TVM client ID: 2000079\n'
                        u'Comment: Test grant\n'
                        u'Access granted\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'list'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Vault API grants list\n'
                        u'Environment: development\n'
                        u'\n'
                        u'+-----------------+-----------------------------+----------------------+---------------------+\n'
                        u'|   TVM client ID | Application                 | Comment              | Created at          |\n'
                        u'|-----------------+-----------------------------+----------------------+---------------------|\n'
                        u'|               1 | -                           | Default external app | 2015-10-21 03:00:00 |\n'
                        u'|         2000079 | Паспорт [testing] (Паспорт) | Test grant           | 2015-10-21 03:00:00 |\n'
                        u'+-----------------+-----------------------------+----------------------+---------------------+\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'grant', '2000079'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'TVM client ID: 2000079\n'
                        u'Comment: \n'
                        u'Grant is already exists\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'revoke', '2000079'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'TVM client ID: 2000079\n'
                        u'Access revoked\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'list'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Vault API grants list\n'
                        u'Environment: development\n'
                        u'\n'
                        u'+-----------------+---------------+----------------------+---------------------+\n'
                        u'|   TVM client ID | Application   | Comment              | Created at          |\n'
                        u'|-----------------+---------------+----------------------+---------------------|\n'
                        u'|               1 | -             | Default external app | 2015-10-21 03:00:00 |\n'
                        u'+-----------------+---------------+----------------------+---------------------+\n'
                    )

                    result = self.runner.invoke(self.cli, ['grants', 'revoke', '2000079'])
                    self.assertEqual(result.exit_code, 0)
                    self.assertEqual(
                        result.output,
                        u'Environment: development\n'
                        u'\n'
                        u'TVM client ID: 2000079\n'
                        u'Grant is not exists\n'
                    )

                self.assertListEqual(
                    logging_mock.getLogger('statbox').entries,
                    [({'action': u'list',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'tvm_grants'},
                      'INFO',
                      None,
                      None),
                     ({'action': u'grant',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'tvm_grants',
                       'tvm_client_id': 2000079},
                      'INFO',
                      None,
                      None),
                     ({'action': u'list',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'tvm_grants'},
                      'INFO',
                      None,
                      None),
                     ({'action': u'revoke',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'tvm_grants',
                       'tvm_client_id': 2000079},
                      'INFO',
                      None,
                      None),
                     ({'action': u'list',
                       'fqdn': 'test_hostname',
                       'login': 'test_username',
                       'mode': 'tvm_grants'},
                      'INFO',
                      None,
                      None)],
                )
