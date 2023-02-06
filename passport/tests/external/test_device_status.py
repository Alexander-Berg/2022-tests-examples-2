# -*- coding: utf-8 -*-
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.base_test_data import (
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_GRANT_TYPE,
    TEST_OTHER_DEVICE_ID,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


class TestDeviceStatus(BundleApiTestCase):
    default_url = reverse_lazy('api_device_status')
    http_method = 'GET'

    def setUp(self):
        super(TestDeviceStatus, self).setUp()
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'device_id': TEST_DEVICE_ID,
            'device_name': TEST_DEVICE_NAME,
        }

    def test_ok(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id=TEST_DEVICE_ID,
            env=self.env,
        )
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            has_auth_on_device=True,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def test_has_no_tokens(self):
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            has_auth_on_device=False,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def test_has_expired_tokens(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id=TEST_DEVICE_ID,
            env=self.env,
        )
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_REVOKER_TOKENS: time() + 10},
            ),
        )
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            has_auth_on_device=False,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def test_has_tokens_for_other_device(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id=TEST_OTHER_DEVICE_ID,
            env=self.env,
        )
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            has_auth_on_device=False,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def test_has_tokens_for_unknown_device(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        rv = self.make_request(exclude=['device_id', 'device_name'])
        self.assert_response_ok(
            rv,
            has_auth_on_device=False,
            device_id=None,
            device_name=None,
        )
