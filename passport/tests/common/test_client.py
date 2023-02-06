# -*- coding: utf-8 -*-

import json
import logging
import time

from library.python.vault_client import instances
from library.python.vault_client.auth import (
    RSAPrivateKeyAuth,
    RSASSHAgentAuth,
    RSASSHAgentHash,
)
from library.python.vault_client.client import _InvalidRSASignature
from library.python.vault_client.errors import (
    ClientError,
    ClientInvalidRsaKeyNumber,
    ClientNoKeysInSSHAgent,
    ClientRsaKeyHashNotFound,
    ClientUnknownRSAAuthType,
)
import mock
import paramiko
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.utils.common import noneless_dict
from passport.backend.vault.api import errors
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_OAUTH_TOKEN_1,
    TEST_RSA_LOGIN_1,
    TEST_RSA_PRIVATE_KEY_1,
    TEST_RSA_PRIVATE_KEY_2_MD5_HASH,
    TEST_RSA_PRIVATE_KEY_2_SHA1_HASH,
    TEST_RSA_PRIVATE_KEY_2_SHA256_HASH,
    TEST_RSA_PRIVATE_KEYS,
    TEST_RSA_PUBLIC_KEY_1,
    TEST_RSA_PUBLIC_KEY_2,
)
from passport.backend.vault.api.test.test_vault_client import TestVaultClient
from passport.backend.vault.api.test.uuid_mock import UuidMock
from passport.backend.vault.api.utils.secrets import (
    default_hash,
    sign_in_memory,
    token_hex,
)
from six import StringIO


class PermissionsTestsMixin(object):
    def _run_permissions_test(self):
        secret_uuid = self.client.create_secret(name='secret_1')
        secret_version = self.client.create_secret_version(
            secret_uuid=secret_uuid,
            value=[{'key': 'password', 'value': '123'}],
        )
        self.client.create_diff_version(secret_version, [{'key': 'name', 'value': '345'}])
        self.client.get_version(secret_version)
        self.client.list_secrets()
        self.client.get_secret(secret_uuid)
        self.client.update_secret(secret_uuid, name='secret_2')
        self.client.add_user_role_to_secret(secret_uuid, 'READER', uid=101)
        self.client.delete_user_role_from_secret(secret_uuid, 'READER', uid=101)
        self.client.get_owners(secret_uuid)

        bundle_uuid = self.client.create_bundle(name='bundle_1')
        self.client.update_bundle(bundle_uuid, comment='bundle comment 1')
        self.client.get_bundle(bundle_uuid)
        self.client.create_bundle_version(bundle_uuid, [secret_version])
        self.client.list_bundles()

        with TimeMock():
            with UuidMock():
                self.client.create_token(secret_uuid, tvm_client_id=101)

        self.assertListEqual(
            self.client.list_tokens(secret_uuid),
            [{
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'state_name': 'normal',
                'tvm_client_id': 101,
                'secret_uuid': secret_uuid,
                'token_uuid': 'tid-0000000000000000000000ygj0',
            }],
        )

        self.client.suggest_tags('test')
        self.client.ping()

        self.client.create_complete_secret(
            name='secret_2',
            secret_version=dict(value={'key': 'password', 'value': '123'}),
            roles=[{'uid': 102, 'role': 'READER'}],
        )


