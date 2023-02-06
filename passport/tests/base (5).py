# coding: utf-8

import base64
from contextlib import contextmanager
import json
import logging
import os
import unittest

import library.python.vault_client as vault_client
import mock
import paramiko
import requests_mock
import six
from vault_client_deploy.configs import (
    DeploySection,
    Environment,
)
import yatest.common as yc


VAULT_API_URL = vault_client.instances.VAULT_PRODUCTION_API
VAULT_API_GET_VERSION_URL = VAULT_API_URL + '/1/versions/{}/'
VAULT_API_STATUS_URL = VAULT_API_URL + '/status/'
VAULT_API_PING_URL = VAULT_API_URL + '/ping.html'


class FakeEnvironment(Environment):
    def __init__(self, enable_fake_file_operation=True, *args, **kwargs):
        super(FakeEnvironment, self).__init__(*args, **kwargs)
        self._test_file_operations = []
        self._test_enable_fake_file_operations = enable_fake_file_operation

    def _test_log_operation(self, name, *args, **kwargs):
        self._test_file_operations.append(dict(
            name=name,
            args=args,
            kwargs=kwargs,
        ))

    def save_file(self, *args, **kwargs):
        if self._test_enable_fake_file_operations:
            self._test_log_operation('save_file', *args, **kwargs)
            return

        return super(FakeEnvironment, self).save_file(*args, **kwargs)


class FakeSection(DeploySection):
    def __init__(self, environment, conf_section=[], name='fake section'):
        super(FakeSection, self).__init__(environment, conf_section, name)


class BaseYavDeployTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.assets_path = self.get_assets_path()
        self.logger = logging.getLogger()
        self.paramiko_mock = mock.patch.object(
            paramiko.agent.Agent,
            'get_keys',
            return_value=[paramiko.RSAKey.from_private_key(six.StringIO(TEST_RSA_PRIVATE_KEY_1))],
        )
        self.paramiko_mock.start()

    def tearDown(self):
        self.paramiko_mock.stop()

    def get_assets_path(self):
        return yc.source_path() + '/passport/backend/vault/cli/yav_deploy/tests/assets'

    def get_config_path(self, path=''):
        return os.path.join(self.assets_path, path)

    @contextmanager
    def get_environment(self, assets_name, logger=None, debug=True, *args, **kwargs):
        yield FakeEnvironment(
            confs_path=self.get_config_path(assets_name),
            logger=logger or self.logger,
            chroot='',
            debug=debug,
            *args,
            **kwargs
        )

    @contextmanager
    def mock_env(self, env_dict):
        old_env = os.environ
        try:
            os.environ = env_dict
            yield
        finally:
            os.environ = old_env

    @contextmanager
    def mock_secrets(self, secrets=None):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', VAULT_API_PING_URL, text='Mocked ping')
            m.register_uri('GET', VAULT_API_STATUS_URL, text=json.dumps(
                {'is_deprecated_client': False, 'status': 'ok', '_mocked': True}
            ))

            if secrets:
                for secret_uuid, response in secrets.items():
                    m.register_uri('GET', VAULT_API_GET_VERSION_URL.format(secret_uuid), text=json.dumps(response))
            yield m

    def assertEnvOperations(self, env, compared):
        self.assertListEqual(
            env._test_file_operations,
            compared,
        )


class LogMock(object):
    def __init__(self):
        self.entries = []

    def log(self, record, level, *args, **kwargs):
        self.entries.append((record, level))

    def info(self, record, *args, **kwargs):
        self.log(record, 'INFO')

    def debug(self, record, *args, **kwargs):
        self.log(record, 'DEBUG')

    def warning(self, record, *args, **kwargs):
        self.log(record, 'WARNING')

    def error(self, record, *args, **kwargs):
        self.log(record, 'ERROR')


def make_encoded_secret_value(key, data):
    return dict(
        key=key,
        encoding='base64',
        value=base64.b64encode(
            data.encode('utf-8') if isinstance(data, six.text_type) else data,
        ).decode('ascii'),
    )


