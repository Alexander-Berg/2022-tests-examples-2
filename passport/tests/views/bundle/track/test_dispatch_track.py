# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_LOGIN,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts
class TestDispatchTrack(BaseBundleTestViews):

    default_url = '/1/bundle/track/dispatch/?consumer=dev'
    http_method = 'POST'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['track.dispatch'])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize', is_short=True)
        self.patches = []

        self.http_headers = dict(
            user_ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            host=TEST_HOST,
            cookie=TEST_USER_COOKIE,
        )
        self.http_query_args = dict(
            track_id=self.track_id,
        )

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches

    def test_redirect_to_auth_forwarding_ok(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.track_type = 'authorize'
            track.source_authid = 'authid'
            track.allow_authorization = True
            track.allow_oauth_authorization = False
            track.uid = str(TEST_UID)
            track.login = TEST_LOGIN

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='forward_auth',
            track_id=self.track_id,
        )

    def test_auth_already_passed(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.track_type = 'authorize'
            track.source_authid = 'authid'
            track.allow_authorization = True
            track.allow_oauth_authorization = False
            track.session = 'session'
            track.uid = str(TEST_UID)
            track.login = TEST_LOGIN

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)

    def test_unknown_track_state(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)
