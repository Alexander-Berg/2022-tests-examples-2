# -*- coding: utf-8 -*-

import time

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.errors import MaximumFieldLengthExceededError
from passport.backend.vault.api.models.secret_version import (
    max_total_key_names_length,
    max_value_length,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestHighloadSecretsView(BaseTestClass):
    fill_database = False
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestHighloadSecretsView, self).setUp()
        self.fixture.add_user(uid=200)

    def test_create_version_with_too_big_value(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    too_big_value = {'key_%d' % i: 'value' for i in range(max_value_length)}
                    r = self.client.create_secret_version(
                        secret,
                        value=too_big_value,
                        return_raw=True,
                    )
                    self.assertResponseError(r, MaximumFieldLengthExceededError)

    def test_create_version_with_too_big_keys(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    too_big_keys = {
                        'a' * (max_total_key_names_length / 2): '1',
                        'b' * (max_total_key_names_length / 2): '1',
                        'cc': '1',
                    }
                    r = self.client.create_secret_version(
                        secret,
                        value=too_big_keys,
                        return_raw=True,
                    )
                    self.assertResponseError(r, MaximumFieldLengthExceededError)

    def test_get_secret_with_many_versions_and_tokens(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    for _ in range(1000):
                        self.client.create_secret_version(secret, {'pass': '12345'})
                        self.client.create_token(secret)

            start = time.time()
            r = self.client.get_secret(secret)
            self.assertLess(time.time() - start, 0.5)

            self.assertEqual(len(r['secret_versions']), 50)
            self.assertEqual(len(r['tokens']), 50)
