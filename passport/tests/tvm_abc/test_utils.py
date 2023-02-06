# -*- coding: utf-8 -*-
from django.conf import settings
from nose.tools import eq_
from passport.backend.oauth.tvm_api.tvm_api.tvm_abc.utils import client_to_response

from .base import (
    BaseTvmAbcTestcase,
    TEST_ABC_REQUEST_ID,
    TEST_ABC_SERVICE_ID,
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_VERSION_UUID_1,
)


class ClientToResponseTestcase(BaseTvmAbcTestcase):
    def test_full(self):
        eq_(
            client_to_response(self.test_client, full_info=True),
            {
                'id': 1,
                'parent': None,
                'url': None,
                'services': [
                    {
                        'abc_service_id': TEST_ABC_SERVICE_ID,
                        'request_id': TEST_ABC_REQUEST_ID,
                    },
                ],
                'name': 'Test Client',
                'attributes': {
                    'client_secret': '{}***{}'.format(
                        self.test_client.client_secret[0],
                        self.test_client.client_secret[-1],
                    ),
                    'old_client_secret': '',
                    'secret_uuid': TEST_VAULT_SECRET_UUID_1,
                    'version_uuid': TEST_VAULT_VERSION_UUID_1,
                    'vault_link': '{}/secret/sec-0000000000000000000000ygj0/explore/'
                                  'version/ver-0000000000000000000000ygj5'.format(settings.VAULT_WEB_URL),
                },
            },
        )

    def test_short(self):
        eq_(
            client_to_response(self.test_client, full_info=False),
            {
                'id': 1,
                'parent': None,
                'url': None,
                'services': [
                    {
                        'abc_service_id': TEST_ABC_SERVICE_ID,
                        'request_id': TEST_ABC_REQUEST_ID,
                    },
                ],
                'name': 'Test Client',
                'attributes': {
                    'secret_uuid': TEST_VAULT_SECRET_UUID_1,
                    'version_uuid': TEST_VAULT_VERSION_UUID_1,
                    'vault_link': '{}/secret/sec-0000000000000000000000ygj0/explore/'
                                  'version/ver-0000000000000000000000ygj5'.format(settings.VAULT_WEB_URL),
                },
            },
        )

    def test_if_version_uuid_is_empty(self):
        self.test_client.vault_version_uuid = ''
        eq_(
            client_to_response(self.test_client, full_info=False),
            {
                'id': 1,
                'parent': None,
                'url': None,
                'services': [
                    {
                        'abc_service_id': TEST_ABC_SERVICE_ID,
                        'request_id': TEST_ABC_REQUEST_ID,
                    },
                ],
                'name': 'Test Client',
                'attributes': {},
            },
        )

    def test_if_secret_uuid_is_empty(self):
        self.test_client.vault_secret_uuid = ''
        eq_(
            client_to_response(self.test_client, full_info=False),
            {
                'id': 1,
                'parent': None,
                'url': None,
                'services': [
                    {
                        'abc_service_id': TEST_ABC_SERVICE_ID,
                        'request_id': TEST_ABC_REQUEST_ID,
                    },
                ],
                'name': 'Test Client',
                'attributes': {},
            },
        )
