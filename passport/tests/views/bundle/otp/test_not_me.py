# -*- coding: utf-8 -*-
from time import time

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_IP = '127.0.0.1'


@with_settings_hosts(
    KOLMOGOR_URL='http://localhost',
)
class TestNotMe(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/auth/otp/not_me/'
    http_method = 'POST'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['app']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args.update(track_id=self.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_allow_otp_magic = True
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = time() + 60

        self.env.kolmogor.set_response_side_effect('inc', ['OK'])
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_IP,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'otp_auth_user_denied',
            action='otp_auth_user_denied',
        )

    def test_invalid_track_state_permanent_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False

        rv = self.make_request()
        self.assert_error_response(rv, ['internal.permanent'])

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)
        eq_(track.correct_2fa_picture_expires_at, TimeNow())

        eq_(len(self.env.kolmogor.requests), 1)
        self.env.kolmogor.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/inc',
            post_args={
                'space': settings.YAKEY_2FA_PICTURES_SHOWN_KEYSPACE,
                'keys': settings.YAKEY_2FA_PICTURES_DENY_FLAG_COUNTER % TEST_UID,
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_user_denied'),
        ])
