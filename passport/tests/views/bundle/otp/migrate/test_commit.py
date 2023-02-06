# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base_test_data import (
    TEST_ENCRYPTED_SECRET,
    TEST_PIN_LENGTH,
    TEST_RETPATH,
    TEST_TOTP_CHECK_TIME,
    TEST_UID,
)
from .test_base import (
    BaseOtpMigrateTestCase,
    OtpMigrateCommonTests,
)


class OtpMigrateCommitTestCase(BaseOtpMigrateTestCase, OtpMigrateCommonTests):

    url = '/1/bundle/otp/migrate/commit/?consumer=dev'
    with_check_cookies = True

    def setUp(self):
        super(OtpMigrateCommitTestCase, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_otp_checked = True
            track.totp_secret_ids = {1: 100}
            track.totp_secret_encrypted = TEST_ENCRYPTED_SECRET
            track.blackbox_totp_check_time = TEST_TOTP_CHECK_TIME
            track.retpath = TEST_RETPATH

    def check_db(self, centraldb_query_count=0, sharddb_query_count=1, sharddb_name='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(sharddb_name), sharddb_query_count)

        self.env.db.check(
            'attributes',
            'account.totp.secret',
            TEST_ENCRYPTED_SECRET,
            uid=TEST_UID,
            db=sharddb_name,
        )
        self.env.db.check(
            'attributes',
            'account.totp.check_time',
            str(TEST_TOTP_CHECK_TIME),
            uid=TEST_UID,
            db=sharddb_name,
        )

    def check_history_db(self, **kwargs):
        base_params = {
            'info.totp_secret.0': '-',
            'info.totp_secret.1': '*',
            'info.totp_update_time': TimeNow(),
            'action': 'migrate_otp',
            'user_agent': 'curl',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            dict(base_params, **kwargs),
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, track_id=self.track_id, retpath=TEST_RETPATH)
        self.assert_statbox_logged(
            with_check_cookies=True,
            action='migrated',
            pin_length=str(TEST_PIN_LENGTH),
        )
        self.check_db()
        self.check_history_db()

        track = self.track_manager.read(self.track_id)
        ok_(not track.allow_authorization)
        ok_(not track.allow_oauth_authorization)

    def test_ok_with_device_info(self):
        app_track_fields = (
            'device_application',
            'device_application_version',
            'device_app_uuid',
            'device_os_id',
            'device_manufacturer',
            'device_hardware_model',
            'device_hardware_id',
            'device_ifv',
        )
        expected_device_info = dict(
            map(
                lambda name: (name, 'test-%s' % name),
                app_track_fields,
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for field_name, value in expected_device_info.items():
                setattr(track, field_name, value)

        rv = self.make_request()
        self.assert_ok_response(rv, track_id=self.track_id, retpath=TEST_RETPATH)
        self.assert_statbox_logged(
            with_check_cookies=True,
            action='migrated',
            pin_length=str(TEST_PIN_LENGTH),
            **expected_device_info
        )
        self.check_db()
        self.check_history_db(app_key_info=json.dumps(expected_device_info, sort_keys=True))

    def test_otp_not_checked__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_otp_checked = False

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)

    def test_encrypted_secret_not_in_track__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.totp_secret_encrypted = None

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)
