# -*- coding: utf-8 -*-
import inspect
from os import path

import mock
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.vault.api import get_config
from passport.backend.vault.api.app import (
    create_app,
    create_cli,
)
from passport.backend.vault.api.models import UserRole
from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.fixtures import DbFixture
from passport.backend.vault.api.test.test_client import TestClient
from passport.backend.vault.api.test.test_vault_client import TestVaultClient


class BaseTestClass(BaseTestCase):
    maxDiff = None
    fill_database = True  # Заполнить базу
    fill_staff = False  # Заполнить базу пользователей, если не заполняем базу полностью
    fill_grants = False  # Заполнить базу грантов, если не заполняем базу полностью
    send_user_ticket = False

    def setUp(self):
        super(BaseTestClass, self).setUp()
        self.config = get_config()
        self.config.set_logging()
        self.config.set_as_passport_settings()
        self.app = create_app(self.config)
        self.cli = create_cli(self.app, self.config)
        self.app.testing = True
        self.fixture = DbFixture(self.app, self.config)
        self.fixture.commit()

        if self.fill_database:
            self.fixture.insert_data()
        else:
            if self.fill_staff:
                self.fixture.fill_staff()
            if self.fill_grants:
                self.fixture.fill_grants()

        self.native_client = TestClient(self.app)
        self.client = TestVaultClient(
            native_client=self.native_client,
            user_ticket='user_ticket' if self.send_user_ticket else None,
            service_ticket='service_ticket' if self.send_user_ticket else None,
            rsa_auth=not self.send_user_ticket,
        )
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()

        self.request_id_patch = mock.patch(
            'passport.backend.vault.api.app.get_request_id',
            return_value='fake_request_id',
        )
        self.request_id_patch.start()

    def tearDown(self):
        self.request_id_patch.stop()
        self.fake_tvm.stop()
        self.fixture.rollback()
        super(BaseTestClass, self).tearDown()

    def assertResponseOk(self, response, code=200):
        self.assertEqual(response.status_code, code)

    def assertResponseEqual(self, response, value):
        self.assertDictEqual(response.json(), value)

    def enrich_error_dict(self, error):
        result = dict(error)
        result.setdefault('hostname', self.config.get('hostname'))
        result.setdefault('environment', self.config.get('environment'))
        result.setdefault('api_request_id', 'fake_request_id')
        return result

    def assertResponseError(self, response, exception):
        data = response.json()
        if inspect.isclass(exception):
            self.assertEqual(exception.code, data['code'])
        else:
            self.assertDictEqual(
                data,
                self.enrich_error_dict(
                    exception.as_dict(),
                ),
            )

    def get_roles(self, uid):
        with self.app.app_context():
            return map(
                lambda x: x.role_id,
                list(UserRole.query.filter(
                    UserRole.uid == uid,
                )),
            )

    def shortDescription(self):
        module_path = path.relpath(inspect.getsourcefile(type(self)))
        class_path, method_name = self.id().rsplit('.', 1)
        _, class_name = class_path.rsplit('.', 1)
        return '%s:%s.%s' % (module_path, class_name, method_name)
