# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


TEST_USER_IP = '37.9.101.188'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts()
class TestSaveTrack(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['track']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/test/track/?consumer=dev',
            data=data,
            headers=headers,
        )

    def request_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def test_empty_request(self):
        resp = self.make_request(self.request_params(), {})

        self.assert_error_response(resp, ['ip.empty'])

    def test_no_track_id_error(self):
        resp = self.make_request(
            {},
            build_headers(),
        )

        self.assert_error_response(resp, ['track_id.empty'])

    def test_ok(self):
        resp = self.make_request(
            self.request_params(is_auth_challenge_shown='1'),
            build_headers(),
        )
        self.assert_ok_response(resp)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_auth_challenge_shown)

    def test_antifraud_tags_ok(self):
        resp = self.make_request(
            self.request_params(antifraud_tags=json.dumps(['call', 'sms'])),
            build_headers(),
        )
        self.assert_ok_response(resp)

        track = self.track_manager.read(self.track_id)
        eq_(track.antifraud_tags, ['call', 'sms'])
