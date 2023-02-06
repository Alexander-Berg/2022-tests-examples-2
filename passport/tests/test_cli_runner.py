# coding: utf-8

import sys

from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.vault_cli_runner import CLIRunner
import six


class FakeCLIException(Exception):
    pass


class FakeCLIManager(object):
    def process(self, args=None):
        args = args or ['run']
        command = args[0]
        if command == 'run':
            six.print_('Success\nУспех', file=sys.stdout)
            six.print_('No errors\nБез ошибок', file=sys.stderr)
        elif command == 'fail':
            sys.exit('Fail')
        elif command == 'echo':
            six.print_(sys.stdin.read(), end='')
        elif command == 'exception':
            raise FakeCLIException('Fake exception')


class TestCLIRunner(BaseTestCase):
    def setUp(self):
        super(TestCLIRunner, self).setUp()
        self.runner = CLIRunner(
            cli_manager=FakeCLIManager(),
        )

    def test_cli_runner_ok(self):
        result = self.runner.invoke(['run'])
        self.assertEqual(repr(result), '<CLIRunnerResult ok>')
        self.assertDictEqual(
            result.as_dict(exc_info=True),
            {
                'exception': None,
                'exc_info': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stdout': u'Success\nУспех\n',
                'stderr': u'No errors\nБез ошибок\n',
            },
        )
        self.assertListEqual(
            result.stdout_as_list(),
            [u'Success', u'Успех', u''],
        )
        self.assertListEqual(
            result.stderr_as_list(),
            [u'No errors', u'Без ошибок', u''],
        )

    def test_cli_runner_fail(self):
        result = self.runner.invoke(['fail'])
        self.assertEqual(repr(result), '<CLIRunnerResult SystemExit(\'Fail\',)>')
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': 'Fail',
                'exit_code': 1,
                'runner_cls': 'CLIRunner',
                'stdout': u'Fail',
                'stderr': u'\n',
            },
        )

    def test_cli_runner_exception(self):
        result = self.runner.invoke(['exception'])
        self.assertEqual(repr(result), '<CLIRunnerResult FakeCLIException(\'Fake exception\',)>')
        self.assertDictEqual(
            result.as_dict(),
            {
                'exception': 'Fake exception',
                'exit_code': 1,
                'runner_cls': 'CLIRunner',
                'stdout': u'',
                'stderr': u'',
            },
        )

    def test_cli_runner_not_catch_exception(self):
        with self.assertRaises(FakeCLIException):
            self.runner.invoke(['exception'], catch_exceptions=False)

    def test_cli_runner_empty_stdin(self):
        result = self.runner.invoke(['echo'])
        self.assertEqual(repr(result), '<CLIRunnerResult ok>')
        self.assertDictEqual(
            result.as_dict(exc_info=True),
            {
                'exc_info': None,
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': u'',
                'stdout': u'',
            },
        )

    def test_cli_runner_stream_stdin(self):
        result = self.runner.invoke(
            ['echo'],
            stdin=six.BytesIO(u'Test input streams\nПроверяем входной поток\n'.encode('utf-8')),
        )
        self.assertEqual(repr(result), '<CLIRunnerResult ok>')
        self.assertDictEqual(
            result.as_dict(exc_info=True),
            {
                'exc_info': None,
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': u'',
                'stdout': u'Test input streams\nПроверяем входной поток\n',
            },
        )

    def test_cli_runner_string_stdin(self):
        result = self.runner.invoke(
            ['echo'],
            stdin=u'Test input streams\nПроверяем входной поток\n',
        )
        self.assertEqual(repr(result), '<CLIRunnerResult ok>')
        self.assertDictEqual(
            result.as_dict(exc_info=True),
            {
                'exc_info': None,
                'exception': None,
                'exit_code': 0,
                'runner_cls': 'CLIRunner',
                'stderr': u'',
                'stdout': u'Test input streams\nПроверяем входной поток\n',
            },
        )
