# coding: utf-8

from contextlib import contextmanager
import json

from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_OAUTH_TOKEN_1,
    TEST_RSA_PRIVATE_KEY_2,
    TEST_RSA_PRIVATE_KEYS,
)
import requests_mock

from .base import BaseCLICommandTestCase


class TestOAuthCommand(BaseCLICommandTestCase):
    OAUTH_GET_TOKEN_URL = 'https://oauth.yandex-team.ru/token'
    OAUTH_TOKEN = TEST_OAUTH_TOKEN_1.split(' ')[1]

    @contextmanager
    def mock_oauth_api(self, response, status_code=200):
        with requests_mock.Mocker() as m:
            m.register_uri('POST', self.OAUTH_GET_TOKEN_URL, text=json.dumps(response), status_code=status_code)
            yield m

    def test_get_oauth_token_ok(self):
        with self.mock_oauth_api(dict(access_token=self.OAUTH_TOKEN)):
            with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEYS):
                result = self.runner.invoke(['oauth'])
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    '{}\n'.format(self.OAUTH_TOKEN),
                )

    def test_get_oauth_token_invalid_grant(self):
        with self.mock_oauth_api(dict(error='invalid_grant')):
            with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEY_2):
                result = self.runner.invoke(['oauth'])
                self.assertEqual(result.exit_code, 3, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'error: OAuth. SSH sign is not valid or ssh-keys not found\n',
                )

    def test_get_oauth_token_error(self):
        with self.mock_oauth_api(dict(error='error', error_dwscription='error description')):
            with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEY_2):
                result = self.runner.invoke(['oauth'])
                self.assertEqual(result.exit_code, 3, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'error: OAuth. error\n',
                )

    def test_get_oauth_token_http_error(self):
        with self.mock_oauth_api(dict(error='error', error_dwscription='error description'), status_code=500):
            with PermissionsMock(ssh_agent_key=TEST_RSA_PRIVATE_KEY_2):
                result = self.runner.invoke(['oauth'])
                self.assertEqual(result.exit_code, 3, result.stdout)
                self.assertEqual(
                    result.stdout,
                    'error: OAuth. HTTP error 500\n',
                )

    def test_missing_ssh_key(self):
        with PermissionsMock(ssh_agent_key=[]):
            result = self.runner.invoke(['oauth'])
            self.assertEqual(result.exit_code, 3, result.stdout)
            self.assertEqual(
                result.stdout,
                'error: No keys in the SSH Agent. Check output of \'ssh-add -l\' command\n',
            )