CLIENT_V3_SIGNATURE_TESTS = [
    {
        'request': {
            'method': 'get',
            'path': 'http://vault-api.passport.yandex.net/1/secrets/',
            'data': u'{"tags": "tag1,tag2", "query": "тестовый секрет"}',
            'timestamp': 1565681543,
            'login': 'ppodolsky',
        },
        'serialized_request':
            'GET\nhttp://vault-api.passport.yandex.net/1/secrets/\n{"tags": "tag1,tag2", '
            '"query": "\xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb9 '
            '\xd1\x81\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82"}\n1565681543\nppodolsky\n',
        'hashed_serialized_request': 'fe1fec702d6e69cf5eca7fd8dab51fa486f69fe4ec752c82b8d72ba5b672d7b6',
        'request_signature':
            'AAAAB3NzaC1yc2EAAAEAABtXq5x7974JjvHNcXktjIMVL6EK8y9QPXh_n14l8gHvhCI87di_n9-xIQ2MGz-hhgwOR'
            'bGcUY-bXF68OJYeO9c2J2VP-ra0EBs1YMBEqxwUp0h9IT4irQY_p8CTheZu9I4cLEFW7IQ1PBPrW-L7LZ8myvR7ED'
            '-WfRLLn87G50_VFOdrHbXYz0J1EbERNqqv1p3V0BkUva1_P9fz_E6mqd-NkBpiHRALXGMp3mXyJSMHGGiwK4H8zrJ'
            'rEg4qIhyWJ_AgX_rs2FlbLeFJhR4NnmTFzgTrxwt0RRJZ07ZMAjqGkb7GvCJTQdE2vZYyHmQCxr0iIgEVEIKumxMu'
            'dqLdHA==',
    },
]