TEST_SECRETS_RESPONSES = {
    'sec-90000000000000000000000001': {
        'status': 'ok',
        'version': {
            'value': [
                {'key': 'login', 'value': 'ppodolsky'},
                {'key': 'password', 'value': '123455'},
            ],
        },
    },
    'sec-90000000000000000000000002': {
        'status': 'ok',
        'version': {
            'value': [
                {'key': 'login', 'value': 'arhibot'},
                {'key': 'password', 'value': '564323123'},
            ],
        },
    },
    'sec-90000000000000000000000004': {
        'status': 'ok',
        'version': {
            'value': [
                {'key': 'test.key', 'value': 'key file'},
                {'key': 'test.crt', 'value': 'cert file'},
                make_encoded_secret_value('test2.key', b'key file'),
                make_encoded_secret_value('test2.crt', b'cert file'),
            ],
        },
    },
    'sec-90000000000000000000000005': {
        'status': 'ok',
        'version': {
            'value': [
                {'key': 'test.key', 'value': 'key file'},
                {'key': 'test.crt', 'value': 'cert file'},
                make_encoded_secret_value('new_test.key', b'key file'),
                make_encoded_secret_value('new_test.crt', b'cert file'),
            ],
        },
    },
    'ver-90000000000000000000000004': {
        'status': 'ok',
        'version': {
            'value': [
                {'key': 'DB_LOGIN', 'value': 'passport_db'},
                {'key': 'DB_PASSWORD', 'value': 'fksdjfw348jdsjfsdlkgj@fsdg'},
            ],
        },
    },
    'sec-90000000000000000000000006': {
        'status': 'ok',
        'version': {
            'value': [
                {
                    'key': 'data',
                    'value': '''
                        {
                            "login": "arhibot",
                            "password": "564323123",
                            "tokens": [
                                "token 1",
                                "token 2"
                            ]
                        }
                    ''',
                }
            ],
        },
    },
}

TEST_RSA_PRIVATE_KEY_1 = u'''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA63Qr2tsZPe9kQJdQE9im/dQ2TU/fc5mt+TD7IdHI6F3NzIlh
m8wX4ferxzma5WUk2sTJpzlNcnHBh7cBAyJMJo0knktKvfZD7uHcxPBrhlHUV58D
HPwpXM9znJaElNQoZXPQ3y/dmvY9ym0khGNCDjGjI5z9C8ATw8+D7Y6DS3ZC5oOQ
Q5r4f/K2sKbVakUutqunkMR14Non5O1abtqjoYCyCAXP08rdj3ooY6I/maOty/yU
I2Xg6NHpP5Q/YvskZPNxB1M3VMh0WZPIX0urb1Qzam/zScM6Ew31nsh55gPQ8r8j
6wkPBk/j0xhdtl53tLTDj317C8BHEGTPmdPhdQIDAQABAoIBAFyMLTC5LhLKJf29
fBxQ7FKZNz7sRkiJ/3gTaKLCctXjCSF8XoF+l2SalUqZueiw+OuErj6sp2R0kj1m
EV/J+2Sr1djif15rjgg3fy9p0NnbEDvgpLif5SI16JuEDljxi29VNqSDi/d9Eoye
mdvvp+csW5OEAXK87QfqaVDW04S1FlKpQqXv3If0MSmt8J26IUUMWeTXfIKGBIGx
N4gfbFlrLxoediyDUFv0CE5bSQpTeEe6q+e1iMdrWXZHA8gWtdU2MEw+v7wcKju7
oP//Jp/Eg8pXmoWC80lje+Tb3pL9WHRMR2yt89Q81nXvIBRVHWSqvWZLfDEWjUoT
IGNYgAECgYEA+CSdesEmh4xKMrQTo95zTomm6vXZ+gJe9gvS24F6lx3DN9x9LMrl
cK1WOSGVus2feVDxjVz4F8Mdu8hPE9BZWhKzSg2AqBXG5t1htKaSQ2D8Jrks3byc
hjIpo5Zzqen/FUpFiA1IxlrSMK8z0o0wXsGRXVoc6+0fskMRluE3owECgYEA8uiz
Tus3ClCrcjL2ycIX2TAQMhlP6pjPt1YvO+SPjBvVj74ArwKZxPrm1XmqVqEekvpg
sdeWU9S6h3J+yhxi2DIDCgM2nUotYBcCaFs6Ir11RXgQyjYKeJsFV1sYrImTFsCY
0QtVG87xWZeYAHkby2qhT8dBr+iyZ/TBJl8AYnUCgYBWhF2r6SBH7nAIUaTvY6YM
Yg4iqemAM8dsPh8cjX5ypdvk5Cl4rp1kter0LHOKGBtcLw6pXRrbHhqF2IdJv0EI
GLEORrru3/jjkZh5ZgJlH7GKxtGP1i001NSTxuc4/O8FO0oW75rKHexfMRb+eF+/
Cfpm8/5Ve+2rN5swYgIGAQKBgCT9grC16P/NIQ6W7DX1NKSCSTUX3a+f7aHBohfA
yotPgcoN6RS9lKUGgDhp+qKOjpVbQ3ZRmjbR4kXWDbDBedvqYcQYkSyKqzZCyr8R
hVzc9QrLKeNhL18GXF3dJXjAyoFgeuT6kM9XSDGYgDEyQCVN65q2gS5EhUaHYxJw
zSIxAoGBAIUHxgTXBStKvvO31Cu2MHLl3VwnNu+7FTQHSArMTndv6BPOJZha8+Bc
U2eCXNWVYzd7dGObEac3iX/tGi7BFKgj3DUgCHpibE2GsByb9GCwRK7ELGMb54HU
S6YpUSO7mgyX1eqSBfcFx0+KOtvk1CvqnxcF+ImyvqkLuDTI120h
-----END RSA PRIVATE KEY-----
'''
