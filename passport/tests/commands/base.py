# coding: utf-8

import contextlib
import os
import time

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api import get_config
from passport.backend.vault.api.app import create_app
from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.fixtures import DbFixture
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    TEST_RSA_LOGIN_1,
    TEST_RSA_PRIVATE_KEY_1,
    TEST_RSA_PUBLIC_KEY_1,
    VALID_USER_TICKET_1,
)
from passport.backend.vault.api.test.test_client import TestClient
from passport.backend.vault.api.test.uuid_mock import UuidMock
from passport.backend.vault.api.test.vault_cli_runner import CLIRunner
import six
from vault_client_cli.client import (
    CLIVaultClient,
    VaultClient,
)
from vault_client_cli.manager import VaultCLIManager


class BaseCLICommandTestCase(BaseTestCase):
    fill_database = True
    fill_external_data = True
    maxDiff = None

    def setUp(self):
        super(BaseCLICommandTestCase, self).setUp()
        self.config = get_config()
        self.app = create_app(self.config)
        self.native_client = TestClient(self.app)
        self.vault_client = VaultClient(
            native_client=self.native_client,
            user_ticket=VALID_USER_TICKET_1,
        )
        self.old_tz = os.environ.get('TZ', '')
        # Фиксируем таймзону на MSK, чтобы не ломалось форматирование времени
        os.environ['TZ'] = 'MSK'
        time.tzset()

        self.maxDiff = None
        self.client = CLIVaultClient(
            vault_client=VaultClient(
                native_client=self.native_client,
                rsa_auth=getattr(self, 'rsa_auth', True),
                rsa_login=getattr(self, 'rsa_login', None),
            ),
        )
        self.stdout = six.BytesIO()
        self.manager = VaultCLIManager(client=self.client, stdout=self.stdout, stderr=self.stdout)
        self.runner = CLIRunner(
            cli_manager=self.manager,
            mix_stderr=True,
            stdout=self.stdout,
        )

        self.app.testing = True
        self.fixture = DbFixture(self.app, self.config)
        self.fixture.create_tables()
        if self.fill_database:
            self.fixture.insert_data()
        elif self.fill_external_data:
            self.fixture.fill_abc()
            self.fixture.fill_staff()
            self.fixture.fill_grants()

    def tearDown(self):
        self.fixture.rollback()
        self.fixture.drop_tables()
        os.environ['TZ'] = self.old_tz
        time.tzset()
        super(BaseCLICommandTestCase, self).tearDown()

    @contextlib.contextmanager
    def time_mock(self, offset=15):
        with TimeMock(offset=offset) as t:
            yield t

    @contextlib.contextmanager
    def uuid_mock(self, base_value=2000000):
        with UuidMock(base_value=base_value):
            yield

    @contextlib.contextmanager
    def user_permissions_and_time_mock(self, uid=100):
        with PermissionsMock(uid=uid):
            with self.time_mock() as t:
                yield t


class BaseCLICommandRSATestCaseMixin(object):
    rsa_auth = TEST_RSA_PRIVATE_KEY_1
    rsa_login = TEST_RSA_LOGIN_1

    @contextlib.contextmanager
    def rsa_permissions_and_time_mock(self, uid=100, offset=15):
        with PermissionsMock(rsa={'uid': uid, 'keys': [TEST_RSA_PUBLIC_KEY_1]}):
            with self.time_mock(offset=offset) as t:
                yield t
