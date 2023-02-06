# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import PROCESS_LOGIN_RESTORE
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_HOST,
    TEST_IP,
    TEST_RETPATH,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_GPS_PACKAGE_NAME
from passport.backend.api.views.bundle.restore.login.controllers import RESTORE_STATE_SUBMITTED
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .test_base import LoginRestoreBaseTestCase


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    **mock_counters()
)
class LoginRestoreSubmitTestCase(LoginRestoreBaseTestCase):

    restore_step = 'submit'

    default_url = '/1/bundle/restore/login/submit/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    http_query_args = dict(retpath=TEST_RETPATH)

    def setUp(self):
        super(LoginRestoreSubmitTestCase, self).setUp()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        super(LoginRestoreSubmitTestCase, self).tearDown()

    def test_submit_passed(self):
        """Submit пройден"""
        resp = self.make_request()

        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_updated(
            is_created=True,
            restore_state=RESTORE_STATE_SUBMITTED,
            retpath=TEST_RETPATH,
            created=TimeNow(),
            is_captcha_required=True,
            process_name=PROCESS_LOGIN_RESTORE,
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
            phone_operation_confirmations=[],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed'),
        ])

    def test_submit_passed_with_gps_package_name(self):
        """Submit пройден, gps_package_name сохранен в трек"""
        resp = self.make_request(query_args={'gps_package_name': TEST_GPS_PACKAGE_NAME})

        self.assert_ok_response(resp, track_id=self.track_id)
        self.assert_track_updated(
            is_created=True,
            restore_state=RESTORE_STATE_SUBMITTED,
            retpath=TEST_RETPATH,
            created=TimeNow(),
            is_captcha_required=True,
            process_name=PROCESS_LOGIN_RESTORE,
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
            phone_operation_confirmations=[],
            gps_package_name=TEST_GPS_PACKAGE_NAME,
        )
