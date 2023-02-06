# -*- coding: utf-8 -*-

from django.conf import settings
from django.urls import reverse_lazy
import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.oauth.core.db.eav import DBIntegrityError
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.tvm_api.tests.base.vault_test import (
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_VERSION_UUID_1,
    VaultMockMixin,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient
from passport.backend.utils.logging_mock import LoggingMock
import requests

from .base import (
    BaseTvmAbcTestcaseWithCookieOrToken,
    CommonRobotAuthTests,
    CommonRoleTests,
    TEST_ABC_REQUEST_ID,
    TEST_ABC_SERVICE_ID,
    TEST_OTHER_UID,
    TEST_ROBOT_UID,
)


class CreateClientV1Testcase(BaseTvmAbcTestcaseWithCookieOrToken, CommonRobotAuthTests, CommonRoleTests, VaultMockMixin):
    default_url = reverse_lazy('tvm_abc_create_client_v1')
    http_method = 'POST'
    enable_vault = True

    def setUp(self):
        super(CreateClientV1Testcase, self).setUp()
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_ROBOT_UID,
                scope='login:info',
            ),
        )

    def default_params(self):
        return dict(
            super(CreateClientV1Testcase, self).default_params(),
            name='Test',
            abc_service_id=TEST_ABC_SERVICE_ID,
            abc_request_id=TEST_ABC_REQUEST_ID + 1,
        )

    def default_headers(self):
        headers = super(CreateClientV1Testcase, self).default_headers()
        headers.pop('HTTP_YA_CLIENT_COOKIE')
        headers.update({'HTTP_YA_CONSUMER_AUTHORIZATION': 'OAuth token'})
        return headers

    def test_ok(self):
        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_ok(vault)
            with LoggingMock() as logging_mock:
                rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(rv['client_id'])
        eq_(client.name, 'Test')
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID + 1)
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_1)

        log_entires = [
            entry[0]
            for entry in logging_mock.getLogger('tvm_api.vault_client').entries
            if entry[1] == 'INFO'
        ]
        eq_(len(vault.request_history), 1)
        eq_(len(log_entires), 1)

        self.assert_vault_request_equals(
            vault.request_history[0],
            {
                'body': {
                    'comment': 'TVM-secret, ID %s' % client.id,
                    'name': 'tvm.secret.%s' % client.id,
                    'roles': [
                        dict(role='OWNER', abc_id=client.abc_service_id, abc_role_id=abc_role_id)
                        for abc_role_id in settings.VAULT_SECRET_TVM_ROLES
                    ],
                    'secret_version': {
                        'value': [{
                            'key': 'client_secret',
                            'value': client.client_secret,
                        }],
                    },
                    'tags': settings.VAULT_SECRET_TAGS,
                },
                'method': 'POST',
                'path': '/web/secrets/',
                'query': '',
            },
        )
        self.assertRegexpMatches(
            log_entires[0],
            r'^tskv\telapsed=\d+\.\d+\thttp_status=200\ttimestamp=\d+-\d+-\d+\s\d+:\d+:\d+'
            r'\turl=https://vault-api[^.]*?.passport.yandex.net/web/secrets/'
            r'\tvault_request_id=[0-9a-fA-F]{32}'
            r'\tvault_status=ok'
            r'$',
        )

    def test_unknown_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['abc_team.member_required'])

    def test_vault_create_secret_error(self):
        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_error(vault)
            with LoggingMock() as logging_mock:
                rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(rv['client_id'])
        eq_(client.name, 'Test')
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID + 1)
        eq_(client.vault_secret_uuid, '')
        eq_(client.vault_version_uuid, '')

        eq_(len(vault.request_history), 1)

        log_entires = [
            entry[0]
            for entry in logging_mock.getLogger('tvm_api.vault_client').entries
            if entry[1] == 'INFO'
        ]
        eq_(len(log_entires), 1)

        self.assertRegexpMatches(
            log_entires[0],
            r'^tskv\telapsed=\d+\.\d+\thttp_status=500\ttimestamp=\d+-\d+-\d+\s\d+:\d+:\d+'
            r'\turl=https://vault-api[^.]*?.passport.yandex.net/web/secrets/'
            r'\tvault_error=Mocked create secret error'
            r'\tvault_request_id=[0-9a-fA-F]{32}'
            r'\tvault_status=error'
            r'$',
        )

    def test_vault_client_create_secret_safely_error(self):
        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_error(
                vault,
                status_code=400,
                code='abc_service_not_found',
                message='ABC service not found (abc_id: {})'.format(TEST_ABC_SERVICE_ID),
            )
            with LoggingMock() as logging_mock:
                rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(rv['client_id'])
        eq_(client.name, 'Test')
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID + 1)
        eq_(client.vault_secret_uuid, '')
        eq_(client.vault_version_uuid, '')

        eq_(len(vault.request_history), 1)

        error_log = logging_mock.getLogger('warning')
        eq_(len(error_log.entries), 1)
        eq_(error_log.entries[0][0], 'ABC service not found (abc_id: {})'.format(TEST_ABC_SERVICE_ID))

    def test_vault_client_create_secret_raises_exception(self):
        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_error(vault, exc=requests.exceptions.ConnectTimeout)
            with LoggingMock() as logging_mock:
                rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(rv['client_id'])
        eq_(client.name, 'Test')
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID + 1)
        eq_(client.vault_secret_uuid, '')
        eq_(client.vault_version_uuid, '')

        eq_(len(vault.request_history), 1)

        error_log = logging_mock.getLogger('exception')
        eq_(len(error_log.entries), 1)
        eq_(type(error_log.entries[0][3]['exc_info'][1]).__name__, '_ClientWrappedError')

    def test_tvm_client_create_secret_raises_exception(self):
        with mock.patch(
            'passport.backend.oauth.tvm_api.tvm_api.db.tvm_client.get_vault_client',
            return_value=None,
            side_effect=Exception('Failed to initialize the Vault Client'),
        ):
            with LoggingMock() as logging_mock:
                rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(rv['client_id'])
        eq_(client.name, 'Test')
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID + 1)
        eq_(client.vault_secret_uuid, '')
        eq_(client.vault_version_uuid, '')

        error_log = logging_mock.getLogger('exception')
        eq_(len(error_log.entries), 1)
        eq_(error_log.entries[0][0], 'Failed to initialize the Vault Client')

    def test_request_id_collizion(self):
        with self.vault_mock() as vault:
            self.register_default_mocks(vault)
            rv = self.make_request(abc_request_id=TEST_ABC_REQUEST_ID)

        self.assert_status_ok(rv)

        eq_(rv['client_id'], self.test_client.id)
        client = TVMClient.by_id(rv['client_id'])
        eq_(client.abc_service_id, TEST_ABC_SERVICE_ID)
        eq_(client.abc_request_id, TEST_ABC_REQUEST_ID)

    def test_db_master_slave_discrepancy(self):
        get_dbm('oauthdbcentral').transaction.side_effect = DBIntegrityError
        with self.vault_mock() as vault:
            self.register_default_mocks(vault)
            rv = self.make_request(abc_request_id=TEST_ABC_REQUEST_ID + 1)

        self.assert_status_error(rv, ['backend.failed'])
