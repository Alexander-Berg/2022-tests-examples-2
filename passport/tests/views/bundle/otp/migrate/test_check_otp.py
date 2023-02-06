# -*- coding: utf-8 -*-
import base64

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_data_equals
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_edit_totp_response
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base_test_data import (
    TEST_APP_SECRET,
    TEST_ENCRYPTED_JUNK_SECRET,
    TEST_ENCRYPTED_SECRET,
    TEST_OTP,
    TEST_TOTP_CHECK_TIME,
    TEST_TOTP_SECRET,
    TEST_UID,
)
from .test_base import (
    BaseOtpMigrateTestCase,
    OtpMigrateCommonTests,
)


DB_SHARD_NAME = 'passportdbshard1'


class OtpMigrateCheckOtpTestCase(BaseOtpMigrateTestCase, OtpMigrateCommonTests):

    url = '/1/bundle/otp/migrate/check_otp/?consumer=dev'
    with_check_cookies = True

    def setUp(self):
        super(OtpMigrateCheckOtpTestCase, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.totp_app_secret = TEST_APP_SECRET

        self.env.blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(
                totp_check_time=TEST_TOTP_CHECK_TIME,
                encrypted_secret=TEST_ENCRYPTED_SECRET,
            ),
        )

    def assert_blackbox_edit_totp_called(self, callnum=1):
        args = {
            'uid': TEST_UID,
            'format': 'json',
            'method': 'edit_totp',
            'op': 'replace',
            'old_secret_id': 0,
            'secret_id': 1,
            'secret': base64.urlsafe_b64encode(TEST_TOTP_SECRET).decode().rstrip('='),
            'password': TEST_OTP,
        }
        assert_builder_data_equals(
            self.env.blackbox,
            args,
            callnum=callnum,
        )

    def check_db(self, is_otp_correct=True):
        if is_otp_correct:
            self.env.db.check_missing(
                'attributes',
                'account.totp.junk_secret',
                uid=TEST_UID,
                db=DB_SHARD_NAME,
            )
        else:
            self.env.db.check(
                'attributes',
                'account.totp.junk_secret',
                TEST_ENCRYPTED_JUNK_SECRET,
                uid=TEST_UID,
                db=DB_SHARD_NAME,
            )

    def test_ok(self):
        rv = self.make_request(otp=TEST_OTP)
        self.assert_ok_response(rv, track_id=self.track_id)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_otp_checked)
        eq_(track.totp_secret_encrypted, TEST_ENCRYPTED_SECRET)
        eq_(track.totp_secret_ids, {'1': TimeNow()})
        eq_(track.blackbox_totp_check_time, str(TEST_TOTP_CHECK_TIME))
        assert_is_none(track.invalid_otp_count.get())

        self.assert_blackbox_edit_totp_called()
        self.check_db()

    def test_otp_not_matched__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(
                status=False,
                encrypted_secret=TEST_ENCRYPTED_JUNK_SECRET,
            ),
        )
        rv = self.make_request(otp=TEST_OTP)
        self.assert_error_response(rv, ['otp.not_matched'], track_id=self.track_id, invalid_otp_count=1)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)
        assert_is_none(track.totp_secret_encrypted)
        assert_is_none(track.blackbox_totp_check_time)
        eq_(track.invalid_otp_count.get(), 1)

        self.assert_blackbox_edit_totp_called()
        self.check_db(is_otp_correct=False)

    def test_secret_not_generated__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.totp_app_secret = None

        rv = self.make_request(otp=TEST_OTP)
        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)
