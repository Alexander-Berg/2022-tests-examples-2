# coding: utf-8

import sys
import warnings

from library.python.vault_client import __version__ as vault_client_version
from passport.backend.vault.api.test.permissions_mock import TEST_RSA_PRIVATE_KEY_2
from vault_client_cli.commands import VaultCLICommand

from .base import BaseCLICommandTestCase


class TestRsaAuthArgs(BaseCLICommandTestCase):
    def test_rsa_private_keys_requires_login(self):
        self.manager.client = None
        result = self.runner.invoke(
            ['list', 'secrets', '--rsa-private-key', '-'],
            stdin=TEST_RSA_PRIVATE_KEY_2,
        )
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(
            result.stdout.split('\n', 1)[0],
            'error: --rsa-private-key requires --rsa-login',
        )


class _WarnCliCommand(VaultCLICommand):
    def process(self, cli_args, client, debug=False, *args, **kwargs):
        if cli_args.skip_warnings:
            warnings.warn('Skip warnings')
        else:
            warnings.warn('Warning')
        self.echo('Test cli commands')


class TestCatchWarnings(BaseCLICommandTestCase):
    def setUp(self):
        super(TestCatchWarnings, self).setUp()
        self.manager.assign_command('catch warnings', _WarnCliCommand)

    def test_no_catch_warnings(self):
        result = self.runner.invoke(['catch', 'warnings'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegexpMatches(
            result.stdout,
            r'UserWarning: Warning\n  warnings.warn\(\'Warning\'\)\nTest cli commands\n',
        )

    def test_catch_warnings(self):
        result = self.runner.invoke(['catch', 'warnings', '--skip-warnings'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, 'Test cli commands\n')


class TestPrintVersion(BaseCLICommandTestCase):
    def test_print_version(self):
        result = self.runner.invoke(['--version'])
        self.assertEqual(
            result.stdout,
            'yav {} (python: {})\n'.format(vault_client_version, sys.version.replace('\n', '')),
        )
