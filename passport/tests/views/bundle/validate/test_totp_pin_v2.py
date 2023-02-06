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
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


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

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.secure_phone_number = PhoneNumber.parse('+79261234567').e164
            track.country = 'ru'
            track.birthday = '2016-01-01'

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
        del self.track_manager

    def make_request(self, **data):
        return self.env.client.post(
            '/2/bundle/validate/otp_pin/?consumer=dev',
            data=data,
            headers=build_headers(),
        )

    def test_empty_pin_error(self):
        rv = self.make_request(track_id=self.track_id)
        self.assert_error_response(rv, ['pin.empty'])

    def test_invalid_pin_error(self):
        rv = self.make_request(track_id=self.track_id, pin='1abc')
        self.assert_error_response(rv, ['pin.invalid'])

    def test_pin_like_year_error(self):
        rv = self.make_request(track_id=self.track_id, pin='1983')
        self.assert_error_response(rv, ['pin.weak'])

    def test_pin_of_same_digits_error(self):
        rv = self.make_request(track_id=self.track_id, pin='7777')
        self.assert_error_response(rv, ['pin.weak'])

    def test_pin_like_phonenumber_error(self):
        rv = self.make_request(track_id=self.track_id, pin='89261234567')
        self.assert_error_response(rv, ['pin.weak'])

        rv = self.make_request(track_id=self.track_id, pin='79261234567')
        self.assert_error_response(rv, ['pin.weak'])

    def test_pin_like_birthday_error(self):
        rv = self.make_request(track_id=self.track_id, pin='01012016')
        self.assert_error_response(rv, ['pin.weak'])

        rv = self.make_request(track_id=self.track_id, pin='010116')
        self.assert_error_response(rv, ['pin.weak'])

    def test_ok(self):
        rv = self.make_request(track_id=self.track_id, pin='0523')
        self.assert_ok_response(rv, '0523')

    def test_long_pin_ok(self):
        rv = self.make_request(track_id=self.track_id, pin='0' * 15 + '1')
        self.assert_ok_response(rv, '0' * 15 + '1')
