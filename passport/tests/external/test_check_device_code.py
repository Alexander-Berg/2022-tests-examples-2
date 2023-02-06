# -*- coding: utf-8 -*-
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.request import (
    accept_request,
    Request,
)
from passport.backend.oauth.core.test.base_test_data import TEST_UID
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


class TestCheckDeviceCode(BundleApiTestCase):
    default_url = reverse_lazy('api_check_device_code')
    http_method = 'GET'

    def setUp(self):
        super(TestCheckDeviceCode, self).setUp()
        with CREATE(Request.create(
            uid=None,
            client=self.test_client,
            is_token_response=False,
        )) as self.token_request:
            pass

        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )

    def default_params(self):
        return {
            'consumer': 'dev',
            'device_code': self.token_request.display_id,
        }

    def test_ok(self):
        accept_request(self.token_request, uid=TEST_UID)

        rv = self.make_request()
        self.assert_response_ok(rv, uid=TEST_UID, scopes=['test:foo', 'test:bar'])

    def test_code_not_found(self):
        rv = self.make_request(device_code='a' * 32)
        self.assert_status_error(rv, ['code.not_found'])

    def test_code_not_accepted(self):
        rv = self.make_request()
        self.assert_status_error(rv, ['code.not_accepted'])

    def test_user_not_found(self):
        accept_request(self.token_request, uid=TEST_UID)
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()
        self.assert_status_error(rv, ['code.not_found'])

    def test_code_invalidated_by_user_glogout(self):
        accept_request(self.token_request, uid=TEST_UID)
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(attributes={
                settings.BB_ATTR_GLOGOUT: time() + 10,
            }),
        )

        rv = self.make_request()
        self.assert_status_error(rv, ['code.not_found'])
