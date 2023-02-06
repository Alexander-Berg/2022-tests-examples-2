# -*- coding: utf-8 -*-
from contextlib import contextmanager
import json

from django.conf import settings
from library.python.vault_client.instances import Production
import mock
from passport.backend.oauth.tvm_api.tvm_api.db.vault_client import VaultClient
import requests
import requests_mock


TEST_VAULT_SECRET_UUID_1 = 'sec-0000000000000000000000ygj0'
TEST_VAULT_SECRET_UUID_2 = 'sec-0000000000000000000000ygj1'
TEST_VAULT_VERSION_UUID_1 = 'ver-0000000000000000000000ygj5'
TEST_VAULT_VERSION_UUID_2 = 'ver-0000000000000000000000ygj6'


class VaultMockMixin(object):
    @contextmanager
    def vault_mock(self):
        with requests_mock.Mocker() as adapter:
            adapter.register_uri(
                'GET',
                settings.VAULT_API_URL + '/status/',
                text=json.dumps({'is_deprecated_client': False, 'status': 'ok', '_mocked': True}),
            )
            adapter.register_uri(
                'GET',
                settings.VAULT_API_URL + '/ping.html',
                text='Mocked ping',
            )

            session = requests.Session()
            session.mount('https', adapter)
            native_vault_client = Production(native_client=session, check_status=False)
            vault_client = VaultClient(native_vault_client=native_vault_client)
            with mock.patch(
                'passport.backend.oauth.tvm_api.tvm_api.db.vault_client.get_vault_client',
                return_value=vault_client,
            ):
                yield adapter

    def register_default_mocks(self, adapter):
        self.vault_register_create_complete_secret_ok(adapter)
        self.vault_register_create_secret_ok(adapter)
        self.vault_register_create_secret_version_ok(adapter)
        self.vault_register_add_user_role_to_secret_ok(adapter)

    def vault_register_create_complete_secret_ok(self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1,
                                                 version_uuid=TEST_VAULT_VERSION_UUID_1):
        adapter.register_uri(
            'POST',
            settings.VAULT_API_URL + '/web/secrets/',
            text=json.dumps(dict(
                status='ok',
                uuid=secret_uuid,
                secret_version=version_uuid,
            )),
        )

    def vault_register_create_complete_secret_error(self, adapter, message='Mocked create secret error',
                                                    code='vault_api_failed', status_code=500, exc=None):
        url = settings.VAULT_API_URL + '/web/secrets/'
        if exc is not None:
            adapter.register_uri(
                'POST',
                url,
                exc=exc,
            )
            return

        adapter.register_uri(
            'POST',
            url,
            status_code=status_code,
            text=json.dumps(dict(
                status='error',
                code=code,
                message=message,
            )),
        )

    def vault_register_create_secret_ok(self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1):
        adapter.register_uri(
            'POST',
            settings.VAULT_API_URL + '/1/secrets/',
            text=json.dumps(dict(
                status='ok',
                uuid=secret_uuid,
            )),
        )

    def vault_register_create_secret_error(self, adapter, message='Mocked create secret error',
                                           status_code=500, exc=None):
        url = settings.VAULT_API_URL + '/1/secrets/'
        if exc is not None:
            adapter.register_uri(
                'POST',
                url,
                exc=exc,
            )
            return

        adapter.register_uri(
            'POST',
            url,
            status_code=status_code,
            text=json.dumps(dict(
                status='error',
                message=message,
            )),
        )

    def vault_register_create_secret_version_ok(
            self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1, version_uuid=TEST_VAULT_VERSION_UUID_1
            ):
        adapter.register_uri(
            'POST',
            settings.VAULT_API_URL + '/1/secrets/{}/versions/'.format(secret_uuid),
            text=json.dumps(dict(
                status='ok',
                secret_version=version_uuid,
            )),
        )

    def vault_register_create_secret_version_error(
            self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1,
            message='Mocked create secret version error', status_code=500,
            exc=None
            ):
        url = settings.VAULT_API_URL + '/1/secrets/{}/versions/'.format(secret_uuid)
        if exc is not None:
            adapter.register_uri(
                'POST',
                url,
                exc=exc,
            )
            return

        adapter.register_uri(
            'POST',
            url,
            status_code=status_code,
            text=json.dumps(dict(
                status='error',
                message=message,
            )),
            exc=exc,
        )

    def vault_register_add_user_role_to_secret_ok(
            self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1,
            ):
        adapter.register_uri(
            'POST',
            settings.VAULT_API_URL + '/1/secrets/{}/roles/'.format(secret_uuid),
            text=json.dumps(dict(
                status='ok',
            )),
        )

    def vault_register_add_user_role_to_secret_error(
            self, adapter, secret_uuid=TEST_VAULT_SECRET_UUID_1,
            message='Mocked add user role to secret error', status_code=400,
            exc=None
            ):
        url = settings.VAULT_API_URL + '/1/secrets/{}/roles/'.format(secret_uuid)
        if exc is not None:
            adapter.register_uri(
                'POST',
                url,
                exc=exc,
            )
            return

        adapter.register_uri(
            'POST',
            url,
            status_code=status_code,
            text=json.dumps(dict(
                status='error',
                message=message,
            )),
            exc=exc,
        )

    def assert_vault_request_equals(self, request, expected):
        local_expected = dict(path='', method='', body='', query='')
        local_expected.update(expected)

        self.assertDictEqual(
            dict(
                path=request.path,
                method=request.method,
                body=request.json(),
                query=request.query,
            ),
            local_expected,
        )
