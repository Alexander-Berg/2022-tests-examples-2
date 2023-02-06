# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_

from .base_test_data import (
    TEST_APP_SECRET,
    TEST_APP_SECRET_CONTAINER,
    TEST_PIN_LENGTH,
    TEST_TOTP_SECRET,
)
from .test_base import (
    BaseOtpMigrateTestCase,
    OtpMigrateCommonTests,
)


class OtpMigrateGetSecretTestCase(BaseOtpMigrateTestCase, OtpMigrateCommonTests):

    url = '/1/bundle/otp/migrate/get_secret/?consumer=dev'
    with_check_cookies = True

    def setUp(self):
        super(OtpMigrateGetSecretTestCase, self).setUp()
        urandom_mock = mock.Mock(return_value=TEST_TOTP_SECRET)
        urandom_patch = mock.patch('os.urandom', urandom_mock)
        self.patches.append(urandom_patch)
        urandom_patch.start()

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            app_secret=TEST_APP_SECRET,
            app_secret_container=TEST_APP_SECRET_CONTAINER,
            pin_length=TEST_PIN_LENGTH,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.totp_app_secret, TEST_APP_SECRET)

    def test_ok_for_long_pin(self):
        self.setup_blackbox(attributes={
            'account.2fa_on': '1',
            'account.totp.secret': 'secret',
            'account.totp.secret_ids': '0:0',
            'account.totp.pin_length': '5',
        })
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            app_secret=TEST_APP_SECRET,
            app_secret_container=TEST_APP_SECRET_CONTAINER,
            pin_length=5,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.totp_app_secret, TEST_APP_SECRET)
