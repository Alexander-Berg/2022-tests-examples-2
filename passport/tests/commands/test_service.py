# coding: utf-8

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.models import (
    DbPoolUpdates,
    SecretVersion,
)
from passport.backend.vault.api.models.db_pool_updates import get_fqdn
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestServiceCommand(BaseTestClass):
    send_user_ticket = True

    def setUp(self):
        super(TestServiceCommand, self).setUp()
        self.fixture.add_user(uid=200)

    def test_repair_version_with_wrong_keys(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_uuid = self.client.create_secret('ololo-secret')
                    wrong_keys = {
                        'a': 'a',
                        'b': 'b',
                    }
                    version_uuid = self.client.create_secret_version(
                        secret_uuid,
                        value=wrong_keys,
                    )
                    right_secret = self.client.get_secret(secret_uuid)
                    with self.app.app_context():
                        secret_version_model = SecretVersion.get_by_id(version_uuid)
                        secret_version_model._keys = 'c,d'
                        get_db().session.add(secret_version_model)
                        get_db().session.commit()
                    wrong_secret = self.client.get_secret(secret_uuid)
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    self.assertDictEqual(
                        self.client.get_secret(secret_uuid),
                        wrong_secret,
                    )
        self.app.test_cli_runner().invoke(self.cli, ['service', 'repair', version_uuid])
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    self.assertDictEqual(
                        self.client.get_secret(secret_uuid),
                        right_secret,
                    )

    def test_update_db_pool(self):
        with self.app.app_context():
            with TimeMock() as tm:
                result = self.app.test_cli_runner().invoke(self.cli, ['service', 'db_pool_update'])
                self.assertEqual(result.exit_code, 0)
                self.assertDictEqual(
                    DbPoolUpdates.get_current_pool().serialize(),
                    {
                        'fqdn': get_fqdn(),
                        'updated_at': 1445385600.0,
                    },
                )

                tm.tick(145)
                result = self.app.test_cli_runner().invoke(self.cli, ['service', 'db_pool_update'])
                self.assertEqual(result.exit_code, 0)
                self.assertDictEqual(
                    DbPoolUpdates.get_current_pool().serialize(),
                    {
                        'fqdn': get_fqdn(),
                        'updated_at': 1445385745.0,
                    },
                )
