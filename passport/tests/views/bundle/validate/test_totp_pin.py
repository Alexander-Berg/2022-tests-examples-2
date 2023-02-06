# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_USER_IP = '37.9.101.188'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts
class TestTotpPinValidate(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['validate']}))

    def assert_ok_response(self, response, pin):
        eq_(response.status_code, 200)
        eq_(
            json.loads(response.data),
            {
                'status': 'ok',
                'pin': pin,
            },
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def make_request(self, data):
        return self.env.client.post(
            '/1/bundle/validate/otp_pin/?consumer=dev',
            data=data,
            headers=build_headers(),
        )

    def test_empty_pin_error(self):
        rv = self.make_request(dict())
        self.assert_error_response(rv, ['pin.empty'])

    def test_invalid_pin_error(self):
        rv = self.make_request(dict(pin='1abc'))
        self.assert_error_response(rv, ['pin.invalid'])

    def test_pin_like_year_error(self):
        rv = self.make_request(dict(pin='1983'))
        self.assert_error_response(rv, ['pin.weak'])

    def test_pin_of_same_digits_error(self):
        rv = self.make_request(dict(pin='7777'))
        self.assert_error_response(rv, ['pin.weak'])

    def test_ok(self):
        rv = self.make_request(dict(pin='0523'))
        self.assert_ok_response(rv, '0523')

    def test_long_pin_ok(self):
        rv = self.make_request(dict(pin='0' * 15 + '1'))
        self.assert_ok_response(rv, '0' * 15 + '1')

    def test_pin_like_phonenumber_ok(self):
        rv = self.make_request(dict(pin='89261234567'))
        self.assert_ok_response(rv, '89261234567')

        rv = self.make_request(dict(pin='79261234567'))
        self.assert_ok_response(rv, '79261234567')
