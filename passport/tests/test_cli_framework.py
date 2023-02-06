# coding: utf-8

import argparse
import sys

from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.vault_cli_runner import CLIRunner
from vault_client_cli.cli_base import (
    CLICommand,
    CLIManager,
    JSONArgument,
)


sys.argv[0] = 'app.py'


class TestJSONArgument(BaseTestCase):
    def test_valid_json_argument(self):
        ja = JSONArgument('-v', 'json')
        ns = argparse.Namespace()
        ja(None, ns, '{"key": "value"}')
        self.assertDictEqual(ns.json, {'key': 'value'})

    def test_invalid_json_argument(self):
        with self.assertRaises(ValueError):
            ja = JSONArgument('-v', 'json')
            ns = argparse.Namespace()
            ja(None, ns, '["key": "value"]', option_string='-v')


class FakeCLICommand(CLICommand):
    """Fake command"""
    def __init__(self, arg_parser, **kwargs):
        super(FakeCLICommand, self).__init__(arg_parser, **kwargs)
        self.usage = 'app.py fake command [-v <value>]'
        self.add_argument('secret_uuid')
        self.add_argument('-v', '--value', action=JSONArgument, metavar='<value>', distinct_group='value')
        self.add_argument('-u', '--update', action=JSONArgument, metavar='<value>', distinct_group='value')

    def process(self, cli_args, *args, **kwargs):
        self.echo('Fake command: success. Usage: {}'.format(self.usage))
        self.echo('args: {}'.format(cli_args))
        self.exit()


class FakeCLIFailedCommand(CLICommand):
    """Fake command"""
    def __init__(self, arg_parser, **kwargs):
        super(FakeCLIFailedCommand, self).__init__(arg_parser, **kwargs)

    def process(self, cli_args, *args, **kwargs):
        raise Exception('Command exception')


class FakeCLIManager(CLIManager):
    """Fake app"""
    def __init__(self, **kwargs):
        super(FakeCLIManager, self).__init__(doc=self.__doc__, **kwargs)
        self.assign_command('fake command', FakeCLICommand)
        self.assign_command('fake error', FakeCLIFailedCommand)
        self.assign_command('command', FakeCLICommand)


class TestCLIManager(BaseTestCase):
    def setUp(self):
        super(TestCLIManager, self).setUp()
        self.manager = FakeCLIManager()
        self.runner = CLIRunner(self.manager)
        self.maxDiff = None

    def test_call_without_command(self):
        result = self.runner.invoke([])
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': '2',
                'exit_code': 2,
                'runner_cls': 'CLIRunner',
                'stderr': 'error: too few arguments\n--------------------\nusage: app.py [-h] command ...\n\n'
                          'Fake app\n\npositional arguments:\n  command\n'
                          '\noptional arguments:\n  -h, --help  show this help message and exit\n'
                          '\navailable commands:\n  fake command\n  fake error\n  command\n'
                          '\nRead the documentation on the website https://vault-api.passport.yandex.net/docs/\n',
                'stdout': '',
            },
        )

    def test_call_command_without_second_part(self):
        result = self.runner.invoke(['fake'])
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': '2',
                'exit_code': 2,
                'runner_cls': 'CLIRunner',
                'stderr': 'error: too few arguments\n--------------------\nusage: app.py fake [-h] command ...\n\n'
                          'positional arguments:\n  command\n\noptional arguments:\n'
                          '  -h, --help  show this help message and exit\n\n'
                          'available commands:\n  fake command\n  fake error\n  command\n'
                          '\nRead the documentation on the website https://vault-api.passport.yandex.net/docs/\n',
                'stdout': u'',
            },
        )

    def test_call_command_help(self):
        result = self.runner.invoke(['fake', 'command', '-h'])
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': '',
                'stdout': 'usage: app.py fake command [-v <value>]\n\nFake command\n\npositional arguments:\n'
                          '  secret_uuid\n\noptional arguments:\n'
                          '  -h, --help            show this help message and exit\n'
                          '  -v <value>, --value <value>\n'
                          '  -u <value>, --update <value>\n'
                          '\navailable commands:\n  fake command\n  fake error\n  command\n'
                          '\nRead the documentation on the website https://vault-api.passport.yandex.net/docs/\n',
            },
        )

    def test_call_fake_command_ok(self):
        result = self.runner.invoke(['fake', 'command', 'sec-00000000000000123', '-v', '{"key": "value"}'])
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': '',
                'stdout': "Fake command: success. Usage: app.py fake command [-v <value>]\n"
                          "args: Namespace(_command_1='fake', _command_2='command', "
                          "secret_uuid='sec-00000000000000123', update=None, value={u'key': u'value'})\n",
            },
        )

    def test_call_command_ok(self):
        result = self.runner.invoke(['command', 'sec-00000000000000123', '-v', '{"key": "value"}'])
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': '',
                'stdout': "Fake command: success. Usage: app.py fake command [-v <value>]\n"
                          "args: Namespace(_command_1='command', secret_uuid='sec-00000000000000123', "
                          "update=None, value={u'key': u'value'})\n",
            },
        )

    def test_manager_print_help_with_message(self):
        with self.runner.isolation() as streams:
            self.manager.print_help('Test message')
            self.assertEqual(
                streams[0].getvalue().decode('utf-8'),
                "Test message\n--------------------\nusage: app.py [-h] command ...\n\nFake app\n\n"
                "positional arguments:\n  command\n\noptional arguments:\n"
                "  -h, --help  show this help message and exit\n",
            )

    def test_catch_command_errors(self):
        result = self.runner.invoke(['fake', 'error'])
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(result.stderr, 'error: Command exception\n')

    def test_catch_command_errors_in_debug_mode(self):
        self.manager.debug = True
        result = self.runner.invoke(['fake', 'error'])
        self.assertEqual(result.exit_code, 3)
        self.assertRegexpMatches(result.stderr, r'raise Exception\(\'Command exception\'\)')

    def test_call_invalid_param(self):
        result = self.runner.invoke(['fake', 'command', 'sec-00000000000000123', '-v', 'ivalid json'])
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(
            result.as_dict()['stderr'],
            r'error: -v: No JSON object could be decoded',
        )
