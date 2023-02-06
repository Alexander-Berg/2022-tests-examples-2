# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import PROCESS_VOLUNTARY_PASSWORD_CHANGE
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestCaptchaStatus(BaseBundleTestViews):

    default_url = '/1/bundle/captcha/status/'
    http_method = 'get'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'captcha': ['*']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.http_query_args = dict(
            consumer='dev',
            track_id=self.track_id,
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def test_captcha_not_generated(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=False,
            is_required=None,
            is_checked=False,
            is_recognized=False,
        )

    def test_captcha_not_required_not_checked(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = 'key'
            track.is_captcha_required = False

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=True,
            is_required=False,
            is_checked=False,
            is_recognized=False,
        )

    def test_captcha_required_not_checked(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = 'key'
            track.is_captcha_required = True

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=True,
            is_required=True,
            is_checked=False,
            is_recognized=False,
        )

    def test_captcha_required_checked_but_not_recognized(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = 'key'
            track.is_captcha_required = True
            track.is_captcha_checked = True

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=True,
            is_required=True,
            is_checked=True,
            is_recognized=False,
        )

    def test_captcha_required_checked_and_recognized(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = 'key'
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=True,
            is_required=True,
            is_checked=True,
            is_recognized=True,
        )

    def test_with_allowed_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = 'key'
            track.process_name = PROCESS_VOLUNTARY_PASSWORD_CHANGE

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            is_generated=True,
            is_required=None,
            is_checked=False,
            is_recognized=False,
        )
