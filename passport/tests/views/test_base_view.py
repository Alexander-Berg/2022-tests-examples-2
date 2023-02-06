# -*- coding: utf-8 -*-

import json
from sqlite3 import OperationalError

import mock
from passport.backend.vault.api import errors
from passport.backend.vault.api.models import TvmGrants
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.open_mock import OpenMock
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_RSA_PRIVATE_KEY_1,
    VALID_SERVICE_TICKET_1,
    VALID_SERVICE_TICKET_SINGLESS_1,
    VALID_USER_TICKET_SIGNLESS_1,
)
from passport.backend.vault.api.views import PingView
from sqlalchemy.exc import OperationalError as SAOperationalError


FILE_VAULT_TICKETS = {
    "tickets": {},
    "client_secret": "AAAAAAAAAAAAAAAAAAAAAA",
    "client_id": 2000733,
}


class TestBaseView(BaseTestClass):
    fill_database = False

    def setUp(self):
        super(TestBaseView, self).setUp()
        self.vault_ticket_mock = OpenMock({
            '/var/cache/yandex/passport-tvm-keyring/%s.tickets' % self.config['application']['tvm_keyring_config_name']:
            json.dumps(FILE_VAULT_TICKETS),
        })
        self.vault_ticket_mock.start()

    def tearDown(self):
        self.vault_ticket_mock.stop()
        super(TestBaseView, self).tearDown()

    def test_with_malformed_user_ticket(self):
        self.fixture.fill_grants()
        self.client.rsa_auth = False
        self.client.service_ticket = VALID_SERVICE_TICKET_1
        self.client.user_ticket = 'malformed_user_ticket'
        with PermissionsMock():
            self.assertResponseError(
                self.client.list_secrets(return_raw=True),
                errors.UserTicketParsingError(
                    ticket_message=u'Malformed ticket',
                    ticket_status=5,
                ),
            )

    def test_requires_grants_error(self):
        self.fixture.fill_grants()
        self.client.rsa_auth = False
        with PermissionsMock(uid=100, tvm_client_id=2):
            self.assertResponseError(
                self.client.list_secrets(return_raw=True),
                errors.TvmGrantRequiredError(
                    tvm_client_id=2,
                ),
            )

    def test_grant_and_revoke_grants(self):
        self.fixture.fill_grants()
        self.client.rsa_auth = False
        with self.app.app_context():
            with PermissionsMock(uid=100, tvm_client_id=2):
                self.assertResponseError(
                    self.client.list_secrets(return_raw=True),
                    errors.TvmGrantRequiredError(
                        tvm_client_id=2,
                    ),
                )

                TvmGrants.grant(2)
                self.assertResponseOk(
                    self.client.list_secrets(return_raw=True),
                )

                TvmGrants.revoke(2)
                self.assertResponseError(
                    self.client.list_secrets(return_raw=True),
                    errors.TvmGrantRequiredError(
                        tvm_client_id=2,
                    ),
                )

    def test_skip_grants(self):
        self.fixture.fill_grants()
        self.client.rsa_auth = False
        old_config_value = self.config['tvm_grants']['skip_grants']
        self.config['tvm_grants']['skip_grants'] = True
        try:
            with LoggingMock() as logging_mock:
                with PermissionsMock(uid=100, tvm_client_id=2):
                    self.assertResponseOk(
                        self.client.list_secrets(return_raw=True),
                    )
                self.assertListEqual(
                    logging_mock.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 2,
                       'auth_type': 'user_ticket',
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'list_secrets',
                       'tvm_grants': 'required',
                       'auth_uid': 100},
                      'INFO',
                      None,
                      None),
                     ({'action': 'success',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 2,
                       'auth_type': 'user_ticket',
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'form_asc': False,
                       'form_order_by': 'created_at',
                       'form_page': 0,
                       'form_page_size': 50,
                       'form_query_type': 'infix',
                       'form_with_hidden_secrets': False,
                       'form_with_tvm_apps': False,
                       'form_without': '',
                       'form_yours': False,
                       'mode': 'list_secrets',
                       'results_count': 0,
                       'tvm_grants': 'required',
                       'auth_uid': 100},
                      'INFO',
                      None,
                      None),
                     ({'action': 'exit',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 2,
                       'auth_type': 'user_ticket',
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'list_secrets',
                       'tvm_grants': 'required',
                       'auth_uid': 100},
                      'INFO',
                      None,
                      None)]
                )
        finally:
            self.config['tvm_grants']['skip_grants'] = old_config_value

    def test_with_missing_service_ticket(self):
        self.client.rsa_auth = False
        self.client.user_ticket = 'malformed_user_ticket'
        self.client.service_ticket = ''
        self.assertResponseError(
            self.client.list_secrets(return_raw=True),
            errors.ServiceTicketRequiredError(),
        )

    def test_skip_fail_if_missing_service_ticket(self):
        self.client.rsa_auth = False
        self.client.service_ticket = ''
        old_config_value = self.config['tvm_grants']['fail_if_service_ticket_missing']
        self.config['tvm_grants']['fail_if_service_ticket_missing'] = False
        try:
            with PermissionsMock(uid=100, service_ticket=None):
                self.assertResponseOk(
                    self.client.list_secrets(return_raw=True),
                )
        finally:
            self.config['tvm_grants']['fail_if_service_ticket_missing'] = old_config_value

    def test_with_malformed_service_ticket(self):
        self.client.rsa_auth = False
        self.client.user_ticket = 'malformed_user_ticket'
        self.client.service_ticket = 'malformed_service_ticket'
        self.assertResponseError(
            self.client.list_secrets(return_raw=True),
            errors.ServiceTicketParsingError(
                ticket_message=u'Malformed ticket',
                ticket_status=5,
            ),
        )

    def test_without_user_ticket(self):
        with mock.patch.object(PingView, 'required_user_auth', return_value=True):
            self.client.rsa_auth = False
            r = self.client.ping()
            self.assertResponseError(r, errors.UserAuthRequiredError)

    def test_ping_error(self):
        with mock.patch.object(PingView, 'process_request', side_effect=RuntimeError):
            r = self.client.ping()
            self.assertResponseEqual(r, self.enrich_error_dict({
                'code': 'internal_server_error',
                'message': 'Internal server error',
                'status': 'error',
            }))

    def test_database_failed(self):
        with mock.patch.object(
            PingView,
            'process_request',
            side_effect=SAOperationalError(None, None, OperationalError('Cannot connect to database (operation timeout)')),
        ):
            with LoggingMock() as log:
                r = self.client.ping()
                self.assertResponseEqual(r, self.enrich_error_dict({
                    'code': 'service_temporary_down',
                    'message': 'Service temporary down',
                    'status': 'error'
                }))
                self.assertListEqual(
                    log.getLogger('statbox').entries,
                    [({'action': 'enter', 'mode': 'ping'}, 'INFO', None, None),
                     (
                        {
                            'action': 'error',
                            'code': 'service_temporary_down',
                            'exception': '(_sqlite3.OperationalError) Cannot connect to database (operation timeout) (Background on this error at: http://sqlalche.me/e/e3q8)',
                            'message': 'Service temporary down',
                            'mode': 'ping',
                            'status': 'error',
                            'use_slave': True,
                        },
                        'INFO', None, None,
                    )],
                )

    def test_send_json_request_with_empty_body(self):
        self.fixture.insert_data()
        with PermissionsMock(uid=100):
            response = self.native_client.get(
                '/1/secrets/',
                content_type='application/json',
                data='')
        self.assertEqual(response.status_code, 200)


class TestBaseAccess(BaseTestClass):
    send_user_ticket = True

    def test_get_groups(self):
        with PermissionsMock(uid=100, ssh_agent_key=TEST_RSA_PRIVATE_KEY_1):
            secret_uuid_1 = self.client.create_secret('secret-1')
            secret_uuid_2 = self.client.create_secret('secret-2')
            secret_uuid_3 = self.client.create_secret('secret-3')
            self.client.add_user_role_to_secret(secret_uuid_1, role='OWNER', abc_id=14)
            self.client.add_user_role_to_secret(secret_uuid_2, role='READER', staff_id=4112)

        with PermissionsMock(uid=1120000000038274):
            self.client.get_secret(secret_uuid_1)
            self.client.get_secret(secret_uuid_2)
            r = self.client.get_secret(secret_uuid_3, return_raw=True)
            self.assertResponseError(r, errors.AccessError)
