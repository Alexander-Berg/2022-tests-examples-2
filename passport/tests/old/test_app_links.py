# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse
from nose.tools import eq_
from passport.backend.oauth.core.db.eav import (
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.test.framework import ApiTestCase


TEST_APP_ID = 'some-app-id'
TEST_APP_ID_WITH_PREFIX = 'prefix.%s' % TEST_APP_ID
TEST_OTHER_APP_ID = 'app-id-2'
TEST_OTHER_APP_ID_WITH_PREFIX = 'prefix.%s' % TEST_OTHER_APP_ID
TEST_PACKAGE_NAME = 'some-package-name'
TEST_OTHER_PACKAGE_NAME = 'package-name-2'
TEST_FINGERPRINTS = ['some-fingerprint', 'other-fingerprint']


class ListUniversalLinksTestCase(ApiTestCase):
    http_method = 'GET'

    def setUp(self):
        super(ListUniversalLinksTestCase, self).setUp()
        self.default_url = reverse('app_links_ios', args=[self.test_client.display_id])

    def default_params(self):
        return {}

    def test_ok(self):
        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = TEST_APP_ID_WITH_PREFIX
            client.ios_extra_app_ids = [TEST_OTHER_APP_ID_WITH_PREFIX]

        rv = self.make_request()
        eq_(
            rv,
            {
                'applinks': {
                    'apps': [],
                    'details': [
                        {
                            'appID': TEST_APP_ID_WITH_PREFIX,
                            'paths': [
                                '/auth/finish',
                                '/magic-link/%s/finish' % TEST_APP_ID,
                            ],
                        },
                        {
                            'appID': TEST_OTHER_APP_ID_WITH_PREFIX,
                            'paths': [
                                '/auth/finish',
                                '/magic-link/%s/finish' % TEST_OTHER_APP_ID,
                            ],
                        },
                    ],
                },
            },
        )

    def test_universal_links_disabled(self):
        rv = self.make_request(expected_status=403, decode_response=False)
        eq_(rv, 'Universal links disabled for client')

    def test_unknown_client(self):
        with DELETE(self.test_client):
            pass
        rv = self.make_request(expected_status=404, decode_response=False)
        eq_(rv, 'Client not found')

    def test_malformed_client_id(self):
        with override_settings(DEBUG=False):
            rv = self.make_request(
                url='app_links/a-b-c/ios',  # такой урл не среврайтится nginx-ом и попадёт в бэк as-is
                expected_status=404,
                decode_response=False,
            )
        eq_(rv, 'Unknown url')


class ListAppLinksTestCase(ApiTestCase):
    http_method = 'GET'

    def setUp(self):
        super(ListAppLinksTestCase, self).setUp()
        self.default_url = reverse('app_links_android', args=[self.test_client.display_id])

    def default_params(self):
        return {}

    def test_ok(self):
        with UPDATE(self.test_client) as client:
            client.android_default_package_name = TEST_PACKAGE_NAME
            client.android_extra_package_names = [TEST_OTHER_PACKAGE_NAME]
            client.android_cert_fingerprints = TEST_FINGERPRINTS

        rv = self.make_request()
        eq_(
            rv,
            [
                {
                    'relation': [
                        'delegate_permission/common.handle_all_urls',
                    ],
                    'target': {
                        'namespace': 'android_app',
                        'package_name': TEST_PACKAGE_NAME,
                        'sha256_cert_fingerprints': sorted(TEST_FINGERPRINTS),
                    },
                },
                {
                    'relation': [
                        'delegate_permission/common.handle_all_urls',
                    ],
                    'target': {
                        'namespace': 'android_app',
                        'package_name': TEST_OTHER_PACKAGE_NAME,
                        'sha256_cert_fingerprints': sorted(TEST_FINGERPRINTS),
                    },
                },
            ],
        )

    def test_app_links_disabled(self):
        rv = self.make_request(expected_status=403, decode_response=False)
        eq_(rv, 'App links disabled for client')

    def test_unknown_client(self):
        with DELETE(self.test_client):
            pass
        rv = self.make_request(expected_status=404, decode_response=False)
        eq_(rv, 'Client not found')

    def test_malformed_client_id(self):
        with override_settings(DEBUG=False):
            rv = self.make_request(
                url='app_links/a-b-c/android',  # такой урл не среврайтится nginx-ом и попадёт в бэк as-is
                expected_status=404,
                decode_response=False,
            )
        eq_(rv, 'Unknown url')
