# -*- coding: utf-8 -*-

from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestStatusView(BaseTestClass):
    def setUp(self):
        super(TestStatusView, self).setUp()
        self.DBV = [int(i) for i in self.config['application']['deprecated_before_version'].split('.')]

        self.GOOD_VERSION = map(str, [self.DBV[0], self.DBV[1], self.DBV[2] + 1])
        self.BAD_VERSION = map(str, [
            self.DBV[0] - 1 if self.DBV[1] == 0 and self.DBV[2] == 0 else self.DBV[0],
            self.DBV[1] - 1 if self.DBV[2] == 0 and self.DBV[1] > 0 else self.DBV[1],
            self.DBV[2] - 1 if self.DBV[2] > 0 else self.DBV[2],
        ])

    def test_ok(self):
        self.client.user_agent = 'YandexVaultClient/{version}'.format(version='.'.join(self.GOOD_VERSION))
        r = self.client.get_status()
        self.assertDictEqual(
            r,
            {
                'is_deprecated_client': False,
                'status': 'ok',
            },
        )

    def test_deprecated_version(self):
        self.client.user_agent = 'YandexVaultClient/{version}'.format(version='.'.join(self.BAD_VERSION))
        r = self.client.get_status()
        self.assertDictEqual(
            r,
            {
                'is_deprecated_client': True,
                'status': 'ok',
            },
        )

    def test_unknown_client(self):
        self.client.user_agent = 'UnknownClient/{version}'.format(version='.'.join(self.GOOD_VERSION))
        r = self.client.get_status()
        self.assertDictEqual(
            r,
            {
                'is_deprecated_client': None,
                'status': 'ok',
            },
        )

    def test_status_without_trailing_slash(self):
        r = self.native_client.get('/status')
        self.assertResponseOk(r)