class TestClientV3(BaseTestClass, PermissionsTestsMixin):
    fill_database = False
    fill_staff = True
    send_user_ticket = False

    def test_serialize_request(self):
        for t in CLIENT_V3_SIGNATURE_TESTS:
            self.assertEqual(
                self.client._serialize_request(
                    **t['request']
                ),
                t['serialized_request'],
            )
            self.assertEqual(
                default_hash(
                    self.client._serialize_request(
                        **t['request']
                    ),
                ),
                t['hashed_serialized_request'],
            )

    def test_sign_request(self):
        key = paramiko.RSAKey.from_private_key(
            StringIO(TEST_RSA_PRIVATE_KEY_1),
        )
        for t in CLIENT_V3_SIGNATURE_TESTS:
            self.assertEqual(
                self.client._rsa_sign_data(
                    self.client._serialize_request(
                        **t['request']
                    ),
                    key=key,
                ),
                t['request_signature'],
            )

    def test_oauth_ok(self):
        with PermissionsMock(oauth={'uid': 100, 'scope': 'vault:use'}):
            self.client.authorization = TEST_OAUTH_TOKEN_1
            self._run_permissions_test()

    def test_oauth_fail(self):
        self.client.authorization = TEST_OAUTH_TOKEN_1
        with LoggingMock() as logging_mock:
            with PermissionsMock(oauth={'uid': 0}):
                self.assertResponseEqual(
                    self.client.list_secrets(return_raw=True),
                    self.enrich_error_dict({
                        'blackbox_error': 'OK',
                        'code': 'invalid_oauth_token_error',
                        'message': 'Invalid oauth token',
                        'status': 'error',
                    })
                )

            with PermissionsMock(oauth={'uid': 100, 'scope': ''}):
                self.assertResponseError(
                    self.client.list_secrets(return_raw=True),
                    errors.InvalidScopesError(uid=100),
                )

            self.assertListEqual(
                logging_mock.getLogger('statbox').entries,
                [
                    (
                        {
                            'action': 'error',
                            'blackbox_error': u'OK',
                            'code': 'invalid_oauth_token_error',
                            'mode': 'list_secrets',
                            'message': 'Invalid oauth token',
                            'oauth_token': 'token-o*******',
                            'status': 'error'
                        },
                        'INFO', None, None,
                    ),
                    (
                        {
                            'action': 'error',
                            'code': 'invalid_scopes_error',
                            'mode': 'list_secrets',
                            'message': 'Invalid scope in a token',
                            'oauth_token': 'token-o*******',
                            'status': 'error',
                            'uid': 100
                        },
                        'INFO', None, None,
                    )
                ]
            )

    def test_rsa(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.client.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
            self._run_permissions_test()

    def test_rsa_agent_multiply_keys(self):
        with PermissionsMock(
            rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]},
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self._run_permissions_test()

    def test_rsa_agent_key_by_number(self):
        with PermissionsMock(
            rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]},
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self.client.rsa_auth = RSASSHAgentAuth(key_num=1)
            self._run_permissions_test()

    def test_rsa_agent_key_by_sha256_hash(self):
        with PermissionsMock(
            rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]},
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self.client.rsa_auth = RSASSHAgentHash(key_hash=TEST_RSA_PRIVATE_KEY_2_SHA256_HASH)
            self._run_permissions_test()

    def test_rsa_agent_key_by_md5_hash(self):
        with PermissionsMock(
            rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]},
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self.client.rsa_auth = RSASSHAgentHash(key_hash=TEST_RSA_PRIVATE_KEY_2_MD5_HASH)
            self._run_permissions_test()

    def test_rsa_agent_key_by_sha1_hash(self):
        with PermissionsMock(
            rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_2]},
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self.client.rsa_auth = RSASSHAgentHash(key_hash=TEST_RSA_PRIVATE_KEY_2_SHA1_HASH)
            self._run_permissions_test()

    def test_rsa_agent_is_empty(self):
        with PermissionsMock(ssh_agent_key=[]):
            with self.assertRaises(ClientNoKeysInSSHAgent):
                self._run_permissions_test()

    def test_unknown_auth_type(self):
        class UnknownRsaAuth(object):
            pass

        with self.assertRaises(ClientUnknownRSAAuthType):
            self.client = TestVaultClient(
                rsa_auth=UnknownRsaAuth(),
            )

    def test_rsa_invalid_agent_key_number(self):
        with PermissionsMock(
            ssh_agent_key=TEST_RSA_PRIVATE_KEYS,
        ):
            self.client.rsa_auth = RSASSHAgentAuth(key_num=10)
            with self.assertRaises(ClientInvalidRsaKeyNumber):
                self._run_permissions_test()

    def test_rsa_agent_hash_not_found(self):
        with PermissionsMock(ssh_agent_key=[TEST_RSA_PRIVATE_KEY_1]):
            self.client.rsa_auth = RSASSHAgentHash(key_hash=TEST_RSA_PRIVATE_KEY_2_SHA256_HASH)
            with self.assertRaises(ClientRsaKeyHashNotFound):
                self._run_permissions_test()

    def test_unpack(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.client.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
            secret_uuid = self.client.create_secret(name='secret_1')
            secret_version = self.client.create_secret_version(
                secret_uuid=secret_uuid,
                value={'password': '123'},
            )
            r = self.client.get_version(secret_version)
            self.assertDictEqual(r['value'], {'password': '123'})
            r = self.client.get_version(secret_version, packed_value=False,)
            self.assertListEqual(r['value'], [{'key': 'password', 'value': '123'}])

    def test_errors(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.client.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
            secret_uuid = self.client.create_secret(name='secret_1')

            self.assertRaises(
                ClientError,
                lambda: self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value='aaa',
                ),
            )

            self.assertRaises(
                ClientError,
                lambda: self.client.create_secret_version('nono', {}),
            )

    def test_client_send_request_id(self):
        self.request_id_patch.stop()
        with mock.patch('library.python.vault_client.client.token_hex', return_value='1234567890123456'):
            r = self.client.ping()

        rid = r.original_response.headers['X-Request-Id']
        self.assertEqual(rid[:16], self.client._request_id_prefix)
        self.assertEqual(rid[16:], '1234567890123456')

    def test_deprecation_warnings(self):
        with mock.patch.object(logging.getLogger('vault_client'), 'warning') as warn_mock:
            with mock.patch('library.python.vault_client.VaultClient.get_client_version', return_value='0.0.45'):
                instances.Custom(host='', native_client=self.native_client, check_status=True)
                warn_mock.assert_called_once_with('DeprecationWarning: please, update your Vault client (0.0.45) as soon as possible!')

    def test_no_deprecation_warnings(self):
        with mock.patch.object(logging.getLogger('vault_client'), 'warning') as warn_mock:
            with mock.patch('library.python.vault_client.VaultClient.get_client_version', return_value='9.9.999'):
                instances.Custom(host='', native_client=self.native_client, check_status=True)
                warn_mock.assert_not_called()


class VaultClientV2(TestVaultClient):
    """Предыдущая версия подписи без хеширования данных"""
    def _serialize_request(self, method, path, data, timestamp, login):
        r = '%s\n%s\n%s\n%s\n%s\n' % (method.upper(), path, data, timestamp, login)
        return r.encode('utf-8')

    def _rsa_sign_data(self, data, key):
        return sign_in_memory(data, key=key)


class TestClientV2(BaseTestClass, PermissionsTestsMixin):
    fill_database = False
    fill_staff = True

    def setUp(self):
        super(TestClientV2, self).setUp()
        self.client = VaultClientV2(
            native_client=self.native_client,
            user_ticket='user_ticket' if self.send_user_ticket else None,
            rsa_auth=not self.send_user_ticket,
        )

    def test_rsa(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self.client.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
            self._run_permissions_test()


class TestRSASignatureV1(BaseTestClass):
    def setUp(self):
        super(TestRSASignatureV1, self).setUp()
        self.rsa_auth = RSAPrivateKeyAuth(TEST_RSA_PRIVATE_KEY_1)
        self.host = ''
        self.rsa_login = TEST_RSA_LOGIN_1
        self._request_id_prefix = token_hex(8)
        self._last_request_id = None
        self.user_agent = 'VaultClient/0.0.42'

    def _headers(self, service_ticket=None, user_ticket=None, authorization=None, bypass_uid=None,
                 bypass_abc=None, bypass_staff=None):
        self._last_request_id = self._request_id_prefix + token_hex(8)
        return noneless_dict({
            'X-Ya-Service-Ticket': service_ticket,
            'X-Ya-User-Ticket': user_ticket,
            'X-Ya-Bypass-Uid': bypass_uid,
            'X-Ya-Bypass-Abc': bypass_abc,
            'X-Ya-Bypass-Staff': bypass_staff,
            'Authorization': authorization,
            'User-Agent': self.user_agent,
            'X-Request-Id': self._last_request_id,
        })

    def _serialize_request(self, url, request_data, timestamp):
        r = '%s\n%s\n%s' % (url.rstrip('?'), json.dumps(request_data or {}, sort_keys=True), timestamp)
        return r.encode('utf-8')

    def _proceed_rsa_auth(self, url, request_data=None, headers=None, skip_headers=False):
        rsa_login = self.rsa_login
        headers = self._headers(**(headers or {}))
        ctx = dict(headers=headers if not skip_headers else {})

        rsa_keys = self.rsa_auth()

        for key in rsa_keys:
            timestamp = str(int(time.time()))
            signature = sign_in_memory(
                default_hash(self._serialize_request(url, request_data, timestamp)),
                key=key,
            )

            ctx['headers']['X-Ya-Rsa-Signature'] = signature
            ctx['headers']['X-Ya-Rsa-Login'] = rsa_login
            ctx['headers']['X-Ya-Rsa-Timestamp'] = timestamp

            yield ctx

    def _validate_rsa_native_response(self, response):
        if response.status_code == 401:
            data = response.json()
            if data.get('code') == 'rsa_signature_error':
                raise _InvalidRSASignature()

    def _call_native_client(self, method, url, headers=None, skip_headers=False, timeout=None, skip_auth=False,
                            *args, **kwargs):
        response = None
        request_data = kwargs.get('json') or kwargs.get('params')
        client_func = getattr(self.native_client, method)

        for ctx in self._proceed_rsa_auth(url, request_data, headers, skip_headers):
            response = client_func(
                url,
                headers=ctx.get('headers'),
                timeout=60,
                *args,
                **kwargs
            )
            self._validate_rsa_native_response(response)
            return response
        return response

    def _list_secrets(self, tags=None, order_by=None, asc=False, role=None, yours=False, page=None, page_size=None,
                      bypass_uid=None, bypass_abc=None, bypass_staff=None, return_raw=False):
        url = self.host + '/1/secrets/'
        request_data = noneless_dict({
            'tags': tags,
            'order_by': order_by,
            'asc': asc,
            'role': role,
            'yours': yours,
            'page': page,
            'page_size': page_size,
        })
        headers = dict(
            bypass_uid=bypass_uid,
            bypass_abc=bypass_abc,
            bypass_staff=bypass_staff,
        )

        r = self._call_native_client('get', url, json=request_data, headers=headers)
        return r

    def test_rsa_signature(self):
        with PermissionsMock(rsa={'uid': 100, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            self._list_secrets()
